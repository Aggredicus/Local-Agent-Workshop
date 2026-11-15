#!/bin/bash
# Only runs inside the pinned, disposable Debian 13 builder container.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive LC_ALL=C
[[ -e /.dockerenv ]] && . /etc/os-release && [[ $ID == debian && $VERSION_ID == 13 ]]
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg python3
curl --fail --location --proto '=https' --tlsv1.2 https://download.docker.com/linux/debian/gpg -o /output/docker.asc
fingerprint=$(gpg --batch --show-keys --with-colons /output/docker.asc | awk -F: '$1=="fpr" {print $10; exit}')
[[ $fingerprint == 9DC858229FC7DD38854AE2D88D81803C0EBFCD88 ]] || { echo 'Docker signing-key fingerprint mismatch' >&2; exit 2; }
gpg --batch --dearmor --output /output/docker.gpg /output/docker.asc
printf 'deb [arch=amd64 signed-by=/output/docker.gpg] https://download.docker.com/linux/debian trixie stable\n' > /etc/apt/sources.list.d/docker.list
apt-get update
mkdir -p /output/downloads
mapfile -t roots < <(PYTHONPATH=/source/src python3 -c 'from workshop.iso.profile import BUILD_ROOTS; print("\n".join(BUILD_ROOTS))')
apt-get -o Dir::State::status=/dev/null -o Dir::Cache::archives=/output/downloads --download-only -y --no-install-recommends install "${roots[@]}"
PYTHONPATH=/source/src python3 -m workshop.iso.repository /output
rm -f /output/downloads/lock
rm -rf /output/downloads/partial
