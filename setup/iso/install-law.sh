#!/bin/bash
# Fresh-installer entry point. Never invoked by the recovery menu.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive LC_ALL=C
[[ $EUID == 0 && -f /etc/law-installer-authorized && ! -e /etc/law-install-complete ]]
. /etc/os-release
[[ $ID == debian && $VERSION_ID == 13 ]]
offline=/opt/law-offline
source=/opt/local-agent-workshop
mkdir -p /etc/apt/law.sources.d
cat > /etc/apt/law.sources.d/offline.sources <<'EOF'
Types: deb
URIs: file:/opt/law-offline/repositories/debian
Suites: trixie trixie-updates
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: file:/opt/law-offline/repositories/debian-security
Suites: trixie-security
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: file:/opt/law-offline/repositories/docker
Suites: trixie
Components: stable
Signed-By: /opt/law-offline/docker.gpg 9DC858229FC7DD38854AE2D88D81803C0EBFCD88
EOF
# Stop maintainer scripts from starting a rootful daemon or SSH during install.
[[ ! -e /usr/sbin/policy-rc.d ]] || { echo 'Existing service policy preserved; refusing fresh-install bootstrap.' >&2; exit 2; }
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 0755 /usr/sbin/policy-rc.d
trap 'rm -f /usr/sbin/policy-rc.d' EXIT
opts=(-o Dir::Etc::sourcelist=/dev/null -o Dir::Etc::sourceparts=/etc/apt/law.sources.d -o Acquire::Languages=none)
apt-get "${opts[@]}" update
mapfile -t roots < "$offline/roots.txt"
[[ ${#roots[@]} -gt 20 ]]
apt-get "${opts[@]}" --no-remove --no-install-recommends -y install "${roots[@]}"
cp /etc/apt/law.sources.d/offline.sources /etc/apt/sources.list.d/law-offline.sources
# All future offline updates use the same authenticated file repositories.
# Their signed expiry is deliberately enforced; rebuild an expired image.
systemctl mask docker.service docker.socket containerd.service ssh.service ssh.socket
install -d -m 0755 /usr/local/lib/law
cat > /usr/local/lib/law/entry.py <<'PY'
import sys
sys.path.insert(0, '/opt/local-agent-workshop/src')
from workshop.cli import main
raise SystemExit(main())
PY
printf '#!/bin/sh\nexec /usr/bin/python3 -I /usr/local/lib/law/entry.py "$@"\n' > /usr/local/bin/workshop
chmod 0755 /usr/local/bin/workshop
install -d -m 0755 /opt/local-agent-workshop-usb
cat > /opt/local-agent-workshop-usb/entry.py <<'PY'
import os
import sys
os.environ['PATH'] = '/usr/sbin:/usr/bin:/sbin:/bin'
sys.path.insert(0, '/opt/local-agent-workshop/src')
from workshop.usb.wifi import main
raise SystemExit(main())
PY
printf '#!/bin/sh\nexec /usr/bin/python3 -I /opt/local-agent-workshop-usb/entry.py "$@"\n' > /usr/local/sbin/law-usb
chmod 0755 /usr/local/sbin/law-usb
mapfile -t users < <(getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 && $7 !~ /(nologin|false)$/ {print $1}')
[[ ${#users[@]} == 1 ]] || { echo 'Expected exactly one installer-created normal user.' >&2; exit 2; }
user=${users[0]}
uid=$(id -u "$user")
home=$(getent passwd "$user" | cut -d: -f6)
[[ $home == /home/"$user" && -d $home && ! -L $home ]]
if ! grep -q "^$user:" /etc/subuid; then usermod --add-subuids 100000-165535 "$user"; fi
if ! grep -q "^$user:" /etc/subgid; then usermod --add-subgids 100000-165535 "$user"; fi
# Rootless daemon is the only enabled Docker service. No docker-group grant.
install -d -o "$user" -g "$user" -m 0700 "$home/.config" "$home/.config/docker"
install -d -o "$user" -g "$user" -m 0755 "$home/.config/systemd/user/default.target.wants"
cat > "$home/.config/systemd/user/docker.service" <<'EOF'
[Unit]
Description=LAW rootless Docker Engine
After=network.target
[Service]
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/dockerd-rootless.sh
Restart=on-failure
RestartSec=3
TimeoutStartSec=0
Delegate=yes
TasksMax=infinity
LimitNOFILE=infinity
LimitNPROC=infinity
[Install]
WantedBy=default.target
EOF
printf '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}\n' > "$home/.config/docker/daemon.json"
ln -s ../docker.service "$home/.config/systemd/user/default.target.wants/docker.service"
chown -R "$user:$user" "$home/.config"
install -d -m 0755 /var/lib/systemd/linger
touch "/var/lib/systemd/linger/$user"
runuser -u "$user" -- docker context create rootless --docker "host=unix:///run/user/$uid/docker.sock"
runuser -u "$user" -- docker context use rootless
cp -a "$source" "$home/Local-Agent-Workshop"
chown -R "$user:$user" "$home/Local-Agent-Workshop"
runuser -u "$user" -- git -C "$home/Local-Agent-Workshop" init -b main
install -m 0755 "$source/setup/iso/enable-ssh.py" /usr/local/sbin/law-enable-ssh
key=$(python3 -c 'import json; print(json.load(open("/opt/law-offline/profile.json"))["ssh_public_key"])')
if [[ -n $key ]]; then
    printf '%s\n' "$key" > /run/law-install-public-key
    /usr/local/sbin/law-enable-ssh /run/law-install-public-key
    rm /run/law-install-public-key
fi
cp "$source/setup/iso/FIRST-BOOT.txt" /etc/motd
printf 'LAW offline install complete. User: %s\n' "$user" > /etc/law-install-complete
rm /etc/law-installer-authorized
echo LAW_OFFLINE_INSTALL_OK
