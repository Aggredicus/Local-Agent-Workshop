# Navigation Index

This index helps humans and agents find the right documentation without relying on prior chat history.

## First-contact path

```text
README.md
→ me.md
→ docs/README.md
→ docs/NAVIGATION_INDEX.md
→ docs/architecture/REPOSITORY_KNOWLEDGE_MAP.md
```

## Implemented or active-stack documentation

| Area | Path | Status | Notes |
|---|---|---|---|
| Instruction spine | `../me.md` | implemented | Canonical route for agents. |
| Branch policy | `governance/BRANCH_POLICY.md` | implemented | Branch meaning and protected-branch rules. |
| Risk policy | `governance/RISK_POLICY.md` | implemented | Risk classes and pause boundaries. |
| Human approval | `governance/HUMAN_APPROVAL_BOUNDARIES.md` | implemented | Actions requiring explicit human approval. |
| Autonomous agents | `governance/AUTONOMOUS_AGENT_POLICY.md` | implemented | Agent operating boundaries. |
| Cleanup | `protocols/REPOSITORY_CLEANUP_PROTOCOL.md` | implemented | Preflight and closeout cleanup gates. |
| Quality analysis | `protocols/QUALITY_ANALYSIS_PROTOCOL.md` | implemented | Baseline and final quality gates. |
| Publish | `protocols/PUBLISH_PROTOCOL.md` | implemented | Human-approved publish flow. |
| Review workflow | `protocols/REVIEW_WORKFLOW.md` | implemented | Review packet expectations. |
| Grind | `protocols/GRIND_PROTOCOL.md` | implemented | Long-running work protocol. |
| Checkpoint/resume | `protocols/CHECKPOINT_RESUME_PROTOCOL.md` | implemented | Resumable agent work. |
| Empty inbox | `protocols/EMPTY_INBOX_PROTOCOL.md` | implemented | Inbox routing protocol. |
| Self improvement | `protocols/SELF_IMPROVEMENT_PROTOCOL.md` | implemented | Reviewable improvement loop. |
| Standard execution contract | `protocols/STANDARD_EXECUTION_CONTRACT.md` | active PR #119 | Agent-executable issue grammar. |
| Schema registry | `protocols/SCHEMA_REGISTRY_AND_COMPATIBILITY.md` | active PR #122 | Schema status and compatibility policy. |
| Validation gate | `protocols/REPO_VALIDATION_GATE.md` | active PR #123 | Read-only registry validation gate. |
| Self-model roadmap | `architecture/REPOSITORY_SELF_MODEL_ROADMAP.md` | active PR #121 | Roadmap seed, not runtime authority. |

## Implemented runtime and script areas

| Area | Path | Status | Notes |
|---|---|---|---|
| HyperKanban state | `../orchestration/hyperkanban/state.json` | implemented | Compact operational projection seed. |
| HyperKanban packet | `../orchestration/hyperkanban/packet.txt` | implemented | Compact agent-readable packet. |
| HyperKanban validator | `../scripts/validate_hyperkanban.py` | implemented | Deterministic state validation. |
| Repository cleanup | `../scripts/repo_cleanup.py` | implemented | Non-destructive cleanup checks. |
| Repo contract validator | `../scripts/validate_repo_contracts.py` | active PR #123 | Validates schema registry. |
| CLI | `../src/workshop/cli.py` | implemented | Current CLI mainly covers HyperKanban. |
| Verification script | `../scripts/verify.sh` | implemented / active PR #123 extends | Runs HyperKanban validation, repo contracts, and pytest. |

## Planned documentation and runtime areas

| Area | Planned paths | Driving issues | Status |
|---|---|---|---|
| Agent arrival | `protocols/AGENT_ARRIVAL_PROTOCOL.md` | #81, #82 | planned |
| Agent permission tiers | `governance/AGENT_PERMISSION_TIERS.md` | #83 | planned |
| Task intake | `schemas/agent_task_intake.schema.json` | #84 | planned |
| Runtime budgets | `schemas/agent_runtime_budget.schema.json` | #85 | planned |
| Evidence contract | `schemas/agent_work_evidence.schema.json` | #86 | planned |
| Handoff packets | `schemas/agent_handoff_packet.schema.json` | #87 | planned |
| Supervisor control plane | `protocols/SUPERVISOR_CONTROL_PLANE.md` | #93, #94 | planned |
| Workflow state | `schemas/workflow_state.schema.json` | #95 | planned |
| Trace context | `schemas/trace_context.schema.json` | #96 | planned |
| Runtime event envelope | `schemas/workshop_event_envelope.schema.json` | #97 | planned |
| Side-effect wrappers | `governance/SIDE_EFFECT_WRAPPER_POLICY.md` | #103 | planned |
| Untrusted content policy | `security/UNTRUSTED_CONTENT_POLICY.md` | #104 | planned |
| Deterministic dashboard | `reports/dashboard/`, `docs/dashboard/` | #117 | planned/generated |
| Proxmox Workshop Node | `infrastructure/PROXMOX_WORKSHOP_NODE.md` | #56–#69 | planned |
| Operations and maintenance | `operations/` | #70–#80 | planned |

## Agent rules for navigation

- Treat `me.md` as the instruction spine.
- Treat this index as a map, not as authority over issue acceptance criteria.
- Check issue bodies and PR branches for active-stack files.
- Do not assume planned paths exist.
- Do not treat dashboards or example seeds as source of truth.
- Stop and create a handoff if docs disagree about authority or current status.
