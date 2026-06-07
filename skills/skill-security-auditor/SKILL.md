---
name: skill-security-auditor
description: Review candidate skills and skill-support files before they are installed or activated in Local Agent Workshop.
---

# Skill Security Auditor

## Purpose

Use `/skill-security-auditor` as the first review gate for imported or newly authored skills. The skill helps an agent inspect skill directories, support scripts, references, templates, and metadata before those files are treated as trusted Local Agent Workshop capabilities.

This scaffold is intentionally review-first. It records the Local Agent Workshop contract and source provenance before any upstream automation is copied or activated.

## When to use

Use this skill when:

- importing a skill from an external source,
- reviewing a new `skills/<skill>/` directory,
- adding support scripts under `scripts/skills/`,
- checking whether a skill has clear evidence, provenance, and approval boundaries,
- preparing a skill implementation review packet.

## Inputs

- Candidate skill path.
- Source provenance, if external.
- Expected local target paths.
- Any planned scripts, templates, fixtures, or report schemas.
- Relevant issue or PR.

## Outputs

- Review summary.
- Findings list.
- Suggested remediation.
- Evidence paths.
- Human decision needed.

Preferred report path:

```text
reports/skills/<run-id>/skill-security-audit.json
reports/skills/<run-id>/skill-security-audit.md
```

## Allowed paths

- `skills/<skill>/`
- `docs/skills/`
- `schemas/skills/`
- `tests/fixtures/skills/`
- `tests/skills/`
- `reports/skills/`
- `reviews/pending/`

## Forbidden paths without explicit human approval

- private credential files,
- protected branch settings,
- production deployment files,
- host or network configuration,
- destructive cleanup targets,
- historical Chronicle event rewrites.

## Human approval boundaries

Pause before enabling any behavior that affects live services, protected branches, public exposure, irreversible host state, or private credentials.

## Execution modes

- `analysis` — inspect files and produce findings.
- `dry-run` — simulate report generation without changing source files.
- `draft-generation` — draft remediation or review artifacts.
- `approved-mutation` — only with explicit human authorization in the issue or PR.

## Evidence required

A completed run should record:

- source paths inspected,
- findings and severity,
- commands or checks used,
- skipped checks and why they were skipped,
- report artifacts,
- next human decision.

## Validation commands

This scaffold does not yet install the upstream scanner. Until the script wrapper is added, validate by confirming the required files exist and the review packet is complete.

Future script validation target:

```sh
python scripts/skills/skill_security_auditor.py skills/<candidate-skill> --json --out reports/skills/<run-id>/skill-security-audit.json
```

## Expected artifacts

- `skills/skill-security-auditor/README.md`
- `skills/skill-security-auditor/IMPROVEMENT_LOG.md`
- `skills/skill-security-auditor/upstream.json`
- `schemas/skills/skill-report.schema.json`
- `reviews/pending/skill-security-auditor-implementation-review.md`

## Failure handling

If required context is missing, create a handoff instead of guessing. If a source file or support script looks risky or unclear, leave it unactivated and describe what review is needed.

## Source attribution

Adapted from the `skill-security-auditor` skill in `alirezarezvani/claude-skills` under the MIT License.

See `upstream.json` for source path, archive hash, copyright, and local changes.

## Improvement-log requirement

After every use, follow `skills/README.md`: create a follow-up improvement issue and update either `SKILL.md` or `IMPROVEMENT_LOG.md`, unless the repository recursion-breaker rule applies.
