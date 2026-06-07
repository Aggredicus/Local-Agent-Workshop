# /env-secrets-manager

`/env-secrets-manager` is a Local Agent Workshop skill for first-pass environment configuration review.

It follows the Universal Agent Skill Creation Kit v2.7 pattern: one bounded skill, concrete trigger, gotchas, verification, stop conditions, redaction-first reporting, and fixture-backed tests.

## Current status

- Status: implemented v1.0 local wrapper
- Source: `alirezarezvani/claude-skills`
- Source path: `claude-skills-2-main/engineering/skills/env-secrets-manager/`
- Source license: MIT
- Tracking issue: #178

## What it does

- Reads local dotenv-style files.
- Redacts all values in reports.
- Flags likely private values in example/template files.
- Compares key drift when explicit files are provided.
- Emits a JSON report in the Local Agent Workshop skill-report shape.
- Records skipped checks clearly.

## What it does not do yet

- It does not print private values.
- It does not modify `.env` files.
- It does not rotate credentials.
- It does not call cloud secret stores.
- It does not parse every configuration format.

## Supported v1.0 files

```text
.env
.env.local
.env.example
.env.sample
.env.template
*.env.example
*.env.sample
*.env.template
```

## Usage

```sh
python scripts/skills/env_secrets_manager.py <project-path> --json --out reports/skills/<run-id>/env-secrets-audit.json
```

Compare an example/template file to a local env file:

```sh
python scripts/skills/env_secrets_manager.py <project-path> --example .env.example --env .env.local --json
```

Strict mode returns non-zero when the verdict is not `pass`:

```sh
python scripts/skills/env_secrets_manager.py <project-path> --json --strict
```

## Tests

```sh
python -m pytest -q tests/skills/test_env_secrets_manager.py
```
