# Repository Knowledge Map

This document explains how Local Agent Workshop organizes authority, memory, projections, reports, and planned runtime systems.

It exists so fresh agents can understand what is implemented, what is planned, and what must not be treated as source of truth.

## Source-of-truth and projection model

```text
me.md
  = instruction spine

GitHub Issues
  = planned work and coordination

Pull Requests
  = review boundary

CI
  = validation proof

Chronicle
  = historical event memory

HyperKanban
  = compact operational projection

Reports
  = evidence artifacts

Dashboard
  = generated visual projection, not authority
```

## Implemented body map

| Subsystem | Current implementation | Role |
|---|---|---|
| Instruction spine | `me.md` | Routes agents to policies, protocols, and workflows. |
| Thin adapter files | `AGENTS.md`, `CODEX.md`, `CLAUDE.md` | Point different agents to `me.md`. |
| Governance | `docs/governance/` | Branch, risk, approval, and autonomous-agent boundaries. |
| Protocols | `docs/protocols/` | Cleanup, quality, publish, grind, review, and related process docs. |
| HyperKanban | `orchestration/hyperkanban/` | Compact current-state projection seed. |
| Scripts | `scripts/` | Cleanup, verification, HyperKanban validation, and active-stack contract validation. |
| CLI | `src/workshop/cli.py` | Initial `workshop` command surface, currently HyperKanban-focused. |
| Tests | `tests/` | Current unit and CLI tests. |
| CI | `.github/workflows/ci.yml` | Installs package and runs local verification. |

## Planned body map

| Subsystem | Planned implementation | Driving issues |
|---|---|---|
| Agent arrival | first-contact protocol and task readiness | #81–#91 |
| Schema governance | registry and validation gate | #109, #111 |
| Self-model | roadmap seed, schema, generated projections | #120, future #117 work |
| Runtime control plane | supervisor, workflow state, traces, envelopes, retries | #93–#104 |
| Deterministic dashboard | generated dependency graph and CI artifact | #117 |
| Proxmox local substrate | local LLM, local runner, model health, local reports | #56–#69 |
| Operations | backup, retention, drift, incidents, hardening | #70–#80 |

## Artifact classes

| Class | Meaning | Examples |
|---|---|---|
| Source | Human or system authority for a domain | `me.md`, GitHub issue bodies, PRs, CI results |
| Projection | Derived working view | HyperKanban cards, dashboard JSON, rendered dashboards |
| Report | Evidence or diagnostic output | cleanup reports, validation reports, model health reports |
| Example | Seed/demo artifact | `examples/self-model/repo_self_model_seed.json` |
| Generated | Produced by script/CI | future `reports/dashboard/latest.json` |
| Planned | Referenced by issues but not necessarily present | future schema/protocol paths |

## Current roadmap spine

```text
#119 standard execution contract
→ #122 schema registry
→ #123 validation gate
→ #114 documentation map
→ #116 hello workflow
→ #117 deterministic dashboard
→ #81–#91 agent arrival layer
→ #93–#104 runtime control plane
→ #56–#80 Proxmox and operations
```

## How agents should reason from this map

1. Find the instruction spine in `me.md`.
2. Find the specific issue or PR that defines the task.
3. Check whether required docs/files are implemented, active-stack, planned, generated, or examples.
4. Use HyperKanban and dashboards as projections only.
5. Use reports and CI as evidence only.
6. Stop if a planned path is required but missing.
7. Stop if source-of-truth layers disagree.
8. Stop before secrets, protected branches, public endpoints, Proxmox host mutation, or destructive action.

## Planned vs implemented rule

Agents must not infer that a file exists just because it appears in an issue, roadmap, dashboard, or schema registry.

If a file is marked planned, the agent may create it only when the active issue scope authorizes that path.

If a file is marked generated, the agent should prefer writing or updating the generator rather than manually editing the generated artifact unless the issue explicitly requests a static prototype.

If a file is marked example, agents must not treat it as runtime authority.

## Future Proxmox relationship

Proxmox should eventually become the local execution substrate for:

- local LLM endpoints,
- local runner workspaces,
- validation and dashboard generation,
- artifact/report storage,
- node health reports,
- local resource budgets.

The repository should remain usable without Proxmox for early validation and review. Proxmox should add local power, not become a required dependency for basic documentation, schema, or validation work.
