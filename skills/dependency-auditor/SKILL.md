---
name: dependency-auditor
description: Use when dependency-management, package manifest review, license field review, version pinning, upgrade planning, or release-readiness dependency checks are requested. Inspect local dependency manifests and produce a reviewable report. Do not install packages or call live services by default.
---

# Dependency Auditor

## Purpose

Use `/dependency-auditor` to inspect local dependency manifests and produce a reviewable Local Agent Workshop report. The v1.0 implementation is intentionally local and manifest-only: it reads package metadata, highlights broad version ranges or missing license metadata, and records skipped checks clearly.

Article category from the Universal Agent Skill Creation Kit v2.7: infrastructure operations / dependency-management.

## When to use

Use this skill when:

- dependency-management or package review is requested,
- a PR changes `package.json`, `requirements.txt`, `pyproject.toml`, or `go.mod`,
- release readiness requires a dependency summary,
- an agent needs a first-pass dependency inventory before a deeper ecosystem-specific review.

Do not use this skill as the only release gate for a production release. It is a first-pass local manifest review.

## Required inputs

- Target project directory.
- Any relevant issue, PR, or release context.
- Optional output path for JSON report.

## Outputs

A good run produces:

- JSON report using the shared skill report shape,
- dependency inventory,
- findings with severity, path, category, and recommendation,
- skipped-check list,
- short handoff for human review.

Preferred report path:

```text
reports/skills/<run-id>/dependency-audit.json
```

## Workflow

1. Read the target repository instructions.
2. Confirm the target path is a local project directory.
3. Scan supported manifests:
   - `package.json`
   - `requirements.txt`
   - `requirements-dev.txt`
   - `pyproject.toml`
   - `go.mod`
4. Build a dependency inventory.
5. Flag broad version specifiers, missing license metadata, malformed manifests, and unusual source directives.
6. Emit a JSON report.
7. Record skipped checks and next recommended review.

## Gotchas

- A clean manifest-only report does not prove the dependency tree is safe; it only means this local scanner did not find its configured review signals.
- JavaScript projects may rely on lockfiles; this v1.0 wrapper does not parse lockfiles yet.
- Python projects can declare dependencies in many places; this v1.0 wrapper covers common simple cases only.
- License metadata in package manifests can be absent or misleading; human review may still be needed.

## Allowed paths

- target project directory passed to the wrapper,
- `reports/skills/`,
- `tests/fixtures/skills/dependency-auditor/`,
- `reviews/pending/`.

## Forbidden behavior without explicit human approval

- package installation,
- package updates,
- lockfile rewrites,
- release publication,
- live service calls,
- protected branch mutation.

## Execution modes

- `analysis` — read local manifests and report findings.
- `dry-run` — same as analysis; no source mutation.
- `approved-mutation` — reserved for future use and not implemented in v1.0.

## Verification

Run:

```sh
python -m pytest -q tests/skills/test_dependency_auditor.py
```

Manual smoke test:

```sh
python scripts/skills/dependency_auditor.py tests/fixtures/skills/dependency-auditor/clean-project --json --run-id smoke-clean
```

## Stop conditions

Stop and create a handoff if:

- the target path is missing,
- the project uses an unsupported dependency ecosystem and the result would be misleading,
- the task requires live advisory lookups or package manager execution,
- the user expects automated upgrades rather than a review report.

## Handoff format

```text
Skill used: /dependency-auditor
Target:
Manifests inspected:
Dependencies found:
Verdict:
Findings:
Skipped checks:
Evidence path:
Recommended next action:
```

## Source attribution

Adapted from the `dependency-auditor` skill in `alirezarezvani/claude-skills` under the MIT License.

See `upstream.json` for source path, archive hash, copyright, and local changes.

## Improvement-log requirement

After every use, follow `skills/README.md`: create a follow-up improvement issue and update either `SKILL.md` or `IMPROVEMENT_LOG.md`, unless the repository recursion-breaker rule applies.
