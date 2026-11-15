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
d-i preseed/early_command string /bin/sh -c 'tail -n 0 -f /var/log/syslog > /dev/ttyS0 2>&1 &'
d-i debconf/priority string critical
d-i passwd/user-fullname string LAW VM Test
d-i passwd/username string lawtest
d-i passwd/user-password password synthetic-vm-only
d-i passwd/user-password-again password synthetic-vm-only
d-i partman-auto/disk string /dev/vda
d-i partman-auto/method string regular
d-i partman-auto/choose_recipe select atomic
d-i partman-partitioning/confirm_write_new_label boolean true
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
trap 'echo LAW_VM_QA_FAILED > /dev/ttyS0; journalctl --no-pager -n 80; poweroff' ERR
test -f /etc/law-install-complete
test -z "$(find /opt/local-agent-workshop /opt/law-offline -not -user root -print -quit)"
test "$(systemctl is-enabled docker.service || true)" = masked
if python3 -c 'import json,sys; sys.exit(not bool(json.load(open("/opt/law-offline/profile.json"))["ssh_public_key"]))'; then
    test "$(systemctl is-enabled ssh.service)" = enabled
    /usr/sbin/sshd -T | grep -x 'passwordauthentication no'
else
    test "$(systemctl is-enabled ssh.service || true)" = masked
fi
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


def vm(command, log, timeout, marker=None, stop_on_marker=False):
    with log.open('wb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            next_notice = time.monotonic() + 60
            while child.poll() is None:
                current = log.read_text(errors='replace')
                if stop_on_marker and marker in current:
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait(timeout=20)
                    break
                if 'Failed to run preseeded command' in current or 'Installation step failed' in current or '!! ERROR:' in current:
                    print(current[-12000:])
                    raise RuntimeError('Debian Installer reported a failed step: ' + str(log))
                if time.monotonic() >= next_notice:
                    tail = current[-800:].replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
                    print(f'::notice::VM progress {log.name}: {tail}', flush=True)
                    next_notice += 60
                if time.monotonic() > deadline:
                    raise RuntimeError('VM timed out: ' + str(log))
                time.sleep(2)
            if child.returncode and not (stop_on_marker and marker in log.read_text(errors='replace')):
                raise RuntimeError('VM failed: ' + str(log))
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=20)
    text = log.read_text(errors='replace')
    if marker and marker not in text:
        print(text[-12000:])
        raise RuntimeError('Missing VM acceptance marker: ' + marker)


def prepare(build):
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
TimeoutStartSec=360
ExecStart=/usr/local/sbin/law-qa-proof
StandardOutput=journal+console
StandardError=journal+console
[Install]
WantedBy=multi-user.target
''')
    (tree / 'isolinux').mkdir()
    (tree / 'isolinux/isolinux.cfg').write_text('''serial 0 115200
console 0
say LAW_BIOS_BOOT_OK
default lawqa
prompt 0
timeout 10
label lawqa
  kernel /install.amd/vmlinuz
  append initrd=/install.amd/initrd.gz auto=true priority=critical preseed/file=/cdrom/law/preseed.cfg console=ttyS0,115200n8 DEBIAN_FRONTEND=text --- console=ttyS0,115200n8
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
    _, accel = machine(build)
    print('::notice::QA images ready; VM accelerator=' + accel)


def machine(build):
    scratch = build / 'qa-private-do-not-upload'
    disk = scratch / 'disposable.qcow2'
    accel = 'kvm' if os.access('/dev/kvm', os.R_OK | os.W_OK) else 'tcg,thread=multi'
    base = ['qemu-system-x86_64', '-accel', accel, '-cpu', 'host' if accel == 'kvm' else 'max', '-smp', '2', '-m', '3072',
            '-nic', 'none', '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
            '-drive', f'file={disk},if=virtio,format=qcow2']
    return base, accel


def install(build):
    scratch = build / 'qa-private-do-not-upload'
    qa_iso = scratch / 'QA-ONLY.iso'
    base, _ = machine(build)
    # Exercise the remastered BIOS boot image, not a direct kernel shortcut.
    vm(base + ['-boot', 'order=d', '-cdrom', str(qa_iso)],
       scratch / 'install.log', 1800, 'LAW_OFFLINE_INSTALL_OK')
    if 'LAW_BIOS_BOOT_OK' not in (scratch / 'install.log').read_text(errors='replace'):
        raise RuntimeError('BIOS bootloader acceptance marker missing.')
    print('::notice::LAW_BIOS_INSTALL_OK: fresh installation completed and powered off with no NIC.')


def boot(build):
    scratch = build / 'qa-private-do-not-upload'
    base, _ = machine(build)
    vm(base, scratch / 'first-boot.log', 600, 'LAW_VM_OFFLINE_ROOTLESS_OK')
    print('::notice::LAW_FIRST_BOOT_OK: rootless Docker, offline container, Compose, Buildx and LAW CLI passed.')


def uefi(build):
    scratch = build / 'qa-private-do-not-upload'
    _, accel = machine(build)
    # Exercise the inherited EFI image and Debian GRUB, without Secure Boot.
    efi = scratch / 'efi.cfg'
    efi.write_text('''serial --unit=0 --speed=115200
terminal_input serial
terminal_output serial
set timeout=1
menuentry 'LAW EFI boot test' {
    echo LAW_UEFI_BOOT_OK
    halt
}
''')
    efi_iso = scratch / 'QA-EFI-ONLY.iso'
    run('xorriso', '-indev', build / OUTPUT, '-outdev', efi_iso, '-map', efi,
        '/boot/grub/grub.cfg', '-boot_image', 'any', 'replay', '-commit')
    import shutil
    variables = scratch / 'OVMF_VARS.fd'
    shutil.copyfile('/usr/share/OVMF/OVMF_VARS_4M.fd', variables)
    vm(['qemu-system-x86_64', '-accel', 'tcg', '-m', '512', '-nic', 'none',
        '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
        '-drive', 'if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
        '-drive', f'if=pflash,format=raw,file={variables}', '-boot', 'order=d', '-cdrom', str(efi_iso)],
       scratch / 'efi.log', 120, 'LAW_UEFI_BOOT_OK', stop_on_marker=True)
    evidence = {'network': 'no NIC (-nic none)', 'installation': 'passed', 'rootless_docker_container': 'passed',
                'accelerator': accel,
                'bios_boot_and_installed_disk_boot': 'passed', 'uefi_grub_boot': 'passed (OVMF, Secure Boot off)',
                'compose_buildx_law_cli': 'passed', 'rootful_docker': 'masked',
                'ssh': 'key-only when profile public key is supplied; otherwise masked',
                'public_iso_disk_answers': 'none; QA-only overlay used a disposable /dev/vda',
                'public_iso_sha256': hashlib.file_digest((build / OUTPUT).open('rb'), 'sha256').hexdigest(),
                'physical_hardware_tested': False}
    (build / 'vm-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print('::notice::LAW_VM_OFFLINE_ROOTLESS_OK: no NIC; real Debian install, rootless Docker smoke, Compose, Buildx and LAW CLI passed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    parser.add_argument('--phase', choices=['all', 'prepare', 'install', 'boot', 'uefi'], default='all')
    args = parser.parse_args()
    build = args.build.resolve()
    for name, action in [('prepare', prepare), ('install', install), ('boot', boot), ('uefi', uefi)]:
        if args.phase in ('all', name):
            action(build)


if __name__ == '__main__':
    main()
