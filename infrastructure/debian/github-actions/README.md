# Opt-in deployment from a PRIVATE GitHub Actions repository

**Do not enable a self-hosted runner in the PUBLIC LAW repository.** GitHub explicitly warns that untrusted workflows in public repositories can compromise self-hosted runners. The template deliberately lives outside `.github/workflows/` so this public LAW branch cannot trigger it.

For first-night setup, use Ansible manually from ThinkCentre A. Only configure this workflow afterward if GitHub-triggered deployments are valuable to you.

## Private deployment repository (manual one-time task)

1. Create a separate **private** repo such as `LAW-Private-Deploy`. Restrict repository write/Actions permissions to trusted maintainers.
2. Copy `PRIVATE_DEPLOY_TEMPLATE.yml` into **the private repo's** `.github/workflows/deploy.yml`. Do not copy it into LAW's public repo.
3. Add a private `inventory.ini` with your LAN addresses. Do not add network topology to the public LAW repo.
4. Set up a dedicated non-root `lawrunner` on ThinkCentre A using GitHub's official **Linux self-hosted runner** steps, registered ONLY with the private repo, using label `law-controller`. Do not register a runner under a privileged root account or allow pull_request workflows from untrusted forks.
5. On ThinkCentre A, pair `lawrunner` SSH keys with both hosts, verify host fingerprints from each host's console, and ensure Ansible can connect noninteractively. Do **not** give the runner Docker socket access.
6. Provision your Ansible sudo credentials encrypted with `ansible-vault` in the private repo's `group_vars/law_nodes/vault.yml` or equivalent. Put the Vault decryption password on the runner only at `/home/lawrunner/.config/law/vault-pass`, mode 0600, owned by lawrunner. Configure no interactive sudo prompts in Actions. Do NOT commit the password or private keys.
7. Optionally configure a GitHub environment `law-production` with available required reviewers and deployment branch restrictions. Availability of private-repo environment reviewer rules depends on GitHub plan. Workflow dispatch itself requires write access.
8. In the private repo Actions tab, choose **LAW two-node Debian deployment**, **Run workflow**, and enter the full SHA of a reviewed LAW commit containing this deployment directory. The workflow requires an immutable SHA rather than a moving branch.

The private repo workflow checks out this public LAW repository **at that SHA**, runs Debian preflight on both hosts, deploys official Docker Engine + localhost-only sentinel in parallel, and verifies both. Only the private runner can reach the LAN hosts. All machine-side mutations are subject to the human approval path you set up.

## Why not GitHub hosted runners?

GitHub-hosted runners cannot normally reach 192.168.x.x devices behind your router. Opening SSH to the Internet or giving a runner a port-forward is not part of this design.

## What ChatGPT can and cannot do

The connected GitHub integration can create branches, commits and pull requests. It cannot access your local machines and currently has no direct Actions `workflow_dispatch` method exposed in this conversation. It can prepare a reviewed commit SHA for you; launching the private workflow remains your authorized GitHub action, unless additional verified tooling is connected later.

## Rollback

To revert Git changes, restore a previously reviewed LAW SHA in the private workflow. To stop the deployed smoke-test service without removing Docker, run `sudo docker compose -f /opt/law/compose.yaml down` on each machine. Docker package upgrades are not automatically downgraded by reverting a source SHA.
