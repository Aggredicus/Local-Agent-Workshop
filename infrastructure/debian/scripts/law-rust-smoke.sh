#!/usr/bin/env bash
set -euo pipefail
# Explicit optional smoke run ONLY after reviewed Rust PR #193 is installed.
# Do not run this with unrestricted agent-submitted input.
: "${LAW_WORKER:?Set LAW_WORKER to verified user@LAN-IP for ThinkCentre B}"
STATE="${HOME}/.local/state/law-swarm-smoke"
law-swarm init --state "$STATE"
law-swarm submit --state "$STATE" --id remote1 --thread t1 --target "ssh:$LAW_WORKER" --tool uppercase --input "hello from LAW"
law-swarm submit --state "$STATE" --id local1 --thread t2 --target local --tool sum --input "2, 4, 6"
law-swarm drive --state "$STATE" --parallel 2 --budget 10
law-swarm status --state "$STATE"
