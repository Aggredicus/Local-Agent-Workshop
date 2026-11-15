from __future__ import annotations

import re
import base64
import binascii


class ISOError(ValueError):
    pass


ROOTS = ('python3', 'git', 'sudo', 'age', 'wpasupplicant', 'ifupdown',
         'isc-dhcp-client', 'iproute2', 'iputils-ping', 'pciutils', 'usbutils',
         'ca-certificates', 'openssh-server', 'uidmap', 'dbus-user-session',
         'slirp4netns', 'fuse-overlayfs', 'busybox-static', 'gpgv',
         'docker-ce', 'docker-ce-cli', 'containerd.io', 'docker-buildx-plugin',
         'docker-compose-plugin', 'docker-ce-rootless-extras')
DOCKER_FINGERPRINT = '9DC858229FC7DD38854AE2D88D81803C0EBFCD88'
CD_FINGERPRINT = 'DF9B9C49EAA9298432589D76DA87E80D6294BE9B'


def validate_profile(data: dict) -> dict:
    expected = {'format', 'debian_version', 'architecture', 'hostname', 'locale', 'keyboard', 'timezone', 'ssh_public_key'}
    if not isinstance(data, dict) or set(data) != expected or type(data['format']) is not int or data['format'] != 1:
        raise ISOError('Profile has missing/unknown fields; secrets and arbitrary commands are not profile inputs.')
    if data['debian_version'] != '13.7.0' or data['architecture'] != 'amd64':
        raise ISOError('This installer is qualified only for Debian 13.7.0 amd64.')
    patterns = {'hostname': r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',
                'locale': r'[a-z]{2}_[A-Z]{2}[.]UTF-8',
                'keyboard': r'[a-z][a-z0-9-]{0,15}',
                'timezone': r'[A-Za-z_+-]+(?:/[A-Za-z_+-]+){1,2}'}
    for field, pattern in patterns.items():
        if not isinstance(data[field], str) or not re.fullmatch(pattern, data[field]):
            raise ISOError(f'Invalid {field}; shell/preseed control characters are rejected.')
    key = data['ssh_public_key']
    if not isinstance(key, str) or len(key) > 1024 or (key and not re.fullmatch(r'ssh-ed25519 [A-Za-z0-9+/]{40,120}={0,2}(?: [A-Za-z0-9_.@ -]{1,120})?', key)):
        raise ISOError('SSH input must be one Ed25519 PUBLIC key; private keys and authorized_keys options are rejected.')
    if key:
        try:
            raw = base64.b64decode(key.split()[1], validate=True)
            if len(raw) != 51 or raw[:19] != b'\0\0\0\x0bssh-ed25519\0\0\0\x20':
                raise ISOError('Malformed Ed25519 public-key encoding.')
        except binascii.Error as exc:
            raise ISOError('Malformed Ed25519 public-key encoding.') from exc
    return dict(data)


def preseed(profile: dict) -> str:
    p = validate_profile(profile)
    # No partitioning, target-disk, username, password/hash or Wi-Fi answers.
    return f'''# LAW offline installation. Confirm the target disk in Debian Installer.
d-i debconf/priority string high
d-i debian-installer/locale string {p['locale']}
d-i keyboard-configuration/xkb-keymap select {p['keyboard']}
d-i time/zone string {p['timezone']}
d-i clock-setup/utc boolean true
d-i clock-setup/ntp boolean false
d-i netcfg/enable boolean false
d-i netcfg/get_hostname string {p['hostname']}
d-i netcfg/get_domain string
d-i apt-setup/use_mirror boolean false
d-i apt-setup/services-select multiselect
d-i pkgsel/run_tasksel boolean false
d-i pkgsel/upgrade select none
d-i popularity-contest/participate boolean false
d-i passwd/root-login boolean false
d-i preseed/late_command string /bin/sh /cdrom/law/installer/late.sh
'''
