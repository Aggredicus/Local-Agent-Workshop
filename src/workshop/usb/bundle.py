"""Build a release/architecture-specific package closure through authenticated APT."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


class USBError(ValueError):
    pass


def collect_metadata(output: Path) -> None:
    """Save decoded indexes whose hashes appear in their signed InRelease file."""
    arch = subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip()
    metadata = output / 'metadata'
    inventory = []
    for index, package_list in enumerate(sorted(Path('/var/lib/apt/lists').glob(f'*_main_binary-{arch}_Packages*'))):
        prefix = package_list.name.split(f'_main_binary-{arch}_Packages')[0]
        release = package_list.with_name(prefix + '_InRelease')
        if not release.is_file():
            raise USBError('APT index lacks its signed release metadata.')
        shutil.copyfile(release, metadata / f'index-{index}.InRelease')
        with (metadata / f'index-{index}.Packages').open('wb') as destination:
            subprocess.run(['/usr/lib/apt/apt-helper', 'cat-file', str(package_list)], stdout=destination, check=True)
        inventory.append(release.name)
    if not inventory:
        raise USBError('No authenticated package indexes collected.')
    packages = []
    for path in sorted((output / 'packages').glob('*.deb')):
        fields = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package', 'Version', 'Architecture'], text=True)
        packages.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'metadata': fields})
    (output / 'manifest.json').write_text(json.dumps({'format': 1, 'architecture': arch,
        'indexes': inventory, 'packages': packages,
        'trust': 'Installer verifies upstream InRelease signatures and Packages/deb hashes; this manifest is informational.'}, indent=2) + '\n')


def build_bundle(repo: Path, output: Path, image: str) -> dict:
    if not re.fullmatch(r'debian:(?:12|13)-slim@sha256:[a-f0-9]{64}', image):
        raise USBError('Use an official Debian 12/13-slim image pinned to a full sha256 digest.')
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise USBError('Output must be a new directory; existing data is never replaced.')
    for parent in output.parents:
        if parent.is_symlink():
            raise USBError('Output parents must not be symlinks.')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.law-usb-build-', dir=output.parent))
    try:
        subprocess.run(['docker', 'run', '--rm', '--platform', 'linux/amd64',
            '--mount', f'type=bind,source={repo.resolve()},target=/source,readonly',
            '--mount', f'type=bind,source={stage},target=/output',
            image, 'bash', '/source/setup/usb/build-packages.sh'], check=True)
        manifest = json.loads((stage / 'manifest.json').read_text())
        # Validate the COMPLETE upstream chain before offering the generated bundle.
        subprocess.run(['docker', 'run', '--rm', '--network', 'none',
            '--mount', f'type=bind,source={repo.resolve()},target=/source,readonly',
            '--mount', f'type=bind,source={stage},target=/bundle,readonly',
            image, 'bash', '/source/setup/usb/packages.sh', 'verify', '/bundle'], check=True)
        if hasattr(os, 'getuid'):
            # Artifact ownership only; never alter the host outside this staging directory.
            subprocess.run(['docker', 'run', '--rm', '--network', 'none',
                '--mount', f'type=bind,source={stage},target=/output', image,
                'chown', '-R', f'{os.getuid()}:{os.getgid()}', '/output'], check=True)
        os.rename(stage, output)
        return {'output': str(output), 'packages': len(manifest['packages']), 'image': image,
                'upstream_verification': 'passed in a disconnected container', 'installation_test': 'not yet run'}
    finally:
        if stage.exists():
            # Preserve failed artifacts for diagnosis instead of deleting root-owned output.
            print(f'Build staging preserved for diagnosis: {stage}')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['metadata'])
    parser.add_argument('output', type=Path)
    args = parser.parse_args(argv)
    collect_metadata(args.output)


if __name__ == '__main__':
    main()
