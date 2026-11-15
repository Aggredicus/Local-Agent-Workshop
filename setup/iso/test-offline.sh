#!/bin/bash
# Disposable network-disabled container; never a host installer.
set -euo pipefail
[[ -f /.dockerenv ]]
mkdir -p /opt/law-offline
cp -a /law/repositories /law/docker.gpg /law/roots.txt /opt/law-offline/
mkdir -p /etc/apt/law.sources.d
sed -n "/^Types: deb/,/^EOF$/p" /law/source/setup/iso/install-law.sh | sed '$d' > /etc/apt/law.sources.d/offline.sources
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 0755 /usr/sbin/policy-rc.d
export DEBIAN_FRONTEND=noninteractive
opts=(-o Dir::Etc::sourcelist=/dev/null -o Dir::Etc::sourceparts=/etc/apt/law.sources.d -o Acquire::Languages=none)
apt-get "${opts[@]}" update
if [[ ${1:-} == --tamper ]]; then
    # Verify rejection through real APT, not our own hash-only assertion.
    files=(/opt/law-offline/repositories/debian/pool/main/a/age/age_*.deb)
    [[ ${#files[@]} == 1 && -f ${files[0]} ]]
    printf 'tampered' >> "${files[0]}"
    if apt-get "${opts[@]}" --no-remove --no-install-recommends -y install age > /tmp/rejection.log 2>&1; then
        echo 'ERROR: APT accepted a modified signed-repository package.' >&2
        exit 2
    fi
    grep -Eqi 'hash sum mismatch|unexpected size|hashes of expected file' /tmp/rejection.log
    echo LAW_OFFLINE_TAMPER_REJECTED
    exit 0
fi
mapfile -t roots < /law/roots.txt
apt-get "${opts[@]}" --no-remove --no-install-recommends -y install "${roots[@]}"
docker --version
docker compose version
docker buildx version
PYTHONPATH=/law/source/src python3 -m workshop --help
echo LAW_OFFLINE_APT_TEST_OK
