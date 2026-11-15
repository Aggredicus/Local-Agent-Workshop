"""Root-owned standalone timer worker; never loads executable code from returning USB."""
from __future__ import annotations
import base64
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def rollback(state_file: Path, *, root: Path = Path('/')) -> bool:
    lock = state_file.with_suffix('.lock')
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        state = json.loads(state_file.read_text())
        if state['status'] != 'pending':
            return False
        interface, nonce = state['interface'], state['nonce']
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,15}', interface) or not re.fullmatch(r'[a-f0-9]{32}', nonce):
            raise ValueError('Invalid recovery state')
        def run(args):
            try:
                subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30, check=False)
            except (OSError, subprocess.TimeoutExpired):
                pass  # Restore files even when the network command itself is unavailable.
        if state['manager'] == 'NetworkManager':
            run(['nmcli', '--wait', '15', 'connection', 'down', 'id', 'law-' + nonce])
        elif state['manager'] == 'ifupdown':
            run(['ifdown', '--force', interface])
        else:
            raise ValueError('Unknown recovery manager')
        allowed = {f'/etc/NetworkManager/system-connections/law-{nonce}.nmconnection',
                   f'/etc/network/interfaces.d/law-{interface}',
                   f'/etc/wpa_supplicant/wpa_supplicant-{interface}.conf'}
        for name, backup in state['backups'].items():
            if name not in allowed:
                raise ValueError('Unexpected recovery path')
            path = root / name.lstrip('/')
            if path.is_symlink():
                raise ValueError('Linked recovery target')
            if backup is None:
                path.unlink(missing_ok=True)
            else:
                fd, temporary = tempfile.mkstemp(dir=path.parent)
                with os.fdopen(fd, 'wb') as restored:
                    restored.write(base64.b64decode(backup, validate=True))
                os.replace(temporary, path)
        if state['manager'] == 'NetworkManager':
            run(['nmcli', 'connection', 'reload'])
            previous = state.get('previous_uuid', '')
            if re.fullmatch(r'[0-9a-fA-F-]{36}', previous):
                run(['nmcli', '--wait', '20', 'connection', 'up', 'uuid', previous])
        state['status'] = 'rolled_back'
        state['network_stop_verified'] = False
        fd, temporary = tempfile.mkstemp(dir=state_file.parent)
        with os.fdopen(fd, 'w') as result:
            json.dump(state, result)
        os.replace(temporary, state_file)
        return True


if __name__ == '__main__':
    path = Path(sys.argv[1])
    expected = Path('/var/lib/local-agent-workshop/usb-wifi')
    if os.geteuid() != 0 or not path.resolve().is_relative_to(expected):
        raise SystemExit('Invalid recovery worker invocation')
    rollback(path)
