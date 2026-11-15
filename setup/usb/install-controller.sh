#!/usr/bin/env bash
# Stage TRUSTED controller code locally BEFORE the USB makes the credential round trip.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Use sudo at the Debian console after verifying the tools ZIP.' >&2; exit 2; }
root=$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd)
target=/opt/local-agent-workshop-usb
[[ ! -e "$target" && ! -L "$target" ]] || { echo 'Controller already exists. Review and preserve it before an upgrade.' >&2; exit 2; }
[[ ! -e /usr/local/sbin/law-usb && ! -L /usr/local/sbin/law-usb ]] || { echo 'law-usb command already exists; preserved.' >&2; exit 2; }
command -v python3 >/dev/null
command -v age >/dev/null
printf 'Install verified USB controller code into %s; private key/data remain under /var/lib.\n' "$target"
read -r -p 'Type VERIFIED to confirm the tools ZIP hash was checked: ' answer
[[ "$answer" == VERIFIED ]] || exit 2
stage=$(mktemp -d /opt/.law-usb-controller.XXXXXXXX)
trap '[[ ! -d "$stage" ]] || rm -rf -- "$stage"' EXIT
install -d -m 0755 "$stage/src/workshop/usb"
install -m 0644 "$root/src/workshop/__init__.py" "$stage/src/workshop/__init__.py"
for name in __init__.py wifi.py transaction.py rollback.py; do
    [[ -f "$root/src/workshop/usb/$name" && ! -L "$root/src/workshop/usb/$name" ]] || exit 2
    install -m 0644 "$root/src/workshop/usb/$name" "$stage/src/workshop/usb/$name"
done
cat > "$stage/entry.py" <<'PY'
import os
import sys
os.environ['PATH'] = '/usr/sbin:/usr/bin:/sbin:/bin'
sys.path.insert(0, '/opt/local-agent-workshop-usb/src')
from workshop.usb.wifi import main
raise SystemExit(main())
PY
chmod 0644 "$stage/entry.py"
chmod 0755 "$stage"
mv -T -- "$stage" "$target"
printf '#!/bin/sh\nexec /usr/bin/python3 -I /opt/local-agent-workshop-usb/entry.py "$@"\n' > /usr/local/sbin/law-usb
chmod 0755 /usr/local/sbin/law-usb
printf 'Controller installed. Use sudo law-usb pair --output /media/USB/debian-request.json\n'
