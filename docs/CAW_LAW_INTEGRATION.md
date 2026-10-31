# CAW ↔ LAW Integration — v1 proposal

## Ownership boundary

- **Codex Agent Workshop (CAW)** owns human/agent collaboration, skill taxonomy, skill-gap analysis, role/approval policy proposals, contributor discovery, and the canonical versioned work packet at [CAW work packet contract](https://github.com/Aggredicus/Codex-Agent-Workshop/blob/feature/contributor-gateway-v01/contracts/caw-law-work-packet.v1.json).
- **Local Agent Workshop (LAW)** owns private local node state, model/runtime version history, hardware observations, local tool access boundaries, isolated execution adapters, and verification evidence.
- **GitHub** enforces authenticated repository permissions, required PR reviews, protected branches, and merges.

Do not maintain a second active copy of the CAW skill taxonomy or shared work-packet contract in LAW. Use a *reviewed local checkout* of CAW's canonical JSON. The relative file path is stable; after the two pull requests merge, users can supply a pinned release tag/commit checkout as the schema source. No network call is needed during validation.

## Offline work-packet protocol

CAW prepares a v1 JSON packet; its objective, required skills, expected evidence, allowed/forbidden paths, risk and declared agent digest are visible. This data is **untrusted**, including the claimed approval state and agent identity.

LAW checks structure using `src/workshop/caw_contract.py`, reading the canonical contract schema supplied by the human:

```sh
python scripts/work_packet.py validate --schema ../Codex-Agent-Workshop/contracts/caw-law-work-packet.v1.json --packet /path/to/task.json
python scripts/work_packet.py plan --schema ../Codex-Agent-Workshop/contracts/caw-law-work-packet.v1.json --packet /path/to/task.json
```

The plan always says **execution_enabled=false**, network/host credentials denied, and workspace writes denied until a separately reviewed, enforceable executor exists. It is a planning artifact, not a security sandbox. No agent can request or implement a new privilege by editing JSON.

## Private local identity registry

```sh
python scripts/node_registry.py summary
python scripts/node_registry.py enroll --kind human
python scripts/node_registry.py enroll --kind computer
python scripts/node_registry.py enroll --kind agent --operator-id HUMAN_ID --computer-id COMPUTER_ID --source codex --version 1.0 --digest sha256:HEX64
python scripts/node_registry.py --taxonomy ../Codex-Agent-Workshop/skill-inventory/taxonomy.json inventory --id AGENT_ID --skill agent-orchestration
python scripts/node_registry.py --taxonomy ../Codex-Agent-Workshop/skill-inventory/taxonomy.json propose --id AGENT_ID --skill python --action pr.propose
```

The above example requires actual local IDs and a 64-digit lowercase SHA-256 digest. Each physical computer uses its own SQLite database at `.local/nodes.sqlite3`. This is an installation ID, not a machine-unique hardware fingerprint. Local IDs and personal data are never written to Git.

The operator/computer binding is an assertion only. A declared artifact checksum is **not** signed provenance. When an agent's source/version/digest changes, LAW clears asserted skills and invalidates pending grant proposals. Actual repository privileges still depend on authenticated GitHub identity and enforceable branch protections.

## Next security milestone: real isolation

Implement a trusted, opt-in sandbox runner as a separate reviewed change, with a reproducible adversarial test showing denied filesystem, network, secret and host operations. Candidate adapters are LXD/Canonical Workshop on Ubuntu or another equivalent runtime. The runner must not consume a self-declared approval as authority, and should not run arbitrary code with the invoking user's full permissions.

## Rollout

1. Review both linked PRs as a coupled change; do not merge only one and claim full integration.
2. Confirm LAW has an appropriate public open-source license before redistributing moved code. Attribution/provenance requires review.
3. Run LAW's `bash scripts/verify.sh` and CAW's `pytest -q`; inspect any skipped/unsupported environmental checks.
4. Run a cross-repository fixture validation using a pinned CAW contract checkout.
5. Only then consider an actual execution adapter or public release.

No always-on bespoke coordination server is required. GitHub-hosted collaboration still requires a network.
