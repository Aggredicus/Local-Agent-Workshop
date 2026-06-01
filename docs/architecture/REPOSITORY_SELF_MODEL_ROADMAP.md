# Repository Self-Model Roadmap

This roadmap is the first repository-native self-model for **Local Agent Workshop**. It is a flexible planning artifact, not a runtime authority.

The goal is to help the repository understand its own structure the way an embodied robot maintains a body model: it should know its bones, muscles, nervous system, memory, senses, immune system, metabolism, and proprioception. As the project evolves, this self-model should be regenerated from GitHub issues, pull requests, commits, HyperKanban state, Chronicle events, CI reports, validation artifacts, and eventually Proxmox-local runtime reports.

## Current anchor

- Active preparation sprint: #118
- First implementation PR: #119
- Current sprint objective: make the repository agent-operable before the larger Proxmox/runtime-control-plane sprint.

## Source-of-truth layers

| Layer | Role |
|---|---|
| `me.md` | Canonical instruction spine |
| GitHub Issues | Planned work and coordination |
| Pull Requests | Review boundary |
| CI | Validation proof |
| Chronicle | Historical event memory |
| HyperKanban | Operational projection |
| Reports | Evidence artifacts |
| Dashboard | Generated visual projection, not authority |

## Repository body schema

| Body part | Repository equivalent |
|---|---|
| Bones | `docs/governance/`, `docs/protocols/`, `schemas/`, `me.md` |
| Muscles | `scripts/`, `skills/`, future `workshop` CLI |
| Nervous system | HyperKanban, workflow state, trace context, event envelope, dashboard projection |
| Memory | Chronicle events, Git commits, PR history, issue history, `reports/` |
| Senses | GitHub issues, commits, PRs, CI results, reports, schema registry, dashboard warnings |
| Immune system | risk policy, human approval boundaries, secret hygiene, prompt-injection policy, side-effect wrappers |
| Metabolism | CI validation gates, cleanup, quality-analysis, publish protocol |
| Proprioception | repository dependency graph, planned-path map, file ownership analysis, dashboard verdicts |

## Core invariants

- JSON artifacts become source-of-truth candidates only when schema-governed and validated.
- Dashboard views are projections, not authority.
- Chronicle is append-only historical memory.
- HyperKanban is a compact operational projection.
- No protected branch mutation without explicit human approval.
- No public endpoint exposure by default.
- No secrets in repository artifacts.
- No work is done without evidence.
- No high-risk output self-approval.
- No prior chat history should be required for cold-start agents.

## Roadmap phases

### M0 — Instruction spine and existing foundation

**Status:** partially complete

**Goal:** Preserve current repo identity, branch model, cleanup/quality/publish protocols, and agent routing.

**Representative issues and PRs:** #48, #118, #119, prior cleanup/quality/publish work.

**Primary paths:**

- `me.md`
- `docs/governance/`
- `docs/protocols/`
- `skills/`
- `reports/`

**Exit criteria:**

- Agents can find `me.md`.
- Branch, risk, and review policies are discoverable.
- Cleanup, quality-analysis, and publish protocols exist.

### M1 — Agent-operable grammar

**Status:** in progress

**Goal:** Give all future work a standard execution contract and issue template.

**Issues:** #92, #118, #119

**Primary paths:**

- `docs/protocols/STANDARD_EXECUTION_CONTRACT.md`
- `.github/ISSUE_TEMPLATE/agent-task.md`
- `me.md`

**Exit criteria:**

- Standard execution contract exists.
- Agent-task issue template exists.
- `me.md` routes agents to the contract.
- PR #119 is reviewed and merged or revised.

### M2 — Schema registry and validation metabolism

**Status:** planned

**Goal:** Make schemas and examples discoverable, versioned, and locally validatable.

**Issues:** #109, #111, #112

**Primary paths:**

- `schemas/registry.schema.json`
- `schemas/schema-registry.json`
- `scripts/validate_repo_contracts.py`
- `reports/validation/`
- `tests/fixtures/workflows/`

**Exit criteria:**

- Schema registry validates.
- At least five schemas are registered.
- Validation gate runs locally.
- Fixtures cover success, blocked, missing-evidence, expired-lease, prompt-injection, and human-approval cases.

### M3 — Navigation and hello workflow self-simulation

**Status:** planned

**Goal:** Give the repository a map of itself and a minimal end-to-end example workflow.

**Issues:** #114, #115, #116

**Primary paths:**

- `docs/README.md`
- `docs/NAVIGATION_INDEX.md`
- `docs/architecture/REPOSITORY_KNOWLEDGE_MAP.md`
- `examples/hello-workflow/`

**Exit criteria:**

- Duplicate #114/#115 is resolved.
- Planned and implemented docs are clearly distinguished.
- Hello workflow examples validate against available schemas.
- Human review packet exists.

### M4 — Deterministic HyperKanban CI dashboard

**Status:** planned

**Goal:** Generate a deterministic repository dependency graph and dashboard from source artifacts.

**Issue:** #117

**Primary paths:**

- `schemas/repository_dependency_graph.schema.json`
- `schemas/dashboard_projection.schema.json`
- `schemas/hyperkanban_repository_timeline.schema.json`
- `scripts/build_dashboard_projection.py`
- `scripts/analyze_repository_graph.py`
- `scripts/validate_dashboard_projection.py`
- `scripts/render_ci_dashboard.py`
- `reports/dashboard/`
- `orchestration/hyperkanban/views/`
- `.github/workflows/hyperkanban-dashboard.yml`

**Exit criteria:**

- Dashboard is generated from repo artifacts, not hand-modeled state.
- Analyzer produces ready, blocked, missing-evidence, and human-gated verdicts.
- Every recommendation includes a reason chain.
- CI uploads dashboard artifacts.

### M5 — Agent arrival and swarm constraints

**Status:** planned

**Goal:** Make cold-start agent entry, task readiness, permissions, budgets, evidence, handoffs, dry-runs, and evaluation explicit.

**Issues:** #81–#91

**Primary paths:**

- `docs/protocols/AGENT_ARRIVAL_PROTOCOL.md`
- `docs/governance/AGENT_PERMISSION_TIERS.md`
- `schemas/agent_task_intake.schema.json`
- `schemas/agent_runtime_budget.schema.json`
- `schemas/agent_work_evidence.schema.json`
- `schemas/agent_handoff_packet.schema.json`
- `reports/dry-run/`
- `reports/project-state/`

**Exit criteria:**

- Fresh agents can orient without prior chat history.
- Every mutable task has role, budget, lease, evidence, and handoff requirements.
- Dry-run can reject under-specified work.
- Project-state diagnosis identifies ready, blocked, missing, and risky work.

### M6 — Runtime control plane

**Status:** planned

**Goal:** Add supervisor, workflow state, trace context, event envelopes, retry/dead-letter semantics, boundaries, MCP/A2A plans, side-effect wrappers, and untrusted-content defense.

**Issues:** #93–#104

**Primary paths:**

- `docs/protocols/SUPERVISOR_CONTROL_PLANE.md`
- `schemas/supervisor_decision_log.schema.json`
- `schemas/workflow_state.schema.json`
- `schemas/trace_context.schema.json`
- `schemas/workshop_event_envelope.schema.json`
- `schemas/dead_letter_record.schema.json`
- `docs/governance/SIDE_EFFECT_WRAPPER_POLICY.md`
- `docs/security/UNTRUSTED_CONTENT_POLICY.md`

**Exit criteria:**

- Runtime state exists outside model context.
- Trace IDs connect decisions, work, evidence, and reports.
- Side-effect wrappers define authorization and idempotency.
- Untrusted content cannot override governance.

### M7 — Proxmox Workshop Node implementation

**Status:** planned

**Goal:** Make Proxmox a first-class local runtime substrate for local model serving, local CI, artifact storage, and local workers.

**Issues:** #56–#69

**Primary paths:**

- `docs/infrastructure/PROXMOX_WORKSHOP_NODE.md`
- `docs/governance/LOCAL_INFRASTRUCTURE_BOUNDARIES.md`
- `schemas/local_model_provider.schema.json`
- `scripts/check_local_llm.py`
- `scripts/workshop_node_report.sh`
- `skills/proxmox-local-llm/SKILL.md`
- `skills/workshop-node-check/SKILL.md`
- `orchestration/leases/`
- `reports/model-health/`
- `reports/local-node/`

**Exit criteria:**

- Local model provider config validates.
- Local LLM health check emits reports.
- Workshop node check is non-destructive.
- Leases protect concurrent worktrees.
- Chronicle/HyperKanban can consume local reports as evidence.

### M8 — Operations and long-term maintenance

**Status:** planned

**Goal:** Keep the Proxmox/local agent system observable, recoverable, secure, and maintainable.

**Issues:** #70–#80

**Primary paths:**

- `docs/operations/BACKUP_AND_RESTORE_POLICY.md`
- `docs/operations/RETENTION_POLICY.md`
- `docs/dashboard/PROXMOX_WORKSHOP_DASHBOARD_SPEC.md`
- `docs/operations/LOCAL_MODEL_REGISTRY.md`
- `docs/operations/INCIDENT_RESPONSE_RUNBOOK.md`
- `docs/security/LOCAL_INFRASTRUCTURE_SECRETS.md`
- `scripts/check_artifact_integrity.py`
- `scripts/check_environment_drift.py`

**Exit criteria:**

- Backups and restore rehearsals are documented.
- Retention audit is read-only by default.
- Endpoint hardening and secret rotation checklists exist.
- Artifact integrity and environment drift can be checked.
- Human review checklist exists.

### M9 — Release readiness and continuous self-improvement

**Status:** planned

**Goal:** Make the repository self-diagnosing, release-aware, and capable of improving from evidence.

**Issues:** #105–#108, #113

**Primary paths:**

- `docs/evaluation/GOLDEN_PATH_RUNTIME_SIMULATION.md`
- `scripts/simulate_golden_path.py`
- `docs/protocols/BOUNDED_FANOUT_POLICY.md`
- `docs/protocols/REVIEWER_CRITIC_AGENT_PROTOCOL.md`
- `docs/project-management/ISSUE_TAXONOMY.md`
- `docs/project-management/MILESTONE_STRATEGY.md`

**Exit criteria:**

- Golden-path simulation runs.
- Parallel work requires dependency/resource checks.
- High-risk outputs require reviewer/critic pass.
- Issue taxonomy and milestones guide humans and agents.

## Adaptive damage model

The repository should respond to degraded subsystems the way a robot updates its body model after losing a limb or sensor.

| Condition | Symptom | Response |
|---|---|---|
| Local model endpoint down | Model health check fails | Mark local-model tasks blocked, route docs/schema tasks to fallback, emit report |
| Schema drift | Fixtures or examples fail validation | Block dependent implementation, update schema registry or migration notes |
| Duplicate issue | Two issues claim the same objective/path | Mark duplicate or stale, require human decision or close one issue |
| Missing evidence | Task claims done but no report/check/packet exists | Mark not human-ready, route back to evidence generation |
| Proxmox node unavailable | Local node smoke test fails | Pause local-runtime-dependent work, continue docs/schema work, preserve incident report |

## Agent operating modes

| Mode | Goal | Inputs | Stop if |
|---|---|---|---|
| cold_start | Orient without prior chat history | `README.md`, `me.md`, navigation index, dashboard latest artifact | instruction spine not found or task lacks execution contract |
| issue_execution | Produce bounded outputs and evidence | GitHub issue, execution contract, work packet, allowed paths | dependency incomplete, evidence impossible, risk boundary reached |
| project_diagnosis | Classify ready, blocked, missing, risky, stale, duplicate work | HyperKanban state, issues, reports, schema registry, dashboard projection | data sources disagree without resolution |
| proxmox_runtime | Run local agents and local model checks safely | local node report, model health report, leases, resource budgets | endpoint exposure risk, host mutation needed, secrets required, local node degraded |

## Immediate next actions

1. Review PR #119 for #92 and merge or request changes.
2. Implement #109: schema registry and compatibility policy.
3. Implement #111: CI/local validation gate.
4. Resolve #114/#115 duplication and implement the surviving documentation map.
5. Implement #116: minimal hello workflow reference implementation.
6. Implement #117 as a generated deterministic CI dashboard rather than a hand-modeled prototype.

## Proxmox optimization path

1. Keep the first dashboard and graph pipeline runnable without Proxmox.
2. Add Proxmox local node checks as optional sensor inputs.
3. Run schema validation and dashboard generation on the local workshop runner.
4. Store large reports/artifacts locally and summarize to GitHub.
5. Use local LLM health checks to select local versus cloud model routing.
6. Use resource budgets to avoid overloading local CPU/RAM/GPU.
7. Treat Proxmox node health as part of the repository self-model.

## How agents should use this roadmap

1. Start with the active sprint and current PR.
2. Use phase exit criteria to understand what done means.
3. Use source-of-truth layers to decide which artifacts are authority and which are projections.
4. Use the adaptive damage model to route around broken subsystems.
5. Use next actions to pick the smallest safe next step.
6. Stop if evidence is missing, source-of-truth layers disagree, or a human approval boundary is reached.

## How this becomes live

This document should eventually be generated from:

- GitHub issues and PRs,
- Git commit history,
- schema registry,
- HyperKanban state,
- Chronicle events,
- CI validation reports,
- dashboard projection JSON,
- Proxmox local node reports,
- local model health reports.

The companion JSON seed in `examples/self-model/repo_self_model_seed.json` is a seed/example artifact only. It should not be treated as canonical runtime state until schema governance and validation exist.
