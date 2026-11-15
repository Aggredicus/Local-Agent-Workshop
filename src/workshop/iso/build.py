"""Authenticated netinst + signed offline repositories, preserving BIOS/UEFI boot."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request

from .profile import CD_FINGERPRINT, ISOError, ROOTS, preseed, validate_profile
from .repository import digest

IMAGE = 'debian:13-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2'
BASE = 'https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/'
NAME = 'debian-13.7.0-amd64-netinst.iso'
OUTPUT = 'LAW-Debian-13.7.0-amd64.iso'


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def fetch(url: str, target: Path):
    if not url.startswith(BASE):
        raise ISOError('Unexpected upstream download origin.')
    # Fixed HTTPS origin. A detached Debian signature authenticates the content.
    with urllib.request.urlopen(url, timeout=120) as source, target.open('xb') as dest:
        shutil.copyfileobj(source, dest, 1024 * 1024)


def verify_image(directory: Path, keyring: Path) -> dict:
    check = run('gpgv', '--status-fd=1', '--keyring', keyring,
                directory / 'SHA512SUMS.sign', directory / 'SHA512SUMS',
                stdout=subprocess.PIPE, text=True)
    signatures = [line.split() for line in check.stdout.splitlines() if line.startswith('[GNUPG:] VALIDSIG ')]
    if not any(CD_FINGERPRINT in (line[2], line[-1]) for line in signatures):
        raise ISOError('Checksums were not signed by the pinned Debian CD signing key.')
    hashes = []
    for line in (directory / 'SHA512SUMS').read_text().splitlines():
        match = re.fullmatch(r'([a-f0-9]{128}) [ *](.+)', line)
        if match and match[2] == NAME:
            hashes.append(match[1])
    if len(hashes) != 1 or digest(directory / NAME, 'sha512') != hashes[0]:
        raise ISOError('Debian netinst does not match the signed SHA512 checksum.')
    return {'filename': NAME, 'url': BASE + NAME, 'sha512': hashes[0], 'cd_primary_fingerprint': CD_FINGERPRINT}


def copy_source(repo: Path, target: Path):
    allowed_dirs = {'src', 'scripts', 'docs', 'skills', 'schemas', 'templates', 'workflows', 'setup', 'orchestration', 'config', 'examples'}
    allowed_roots = {'README.md', 'me.md', 'AGENTS.md', 'pyproject.toml', '.branch-policy.yaml', 'START-USB.cmd'}
    extensions = {'.py', '.sh', '.md', '.json', '.yaml', '.yml', '.toml', '.txt', '.ps1', '.cs', '.html', '.tmpl', '.cmd'}
    files = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z']).decode().split('\0')
    for name in filter(None, files):
        path = Path(name)
        if not (name in allowed_roots or (path.parts[0] in allowed_dirs and path.suffix in extensions)):
            continue
        origin = repo / path
        if origin.is_symlink() or not origin.is_file():
            raise ISOError('Source payload must contain only regular tracked files.')
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origin, destination)
    (target / 'SOURCE.txt').write_text(subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True))


def boot_menus(tree: Path):
    isolinux = tree / 'isolinux/isolinux.cfg'
    grub = tree / 'boot/grub/grub.cfg'
    for path in (isolinux, grub):
        if not path.is_file():
            raise ISOError('Expected official BIOS and UEFI installer menus are missing.')
        shutil.copyfile(path, path.with_name('law-original.cfg'))
    isolinux.write_text('''path /isolinux/
include menu.cfg
default law
prompt 0
timeout 0
label law
  menu label LAW offline Debian + rootless Docker (confirm disk in installer)
  kernel /install.amd/vmlinuz
  append initrd=/install.amd/initrd.gz auto=true priority=critical preseed/file=/cdrom/law/preseed.cfg --- quiet
''')
    grub.write_text('''set timeout=-1
menuentry 'LAW offline Debian + rootless Docker (confirm disk in installer)' {
    linux /install.amd/vmlinuz auto=true priority=critical preseed/file=/cdrom/law/preseed.cfg --- quiet
    initrd /install.amd/initrd.gz
}
menuentry 'Original Debian installer menu' {
    configfile /boot/grub/law-original.cfg
}
''')


def checksums(tree: Path):
    # Debian Installer's optional media integrity test; final ISO has SHA256 too.
    with (tree / 'md5sum.txt').open('w') as stream:
        for path in sorted(tree.rglob('*')):
            if path.is_file() and not path.is_symlink() and path.name not in {'md5sum.txt', 'boot.cat'}:
                stream.write(f'{digest(path, "md5")}  ./{path.relative_to(tree).as_posix()}\n')


def remaster(base: Path, tree: Path, output: Path):
    run('xorriso', '-indev', base, '-outdev', output, '-map', tree, '/', '-boot_image', 'any', 'replay', '-commit')
    report = run('xorriso', '-indev', output, '-report_el_torito', 'plain', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    if 'BIOS' not in report or 'UEFI' not in report:
        raise ISOError('Remastered image lost BIOS or UEFI boot metadata.')
    return report


def build(repo: Path, output: Path, profile_path: Path, keyring: Path) -> dict:
    profile = validate_profile(json.loads(profile_path.read_text()))
    if output.exists() or output.is_symlink() or any(p.is_symlink() for p in output.absolute().parents):
        raise ISOError('Choose a new output directory with no linked parents; existing data is preserved.')
    output.mkdir(parents=True)
    upstream = output / 'upstream'
    upstream.mkdir()
    for name in ('SHA512SUMS', 'SHA512SUMS.sign', NAME):
        fetch(BASE + name, upstream / name)
    provenance = verify_image(upstream, keyring)
    tree = output / 'tree'
    run('xorriso', '-osirrox', 'on', '-indev', upstream / NAME, '-extract', '/', tree)
    # The ISO filesystem is read-only; its extracted copy is build scratch space.
    for path in (tree, *tree.rglob('*')):
        if not path.is_symlink():
            path.chmod(path.stat().st_mode | 0o200)
    law = tree / 'law'
    law.mkdir()
    source = law / 'source'
    copy_source(repo, source)
    (law / 'installer').mkdir()
    shutil.copyfile(repo / 'setup/iso/late.sh', law / 'installer/late.sh')
    (law / 'preseed.cfg').write_text(preseed(profile))
    (law / 'profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    (law / 'roots.txt').write_text('\n'.join(ROOTS) + '\n')
    run('docker', 'run', '--rm', '--platform', 'linux/amd64',
        '--mount', f'type=bind,source={repo.resolve()},target=/source,readonly',
        '--mount', f'type=bind,source={law.resolve()},target=/output',
        IMAGE, 'bash', '/source/setup/iso/build-packages.sh')
    # Deterministic offline smoke workload from an authenticated Debian binary.
    smoke = output / 'smoke'
    smoke.mkdir()
    manifest = json.loads((law / 'packages.json').read_text())
    busybox = next(p for p in manifest['packages'] if p['name'] == 'busybox-static')
    run('dpkg-deb', '-x', law / busybox['path'], smoke)
    binary = next(p for p in smoke.rglob('busybox') if p.is_file())
    shutil.copyfile(binary, smoke / 'busybox')
    (smoke / 'Dockerfile').write_text('FROM scratch\nCOPY --chmod=755 busybox /busybox\nENTRYPOINT ["/busybox", "echo", "LAW_OFFLINE_DOCKER_OK"]\n')
    run('docker', 'build', '--network=none', '-t', 'law-offline-smoke:1', smoke)
    run('docker', 'save', '-o', law / 'smoke.tar', 'law-offline-smoke:1')
    run('docker', 'run', '--rm', '--network', 'none', '--mount', f'type=bind,source={law.resolve()},target=/output',
        IMAGE, 'chown', '-R', f'{os.getuid()}:{os.getgid()}', '/output')
    shutil.rmtree(law / 'downloads')
    (law / 'docker.asc').unlink()
    # Verify install against real APT while the container has NO network device.
    run('docker', 'run', '--rm', '--network', 'none',
        '--mount', f'type=bind,source={law.resolve()},target=/law,readonly', IMAGE,
        'bash', '/law/source/setup/iso/test-offline.sh')
    boot_menus(tree)
    checksums(tree)
    report = remaster(upstream / NAME, tree, output / OUTPUT)
    (output / 'boot-metadata.txt').write_text(report)
    if (output / OUTPUT).stat().st_size >= 2 * 1024**3:
        raise ISOError('ISO exceeds the single GitHub Release asset size limit.')
    sha = digest(output / OUTPUT)
    (output / (OUTPUT + '.sha256')).write_text(f'{sha}  {OUTPUT}\n')
    evidence = {'format': 1, 'source_commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
                'base': provenance, 'profile': profile, 'builder_image': IMAGE, 'packages': len(manifest['packages']),
                'iso': OUTPUT, 'sha256': sha, 'bytes': (output / OUTPUT).stat().st_size,
                'offline_apt_install': 'passed with Docker --network none',
                'physical_usb_and_wifi_tested': False, 'disk_partitioning_preseeded': False}
    (output / 'build-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, default=Path('setup/iso/profile.json'))
    parser.add_argument('--cd-keyring', type=Path, default=Path('/usr/share/keyrings/debian-role-keys.gpg'))
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.repo, args.output, args.profile, args.cd_keyring), indent=2))
        return 0
    except (ISOError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ISO build stopped: {exc}. Incomplete output is preserved for diagnosis.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
