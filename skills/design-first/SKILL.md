# Skill: design-first

## Purpose

Use this skill before implementation begins to produce a structured, reviewable design decision artifact.

The skill should clarify:

- the problem being solved,
- constraints and invariants,
- architecture options,
- chosen design,
- risk boundaries,
- implementation slices,
- verification plan,
- approval gates,
- and next action.

## Required reads

Before producing a design-first report, read:

- `me.md`
- `docs/VISION.md`, if present
- `docs/ARCHITECTURE.md`, if present
- `docs/MVP_SPEC.md`
- `docs/ROADMAP.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/governance/RISK_POLICY.md`
- `docs/governance/HUMAN_APPROVAL_BOUNDARIES.md`
- `docs/governance/AUTONOMOUS_AGENT_POLICY.md`
- `docs/protocols/GRIND_PROTOCOL.md`
- `docs/protocols/REVIEW_WORKFLOW.md`
- `docs/protocols/CHECKPOINT_RESUME_PROTOCOL.md`
- `.branch-policy.yaml`

If an intended future document is missing, continue with available context and clearly mark the gap.

## Output

Primary output path:

```text
reports/design-first/<run-id>.html
```

Related artifacts:

```text
chronicle/events/<event-id>.json
reviews/pending/<review-id>.json
```

## Procedure

1. Load `me.md` and branch policy.
2. Frame the problem and user/operator need.
3. Identify constraints, assumptions, non-goals, and unknowns.
4. Compare at least two architecture options.
5. Select a recommended design and explain tradeoffs.
6. Classify risk as `low`, `medium`, `high`, or `critical`.
7. Define small reviewable implementation slices.
8. Define verification commands and acceptance criteria.
9. State approval gates and stop conditions.
10. Generate the HTML report and traceability artifacts.

## Stop rules

Pause for human input if the design requires:

- protected branch changes,
- live credentials,
- production side effects,
- payment/auth/secrets live effects,
- destructive actions,
- or a governance change.
