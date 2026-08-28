---
name: skill-discovery
description: Use when skill selection, available skills, which skill should I use, before starting development, before creating a new skill, before PR review, before merge, merge-review, skills registry, skills/*/SKILL.md, missed skill, duplicate skill, or local skill discovery is involved.
---

# /skill-discovery

Use this skill when skill selection, available skills, "which skill should I use?", before starting development, before creating a new skill, before PR review, before merge, merge-review, skills registry, `skills/*/SKILL.md`, missed skill, duplicate skill, or local skill discovery is involved.

## Purpose

`/skill-discovery` prevents agents from missing existing Local Agent Workshop skills. It forces deterministic local skill discovery before an agent chooses a workflow, creates a new skill, recommends a review path, or proceeds toward merge.

## When to use

Use this skill when:

- the user asks which skill should be used,
- the task involves PR review or merge,
- a new skill is being proposed,
- the agent is about to claim no skill exists,
- a workflow choice depends on available local skills,
- there is a risk of duplicate or overlapping skills.

Do not use this skill as a substitute for the selected skill. It selects and composes skills; it does not replace `/merge-review`, `/skill-security-auditor`, or other workflow-specific skills.

## Required inputs

- Repository root or repository full name.
- Branch/ref to inspect.
- Optional task summary.
- Optional named skill to check directly.
- Optional PR number or head branch.

## Outputs

A good run produces:

- local skill inventory,
- selected primary skill,
- secondary/composed skills,
- alternatives considered,
- evidence paths from `SKILL.md`,
- registry/tree drift notes,
- whether a new skill is needed,
- approval boundary and next action.

## Workflow

1. Read repository instructions.
2. Determine branch/ref to inspect.
3. If the user named a skill, check `skills/<skill>/SKILL.md` directly before search.
4. Scan `skills/*/SKILL.md`.
5. Read `skills/registry.json`, `skills/INDEX.md`, or `docs/skills/SKILL_INDEX.md` if present.
6. Compare registry/index entries against the skill tree.
7. Rank candidate skills against the task summary.
8. Apply mandatory gate rules:
   - merge/review task => consider `/merge-review`;
   - external skill import/activation => consider `/skill-security-auditor`;
   - dependency review => consider `/dependency-auditor`;
   - env/config review => consider `/env-secrets-manager`.
9. Select the narrowest primary skill and list secondary skills.
10. Produce a handoff with evidence.

## Gotchas

- GitHub code search can miss existing skills.
- Registry files can be stale.
- Branch choice matters; `main` may differ from the active PR branch.
- Governance skills are not ordinary helper docs.
- Do not create a new skill until overlapping existing skills have been checked.
- Multiple skills may apply; choose one primary skill and list secondary/composed skills.

## Verification

Run:

```sh
python -m pytest -q tests/skills/test_skill_discovery.py
```

Required test scenarios:

- direct path lookup finds `skills/merge-review/SKILL.md`,
- broad search failure is not treated as absence,
- registry drift is detected,
- merge task ranks `/merge-review`,
- external skill import task ranks `/skill-security-auditor`,
- duplicate-skill prevention works.

## Stop conditions

Stop or ask for human review if:

- the skill tree cannot be inspected,
- branch/ref is ambiguous and the difference matters,
- governance/merge policy would change,
- a new skill is proposed but overlap has not been checked,
- the result would bypass `/merge-review` or another governance gate.

## Handoff format

```text
Skill used: /skill-discovery
Task summary:
Branch/ref checked:
Skill sources checked:
Selected primary skill:
Secondary/composed skills:
Alternatives considered:
Evidence paths:
Registry/tree drift:
New skill needed: yes | no
Approval boundary:
Recommended next action:
```

## Improvement-log requirement

After every use, follow `skills/README.md`: create a follow-up improvement issue and update either `SKILL.md` or `IMPROVEMENT_LOG.md`, unless the repository recursion-breaker rule applies.
