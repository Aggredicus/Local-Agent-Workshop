# Issue Taxonomy

This document defines the recommended issue classification system for Local Agent Workshop.

It exists so humans and agents can understand roadmap status, work type, risk level, readiness, and domain without reading every issue in full.

## Source-of-truth note

This document is a proposed classification guide. It does not mutate GitHub labels directly.

Actual label creation, deletion, renaming, or bulk relabeling requires explicit human approval unless a future governance policy grants a narrow autonomous lane for label maintenance.

## Label groups

Use labels in groups. Avoid using a single label to carry too much meaning.

```text
work type
+ readiness
+ risk
+ domain
+ lifecycle
```

## Work-type labels

| Label | Use when |
|---|---|
| `epic` | Issue groups multiple implementation issues or phases. |
| `docs` | Main output is documentation. |
| `schema` | Main output is a JSON schema or schema registry change. |
| `script` | Main output is executable automation or validation code. |
| `protocol` | Main output is a process, workflow, or operating contract. |
| `governance` | Main output changes authority, approval, safety, or policy boundaries. |
| `runtime` | Main output affects orchestration state, queues, leases, traces, events, or workers. |
| `evaluation` | Main output is a test, fixture, simulation, benchmark, or review gate. |
| `maintenance` | Main output is cleanup, refactor, status refresh, or dependency upkeep. |

## Domain labels

| Label | Use when |
|---|---|
| `agent-arrival` | Issue affects cold-start orientation, task intake, handoff, permissions, or agent readiness. |
| `hyperkanban` | Issue affects HyperKanban state, views, transition proposals, or dashboard projections. |
| `proxmox` | Issue affects Proxmox, local nodes, local LLMs, leases, or local infrastructure reports. |
| `security` | Issue affects secrets, prompt injection, untrusted content, permissions, public endpoints, or threat handling. |
| `ci` | Issue affects GitHub Actions, verification scripts, generated reports, or CI artifacts. |
| `dashboard` | Issue affects rendered dashboard, projection data, graph views, or visual diagnostics. |
| `schema-registry` | Issue affects schema registry, compatibility, versioning, migration notes, or validation contracts. |

## Readiness labels

| Label | Use when |
|---|---|
| `ready-for-agent` | Issue has clear inputs, outputs, evidence, stop conditions, and bounded paths. |
| `needs-spec` | Issue lacks enough detail for safe implementation. |
| `blocked` | Work cannot proceed because a dependency, decision, CI result, or required artifact is missing. |
| `human-review-required` | Explicit human approval is required before merge or before continuing. |
| `ready-for-human-review` | Work has evidence and can be reviewed by a human. |
| `ready-for-autonomous-merge` | PR fits the approved low-risk autonomous merge lane after `/merge-review`. |
| `stack-wait` | PR or issue depends on an earlier stacked change merging first. |

## Risk labels

| Label | Use when |
|---|---|
| `risk:low` | Docs/examples/reports only, small bounded diff, no authority/security/runtime impact. |
| `risk:medium` | Scripts, schemas, CI, generated projections, workflow behavior, or non-destructive automation. |
| `risk:high` | Governance boundaries, security-sensitive areas, Proxmox/local infrastructure, public endpoints, destructive behavior, migrations, or source-of-truth promotion. |

## Lifecycle labels

| Label | Use when |
|---|---|
| `planned` | Issue is accepted as future work but not started. |
| `in-progress` | A branch or PR is actively implementing the issue. |
| `implemented` | Work appears implemented but issue may still need closeout review. |
| `superseded` | Issue has been replaced by another issue or PR. |
| `duplicate` | Issue repeats another issue's purpose. |
| `needs-closeout` | Merged work exists but issue status, docs, or evidence still need cleanup. |

## Recommended label combinations

Use combinations such as:

```text
docs + risk:low + ready-for-agent
schema + schema-registry + risk:medium + human-review-required
script + ci + risk:medium + human-review-required
governance + risk:high + human-review-required
proxmox + runtime + risk:high + human-review-required
dashboard + hyperkanban + risk:medium + ready-for-agent
maintenance + docs + risk:low + ready-for-autonomous-merge
```

## Classification examples

| Issue type | Suggested labels |
|---|---|
| Documentation status refresh | `docs`, `maintenance`, `risk:low`, `ready-for-autonomous-merge` |
| New schema file | `schema`, `risk:medium`, `human-review-required` |
| CI dashboard generator | `script`, `dashboard`, `ci`, `risk:medium`, `human-review-required` |
| Proxmox node setup | `proxmox`, `runtime`, `risk:high`, `human-review-required` |
| Prompt-injection policy | `security`, `protocol`, `risk:high`, `human-review-required` |
| Duplicate issue cleanup | `maintenance`, `duplicate`, `risk:low` |

## Agent classification procedure

When an agent evaluates an issue:

1. Identify the primary output.
2. Identify changed paths.
3. Assign one work-type label.
4. Add one or more domain labels if relevant.
5. Assign one risk label.
6. Assign readiness labels based on the issue body.
7. Add lifecycle labels only when state evidence exists.
8. Stop if the labels would authorize work beyond the issue's scope.

## Readiness decision rules

An issue is `ready-for-agent` only if it includes:

- objective,
- required inputs,
- allowed output paths,
- acceptance criteria,
- evidence required,
- stop conditions,
- non-goals or out-of-scope boundaries.

A PR is `ready-for-autonomous-merge` only after `/merge-review` confirms it fits the approved low-risk lane.

## Relationship to HyperKanban

HyperKanban can use labels as hints, but labels are not the full state model.

The dashboard should derive readiness from:

- issue labels,
- issue body completeness,
- PR state,
- CI state,
- schema registry state,
- reports/evidence,
- HyperKanban state,
- governance boundaries.

Labels are useful signals, not the sole source of truth.
