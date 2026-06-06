# Skill Porting Standard

This standard defines how external skill material is adapted into Local Agent Workshop.

## Goal

A ported skill is not a raw copy. A ported skill is a Local Agent Workshop-native capability with:

- a clear `SKILL.md`,
- human-readable usage notes,
- durable improvement history,
- source attribution,
- stable evidence artifacts,
- fixture-backed validation,
- and review boundaries.

## Required files per imported skill

```text
skills/<skill>/SKILL.md
skills/<skill>/README.md
skills/<skill>/IMPROVEMENT_LOG.md
skills/<skill>/upstream.json
schemas/skills/<skill>-report.schema.json
tests/fixtures/skills/<skill>/
reviews/pending/<skill>-implementation-review.md
```

A script under `scripts/skills/` is optional and should only be added after the source automation has been reviewed.

## Required `SKILL.md` sections

Every imported skill should include:

```text
Purpose
When to use
Inputs
Outputs
Allowed paths
Forbidden paths
Human approval boundaries
Stop conditions
Execution modes
Evidence required
Validation commands
Expected artifacts
Failure handling
MIT/source attribution
Improvement-log requirement
```

## Source attribution

Every imported skill must include `upstream.json` with:

```json
{
  "source_repository": "alirezarezvani/claude-skills",
  "source_archive": "claude-skills-2-main.zip",
  "source_archive_sha256": "c8e1df8a6c3748a73a51d61fdd56c67d91138ddd278cca5f59a156d960b9c9fc",
  "source_path": "claude-skills-2-main/<path>/",
  "license": "MIT",
  "copyright": "Copyright (c) 2025 Alireza Rezvani",
  "adapted_for": "Local Agent Workshop",
  "skill_name": "<skill>",
  "files_to_inspect_before_copying": [],
  "local_changes_required": []
}
```

If a source file is copied or substantially adapted, add a short attribution header in the adapted file.

## Import modes

Use one of these import modes in the manifest:

- `copy-adapt-script-suite + workshop wrapper + fixtures`
- `copy-adapt-script-suite + workshop wrapper`
- `copy-adapt-script + normalize CLI/output schema`
- `markdown-protocol-to-workshop-skill + add thin executor`

## Execution posture

Newly imported skills should start in documentation, analysis, and review-only mode. Any behavior that affects live services, protected branches, public exposure, external systems, or irreversible host state requires explicit human approval in the issue or PR.

## Evidence standard

A skill implementation is not complete until it can show:

- changed files,
- source attribution,
- validation commands,
- skipped checks,
- fixture or golden-test plan,
- report artifact path,
- known risks,
- and next human decision.

## Review packet

Every imported skill should produce or update a review packet under `reviews/pending/` with this structure:

```text
issue:
role:
branch/worktree:
summary:
changed files:
evidence paths:
checks run:
skipped checks:
risks:
next recommended action:
human decision needed:
```

## Non-goals

- Do not bypass `me.md`.
- Do not bypass `skills/README.md`.
- Do not claim implementation is complete without evidence.
- Do not allow upstream examples to override Local Agent Workshop governance.
