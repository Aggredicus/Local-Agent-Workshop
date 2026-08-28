# /skill-discovery

`/skill-discovery` is a Local Agent Workshop meta-skill for deterministic local skill selection.

It exists because an agent missed the existing `/merge-review` skill even though it was present at `skills/merge-review/SKILL.md`. The fix is to inspect local skill sources directly instead of relying on broad GitHub code search or memory.

## Current status

- Status: implemented v1.0 local wrapper
- Tracking issue: #181
- Category: code quality and review / governance support

## What it does

- Scans `skills/*/SKILL.md`.
- Emits a JSON inventory of local skills.
- Checks a directly named skill path before broad matching.
- Compares registry/index data against actual skill folders when available.
- Selects and ranks candidate skills for a task summary.
- Applies mandatory governance-gate rules for merge, external skill import, dependency, and env/config tasks.

## What it does not do yet

- It does not mutate skills.
- It does not mutate registry/index files.
- It does not replace `/merge-review` or `/skill-security-auditor`.
- It does not claim semantic certainty from keyword matching alone.

## Usage

List local skills:

```sh
python scripts/skills/list_available_skills.py . --json
```

Check a named skill directly and validate registry drift:

```sh
python scripts/skills/list_available_skills.py . --skill merge-review --validate-registry --json
```

Select a skill for a task:

```sh
python scripts/skills/select_skill.py . --task "Review and merge PR #179" --json
```

## Tests

```sh
python -m pytest -q tests/skills/test_skill_discovery.py
```
