#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd)
command -v python3 >/dev/null || { echo 'Install the matching offline recovery package bundle first.' >&2; exit 2; }
command -v age >/dev/null || { echo 'Install age from the matching verified Debian bundle first.' >&2; exit 2; }
export PYTHONPATH="$root/src"
exec python3 -m workshop.usb.wifi "$@"
