# /skill-security-auditor

`/skill-security-auditor` is the first safety and provenance gate for importing new skills into Local Agent Workshop.

This first development slice adds the repo-native scaffold only. It does not activate upstream automation.

## Current status

- Status: scaffolded
- Source: `alirezarezvani/claude-skills`
- Source path: `claude-skills-2-main/engineering/skills/skill-security-auditor/`
- Source license: MIT
- Tracking issue: #174

## What this skill should eventually do

- Inspect candidate skill directories.
- Review support scripts, references, templates, and metadata.
- Produce JSON and Markdown reports.
- Identify findings that require remediation or human review.
- Block activation of unclear or high-risk skill behavior until reviewed.

## Required local files

```text
skills/skill-security-auditor/SKILL.md
skills/skill-security-auditor/README.md
skills/skill-security-auditor/IMPROVEMENT_LOG.md
skills/skill-security-auditor/upstream.json
schemas/skills/skill-report.schema.json
reviews/pending/skill-security-auditor-implementation-review.md
```

## Follow-up implementation work

A future issue should decide whether to adapt the upstream scanner script into:

```text
scripts/skills/skill_security_auditor.py
```

That issue should add fixtures and tests before marking the skill implemented.
