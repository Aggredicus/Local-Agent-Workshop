#!/usr/bin/env bash
# Trusted recovery entrypoint. Does not execute scripts supplied by the package bundle.
set -euo pipefail
export LC_ALL=C
fail() { printf 'STOP: %s\n' "$1" >&2; exit 2; }
action=${1:-}
[[ "$action" == verify || "$action" == install ]] || fail 'Usage: packages.sh verify|install BUNDLE_DIRECTORY'
bundle=$(realpath -- "${2:?bundle directory required}")
[[ -d "$bundle/metadata" && -d "$bundle/packages" ]] || fail 'Incomplete bundle.'
[[ "$action" != install || $EUID == 0 ]] || fail 'Install requires sudo at the local console.'
for command in sha256sum dpkg-deb awk date; do command -v "$command" >/dev/null || fail "Missing $command; use authenticated Debian media or temporary Ethernet."; done
. /etc/os-release
[[ "$ID" == debian ]] || fail 'Target is not Debian.'
case "$VERSION_ID" in 12) codename=bookworm ;; 13) codename=trixie ;; *) fail 'Only Debian 12/13 are supported.' ;; esac
arch=$(dpkg --print-architecture)
[[ "$arch" == amd64 ]] || fail 'This first bundle supports amd64 only.'
if command -v gpgv >/dev/null; then verifier=gpgv; elif command -v sqv >/dev/null; then verifier=sqv; else fail "Missing gpgv/sqv; use authenticated Debian media."; fi
keyring=/usr/share/keyrings/debian-archive-keyring.gpg
[[ -r "$keyring" ]] || fail 'Trusted Debian archive keyring is absent. Never trust a replacement key from the USB bundle.'
[[ $(date +%s) -gt 1735689600 ]] || fail 'Correct the system clock before verifying package freshness.'
# Bound untrusted staging before copying anything. These recovery bundles are <150 MiB.
bytes=0; files=0
for source in "$bundle"/metadata/* "$bundle"/packages/*; do
    [[ -f "$source" && ! -L "$source" ]] || fail 'Bundle contains a missing, linked or special payload.'
    size=$(stat -c %s -- "$source")
    [[ $size -le 134217728 ]] || fail 'Oversized payload.'
    bytes=$((bytes + size)); files=$((files + 1))
done
[[ $bytes -le 536870912 && $files -le 1024 ]] || fail 'Bundle exceeds recovery staging limits.'
free=$(df -Pk /tmp | awk 'NR==2 {print $4}')
[[ $((free * 1024)) -ge 805306368 ]] || fail 'Insufficient temporary disk space.'
stage=$(mktemp -d /tmp/law-usb-packages.XXXXXXXX)
trap 'rm -rf -- "$stage"' EXIT
chmod 700 "$stage"
mkdir "$stage/metadata" "$stage/packages"
copied=0
# Copy only expected payload types into protected storage before trusting or installing them.
# GNU dd refuses links and bounds file growth; private copies are verified before use.
for source in "$bundle"/metadata/* "$bundle"/packages/*; do
    [[ -f "$source" && ! -L "$source" ]] || fail 'Bundle contains a missing, linked or special payload.'
    case "$source" in
        "$bundle"/metadata/*) name=${source##*/}; [[ "$name" =~ ^index-[0-9]+\.(InRelease|Packages)$ ]] || fail 'Unexpected metadata filename.'; target="$stage/metadata/$name" ;;
        "$bundle"/packages/*) name=${source##*/}; [[ "$name" =~ ^[A-Za-z0-9.+_%:~=-]+\.deb$ ]] || fail 'Unexpected package filename.'; target="$stage/packages/$name" ;;
    esac
    # GNU dd bounds growth and refuses symlink opens, even if the source changes.
    limit=$((536870912 - copied))
    [[ $limit -le 134217728 ]] || limit=134217728
    [[ $limit -gt 0 ]] || fail 'Bundle exceeded its total size limit.'
    timeout 30 dd if="$source" of="$target" iflag=nofollow,nonblock,count_bytes count=$((limit + 1)) bs=1048576 status=none || fail 'Payload copy failed.'
    actual=$(stat -c %s -- "$target")
    [[ $actual -le $limit ]] || fail 'Payload grew beyond its size limit.'
    copied=$((copied + actual))
    [[ $copied -le 536870912 ]] || fail 'Bundle grew beyond the total limit.' 
    [[ -f "$target" && ! -L "$target" ]] || fail 'Payload changed while copying.'
done
mkdir "$stage/apt-lists"
: > "$stage/apt-sources.list"
: > "$stage/authenticated-hashes"
indexes=0
for signed in "$stage"/metadata/*.InRelease; do
    release="$stage/release-$indexes"
    if [[ "$verifier" == gpgv ]]; then
        gpgv --keyring "$keyring" --output "$release" "$signed" >/dev/null 2>&1 || fail 'Debian release signature verification failed.'
    else
        sqv --keyring "$keyring" --output "$release" --cleartext "$signed" >/dev/null 2>&1 || fail 'Debian release signature verification failed.'
    fi
    release_codename=$(awk -F': ' '$1=="Codename" {print $2}' "$release")
    [[ "$release_codename" == "$codename" || "$release_codename" == "$codename-updates" || "$release_codename" == "$codename-security" ]] || fail 'Bundle release does not match the installed Debian version.'
    issued=$(awk -F': ' '$1=="Date" {print $2}' "$release")
    issued_epoch=$(date -d "$issued" +%s) || fail 'Invalid signed release date.'
    now=$(date +%s)
    [[ $issued_epoch -le $((now + 86400)) && $issued_epoch -ge $((now - 31968000)) ]] || fail 'Signed metadata is too old or the clock is wrong.'
    expires=$(awk -F': ' '$1=="Valid-Until" {print $2}' "$release")
    if [[ -n "$expires" ]]; then [[ $(date -d "$expires" +%s) -ge $now ]] || fail 'Signed metadata expired; prepare a fresh bundle.'; fi
    list=${signed%.InRelease}.Packages
    [[ -f "$list" ]] || fail 'Missing package index.'
    expected=$(awk -v path="main/binary-$arch/Packages" '$0=="SHA256:" {section=1;next} section && /^[^ ]/ {section=0} section && $3==path {print $1; count++} END {if(count!=1)exit 1}' "$release") || fail 'Signed release has no unique uncompressed package index hash.'
    [[ $(sha256sum "$list" | awk '{print $1}') == "$expected" ]] || fail 'Package index integrity failure.'
    awk '$1=="SHA256:" {print $2}' "$list" >> "$stage/authenticated-hashes"
    origin=debian
    [[ "$release_codename" != *-security ]] || origin=debian-security
    prefix="deb.debian.org_${origin}_dists_${release_codename}"
    cp -- "$signed" "$stage/apt-lists/${prefix}_InRelease"
    cp -- "$list" "$stage/apt-lists/${prefix}_main_binary-${arch}_Packages"
    printf 'deb [signed-by=%s] http://deb.debian.org/%s %s main\n' "$keyring" "$origin" "$release_codename" >> "$stage/apt-sources.list"
    indexes=$((indexes + 1))
done
[[ $indexes -gt 0 ]] || fail 'No signed indexes.'
count=0
: > "$stage/package-plan"
: > "$stage/package-inventory"
for package in "$stage"/packages/*.deb; do
    sum=$(sha256sum "$package" | awk '{print $1}')
    grep -Fxq "$sum" "$stage/authenticated-hashes" || fail 'Package is not authenticated by the signed Debian indexes.'
    package_arch=$(dpkg-deb -f "$package" Architecture)
    [[ "$package_arch" == "$arch" || "$package_arch" == all ]] || fail 'Wrong package architecture.'
    dpkg-deb -f "$package" Package Version >> "$stage/package-plan"
    printf '%s|%s|%s\n' "$(dpkg-deb -f "$package" Package)" "$(dpkg-deb -f "$package" Version)" "$package_arch" >> "$stage/package-inventory"
    count=$((count + 1))
done
[[ $count -gt 0 ]] || fail 'No packages.'
# Solve only a fixed recovery root set against the authenticated indexes.
# Extra authenticated .debs cannot make an unrelated service/runtime an install target.
roots=(age python3 wpasupplicant ifupdown isc-dhcp-client iproute2 iputils-ping pciutils usbutils)
[[ "$verifier" != gpgv ]] || roots+=(gpgv)
mkdir "$stage/empty.sources.d"
options=(-o "Dir::Cache::archives=$stage/packages" -o "Dir::Etc::sourcelist=$stage/apt-sources.list" -o "Dir::Etc::sourceparts=$stage/empty.sources.d" -o "Dir::State::lists=$stage/apt-lists")
apt-get "${options[@]}" -o Dir::State::status=/dev/null --simulate --no-download --no-install-recommends install "${roots[@]}" > "$stage/closure-plan" || fail 'Recovery dependency closure cannot be resolved.'
awk '/^Inst / {name=$2; sub(/:[a-z0-9]+$/,"",name); for(i=3;i<=NF;i++) if(substr($i,1,1)=="(") {version=substr($i,2); sub(/\)$/,"",version); print name "|" version; break}}' "$stage/closure-plan" > "$stage/required"
while IFS='|' read -r name version; do
    awk -F'|' -v name="$name" -v version="$version" '$1==name && $2==version {found=1} END{exit !found}' "$stage/package-inventory" || fail 'Bundle is missing an exact package in the recovery dependency closure.'
done < "$stage/required"
printf 'VERIFIED: %s Debian %s/%s packages; complete recovery dependency closure authenticated.\n' "$count" "$VERSION_ID" "$arch"
[[ "$action" == install ]] || exit 0
[[ -z $(dpkg --audit) ]] || fail 'Interrupted dpkg transaction detected; diagnose it before provisioning.'
apt-get "${options[@]}" --simulate --no-download --no-remove --no-install-recommends install "${roots[@]}" > "$stage/install-plan" || fail 'Installed packages conflict with this recovery plan; no changes applied.'
printf '\nActual APT plan (package maintainer scripts run as root):\n'
cat "$stage/install-plan"
printf '\nThis fixed recovery set does not install Docker, NetworkManager or an SSH server. Existing packages are never removed.\n'
read -r -p 'Type INSTALL to install the verified local packages: ' answer
[[ "$answer" == INSTALL ]] || fail 'Cancelled; no package changes applied.'
apt-get "${options[@]}" -y --no-install-recommends --no-download --no-remove install "${roots[@]}"
printf 'Recovery tools installed. Run inspect.sh, then pair the encrypted Wi-Fi transfer.\n'
