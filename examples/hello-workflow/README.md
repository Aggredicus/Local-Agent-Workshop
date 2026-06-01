# Hello Workflow Reference Implementation

This is the smallest safe end-to-end Local Agent Workshop workflow example.

It demonstrates how a docs-only task should move through the intended architecture without touching Proxmox, secrets, protected branches, public endpoints, or destructive side effects.

## Artifact status

These files are **examples**, not canonical runtime state.

They are intentionally schema-adjacent while the full schemas are still planned. Once the task intake, supervisor decision, workflow state, evidence, handoff, HyperKanban transition, and Chronicle event schemas exist, this directory should become a validation fixture.

## Workflow path

```text
task intake
→ supervisor decision
→ workflow state
→ evidence record
→ handoff packet
→ HyperKanban transition proposal
→ Chronicle event
→ human review packet
```

## Files

| File | Purpose |
|---|---|
| `task-intake.json` | Defines the bounded docs-only task. |
| `supervisor-decision.json` | Shows a supervisor routing the task to a documenter role. |
| `workflow-state.json` | Shows the workflow lifecycle ending in `completed`. |
| `evidence.json` | Captures reviewable evidence for the docs-only example. |
| `handoff.json` | Provides a complete agent handoff packet. |
| `hyperkanban-transition-proposal.json` | Proposes an `add_evidence` transition without mutating HyperKanban directly. |
| `chronicle-event.json` | Shows the append-only historical event that would be emitted. |
| `human-review-packet.md` | Human-readable review summary and decision request. |

## Safety properties

- No secrets.
- No live endpoints.
- No Proxmox mutation.
- No protected branch mutation.
- No destructive commands.
- No generated dashboard authority claims.

## Expected use

A fresh agent should be able to read this directory and understand how the core contracts fit together before implementing larger workflows.

Later validation should check that these examples conform to their schemas once those schemas exist.
