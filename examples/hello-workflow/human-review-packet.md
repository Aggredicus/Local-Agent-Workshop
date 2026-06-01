# Hello Workflow Human Review Packet

Issue: #116

Workflow: `hello-workflow-001`

Status: complete, waiting for human review

## Summary

This example creates the smallest safe Local Agent Workshop workflow reference. It shows how a docs-only task can move from intake through supervisor decision, workflow state, evidence, handoff, HyperKanban proposal, Chronicle event, and human review.

## Changed files

```text
examples/hello-workflow/README.md
examples/hello-workflow/task-intake.json
examples/hello-workflow/supervisor-decision.json
examples/hello-workflow/workflow-state.json
examples/hello-workflow/evidence.json
examples/hello-workflow/handoff.json
examples/hello-workflow/hyperkanban-transition-proposal.json
examples/hello-workflow/chronicle-event.json
examples/hello-workflow/human-review-packet.md
```

## Evidence paths

```text
examples/hello-workflow/evidence.json
examples/hello-workflow/handoff.json
examples/hello-workflow/human-review-packet.md
```

## Checks run

- Manual artifact review.
- Confirmed no secrets, endpoints, protected branch changes, Proxmox runtime changes, or destructive commands are represented.

## Skipped checks

- Schema validation is skipped because the target schemas are planned but not implemented yet.
- Future #111/#112 work should promote this directory into a fixture set once schemas exist.

## Known risks

- These artifacts are schema-adjacent examples, not validated runtime state.
- Agents must not treat this example as a live workflow log.
- HyperKanban and Chronicle files here are examples only.

## Human decision needed

Choose one:

- Accept this as the minimal hello workflow reference.
- Request changes to the artifact shape or naming.
- Reject it as too early until more schemas exist.

## Recommended next action

After acceptance, use this example as the seed fixture for future golden-path simulation and deterministic dashboard validation work.
