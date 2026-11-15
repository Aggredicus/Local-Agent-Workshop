"""Install a QA-only derivative with no NIC; never upload this ISO or disk."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import os
import signal
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from workshop.iso.build import OUTPUT, run


QA = '''
# QA ONLY: disposable virtual disk; never included in public installer.
d-i passwd/user-fullname string LAW VM Test
d-i passwd/username string lawtest
d-i passwd/user-password password synthetic-vm-only
d-i passwd/user-password-again password synthetic-vm-only
d-i partman-auto/disk string /dev/vda
d-i partman-auto/method string regular
d-i partman-auto/choose_recipe select atomic
d-i partman/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true
d-i grub-installer/only_debian boolean true
d-i grub-installer/bootdev string /dev/vda
d-i finish-install/reboot_in_progress note
d-i debian-installer/exit/poweroff boolean true
'''
PROOF = '''#!/bin/bash
set -euxo pipefail
test -f /etc/law-install-complete
test "$(systemctl is-enabled docker.service || true)" = masked
test "$(systemctl is-enabled ssh.service || true)" = masked
! id -nG lawtest | tr ' ' '\\n' | grep -qx docker
uid=$(id -u lawtest)
for i in $(seq 1 120); do
  if runuser -u lawtest -- env XDG_RUNTIME_DIR=/run/user/$uid docker info >/dev/null 2>&1; then break; fi
  sleep 2
done
runuser -u lawtest -- env XDG_RUNTIME_DIR=/run/user/$uid docker info
runuser -u lawtest -- env XDG_RUNTIME_DIR=/run/user/$uid docker info --format '{{json .SecurityOptions}}' | grep -q rootless
runuser -u lawtest -- env XDG_RUNTIME_DIR=/run/user/$uid docker load -i /opt/law-offline/smoke.tar
runuser -u lawtest -- env XDG_RUNTIME_DIR=/run/user/$uid docker run --rm --network none law-offline-smoke:1
runuser -u lawtest -- docker compose version
runuser -u lawtest -- docker buildx version
runuser -u lawtest -- workshop --help
echo LAW_VM_OFFLINE_ROOTLESS_OK > /dev/ttyS0
sync
poweroff
'''


def vm(command, log, timeout, marker=None):
    with log.open('wb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            while child.poll() is None:
                if time.monotonic() > deadline:
                    raise RuntimeError('VM timed out: ' + str(log))
                time.sleep(2)
            if child.returncode:
                raise RuntimeError('VM failed: ' + str(log))
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=20)
    text = log.read_text(errors='replace')
    if marker and marker not in text:
        print(text[-12000:])
        raise RuntimeError('Missing VM acceptance marker: ' + marker)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    args = parser.parse_args()
    build = args.build.resolve()
    scratch = build / 'qa-private-do-not-upload'
    scratch.mkdir()
    tree = scratch / 'tree'
    tree.mkdir()
    # Overlay only QA files; the rest stays in the already-verified public ISO.
    (tree / 'law').mkdir()
    (tree / 'law/preseed.cfg').write_text((build / 'tree/law/preseed.cfg').read_text() + QA)
    late = (build / 'tree/law/installer/late.sh').read_text()
    (tree / 'law/installer').mkdir()
    (tree / 'law/installer/late.sh').write_text(late + '''
echo LAW_OFFLINE_INSTALL_OK > /dev/ttyS0
cp /cdrom/law/qa-proof.sh /target/usr/local/sbin/law-qa-proof
chmod 755 /target/usr/local/sbin/law-qa-proof
cp /cdrom/law/qa-proof.service /target/etc/systemd/system/law-qa-proof.service
in-target systemctl enable law-qa-proof.service
''')
    (tree / 'law/qa-proof.sh').write_text(PROOF)
    (tree / 'law/qa-proof.service').write_text('''[Unit]
After=systemd-user-sessions.service systemd-logind.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/law-qa-proof
StandardOutput=journal+console
StandardError=journal+console
[Install]
WantedBy=multi-user.target
''')
    qa_iso = scratch / 'QA-ONLY.iso'
    # Remap the four QA files without replacing the entire base tree.
    cmd = ['xorriso', '-indev', str(build / OUTPUT), '-outdev', str(qa_iso)]
    for path in sorted(tree.rglob('*')):
        if path.is_file():
            cmd += ['-map', str(path), '/' + path.relative_to(tree).as_posix()]
    run(*cmd, '-boot_image', 'any', 'replay', '-commit')
    disk = scratch / 'disposable.qcow2'
    run('qemu-img', 'create', '-f', 'qcow2', disk, '16G')
    base = ['qemu-system-x86_64', '-accel', 'tcg,thread=multi', '-cpu', 'max', '-smp', '2', '-m', '3072',
            '-nic', 'none', '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
            '-drive', f'file={disk},if=virtio,format=qcow2']
    # Direct boot of the real installer kernel; serial output is safe (synthetic account only).
    vm(base + ['-cdrom', str(qa_iso), '-kernel', str(build / 'tree/install.amd/vmlinuz'),
               '-initrd', str(build / 'tree/install.amd/initrd.gz'), '-append',
               'auto=true priority=critical preseed/file=/cdrom/law/preseed.cfg console=ttyS0,115200n8 DEBIAN_FRONTEND=text --- console=ttyS0,115200n8'],
       scratch / 'install.log', 1800, 'LAW_OFFLINE_INSTALL_OK')
    vm(base, scratch / 'first-boot.log', 600, 'LAW_VM_OFFLINE_ROOTLESS_OK')
    evidence = {'network': 'no NIC (-nic none)', 'installation': 'passed', 'rootless_docker_container': 'passed',
                'compose_buildx_law_cli': 'passed', 'rootful_docker_and_ssh': 'masked',
                'public_iso_disk_answers': 'none; QA-only overlay used a disposable /dev/vda',
                'public_iso_sha256': hashlib.file_digest((build / OUTPUT).open('rb'), 'sha256').hexdigest(),
                'physical_hardware_tested': False}
    (build / 'vm-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print('::notice::LAW_VM_OFFLINE_ROOTLESS_OK: no NIC; real Debian install, rootless Docker smoke, Compose, Buildx and LAW CLI passed.')


if __name__ == '__main__':
    main()
