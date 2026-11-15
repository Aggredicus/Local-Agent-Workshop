"""Reproducible data payload; never partitions or writes a block device."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from .bundle import USBError

AGE_ARCHIVE_SHA256 = 'f48d8f8f9ebe903ab5027ed067652f2cc1db94bc206976430133b905dcd8e8c7'
AGE_EXE_SHA256 = '2821a4ed191da07372acd302e5f6feae7a7985e285e1417765ebe74025af45f0'


def pack(repo: Path, packages: Path, age_archive: Path, output: Path) -> dict:
    if output.exists() or output.is_symlink():
        raise USBError('Output already exists; existing artifacts are preserved.')
    if hashlib.sha256(age_archive.read_bytes()).hexdigest() != AGE_ARCHIVE_SHA256:
        raise USBError('age archive does not match the pinned upstream/Microsoft winget digest.')
    contents: dict[str, bytes] = {}
    for name in ['START-USB.cmd', 'pyproject.toml', 'me.md', 'AGENTS.md']:
        contents[name] = (repo / name).read_bytes()
    for directory, extensions in [('setup/usb', {'.sh', '.ps1', '.cs', '.md'}), ('src/workshop', {'.py'})]:
        for path in sorted((repo / directory).rglob('*')):
            if path.is_symlink():
                raise USBError('Linked source file rejected.')
            if path.is_file() and path.suffix in extensions:
                contents[path.relative_to(repo).as_posix()] = path.read_bytes()
    contents['README.md'] = (repo / 'setup/usb/README.md').read_bytes()
    for name in ('README.md', 'FIRST-BOOT.txt'):
        path = repo / 'setup/iso' / name
        if path.is_symlink() or not path.is_file():
            raise USBError('The offline ISO installation guide is missing or linked.')
        contents['setup/iso/' + name] = path.read_bytes()
    with zipfile.ZipFile(age_archive) as archive:
        executable = archive.read('age/age.exe')
        if hashlib.sha256(executable).hexdigest() != AGE_EXE_SHA256:
            raise USBError('Pinned age executable checksum mismatch.')
        contents['setup/usb/tools/age.exe'] = executable
        contents['setup/usb/tools/age-LICENSE'] = archive.read('age/LICENSE')
    for version in ('12', '13'):
        bundle = packages / f'debian{version}-amd64'
        if not (bundle / 'manifest.json').is_file():
            raise USBError('Both verified Debian 12/13 recovery bundles are required.')
        for path in sorted(bundle.rglob('*')):
            if path.is_symlink():
                raise USBError('Linked bundle payload rejected.')
            if path.is_file():
                if path.name != 'manifest.json' and path.suffix not in {'.deb', '.Packages', '.InRelease'}:
                    raise USBError('Unexpected package bundle file.')
                contents[f'packages/debian{version}-amd64/' + path.relative_to(bundle).as_posix()] = path.read_bytes()
    manifest = {'format': 1, 'files': [{'path': name, 'sha256': hashlib.sha256(data).hexdigest()} for name, data in sorted(contents.items())],
                'includes_installer_iso': False, 'bootable_by_itself': False,
                'requires': 'The verified LAW offline Debian ISO (menu option 2) and operator-installed Ventoy for booting.'}
    contents['USB-PAYLOAD.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    # CreateNew preserves data even if another process creates the path concurrently.
    with output.open('xb') as file:
        with zipfile.ZipFile(file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, data in sorted(contents.items()):
                info = zipfile.ZipInfo('LAW/' + name, date_time=(2026, 11, 15, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o644 << 16)
                archive.writestr(info, data)
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(checksum + '  ' + output.name + '\n')
    return {'file': str(output), 'sha256': checksum, 'bytes': output.stat().st_size,
            'contains_private_keys_or_credentials': False, 'iso_included': False}
