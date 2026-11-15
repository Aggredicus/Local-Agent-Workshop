"""Bounded local-console network changes with a systemd rollback timer."""
from __future__ import annotations

import base64
import fcntl
import json
from pathlib import Path
import time

from .wifi import STATE, WifiError, atomic_private, command, configuration, decrypt, manager_for, private_directory, validate_payload, exclusive, no_pending
from .rollback import rollback


def associated(interface: str, manager: str = 'ifupdown', nonce: str = '') -> list[str]:
    if manager == 'NetworkManager':
        connected = command(['nmcli', '-g', 'GENERAL.STATE', 'device', 'show', interface]).strip().startswith('100')
        active = command(['nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', interface]).strip()
        if not connected or active != 'law-' + nonce:
            return []
        status = 'wpa_state=COMPLETED'
    else:
        status = command(['wpa_cli', '-i', interface, 'status'])
    if manager == 'ifupdown' and ('id_str=law-' + nonce) not in status.splitlines():
        return []
    if 'wpa_state=COMPLETED' not in status.splitlines():
        return []
    try:
        devices = json.loads(command(['ip', '-j', '-4', 'address', 'show', 'dev', interface]))
        return [a['local'] for item in devices for a in item.get('addr_info', []) if a.get('scope') == 'global']
    except (KeyError, ValueError):
        return []


def apply_wifi(capsule: Path, expected_hash: str, interface: str, *, root: Path = Path('/'), state_root: Path = STATE) -> None:
    with exclusive(state_root):
        no_pending(state_root)
        _apply_wifi(capsule, expected_hash, interface, root=root, state_root=state_root)


def _apply_wifi(capsule: Path, expected_hash: str, interface: str, *, root: Path = Path('/'), state_root: Path = STATE) -> None:
    private_directory(state_root)
    payload, request = decrypt(capsule, expected_hash, state_root)
    ssid, psk = validate_payload(payload, request)
    manager = manager_for(interface, root)
    files = configuration(interface, manager, request['nonce'], ssid, psk)
    print('Target interface:', interface, '| existing owner:', manager)
    print('Requested network (escaped):', ascii(ssid))
    print('Files to create/update:', ', '.join(files))
    print('Password and equivalent PSK are never displayed. Automatic rollback in 180 seconds unless association/IP and KEEP succeed.')
    if input('Type APPLY to approve this local change: ') != 'APPLY':
        raise WifiError('Cancelled before network changes.')
    private_directory(state_root / request['nonce'])
    directory = state_root / request['nonce']
    state_file = directory / 'transaction.json'
    if state_file.exists():
        raise WifiError('Transaction already exists; inspect its recovery status before retrying.')
    previous = ''
    if manager == 'NetworkManager':
        previous = command(['nmcli', '-g', 'GENERAL.CON-UUID', 'device', 'show', interface]).strip()
    else:
        try:
            previous_status = command(['wpa_cli', '-i', interface, 'status'])
        except WifiError:
            previous_status = ''
        if any(line.startswith('wpa_state=') for line in previous_status.splitlines()):
            raise WifiError('A supplicant already owns this wireless adapter, even if DHCP failed; preserve it for migration review.')
    backups = {}
    for name in files:
        path = root / name.lstrip('/')
        for parent in (path, *path.parents):
            if parent.is_symlink():
                raise WifiError('Linked network configuration requires manual review.')
        if path.exists() and not path.is_file():
            raise WifiError('Configuration target is not a regular file.')
        backups[name] = base64.b64encode(path.read_bytes()).decode() if path.exists() else None
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    state = {'status': 'pending', 'nonce': request['nonce'], 'interface': interface,
             'manager': manager, 'previous_uuid': previous, 'backups': backups}
    atomic_private(state_file, json.dumps(state).encode())
    worker = directory / 'rollback_worker.py'
    atomic_private(worker, Path(__file__).with_name('rollback.py').read_bytes())
    unit = 'law-wifi-' + request['nonce']
    # Timer must be successfully armed BEFORE any network/configuration mutation.
    command(['systemd-run', '--unit', unit, '--on-active=180', '--property=UMask=0077', '/usr/bin/python3', str(worker), str(state_file)])
    try:
        with state_file.with_suffix('.lock').open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            if json.loads(state_file.read_text())['status'] != 'pending':
                raise WifiError('Rollback already ran; no changes permitted.')
            for name, content in files.items():
                atomic_private(root / name.lstrip('/'), content)
        if manager == 'NetworkManager':
            command(['nmcli', 'connection', 'load', next(iter(files))])
            command(['nmcli', '--wait', '40', 'connection', 'up', 'id', 'law-' + request['nonce']], timeout=45)
        else:
            command(['ifup', interface], timeout=45)
        addresses = []
        until = time.monotonic() + 45
        while not addresses and time.monotonic() < until:
            try:
                addresses = associated(interface, manager, request['nonce'])
            except WifiError:
                pass
            if not addresses:
                time.sleep(1)
        if not addresses:
            raise WifiError('No authenticated association with a global IPv4 address; rollback required.')
        print('Association and IPv4 confirmed:', ', '.join(addresses))
        print('Test access from Windows now. This does not prove internet/DNS access or SSH configuration.')
        if input('Type KEEP before timeout to retain this configuration: ') != 'KEEP':
            raise WifiError('Configuration not confirmed.')
        with state_file.with_suffix('.lock').open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            current = json.loads(state_file.read_text())
            if current['status'] != 'pending':
                raise WifiError('Timed rollback already ran; configuration was not kept.')
            latest_request = json.loads((state_root / 'request.json').read_text())
            if latest_request['nonce'] != request['nonce']:
                raise WifiError('Pairing state changed; rollback rather than consume another request.')
            current['status'] = 'kept'
            atomic_private(state_file, json.dumps(current).encode())
            request['used'] = True
            atomic_private(state_root / 'request.json', json.dumps(request).encode())
        command(['systemctl', 'stop', unit + '.timer'])
        print('Wi-Fi configuration kept. Private backups remain on Debian; private key never left this device.')
    except BaseException:
        rollback(state_file, root=root)
        raise
