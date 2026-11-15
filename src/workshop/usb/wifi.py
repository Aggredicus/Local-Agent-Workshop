"""Local-console, device-paired Wi-Fi recovery. Never accepts a password in argv."""
from __future__ import annotations

import argparse
import fcntl
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid

STATE = Path('/var/lib/local-agent-workshop/usb-wifi')


class WifiError(ValueError):
    pass


def command(args: list[str], *, timeout=30) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise WifiError('A required recovery command is missing or timed out.') from None
    if result.returncode:
        raise WifiError('Recovery command failed; no credential-bearing command output is emitted.')
    return result.stdout


def private_directory(path: Path) -> None:
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise WifiError('Refusing linked private state/configuration.')
    if path.exists() and path.stat().st_uid != os.geteuid():
        raise WifiError("Private state must be owned by the invoking administrative account.")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)


def atomic_private(path: Path, content: bytes) -> None:
    if path.is_symlink():
        raise WifiError('Refusing linked configuration.')
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def exclusive(state: Path):
    private_directory(state)
    path = state / '.control.lock'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise WifiError('Another local Wi-Fi operation is active; finish/cancel it first.') from None
        yield
    finally:
        os.close(fd)


def no_pending(state: Path) -> None:
    for path in state.glob('*/transaction.json'):
        if json.loads(path.read_text()).get('status') == 'pending':
            raise WifiError('A pending transaction needs rollback/recovery before a new pairing or apply.')


def pair(output: Path, state: Path = STATE) -> dict:
    with exclusive(state):
        no_pending(state)
        return _pair(output, state)


def _pair(output: Path, state: Path = STATE) -> dict:
    if output.exists() or output.is_symlink():
        raise WifiError("Public request output already exists.")
    private_directory(state)
    identity = state / 'identity.age-key'
    if identity.is_symlink():
        raise WifiError('Linked identity is forbidden.')
    if not identity.exists():
        command(['age-keygen', '-o', str(identity)])
    if identity.is_symlink() or identity.stat().st_mode & 0o077:
        raise WifiError('Private key permissions must be 0600 and it must stay on Debian.')
    recipient = command(['age-keygen', '-y', str(identity)]).strip()
    if not re.fullmatch(r'age1[a-z0-9]{58}', recipient):
        raise WifiError('Expected an age X25519 public recipient.')
    public = {'schema': 1, 'recipient': recipient,
              'fingerprint': hashlib.sha256(recipient.encode()).hexdigest(),
              'nonce': uuid.uuid4().hex, 'expires': int(time.time()) + 86400,
              'hostname': os.uname().nodename}
    atomic_private(state / 'request.json', json.dumps(public).encode())
    # Public data only; no identity/private-key file is ever copied to output.
    if output.exists() or output.is_symlink():
        raise WifiError('Public request output exists; preserve it and choose another filename.')
    with output.open('x', encoding='utf-8') as handle:
        json.dump(public, handle, indent=2)
    return public


def validate_payload(payload: dict, request: dict) -> tuple[str, str]:
    if not isinstance(payload, dict) or payload.get('schema') != 1:
        raise WifiError('Invalid encrypted Wi-Fi payload.')
    if payload.get('nonce') != request['nonce'] or payload.get('fingerprint') != request['fingerprint']:
        raise WifiError('Payload belongs to a different pairing request.')
    if request['expires'] <= time.time() or request.get('used'):
        raise WifiError('Pairing request expired or was already used.')
    ssid, password = payload.get('ssid'), payload.get('password')
    if not isinstance(ssid, str) or not 1 <= len(ssid.encode()) <= 32 or any(ord(c) < 32 or ord(c) == 127 for c in ssid):
        raise WifiError('SSID must have 1-32 UTF-8 bytes without control characters.')
    if not isinstance(password, str) or not 8 <= len(password) <= 63 or any(not 32 <= ord(c) <= 126 for c in password):
        raise WifiError('Only WPA2-Personal printable ASCII passphrases are supported.')
    return ssid, hashlib.pbkdf2_hmac('sha1', password.encode(), ssid.encode(), 4096, 32).hex()


def decrypt(capsule: Path, expected_hash: str, state: Path = STATE) -> tuple[dict, dict]:
    if not re.fullmatch(r'[a-fA-F0-9]{64}', expected_hash):
        raise WifiError('Compare and enter the full ciphertext SHA256 displayed on Windows.')
    if capsule.is_symlink() or not capsule.is_file() or capsule.stat().st_size > 65536:
        raise WifiError('Invalid or oversized encrypted file.')
    # Read once, then decrypt that exact private copy; USB replacement cannot change it.
    encrypted = capsule.read_bytes()
    if hashlib.sha256(encrypted).hexdigest() != expected_hash.lower():
        raise WifiError('Encrypted file hash mismatch; no network changes applied.')
    fd, copied = tempfile.mkstemp(dir=state)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(encrypted)
        plaintext = command(['age', '--decrypt', '-i', str(state / 'identity.age-key'), copied])
        try:
            payload = json.loads(plaintext)
            request = json.loads((state / 'request.json').read_text())
        except (ValueError, OSError):
            raise WifiError('Invalid decrypted payload or pairing state.') from None
        validate_payload(payload, request)
        return payload, request
    finally:
        os.unlink(copied)


def manager_for(interface: str, root: Path = Path('/')) -> str:
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,15}', interface) or not (root / 'sys/class/net' / interface / 'wireless').is_dir():
        raise WifiError('Select a detected wireless adapter; inspect hardware/firmware first.')
    nm = False
    if shutil.which('nmcli'):
        try:
            nm = command(['nmcli', '-g', 'GENERAL.NM-MANAGED', 'device', 'show', interface]).strip().lower() == 'yes'
        except WifiError:
            pass
    networkd = False
    if shutil.which('networkctl'):
        try:
            status = command(['networkctl', 'status', interface, '--no-pager', '--lines=0'])
            networkd = bool(re.search(r'Network File:\s+/', status))
        except WifiError:
            pass
    if nm and networkd:
        raise WifiError('Conflicting network managers detected; resolve ownership at the console.')
    if nm:
        return 'NetworkManager'
    if networkd:
        raise WifiError('systemd-networkd ownership detected. Automatic changes are unavailable until its configuration is reviewed.')
    interfaces = root / 'etc/network/interfaces'
    if not shutil.which('ifup') or not interfaces.is_file():
        raise WifiError('No supported network owner/configuration. Install the offline tools and inspect the existing configuration.')
    text = interfaces.read_text()
    if not re.search(r'^\s*(?:source\s+/etc/network/interfaces\.d/\*|source-directory\s+/etc/network/interfaces\.d/?)\s*$', text, re.M):
        raise WifiError('ifupdown does not include the standard interfaces.d drop-ins; preserve existing configuration and review it manually.')
    # Do not override an existing interface definition, regardless of where it lives.
    for path in [interfaces, *sorted((root / 'etc/network/interfaces.d').glob('*'))]:
        if path.is_symlink():
            raise WifiError('Linked network configuration requires manual review.')
        if path.is_file() and re.search(r'^\s*iface\s+' + re.escape(interface) + r'\s', path.read_text(), re.M):
            raise WifiError('Wireless interface already has an ifupdown definition; preserve it for a separate migration plan.')
    return 'ifupdown'


def configuration(interface: str, manager: str, nonce: str, ssid: str, psk: str) -> dict[str, bytes]:
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,15}', interface) or not re.fullmatch(r'[a-f0-9]{32}', nonce):
        raise WifiError('Invalid interface or transaction identifier.')
    if not re.fullmatch(r'[a-f0-9]{64}', psk):
        raise WifiError('Invalid derived WPA2 key.')
    if manager == 'NetworkManager':
        # Numeric byte-array SSID avoids keyfile injection/encoding ambiguities.
        data = ('[connection]\nid=law-' + nonce + '\ntype=wifi\ninterface-name=' + interface + '\nautoconnect=true\n'
                '[wifi]\nmode=infrastructure\nssid=' + ''.join(str(b) + ';' for b in ssid.encode()) + '\n'
                '[wifi-security]\nkey-mgmt=wpa-psk\npsk=' + psk + '\n[ipv4]\nmethod=auto\n[ipv6]\nmethod=auto\n')
        return {f'/etc/NetworkManager/system-connections/law-{nonce}.nmconnection': data.encode()}
    if manager != 'ifupdown':
        raise WifiError('Unsupported network manager.')
    supplicant = f'/etc/wpa_supplicant/wpa_supplicant-{interface}.conf'
    data = 'ctrl_interface=/run/wpa_supplicant\nupdate_config=0\nnetwork={\n id_str="law-' + nonce + '"\n ssid=' + ssid.encode().hex() + '\n psk=' + psk + '\n key_mgmt=WPA-PSK\n}\n'
    stanza = f'allow-hotplug {interface}\niface {interface} inet dhcp\n    wpa-conf {supplicant}\n'
    return {supplicant: data.encode(), f'/etc/network/interfaces.d/law-{interface}': stanza.encode()}


def _root_console() -> None:
    tty = os.ttyname(0) if os.isatty(0) else ''
    if os.geteuid() != 0 or not re.fullmatch(r'/dev/tty[0-9]+', tty) or os.environ.get('SSH_CONNECTION') or os.environ.get('SSH_CLIENT'):
        raise WifiError('Use sudo at the physical Debian console; remote/network mutation is not supported by this bootstrap.')


def recover(transaction_id: str, *, state_root: Path = STATE, root: Path = Path('/')) -> int:
    if not re.fullmatch(r'[a-f0-9]{32}', transaction_id):
        raise WifiError('Invalid recovery transaction identifier.')
    state_file = state_root / transaction_id / 'transaction.json'
    record = json.loads(state_file.read_text())
    print('Restore this transaction’s saved network configuration:', transaction_id)
    if input('Type ROLLBACK to approve: ') != 'ROLLBACK':
        raise WifiError('Recovery cancelled.')
    with state_file.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        record['status'] = 'pending'
        atomic_private(state_file, json.dumps(record).encode())
    from .rollback import rollback
    rollback(state_file, root=root)
    print('Saved configuration restored; check the adapter and local access.')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Device-paired encrypted Wi-Fi USB recovery')
    sub = parser.add_subparsers(dest='action', required=True)
    pairing = sub.add_parser('pair')
    pairing.add_argument('--output', type=Path, required=True)
    apply = sub.add_parser('apply')
    apply.add_argument('--capsule', type=Path, required=True)
    apply.add_argument('--sha256', required=True, help='Public ciphertext hash displayed on Windows')
    apply.add_argument('--interface', required=True)
    sub.add_parser('status')
    recovery = sub.add_parser('recover')
    recovery.add_argument('--transaction', required=True)
    args = parser.parse_args(argv)
    try:
        _root_console()
        if args.action == 'status':
            for path in sorted(STATE.glob('*/transaction.json')):
                record = json.loads(path.read_text())
                print(json.dumps({key: record[key] for key in ('nonce', 'status', 'interface', 'manager')}))
            return 0
        if args.action == 'recover':
            if not re.fullmatch(r'[a-f0-9]{32}', args.transaction):
                raise WifiError('Invalid transaction identifier.')
            with exclusive(STATE):
                return recover(args.transaction)
        if args.action == 'pair':
            data = pair(args.output)
            print('Public pairing request written. Private key stays on this Debian machine.')
            print('Compare this fingerprint on Windows:', data['fingerprint'])
            return 0
        from .transaction import apply_wifi
        apply_wifi(args.capsule, args.sha256, args.interface)
        return 0
    except WifiError as exc:
        print(str(exc))
        return 1
    except (OSError, KeyboardInterrupt, EOFError):
        print('Wi-Fi operation did not complete. No credential values are emitted. Inspect the local ownership/permissions, pairing hash/expiry, tools and firmware; use the recovery guide.', flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
