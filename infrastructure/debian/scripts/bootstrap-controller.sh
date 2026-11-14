#!/usr/bin/env bash
set -euo pipefail
# Run on Debian 13 ThinkCentre A from a human-operated shell.
if [[ "$EUID" -eq 0 ]]; then
  echo "Run as your regular Debian account; sudo will be requested." >&2
  exit 1
fi
if ! grep -q 'VERSION_ID="13"' /etc/os-release; then
  echo "Expected Debian 13; stop and verify operating system." >&2
  exit 1
fi
sudo apt-get update
sudo apt-get install -y ansible git openssh-client python3 curl
printf '\nController ready. Continue with SSH key pairing and the inventory in the installation guide.\n'
