#!/usr/bin/env python3
"""Exercise both recovery installers without networking in disposable containers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from workshop.usb.cli import IMAGES

SCRIPT = r'''set -euo pipefail
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
cp /source/setup/usb/packages.sh /tmp/verified-installer.sh
for attempt in 1 2; do
    printf 'INSTALL\n' | bash /tmp/verified-installer.sh install /bundle > /tmp/install.log 2>&1 || { tail -40 /tmp/install.log; exit 1; }
done
age --version
python3 --version
wpa_cli -v
if dpkg-query -W -f='${Status}' openssh-server 2>/dev/null | grep -qx 'install ok installed'; then
    echo 'Unexpected SSH server installation' >&2
    exit 3
fi
printf 'OFFLINE_INSTALL_AND_REPEAT_PASSED\n'
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    results = []
    for version, image in IMAGES.items():
        bundle = (args.packages / f'debian{version}-amd64').resolve(strict=True)
        with tempfile.TemporaryFile(mode='w+') as log:
            result = subprocess.run(['docker', 'run', '--rm', '--network', 'none',
                '--mount', f'type=bind,source={repo},target=/source,readonly',
                '--mount', f'type=bind,source={bundle},target=/bundle,readonly',
                image, 'bash', '-c', SCRIPT], stdout=log, stderr=subprocess.STDOUT, check=False)
            log.seek(0)
            output = log.read()
        print(output, end='', flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
        results.append({'debian': version, 'image': image, 'network': 'none',
                        'install_and_repeat': 'passed', 'hardware_tested': False})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
