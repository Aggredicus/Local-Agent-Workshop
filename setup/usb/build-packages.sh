#!/usr/bin/env bash
# Runs only in a disposable official Debian container, invoked by workshop usb bundle.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive LC_ALL=C
[[ -f /.dockerenv ]] || { echo 'Use the documented disposable builder container.' >&2; exit 2; }
. /etc/os-release
[[ "$ID" == debian && ( "$VERSION_ID" == 12 || "$VERSION_ID" == 13 ) ]] || exit 2
arch=$(dpkg --print-architecture)
[[ "$arch" == amd64 ]] || { echo 'This first recovery bundle is validated for amd64 only.' >&2; exit 2; }
mkdir -p /output/packages /output/metadata
apt-get update
apt-get install -y --no-install-recommends python3 ca-certificates
# Resolve against an EMPTY installed-package status to include already-present dependencies.
apt-get -o Dir::State::status=/dev/null -o Dir::Cache::archives=/output/packages --download-only -y --no-install-recommends install age python3 wpasupplicant ifupdown isc-dhcp-client iproute2 iputils-ping pciutils usbutils gpgv
PYTHONPATH=/source/src python3 -m workshop.usb.bundle metadata /output
rm -f /output/packages/lock
rmdir /output/packages/partial 2>/dev/null || true
