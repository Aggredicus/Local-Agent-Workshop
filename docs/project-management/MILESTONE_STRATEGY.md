# Milestone Strategy

This document defines a lightweight milestone strategy for Local Agent Workshop.

It exists so humans and agents can understand the project roadmap at a glance without treating a generated dashboard as the source of truth.

## Source-of-truth note

This document is a proposed milestone map. It does not create, rename, close, or assign GitHub milestones directly.

Actual milestone mutation requires explicit human approval unless a future policy grants a narrow autonomous lane for milestone maintenance.

## Milestone principles

Milestones should be:

- small enough to guide work,
- large enough to represent a coherent release step,
- tied to issue groups and evidence,
- compatible with HyperKanban projections,
- clear about human approval boundaries,
- independent of prior chat history.

## Recommended milestone map

| Milestone | Goal | Representative issues | Completion signal |
|---|---|---|---|
| M1: Repo self-explaining | Fresh agents can orient, find instructions, understand docs, and classify work. | #48, #92, #113, #114, #116, #118, #120, #126, #128, #130 | Navigation, execution contract, hello workflow, taxonomy, and merge-review policy are present. |
| M2: Schema and validation metabolism | JSON contracts are discoverable, versioned, validated, and supported by fixtures. | #109, #111, #112 | Registry validates; examples and fixtures cover common outcomes. |
| M3: Deterministic dashboard | HyperKanban/dashboard projections are generated from explicit repository artifacts. | #117 | Dashboard projection and CI artifact are deterministic and explain recommendation chains. |
| M4: Agent arrival and evidence | Agents can safely accept tasks, respect budgets, produce evidence, and hand off. | #81–#91 | Arrival protocol, permission tiers, task intake, budgets, evidence, handoff, dry-run, and project-state reports exist. |
| M5: Runtime control plane | Supervisor, workflow state, trace context, event envelopes, retries, and side-effect wrappers exist. | #93–#104 | Runtime orchestration semantics are documented and schema-governed. |
| M6: Proxmox local runtime | Local workshop node supports model health, local reports, leases, and local agent execution boundaries. | #56–#69 | Proxmox node checks and local model provider reports are non-destructive and evidence-producing. |
| M7: Operations and maintenance | Local/runtime system is observable, recoverable, secure, and maintainable. | #70–#80 | Backup, retention, drift, incident response, hardening, and artifact integrity plans exist. |
| M8: Release readiness | System can prove a golden path and release with ongoing quality controls. | #105–#108 | Golden-path simulation, fan-out policy, critic review, taxonomy, and release readiness gates pass. |

## Milestone readiness states

Use these states in dashboard/report prose rather than as mandatory GitHub milestone statuses:

| State | Meaning |
|---|---|
| `planned` | Milestone is accepted as a roadmap group. |
| `active` | Current sprint work primarily targets this milestone. |
| `blocked` | Dependencies or approval boundaries prevent progress. |
| `reviewing` | Implementation exists and is being reviewed. |
| `complete` | Acceptance evidence exists and merged artifacts satisfy the milestone goal. |
| `maintenance` | Milestone remains in use but is no longer primary development focus. |

## Suggested current milestone posture

| Milestone | Suggested state | Notes |
|---|---|---|
| M1: Repo self-explaining | active/reviewing | Major pieces are merged; taxonomy and issue closeout remain. |
| M2: Schema and validation metabolism | active | Registry and validation gate are merged; fixture set remains. |
| M3: Deterministic dashboard | planned/next | Best next major implementation target after cleanup. |
| M4: Agent arrival and evidence | planned | Should build on taxonomy, dashboard, schema registry, and hello workflow. |
| M5: Runtime control plane | planned | Should wait until agent-arrival contracts are clearer. |
| M6: Proxmox local runtime | planned | Should remain optional and non-destructive at first. |
| M7: Operations and maintenance | planned | Should follow or accompany local runtime setup. |
| M8: Release readiness | planned | Should validate the system after major contracts exist. |

## Mapping milestones to issue selection

When choosing the next issue:

1. Prefer completing active milestone gaps before starting distant milestones.
2. Prefer low-risk documentation cleanup when the repo map is stale.
3. Prefer schema/validation work before runtime automation.
4. Prefer deterministic analysis before dashboard rendering.
5. Prefer non-destructive Proxmox checks before any local host mutation.
6. Prefer evidence-producing tasks over speculative implementation.

## Risk by milestone

| Milestone | Typical risk |
|---|---|
| M1: Repo self-explaining | low to medium |
| M2: Schema and validation metabolism | medium |
| M3: Deterministic dashboard | medium |
| M4: Agent arrival and evidence | medium |
| M5: Runtime control plane | medium to high |
| M6: Proxmox local runtime | high |
| M7: Operations and maintenance | medium to high |
| M8: Release readiness | medium |

## Autonomous merge implications

Milestone documentation updates may qualify for autonomous merge if they are:

- docs-only,
- low-risk,
- small and bounded,
- limited to approved low-risk paths,
- supported by `/merge-review`,
- not changing governance, security, source-of-truth, Proxmox, CI, scripts, schemas, or runtime behavior.

Milestone mutations in GitHub itself do not qualify for autonomous merge unless a future policy explicitly allows them.

## Relationship to HyperKanban

HyperKanban should be able to use this milestone map to organize work, but this document is not the operational state source.

The deterministic dashboard should eventually compute milestone posture from:

- open issues,
- closed issues,
- merged PRs,
- labels,
- HyperKanban cards,
- validation reports,
- evidence artifacts,
- roadmap docs.

## Release train suggestion

A practical release train could be:

```text
v0.1 — Repo self-explaining
v0.2 — Schema and validation metabolism
v0.3 — Deterministic dashboard
v0.4 — Agent arrival and evidence
v0.5 — Runtime control plane
v0.6 — Proxmox local runtime
v0.7 — Operations and maintenance
v1.0 — Release-ready local agent workshop
```

These versions are planning anchors, not required semantic versions.
