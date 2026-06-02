# Skills Protocol

This directory contains reusable agent skills for Local Agent Workshop.

## Mandatory skill-use improvement issue rule

Every time an agent uses a skill, the run must create a follow-up improvement issue for that skill.

This is mandatory even when the skill worked well.

The issue may be tiny. It may record that no change is recommended. It may later be closed as `not_planned`. The point is to create a durable audit hook so every skill invocation can produce learning at repository scale.

## Required post-skill action

After every skill run:

1. Identify the skill that was used.
2. Create one improvement issue for that skill.
3. Link the issue to the work that used the skill when practical.
4. Record one of these outcomes:
   - improve now,
   - improve later,
   - no change recommended,
   - blocked by missing context,
   - superseded by another improvement issue.
5. If no improvement is needed, close the issue as `not_planned` only after leaving a brief reason.

## Recursion breaker

The mandatory issue rule must not create an infinite closeout loop.

When `/close-issue` is used only to close a no-change improvement issue that already exists solely because of this protocol, that same issue may serve as the terminal audit record for the `/close-issue` run.

In that narrow case:

- do not create another improvement issue,
- leave a public comment saying the issue is the terminal no-change audit record,
- close it as `not_planned`,
- stop.

This exception applies only to no-change improvement issues created by this skill-use protocol. It does not apply to normal feature, bug, governance, schema, script, CI, or release issues.

## Improvement issue template

```text
Title: Improve /<skill-name> after use in <context>

Body:
Skill used: /<skill-name>
Used for: <issue, PR, or task>
Observed friction: <what happened>
Reusable lesson: <what should be learned>
Recommended action: improve now | improve later | no change recommended | blocked | superseded
Scope: docs-only | script | schema | governance | unknown
Risk: low | medium | high
Links: <issue/PR/report>
```

## Scale rule

Prefer small, cheap improvement issues over large bundled retrospectives. Many tiny skill-improvement issues are acceptable because they preserve a searchable trail of actual skill use.

## Non-goals

This rule does not require every improvement issue to produce a PR. It requires every skill use to produce an improvement issue so the repo can decide whether the lesson is actionable.

Do not use this rule to bypass human-review boundaries, merge policy, branch policy, or evidence requirements.
