#!/usr/bin/python3 -I
"""Enable key-only SSH after a local operator supplies their PUBLIC key."""
import os
from pathlib import Path
import pwd
import subprocess
import sys
sys.path.insert(0, '/opt/local-agent-workshop/src')
from workshop.iso.profile import validate_profile
import json

if os.geteuid() != 0 or len(sys.argv) != 2:
    raise SystemExit('Use sudo law-enable-ssh /path/to/your_ed25519_PUBLIC_key.pub')
profile = json.loads(Path('/opt/law-offline/profile.json').read_text())
profile['ssh_public_key'] = Path(sys.argv[1]).read_text().strip()
key = validate_profile(profile)['ssh_public_key']
if not key:
    raise SystemExit('An Ed25519 public key is required.')
users = [p for p in pwd.getpwall() if 1000 <= p.pw_uid < 60000 and p.pw_shell not in ('/bin/false', '/usr/sbin/nologin')]
if len(users) != 1:
    raise SystemExit('Expected one installer-created account.')
user = users[0]
directory = Path(user.pw_dir) / '.ssh'
if directory.is_symlink() or (directory / 'authorized_keys').exists():
    raise SystemExit('Existing SSH configuration preserved; review manually.')
directory.mkdir(mode=0o700, exist_ok=True)
os.chown(directory, user.pw_uid, user.pw_gid)
path = directory / 'authorized_keys'
with path.open('x') as stream:
    stream.write(key + '\n')
os.chmod(path, 0o600)
os.chown(path, user.pw_uid, user.pw_gid)
Path('/etc/ssh/sshd_config.d/10-law.conf').write_text('PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\nPubkeyAuthentication yes\n')
subprocess.run(['sshd', '-t'], check=True)
subprocess.run(['systemctl', 'unmask', 'ssh.service'], check=True)
subprocess.run(['systemctl', 'enable', 'ssh.service'], check=True)
print('Key-only SSH enabled for the next boot. Verify the Debian host-key fingerprint before connecting.')
