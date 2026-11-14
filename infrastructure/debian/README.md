# Debian 13 two-ThinkCentre LAW deployment

This directory provisions **two already-installed Debian 13 x86_64 ThinkCentres** with official Docker Engine, Docker Compose v2, and a **localhost-only** smoke-test container. It does NOT erase disks, install an operating system, expose an AI API, deploy agents, or configure SSH identities. The host installation and first SSH trust pairing remain manual.

## Start here

Open [INSTALL_GUIDE.html](INSTALL_GUIDE.html) in a browser (download the raw file if GitHub shows source) for the detailed walkthrough. Read the cautions before choosing to overwrite Windows 11.

## After installing Debian 13 and OpenSSH on both machines

On ThinkCentre A, the Ansible controller:

```bash
git clone -b agent/debian-server-deployment https://github.com/Aggredicus/Local-Agent-Workshop.git
cd Local-Agent-Workshop/infrastructure/debian
bash scripts/bootstrap-controller.sh
cp inventory.ini.example inventory.ini
# Edit IP addresses / user in inventory.ini after making DHCP reservations.
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_law
ssh-copy-id -i ~/.ssh/id_ed25519_law.pub lawadmin@<THINKCENTRE_A_IP>
ssh-copy-id -i ~/.ssh/id_ed25519_law.pub lawadmin@<THINKCENTRE_B_IP>
# Verify host fingerprints out-of-band and accept only trusted keys.
ssh -i ~/.ssh/id_ed25519_law lawadmin@<THINKCENTRE_B_IP> 'cat /etc/debian_version'
ansible-galaxy collection install -r requirements.yml
ansible -i inventory.ini law_nodes -m ping --private-key ~/.ssh/id_ed25519_law
ansible-playbook -i inventory.ini preflight.yml --private-key ~/.ssh/id_ed25519_law --forks 2
ansible-playbook -i inventory.ini site.yml --private-key ~/.ssh/id_ed25519_law --forks 2 --ask-become-pass
ansible-playbook -i inventory.ini verify.yml --private-key ~/.ssh/id_ed25519_law --forks 2 --ask-become-pass
```

**Credential note:** If the sudo passwords differ, supply encrypted per-host `ansible_become_password` values via Ansible Vault rather than a single `--ask-become-pass`. Never commit passwords, private keys, known_hosts, inventories, or real network topology to the public repo.

**SSH hardening note:** Debian has to have `openssh-server` installed on both hosts. Do not disable host key checking. The inventory deliberately references LAN IPs, never a public address. SSH access should be restricted at the router and firewall to your trusted LAN.

## GitHub-triggered deployment

The primary LAW repository is public. **Do not register a privileged self-hosted runner on it.** See `github-actions/README.md` and the workflow *template* intended for a separately configured **private** deployment repo. A public hosted GitHub runner cannot access your private LAN without a tunnel, VPN, or private runner; this kit intentionally opens none.

Once configured, the private workflow manually deploys a reviewed **immutable LAW commit SHA** from its private self-hosted LAN controller and uses private inventory and SSH keys. GitHub approval rules and runner permissions remain operator-controlled. ChatGPT's GitHub connector can author and review code; the currently available connector does not provide direct workflow-dispatch access and cannot SSH into your computers.

## Optional LAW Python CLI on ThinkCentre A

After both Docker smoke tests pass, install the existing reviewed LAW Python CLI only on the controller (no general-purpose agent execution):

```bash
ansible-playbook -i inventory.ini law-cli.yml --private-key ~/.ssh/id_ed25519_law --ask-become-pass
sudo /opt/law/cli-venv/bin/workshop doctor --repo /opt/law/cli-source
```

The CLI checkout is pinned to the existing reviewed main-branch commit. It does not create a remote API or grant agent privileges.

## Optional Rust v0 prototype

Open draft [LAW PR #193](https://github.com/Aggredicus/Local-Agent-Workshop/pull/193). That prototype's native SSH/stdin worker runs only the allowlisted operations `uppercase`, `word-count`, and `sum`. No agent inference, generic shell, live scheduling or Docker isolation exists in it. **Do not mistake it for a production agent swarm.** After independent review, opt in:

```bash
ansible-playbook -i inventory.ini rust-swarm.yml --private-key ~/.ssh/id_ed25519_law --forks 2 --ask-become-pass -e rust_prototype_review_approved=true
```

Before any Rust remote demonstration: verify host fingerprints, ensure `law-swarm` is on the remote PATH, then use the upstream crate README for explicit `submit`/`drive` commands. This is a separate, reversible installation from Docker.

## Architectural alignment

- `me.md` remains the instruction spine; GitHub PRs remain the review boundary.
- `workshop` Python CLI, Chronicle, and HyperKanban remain the governance and project-state interfaces.
- Ansible = provisioning; Docker Compose = each host's containers; Rust prototype = optional bounded worker execution.
- CAW → LAW registry/contracts from draft PR #192 are **not silently copied**. They require licensing/security review and coordinated integration.
- Older Proxmox epics #56/#70/#81 are retained as optional future virtualized deployment, not a prerequisite.
- Existing main-branch licensing concern remains unresolved; review provenance before distributing migrated CAW source.

## Acceptance test

- Preflight detects exactly two Debian 13 hosts.
- `docker info` and `docker compose version` pass on each.
- `curl -fsS http://127.0.0.1:8088/` runs on each node locally.
- `docker ps --format '{{.Names}}'` lists `law-sentinel` on each.
- No Docker socket is mounted in the smoke container; no host port is bound to 0.0.0.0.
- No agent has received credentials or arbitrary shell access.

## Rollback

To stop the smoke-test container without uninstalling Docker:

```bash
sudo docker compose -f /opt/law/compose.yaml down
```

Ansible does not wipe or revert a Windows installation. Keep your verified Windows backup/recovery media and encryption recovery information before any OS change.

## Documentation

- [Debian 13 releases](https://www.debian.org/releases/)
- [Debian installation](https://www.debian.org/distrib/)
- [Docker Debian Engine install](https://docs.docker.com/engine/install/debian/)
- [Ansible documentation](https://docs.ansible.com/)
- [GitHub self-hosted runner security](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
