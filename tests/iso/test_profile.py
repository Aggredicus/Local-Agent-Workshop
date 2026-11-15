import base64
import json
from pathlib import Path
import pytest
from workshop.iso.profile import ISOError, preseed, validate_profile
from workshop.iso.build import NAME, CD_FINGERPRINT, verify_image
from workshop.iso.repository import digest

ROOT = Path(__file__).resolve().parents[2]


def profile():
    return json.loads((ROOT / 'setup/iso/profile.json').read_text())


def test_public_preseed_keeps_disk_and_accounts_interactive():
    text = preseed(profile())
    assert 'preseed/late_command' in text
    assert 'netcfg/enable boolean false' in text
    assert 'debconf/priority string high' in text
    for forbidden in ('partman', 'passwd/username', 'passwd/user-password', '/dev/sd', '/dev/vd', 'password-crypted'):
        assert forbidden not in text


@pytest.mark.parametrize('field,value', [('hostname', 'pc\nd-i partman/confirm boolean true'), ('timezone', 'UTC; reboot'), ('ssh_public_key', '-----BEGIN OPENSSH PRIVATE KEY-----'), ('ssh_public_key', 'command="id" ssh-ed25519 AAAA'), ('ssh_public_key', 'ssh-ed25519 ' + 'A' * 68), ('wifi_password', 'secret')])
def test_profile_rejects_injection_private_inputs_and_invalid_keys(field, value):
    data = profile()
    data[field] = value
    with pytest.raises(ISOError):
        validate_profile(data)


def test_ed25519_key_must_have_exact_ssh_wire_encoding():
    data = profile()
    key = b'\0\0\0\x0bssh-ed25519\0\0\0\x20' + bytes(range(32))
    data['ssh_public_key'] = 'ssh-ed25519 ' + base64.b64encode(key).decode() + ' synthetic@test'
    assert validate_profile(data) == data


def test_image_signature_and_exact_checksum_are_required(tmp_path, monkeypatch):
    image = tmp_path / NAME
    image.write_bytes(b'synthetic test ISO')
    (tmp_path / 'SHA512SUMS').write_text(digest(image, 'sha512') + '  ' + NAME + '\n')
    from types import SimpleNamespace
    def signing_key(*args, **kwargs):
        return SimpleNamespace(stdout='[GNUPG:] VALIDSIG ' + CD_FINGERPRINT + ' 2026 1 0 4 0 1 10 00 ' + CD_FINGERPRINT + '\n')
    monkeypatch.setattr('workshop.iso.build.run', signing_key)
    assert verify_image(tmp_path, tmp_path / 'trusted-keyring')['filename'] == NAME
    image.write_bytes(b'changed')
    with pytest.raises(ISOError, match='SHA512'):
        verify_image(tmp_path, tmp_path / 'trusted-keyring')
    monkeypatch.setattr('workshop.iso.build.run', lambda *a, **k: SimpleNamespace(stdout='[GNUPG:] VALIDSIG ' + '0'*40 + ' invalid'))
    with pytest.raises(ISOError, match='signing key'):
        verify_image(tmp_path, tmp_path / 'trusted-keyring')
