from __future__ import annotations

import base64
import json
from pathlib import Path
import time

import pytest

from workshop.usb import wifi, rollback, transaction


@pytest.fixture
def pairing():
    return {'nonce': 'a' * 32, 'fingerprint': 'b' * 64, 'expires': int(time.time()) + 3600}


def payload(pairing, **changes):
    return {'schema': 1, 'nonce': pairing['nonce'], 'fingerprint': pairing['fingerprint'],
            'ssid': 'IEEE', 'password': 'password', **changes}


def test_wpa2_derivation_matches_published_ieee_test_vector(pairing):
    ssid, psk = wifi.validate_payload(payload(pairing), pairing)
    assert ssid == 'IEEE'
    assert psk == 'f42c6fc52df0ebef9ebb4b90b38a5f902e83fe1b135a70e23aed762e9710a12e'


@pytest.mark.parametrize('change', [{'password': 'short'}, {'ssid': 'x\nINJECT'}, {'ssid': 'x'*33}, {'nonce': 'wrong'}, {'password': 'pässword'}])
def test_invalid_credentials_and_wrong_pairing_fail_without_echo(pairing, change):
    with pytest.raises(wifi.WifiError) as error:
        wifi.validate_payload(payload(pairing, **change), pairing)
    assert 'password' not in str(error.value).lower()  # No credential values in error.


def test_expired_or_used_pairing_is_rejected(pairing):
    for change in [{'expires': 0}, {'used': True}]:
        with pytest.raises(wifi.WifiError):
            wifi.validate_payload(payload(pairing), {**pairing, **change})


def test_configuration_encodes_injection_prone_ssid_and_never_stores_passphrase(pairing):
    ssid, psk = wifi.validate_payload(payload(pairing, ssid='Coffee " café'), pairing)
    for manager in ['ifupdown', 'NetworkManager']:
        files = wifi.configuration('wlan0', manager, pairing['nonce'], ssid, psk)
        rendered = b'\n'.join(files.values())
        assert b'password' not in rendered
        assert psk.encode() in rendered
        assert b'Coffee "' not in rendered


def test_wrong_ciphertext_hash_never_invokes_decryption(tmp_path, monkeypatch):
    capsule = tmp_path / 'wifi.age'
    capsule.write_bytes(b'not a real encrypted file')
    monkeypatch.setattr(wifi, 'command', lambda *a, **k: pytest.fail('must not invoke age'))
    with pytest.raises(wifi.WifiError, match='hash mismatch'):
        wifi.decrypt(capsule, '0' * 64, tmp_path)


def test_pair_exports_public_data_only_and_preserves_existing_request(tmp_path, monkeypatch):
    root = tmp_path / 'state'
    target = tmp_path / 'pairing.json'
    public = 'age1' + 'q' * 58
    def tool(args, **kwargs):
        if '-o' in args:
            private = Path(args[-1])
            private.write_text('SYNTHETIC-PRIVATE-KEY-CANARY')
            private.chmod(0o600)
            return ''
        return public
    monkeypatch.setattr(wifi, 'command', tool)
    result = wifi.pair(target, root)
    assert result['recipient'] == public
    assert 'SYNTHETIC-PRIVATE-KEY-CANARY' not in target.read_text()
    original = (root / 'request.json').read_bytes()
    with pytest.raises(wifi.WifiError):
        wifi.pair(target, root)
    assert (root / 'request.json').read_bytes() == original


def test_rollback_restores_config_even_if_ifdown_is_unavailable(tmp_path, monkeypatch):
    root = tmp_path / 'filesystem'
    target = root / 'etc/wpa_supplicant/wpa_supplicant-wlan0.conf'
    target.parent.mkdir(parents=True)
    target.write_text('new derived secret')
    state = tmp_path / 'transaction.json'
    state.write_text(json.dumps({'status': 'pending', 'nonce': 'a'*32, 'interface': 'wlan0', 'manager': 'ifupdown',
                                'backups': {'/etc/wpa_supplicant/wpa_supplicant-wlan0.conf': base64.b64encode(b'original config').decode()}}))
    def broken(*args, **kwargs):
        raise OSError('network tool missing')
    monkeypatch.setattr(rollback.subprocess, 'run', broken)
    assert rollback.rollback(state, root=root)
    assert target.read_text() == 'original config'
    assert target.stat().st_mode & 0o077 == 0
    assert json.loads(state.read_text())['status'] == 'rolled_back'
    assert rollback.rollback(state, root=root) is False


def test_nm_old_profile_cannot_masquerade_as_new_authentication(monkeypatch):
    def tool(args, **kwargs):
        return '100 (connected)' if 'GENERAL.STATE' in args else 'old-saved-profile'
    monkeypatch.setattr(transaction, 'command', tool)
    assert transaction.associated('wlan0', 'NetworkManager', 'a'*32) == []


def test_timer_failure_applies_no_network_configuration(tmp_path, monkeypatch, pairing):
    root, state = tmp_path / 'system', tmp_path / 'state'
    monkeypatch.setattr(transaction, 'decrypt', lambda *a: (payload(pairing), pairing))
    monkeypatch.setattr(transaction, 'manager_for', lambda *a: 'ifupdown')
    monkeypatch.setattr(transaction, 'associated', lambda *a: [])
    monkeypatch.setattr('builtins.input', lambda *a: 'APPLY')
    calls = []
    def fail_timer(args, **kwargs):
        calls.append(args)
        raise wifi.WifiError('timer unavailable')
    monkeypatch.setattr(transaction, 'command', fail_timer)
    with pytest.raises(wifi.WifiError, match='timer'):
        transaction.apply_wifi(Path('not-used'), '0'*64, 'wlan0', root=root, state_root=state)
    assert any(call[0] == 'systemd-run' for call in calls)
    assert not (root / 'etc/network/interfaces.d/law-wlan0').exists()
    assert not (root / 'etc/wpa_supplicant/wpa_supplicant-wlan0.conf').exists()


def test_pending_transaction_blocks_pair_rotation(tmp_path, monkeypatch):
    state = tmp_path / 'state'
    pending = state / ('a'*32)
    pending.mkdir(parents=True)
    (pending / 'transaction.json').write_text('{"status":"pending"}')
    monkeypatch.setattr(wifi, 'command', lambda *a, **k: pytest.fail('key generation must not run'))
    with pytest.raises(wifi.WifiError, match='pending'):
        wifi.pair(tmp_path / 'public.json', state)
    assert not (tmp_path / 'public.json').exists()


def test_another_local_operation_cannot_acquire_active_control_lock(tmp_path):
    with wifi.exclusive(tmp_path):
        with pytest.raises(wifi.WifiError, match='active'):
            with wifi.exclusive(tmp_path):
                pytest.fail('second operation must not enter')


def test_apply_keep_and_manual_recovery_preserve_secret_boundaries(tmp_path, monkeypatch, pairing):
    root, state = tmp_path / 'system', tmp_path / 'state'
    state.mkdir()
    (state / 'request.json').write_text(json.dumps(pairing))
    monkeypatch.setattr(transaction, 'decrypt', lambda *a: (payload(pairing), pairing.copy()))
    monkeypatch.setattr(transaction, 'manager_for', lambda *a: 'ifupdown')
    checks = iter([['192.0.2.10']])
    monkeypatch.setattr(transaction, 'associated', lambda *a: next(checks))
    answers = iter(['APPLY', 'KEEP'])
    monkeypatch.setattr('builtins.input', lambda *a: next(answers))
    calls = []
    def tool(args, **kwargs):
        assert 'password' not in ' '.join(args)
        if args[0] == 'systemd-run':
            assert not (root / 'etc/network/interfaces.d/law-wlan0').exists()
        calls.append(args)
        return ''
    monkeypatch.setattr(transaction, 'command', tool)
    transaction.apply_wifi(Path('unused'), '0'*64, 'wlan0', root=root, state_root=state)
    config = root / 'etc/wpa_supplicant/wpa_supplicant-wlan0.conf'
    assert config.is_file() and config.stat().st_mode & 0o077 == 0
    assert 'password' not in config.read_text()
    assert json.loads((state / 'request.json').read_text())['used'] is True
    record = state / pairing['nonce'] / 'transaction.json'
    assert json.loads(record.read_text())['status'] == 'kept'
    assert rollback.rollback(record, root=root) is False
    monkeypatch.setattr('builtins.input', lambda *a: 'ROLLBACK')
    monkeypatch.setattr(rollback.subprocess, 'run', lambda *a, **k: None)
    with wifi.exclusive(state):
        assert wifi.recover(pairing['nonce'], state_root=state, root=root) == 0
    assert not config.exists()
    assert json.loads(record.read_text())['status'] == 'rolled_back'


def test_unrelated_supplicant_cannot_confirm_requested_credentials(monkeypatch):
    def tool(args, **kwargs):
        if args[0] == 'wpa_cli':
            return 'wpa_state=COMPLETED\nssid=OLD_NETWORK\nid=0\n'
        return '[{"addr_info":[{"scope":"global","local":"192.0.2.12"}]}]'
    monkeypatch.setattr(transaction, 'command', tool)
    assert transaction.associated('wlan0', 'ifupdown', 'a'*32) == []


def test_new_unique_supplicant_profile_and_ip_confirm_connection(monkeypatch):
    def tool(args, **kwargs):
        if args[0] == 'wpa_cli':
            return 'wpa_state=COMPLETED\nid_str=law-' + 'a'*32 + '\n'
        return '[{"addr_info":[{"scope":"global","local":"192.0.2.12"}]}]'
    monkeypatch.setattr(transaction, 'command', tool)
    assert transaction.associated('wlan0', 'ifupdown', 'a'*32) == ['192.0.2.12']
