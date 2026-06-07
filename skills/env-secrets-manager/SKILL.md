---
name: env-secrets-manager
description: Use when environment config, .env templates, secret drift, missing env keys, redaction, config examples, or environment setup review is requested. Inspect local env files and produce a redacted review report. Do not print private values, rotate credentials, or modify env files by default.
---

# Env Secrets Manager

## Purpose

Use `/env-secrets-manager` to review local environment configuration files and templates without exposing values. The v1.0 implementation is local, read-only, and redaction-first: it parses dotenv-style files, compares key sets when explicitly given both files, flags likely private values in example/template files, and records skipped checks clearly.

Article category from the Universal Agent Skill Creation Kit v2.7: infrastructure operations / environment configuration review.

## When to use

Use this skill when:

- `.env`, `.env.example`, `.env.sample`, or `.env.template` files are being reviewed,
- an agent needs to compare real config keys against an example/template,
- missing environment keys or stale templates are suspected,
- a PR changes environment configuration docs,
- a report must be produced without exposing private values.

Do not use this skill for credential rotation or cloud secret-store mutation. It is a local review and reporting skill.

## Required inputs

- Target project directory, or explicit dotenv/example file paths.
- Optional comparison pair: example/template file and local env file.
- Optional output path for JSON report.

## Outputs

A good run produces:

- JSON report using the shared skill report shape,
- redacted key inventory,
- findings with severity, path, category, and recommendation,
- drift summary when comparing two files,
- skipped-check list,
- short handoff for human review.

Preferred report path:

```text
reports/skills/<run-id>/env-secrets-audit.json
```

## Workflow

1. Read the target repository instructions.
2. Confirm the target path is local and readable.
3. Find supported dotenv-style files.
4. Parse key names while redacting values.
5. Flag likely private values in example/template files.
6. If comparison paths are supplied, compare key sets and report drift.
7. Emit a JSON report.
8. Record skipped checks and next recommended review.

## Gotchas

- A value that looks harmless may still be private; reports must redact all values, not only suspicious ones.
- `.env.example` files should usually contain placeholders, not real tokens or passwords.
- Missing keys can be intentional for optional integrations, so drift findings require human review.
- Dotenv syntax varies; this v1.0 wrapper covers common `KEY=value` lines only.

## Allowed paths

- target project directory passed to the wrapper,
- explicit env/example files passed to the wrapper,
- `reports/skills/`,
- `tests/fixtures/skills/env-secrets-manager/`,
- `reviews/pending/`.

## Forbidden behavior without explicit human approval

- printing private values,
- modifying `.env` files,
- rotating credentials,
- calling cloud secret stores,
- writing generated env files,
- protected branch mutation.

## Execution modes

- `analysis` — read local files and report findings with redacted values.
- `dry-run` — same as analysis; no source mutation.
- `approved-mutation` — reserved for future use and not implemented in v1.0.

## Verification

Run:

```sh
python -m pytest -q tests/skills/test_env_secrets_manager.py
```

Manual smoke test:

```sh
python scripts/skills/env_secrets_manager.py tests/fixtures/skills/env-secrets-manager/clean-project --json --run-id smoke-clean
```

## Stop conditions

Stop and create a handoff if:

- the task requires printing raw private values,
- the user expects credential rotation,
- the target configuration format is unsupported and the result would be misleading,
- the task requires cloud secret-store access or mutation.

## Handoff format

```text
Skill used: /env-secrets-manager
Target:
Files inspected:
Keys found:
Verdict:
Findings:
Skipped checks:
Evidence path:
Recommended next action:
```

## Source attribution

Adapted from the `env-secrets-manager` skill in `alirezarezvani/claude-skills` under the MIT License.

See `upstream.json` for source path, archive hash, copyright, and local changes.

## Improvement-log requirement

After every use, follow `skills/README.md`: create a follow-up improvement issue and update either `SKILL.md` or `IMPROVEMENT_LOG.md`, unless the repository recursion-breaker rule applies.
