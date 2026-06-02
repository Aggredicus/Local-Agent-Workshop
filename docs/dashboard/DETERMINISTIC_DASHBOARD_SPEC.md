# Deterministic Dashboard Specification

This document defines the first implementation contract for the deterministic HyperKanban CI dashboard.

It is a specification only. It does not add schemas, scripts, workflows, generated artifacts, Proxmox behavior, or runtime mutation.

## Purpose

The dashboard should give humans and agents first-glance guidance about the repository's current work state.

It should answer:

```text
What can I safely do next?
Why is it next?
What is blocked?
What evidence is missing?
What needs human approval?
Which files and issues are involved?
```

## Non-authority rule

The dashboard is a generated projection. It is not the source of truth.

Source-of-truth layers remain:

| Layer | Role |
|---|---|
| `me.md` | Canonical instruction spine. |
| GitHub Issues | Planned work and coordination. |
| Pull Requests | Review and merge boundary. |
| CI | Validation proof. |
| Schema registry | Discoverability and compatibility for JSON contracts. |
| HyperKanban | Compact operational projection. |
| Chronicle/reports | Historical evidence and diagnostics. |

The dashboard may summarize these layers, but it must not override them.

## Determinism requirement

The dashboard must be produced from explicit repository artifacts and deterministic rules.

It must not depend on model intuition, hidden conversation context, or unstated assumptions.

A future script should be able to run repeatedly on the same inputs and produce the same projection output, except for timestamps or explicitly declared volatile metadata.

## Input sources

Initial dashboard generation may read:

| Source | Expected role |
|---|---|
| `docs/NAVIGATION_INDEX.md` | Implemented/planned path map. |
| `docs/architecture/REPOSITORY_KNOWLEDGE_MAP.md` | Source-of-truth and projection model. |
| `docs/project-management/ISSUE_TAXONOMY.md` | Label/risk/readiness rules. |
| `docs/project-management/MILESTONE_STRATEGY.md` | Milestone grouping. |
| `schemas/schema-registry.json` | Registered schema status. |
| `orchestration/hyperkanban/state.json` | Current compact operational projection. |
| `orchestration/hyperkanban/packet.txt` | Agent-readable operational packet. |
| `reports/review/` | Review and closeout evidence. |
| `reports/validation/` | Validation evidence. |
| GitHub issue metadata | Issue state, labels, relationships, body completeness. |
| GitHub PR metadata | PR state, mergeability, changed files, CI, review status. |

Future Proxmox/local reports may become optional sensor inputs, but the first dashboard must run without Proxmox.

## Output artifacts

Future implementation should produce outputs such as:

```text
reports/dashboard/latest.json
reports/dashboard/latest.md
reports/dashboard/latest.html
orchestration/hyperkanban/views/dashboard-projection.json
```

The exact names may change when schemas are implemented, but the dashboard should always produce:

- machine-readable projection,
- human-readable summary,
- optional interactive HTML view,
- evidence/reason chains for every recommendation.

## Required object classes

The dashboard projection should eventually model these object classes:

| Class | Meaning |
|---|---|
| `issue` | GitHub issue and its readiness/risk/dependency state. |
| `pull_request` | PR state, checks, changed paths, review status, and merge lane. |
| `file` | Repository file or planned path. |
| `schema` | Registered schema and validation status. |
| `report` | Evidence or diagnostic artifact. |
| `hyperkanban_card` | Operational card or projected work item. |
| `milestone` | Roadmap grouping or phase. |
| `dependency` | Relationship between issues, PRs, files, schemas, and reports. |

## Verdicts

The dashboard should compute deterministic verdicts.

| Verdict | Meaning |
|---|---|
| `ready` | Work has clear inputs, allowed paths, acceptance criteria, and no blocking dependencies. |
| `ready_for_autonomous_merge` | PR fits the approved low-risk merge lane after `/merge-review`. |
| `human_gated` | Explicit human approval is required. |
| `blocked` | Dependency, failed check, missing artifact, conflict, or risk boundary blocks progress. |
| `missing_evidence` | Work claims completion or readiness but lacks required reports/checks/evidence. |
| `needs_spec` | Issue or task lacks required execution details. |
| `stack_wait` | PR or task must wait for an earlier stacked item. |
| `stale` | Documentation/projection/status is outdated relative to merged PRs or current issue state. |
| `superseded` | Work has been replaced by a newer issue, PR, or artifact. |
| `unknown` | Dashboard lacks enough evidence to classify safely. |

## Reason chains

Every recommendation must include a reason chain.

A reason chain should answer:

```text
Why did the dashboard assign this verdict?
Which artifacts were checked?
Which rules fired?
Which evidence supports the recommendation?
What would change the verdict?
```

Example:

```json
{
  "target": "PR #134",
  "verdict": "ready_for_autonomous_merge",
  "reasons": [
    "PR is open and non-draft",
    "PR is mergeable",
    "CI conclusion is success",
    "Changed file is docs/NAVIGATION_INDEX.md",
    "Diff is docs-only and low-risk",
    "No disallowed paths touched",
    "No governance/security/runtime/Proxmox behavior changed"
  ],
  "next_action": "merge with minimal payload"
}
```

## First-glance agent guidance

The dashboard should prioritize action clarity.

A fresh agent should see:

1. current safe next action,
2. why it is safe,
3. what issue/PR it belongs to,
4. allowed paths,
5. required evidence,
6. stop conditions,
7. merge lane or human gate,
8. dependency blockers.

## Dependency rules

At minimum, the dashboard should infer dependencies from:

- explicit issue references such as `Depends on`, `Related`, `Parent epic`, and issue number mentions,
- PR bodies referencing issues,
- files changed by PRs,
- schema registry entries,
- navigation/planned path maps,
- HyperKanban card dependencies,
- milestone strategy grouping,
- reports that cite issue/PR IDs.

The dashboard should never invent dependencies that are not supported by source artifacts. It may flag likely missing dependencies as `needs_spec` or `unknown`.

## Readiness rules

An issue can be `ready` only when it includes:

- objective,
- scope or allowed paths,
- outputs,
- acceptance criteria,
- evidence requirements,
- stop conditions or risk boundaries,
- no unresolved blocker.

A PR can be `ready_for_autonomous_merge` only when `/merge-review` policy conditions are satisfied.

A PR can be `ready_for_human_approval` when evidence is sufficient but the change is medium-risk, high-risk, or outside the autonomous lane.

## Human-gated categories

The dashboard must mark these as `human_gated` unless a later policy explicitly changes the boundary:

- governance policy changes,
- security-sensitive changes,
- schemas,
- scripts,
- source code,
- CI/workflows,
- Proxmox/local infrastructure,
- public endpoints,
- destructive actions,
- migrations or persistent state changes,
- source-of-truth promotions,
- changes to merge/approval policy.

## Staleness rules

The dashboard should mark projections as stale when:

- docs refer to merged PRs as active,
- issue body status conflicts with merged PRs,
- HyperKanban cards refer to nonexistent files,
- registered schema paths are missing unexpectedly,
- reports are older than the source artifacts they summarize,
- generated dashboard outputs are older than source inputs.

## Future schema/script/CI plan

A future implementation should add, in order:

1. `schemas/repository_dependency_graph.schema.json`
2. `schemas/dashboard_projection.schema.json`
3. `scripts/analyze_repository_graph.py`
4. `scripts/build_dashboard_projection.py`
5. `scripts/validate_dashboard_projection.py`
6. `scripts/render_ci_dashboard.py`
7. `reports/dashboard/.gitkeep`
8. `.github/workflows/hyperkanban-dashboard.yml`

Those changes are outside this specification slice and should be treated as medium-risk or human-gated because they touch schemas, scripts, and CI.

## Non-goals for first implementation

The first implementation should not:

- call local LLMs,
- require Proxmox,
- mutate issues or PRs,
- mutate HyperKanban state directly,
- write to protected branches,
- deploy public endpoints,
- treat generated HTML as source of truth,
- silently close issues,
- bypass `/merge-review`.

## Review checklist

Before implementing scripts, confirm:

- source artifacts are listed,
- output artifacts are defined,
- verdicts are deterministic,
- reason chains are required,
- human-gated categories are explicit,
- autonomous merge boundaries are preserved,
- Proxmox remains optional for the first dashboard.
