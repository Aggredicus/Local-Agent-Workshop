# Skills Protocol

This directory contains reusable agent skills for Local Agent Workshop.

## Mandatory skill-use improvement issue rule

Every time an agent uses a skill, the run must create a follow-up improvement issue for that skill.

This is mandatory even when the skill worked well.

The issue may be tiny. It may record that no change is recommended. It may later be closed as `not_planned`. The point is to create a durable audit hook so every skill invocation can produce learning at repository scale.

## Mandatory skill artifact update rule

Every time an agent uses a skill, the run must also update that skill's durable artifact trail.

This applies to every skill, including:

- `/merge-review`,
- `/close-issue`,
- `/quality-analysis`,
- `/repo-cleanup`,
- `/publish`,
- `/grind`,
- and any future skill under `skills/*/SKILL.md`.

A skill artifact update must be one of these two forms:

1. **Behavior update** — if the run reveals a reusable lesson that changes how the skill should operate, patch `skills/<skill>/SKILL.md`.
2. **No-change audit update** — if the skill worked correctly and no behavior change is needed, append a compact entry to `skills/<skill>/IMPROVEMENT_LOG.md`.

A follow-up improvement issue is still required. The issue is the planning/audit record. The skill artifact update is the durable repository update proving the skill learned from or recorded the use.

## Required post-skill action

After every skill run:

1. Identify the skill that was used.
2. Create one improvement issue for that skill.
3. Update that skill's artifact trail:
   - patch `skills/<skill>/SKILL.md` when behavior should change, or
   - append to `skills/<skill>/IMPROVEMENT_LOG.md` when no behavior change is recommended.
4. Link the improvement issue, PR, task, or report that triggered the skill use when practical.
5. Record one of these outcomes:
   - behavior updated,
   - log-only update,
   - improve later,
   - blocked by missing context,
   - superseded by another improvement issue.
6. If no behavior improvement is needed, close the issue as `not_planned` only after leaving a brief reason and ensuring the no-change log update exists.

## No-change improvement log format

Use this compact format for `skills/<skill>/IMPROVEMENT_LOG.md` entries:

```text
## YYYY-MM-DD — <context>

Skill used: /<skill-name>
Used for: <issue, PR, or task>
Outcome: behavior updated | log-only update | improve later | blocked | superseded
Observation: <what happened>
Decision: <why SKILL.md changed or why no behavior change is recommended>
Links: <issue/PR/report>
```

Prefer short entries. The log is an audit trail, not a narrative report.

## Recursion breaker

The mandatory issue rule and mandatory artifact update rule must not create an infinite closeout loop.

When `/close-issue` is used only to close a no-change improvement issue that already exists solely because of this protocol, that same issue may serve as the terminal audit record for the `/close-issue` run.

In that narrow case:

- do not create another improvement issue,
- do not require another `SKILL.md` behavior patch,
- append one terminal no-change entry to `skills/close-issue/IMPROVEMENT_LOG.md` when practical,
- leave a public comment saying the issue is the terminal no-change audit record,
- close it as `not_planned`,
- stop.

This exception applies only to no-change improvement issues created by this skill-use protocol. It does not apply to normal feature, bug, governance, schema, script, CI, release, or skill-behavior-change issues.

## Improvement issue template

```text
Title: Improve /<skill-name> after use in <context>

Body:
Skill used: /<skill-name>
Used for: <issue, PR, or task>
Observed friction: <what happened>
Reusable lesson: <what should be learned>
Recommended action: behavior updated | log-only update | improve later | blocked | superseded
Artifact update: SKILL.md patch | IMPROVEMENT_LOG.md entry | blocked
Scope: docs-only | script | schema | governance | unknown
Risk: low | medium | high
Links: <issue/PR/report>
```

## Scale rule

Prefer small, cheap improvement issues and compact improvement-log entries over large bundled retrospectives. Many tiny skill-improvement records are acceptable because they preserve a searchable trail of actual skill use.

Do not make meaningless rewrites to `SKILL.md` just to satisfy the update rule. Use `IMPROVEMENT_LOG.md` for no-change runs.

## Non-goals

This rule does not require every improvement issue to produce a behavior PR. It requires every skill use to create both:

- an improvement issue, and
- a durable skill artifact update.

Do not use this rule to bypass human-review boundaries, merge policy, branch policy, or evidence requirements.
