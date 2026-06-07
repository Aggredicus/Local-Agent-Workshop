# /dependency-auditor

`/dependency-auditor` is a Local Agent Workshop skill for first-pass dependency manifest review.

It follows the Universal Agent Skill Creation Kit v2.7 pattern: one bounded skill, concrete trigger, gotchas, verification, stop conditions, and fixture-backed tests.

## Current status

- Status: implemented v1.0 local wrapper
- Source: `alirezarezvani/claude-skills`
- Source path: `claude-skills-2-main/engineering/skills/dependency-auditor/`
- Source license: MIT
- Tracking issue: #176

## What it does

- Reads local dependency manifests.
- Builds a small dependency inventory.
- Flags broad version specifiers and missing license metadata.
- Emits a JSON report in the Local Agent Workshop skill-report shape.
- Records skipped checks clearly.

## What it does not do yet

- It does not install packages.
- It does not update dependencies.
- It does not run package-manager commands.
- It does not perform live advisory lookups.
- It does not parse every ecosystem-specific lockfile.

## Supported v1.0 manifests

```text
package.json
requirements.txt
requirements-dev.txt
pyproject.toml
go.mod
```

## Usage

```sh
python scripts/skills/dependency_auditor.py <project-path> --json --out reports/skills/<run-id>/dependency-audit.json
```

Strict mode returns non-zero when the verdict is not `pass`:

```sh
python scripts/skills/dependency_auditor.py <project-path> --json --strict
```

## Tests

```sh
python -m pytest -q tests/skills/test_dependency_auditor.py
```
