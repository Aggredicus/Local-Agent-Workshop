#!/usr/bin/env bash
# Read-only local diagnostics. No raw network configs, passphrases or logs are emitted.
set -u
export LC_ALL=C
printf 'Local Agent Workshop USB recovery — read-only inspection\n'
printf 'Debian release: '
if [[ -r /etc/debian_version ]]; then cat /etc/debian_version; else printf 'not detected\n'; fi
printf 'Architecture: '
if command -v dpkg >/dev/null; then dpkg --print-architecture; else uname -m; fi
printf 'Kernel: '; uname -r
printf 'Firmware boot mode: '
if [[ -d /sys/firmware/efi ]]; then printf 'UEFI\n'; else printf 'BIOS or undetectable in this environment\n'; fi
printf '\nAvailable tools:\n'
for tool in bash apt-get dpkg-deb gpgv sha256sum python3 ip wpa_supplicant nmcli ifquery networkctl dhclient ssh sshd; do
    if command -v "$tool" >/dev/null 2>&1; then printf '  %-18s available\n' "$tool"; else printf '  %-18s MISSING\n' "$tool"; fi
done
printf '\nInterfaces (no network configuration is changed):\n'
if command -v ip >/dev/null; then ip -brief address; else printf '  iproute2 is missing\n'; fi
for path in /sys/class/net/*; do
    [[ -e "$path" ]] || continue
    iface=${path##*/}
    [[ "$iface" == lo ]] && continue
    kind=wired-or-virtual
    [[ -d "$path/wireless" ]] && kind=wireless
    printf '  %s: %s\n' "$iface" "$kind"
    if command -v ifquery >/dev/null; then ifquery --list 2>/dev/null | awk -v iface="$iface" '$0==iface { print "    ifupdown knows this interface" }'; fi
    if command -v networkctl >/dev/null; then
        networkctl status "$iface" --no-pager 2>/dev/null | awk '/Network File:/ {print "    " $0}'
    fi
    if command -v nmcli >/dev/null; then
        nmcli -g GENERAL.STATE device show "$iface" 2>/dev/null | awk 'NF {print "    NetworkManager state: " $0}'
    fi
done
printf '\nHardware IDs (share these to identify a missing firmware package):\n'
if command -v lspci >/dev/null; then lspci -nn | awk '/[Nn]etwork|[Ee]thernet|[Ww]ireless/'; fi
if command -v lsusb >/dev/null; then lsusb; fi
printf '\nRoot filesystem space:\n'; df -h /
printf '\nPackage-manager interrupted transactions:\n'
if command -v dpkg >/dev/null; then dpkg --audit; fi
printf '\nNext: use the guide in setup/usb/README.md. No changes were applied.\n'
