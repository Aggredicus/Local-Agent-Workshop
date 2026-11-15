#!/bin/sh
# Debian Installer invokes this only after its normal disk/account confirmations.
set -eu
test -d /target/etc
test -f /target/etc/debian_version
test ! -e /target/etc/law-install-complete
mkdir -p /target/opt/law-offline /target/opt/local-agent-workshop
cp -a /cdrom/law/repositories /target/opt/law-offline/
cp /cdrom/law/docker.gpg /target/opt/law-offline/docker.gpg
cp /cdrom/law/profile.json /target/opt/law-offline/profile.json
cp /cdrom/law/roots.txt /target/opt/law-offline/roots.txt
cp /cdrom/law/smoke.tar /target/opt/law-offline/smoke.tar
cp -a /cdrom/law/source/. /target/opt/local-agent-workshop/
touch /target/etc/law-installer-authorized
in-target /bin/bash /opt/local-agent-workshop/setup/iso/install-law.sh
