from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
from .bundle import USBError, build_bundle
from .media import pack

IMAGES = {
    '12': 'debian:12-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc',
    '13': 'debian:13-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2',
}


def add_parser(subparsers):
    parser = subparsers.add_parser('usb', help='Prepare recovery data artifacts; never flash or format a disk')
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    actions = parser.add_subparsers(dest='usb_command', required=True)
    build = actions.add_parser('bundle', help='Build and verify a signed Debian package closure in disposable Docker containers')
    build.add_argument('--debian', choices=['12', '13'], required=True)
    build.add_argument('--output', type=Path, required=True)
    packing = actions.add_parser('pack', help='Package Windows tools and preverified Debian bundles into a data ZIP')
    packing.add_argument('--packages', type=Path, required=True)
    packing.add_argument('--age-archive', type=Path, required=True)
    packing.add_argument('--output', type=Path, required=True)


def handle(args: argparse.Namespace) -> int:
    try:
        if args.usb_command == 'bundle':
            result = build_bundle(args.repo, args.output, IMAGES[args.debian])
        else:
            # Re-verify both bundles using the trusted verifier before distribution.
            for version, image in IMAGES.items():
                bundle = (args.packages / f'debian{version}-amd64').resolve()
                subprocess.run(['docker', 'run', '--rm', '--network', 'none',
                    '--mount', f'type=bind,source={args.repo.resolve()},target=/source,readonly',
                    '--mount', f'type=bind,source={bundle},target=/bundle,readonly',
                    image, 'bash', '/source/setup/usb/packages.sh', 'verify', '/bundle'], check=True)
            result = pack(args.repo, args.packages, args.age_archive, args.output)
        print(json.dumps(result, indent=2))
        return 0
    except (USBError, OSError, ValueError, subprocess.CalledProcessError):
        print('USB artifact preparation failed. Existing outputs are preserved; inspect the package verifier, Docker access and pinned inputs.')
        return 1
