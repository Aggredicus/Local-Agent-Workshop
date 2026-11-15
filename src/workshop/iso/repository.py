"""Turn authenticated APT downloads into unchanged, signed file repositories."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess

from .profile import ISOError, ROOTS


def digest(path: Path, algorithm='sha256') -> str:
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def records(path: Path):
    record = {}
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            if not line.strip():
                if record:
                    yield record
                record = {}
            elif not line.startswith((' ', '\t')) and ': ' in line:
                name, value = line.rstrip('\n').split(': ', 1)
                if name in {'Package', 'Version', 'Architecture', 'Filename', 'SHA256', 'Size'}:
                    record[name] = value
    if record:
        yield record


def collect(output: Path, lists: Path = Path('/var/lib/apt/lists')) -> dict:
    inventories = {}
    suites = []
    for index in sorted(lists.glob('*_binary-amd64_Packages*')):
        match = re.fullmatch(r'(.+)_(main|stable)_binary-amd64_Packages(?:[.].*)?', index.name)
        if not match:
            continue
        prefix, component = match.groups()
        signed = index.with_name(prefix + '_InRelease')
        if not signed.is_file():
            raise ISOError('Missing authenticated APT release.')
        if prefix.startswith('download.docker.com_linux_debian_dists_'):
            vendor, suite = 'docker', prefix.removeprefix('download.docker.com_linux_debian_dists_')
        elif '_debian-security_dists_' in prefix:
            vendor, suite = 'debian-security', prefix.split('_dists_', 1)[1]
        elif prefix.startswith('deb.debian.org_debian_dists_'):
            vendor, suite = 'debian', prefix.split('_dists_', 1)[1]
        else:
            raise ISOError('Unexpected package origin.')
        if suite not in {'trixie', 'trixie-updates', 'trixie-security'} or component != ('stable' if vendor == 'docker' else 'main'):
            raise ISOError('Unexpected suite/component.')
        root = output / 'repositories' / vendor
        destination = root / 'dists' / suite
        package_index = destination / component / 'binary-amd64' / 'Packages'
        package_index.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(signed, destination / 'InRelease')
        with package_index.open('wb') as stream:
            subprocess.run(['/usr/lib/apt/apt-helper', 'cat-file', str(index)], stdout=stream, check=True)
        # Preserve signed indexes exactly. APT itself verifies InRelease and index
        # hashes again when the target reads these file: repositories offline.
        by_hash = package_index.parent / 'by-hash' / 'SHA256' / digest(package_index)
        by_hash.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package_index, by_hash)
        for item in records(package_index):
            if 'SHA256' in item:
                inventories[item['SHA256']] = (vendor, item)
        suites.append({'vendor': vendor, 'suite': suite, 'component': component,
                       'inrelease_sha256': digest(destination / 'InRelease')})
    packages = []
    for source in sorted((output / 'downloads').glob('*.deb')):
        checksum = digest(source)
        if checksum not in inventories:
            raise ISOError('A downloaded package is absent from authenticated indexes.')
        vendor, record = inventories[checksum]
        relative = PurePosixPath(record['Filename'])
        if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] not in {'pool', 'dists'}:
            raise ISOError('Unsafe upstream package filename.')
        if source.stat().st_size != int(record['Size']):
            raise ISOError('Package size mismatch.')
        target = output / 'repositories' / vendor / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        packages.append({'name': record['Package'], 'version': record['Version'],
                         'vendor': vendor, 'path': str(target.relative_to(output)), 'sha256': checksum})
    if set(ROOTS) - {p['name'] for p in packages}:
        raise ISOError('Required LAW/Docker packages missing from the offline closure.')
    manifest = {'format': 1, 'architecture': 'amd64', 'roots': list(ROOTS), 'repositories': suites, 'packages': packages}
    (output / 'packages.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    import sys
    collect(Path(sys.argv[1]))
