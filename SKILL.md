# Skill: design-first

## Purpose

Use this skill when a user, agent, or workflow needs to clarify design before implementation.

The goal is to prevent premature coding by producing a structured, reviewable design decision artifact that explains:

- the problem being solved,
- constraints and invariants,
- architecture options,
- chosen design,
- risk boundaries,
- implementation slices,
- verification plan,
- approval gates,
- and next action.

The primary output is an interactive HTML report generated from:

```text
templates/reports/design-first-output.html.tmpl
```

Expected output path:

```text
reports/design-first/<run-id>.html
```

## Canonical instruction flow

Before using this skill, the agent must follow the repository instruction hierarchy:

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ↓
me.md
  ↓
docs/, schemas/, skills/, workflows/, plan/, scripts/
```

This skill assumes `me.md` is the canonical instruction spine.

## Required reads

Read these before producing a design-first report:

```text
me.md
docs/VISION.md
docs/ARCHITECTURE.md
docs/MVP_SPEC.md
docs/ROADMAP.md
docs/governance/BRANCH_POLICY.md
docs/governance/RISK_POLICY.md
docs/governance/HUMAN_APPROVAL_BOUNDARIES.md
docs/governance/AUTONOMOUS_AGENT_POLICY.md
docs/governance/ENVIRONMENTAL_BUDGET_POLICY.md
docs/protocols/GRIND_PROTOCOL.md
docs/protocols/REVIEW_WORKFLOW.md
docs/protocols/CHECKPOINT_RESUME_PROTOCOL.md
docs/protocols/ESCALATION_POLICY.md
schemas/event.schema.json
schemas/review-card.schema.json
schemas/run-state.schema.json
schemas/risk-assessment.schema.json
schemas/repo-graph.schema.json
```

If any of these documents do not exist yet, treat them as intended future documents and use the best available project context. Do not fail just because the fully released documentation set is incomplete.

## When to use

Use `/design-first` before:

- implementing a new feature,
- changing architecture,
- creating a new subsystem,
- introducing a dependency,
- changing branch or CI/CD behavior,
- touching auth, secrets, payments, deployment, or customer data,
- creating a new workflow or skill,
- changing schemas,
- building dashboard UX,
- or launching a long-running grind task.

## Inputs

A design-first run should accept:

```yaml
request: string
repo_path: string
branch: string
run_id: string
agent_name: string
target_files: string[]
risk_hint: low | medium | high | critical | unknown
desired_output_path: reports/design-first/<run-id>.html
```

## Procedure

### 1. Load canonical context

- Read `me.md`.
- Read the required governance, protocol, schema, UX, and architecture docs.
- Read current `plan/NEXT.md`, `plan/STATUS.md`, `plan/BLOCKERS.md`, and `plan/DECISIONS.md` if present.
- Check `.branch-policy.yaml`.

### 2. Frame the problem

Identify:

- operator/user,
- job to be done,
- success outcome,
- non-goals,
- assumptions,
- unknowns,
- and constraints.

### 3. Compare design options

Produce at least two viable architecture options. Prefer three when the design space is meaningfully uncertain.

For each option, document:

- summary,
- benefits,
- tradeoffs,
- failure modes,
- verification difficulty,
- and fit with Local Agent Workshop governance.

### 4. Select a design

Choose the most appropriate option and explain why.

The chosen design must preserve:

- local-first operation,
- branch-aware automation,
- reviewable patches,
- resumable long-running work,
- human approval at risk boundaries,
- Chronicle event traceability,
- and low-waste compute behavior.

### 5. Identify risk boundaries

Classify the work as:

```text
low
medium
high
critical
```

Then state:

- what can continue autonomously,
- what requires review,
- what requires explicit human approval,
- and what must stop the run.

### 6. Slice implementation

Break the work into small, reviewable, testable implementation slices.

Each slice should be small enough to produce a review card.

### 7. Define verification

List:

- commands to run,
- expected outputs,
- schema validations,
- tests to add,
- security checks,
- and dashboard/report artifacts to inspect.

Use existing scripts when possible:

```text
scripts/verify.sh
scripts/test-fast.sh
scripts/test-full.sh
scripts/security-scan.sh
scripts/ci-local.sh
```

### 8. Prepare traceability

The design-first output should identify future traceability artifacts:

```text
chronicle/events/<event-id>.json
reviews/pending/<review-id>.json
reports/design-first/<run-id>.html
repo_graph/manifest.json
```

### 9. Generate HTML report

Fill the HTML template:

```text
templates/reports/design-first-output.html.tmpl
```

Write it to:

```text
reports/design-first/<run-id>.html
```

### 10. Recommend next action

The report must end with one of these statuses:

```text
ready_for_implementation
needs_human_decision
needs_more_context
blocked_by_risk
blocked_by_missing_docs
```

## Output quality bar

A good design-first report is:

- specific enough that an implementation agent can act,
- conservative about risk,
- clear about what is unknown,
- explicit about verification,
- linked to relevant project docs,
- and small enough to support the next reviewable patch.

## Stop rules

Stop and request human input if:

- the design would cross a protected branch boundary,
- the design would require live credentials,
- the design would create production side effects,
- the design would touch payment/auth/secret behavior without a safe mock path,
- the design conflicts with `me.md`,
- or there is no safe reversible implementation slice.

## Chronicle event recommendation

A design-first run should emit an event similar to:

```json
{
  "event_type": "design_first.completed",
  "run_id": "<run-id>",
  "branch": "<branch>",
  "summary": "Generated design-first report for <request>.",
  "details": {
    "report_path": "reports/design-first/<run-id>.html",
    "risk_level": "<risk-level>",
    "readiness_status": "<status>"
  }
}
```
