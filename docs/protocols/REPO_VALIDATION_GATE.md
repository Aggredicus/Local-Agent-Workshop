# Repository Validation Gate

The repository validation gate is a read-only quality check for schema-governed contracts and examples.

It exists so Local Agent Workshop can detect contract drift before agents rely on incomplete, stale, or contradictory JSON artifacts.

## Script

```text
scripts/validate_repo_contracts.py
```

## Current scope

The first validation target is the schema registry created by #109:

```text
schemas/schema-registry.json
```

The validator currently checks:

- the registry file is valid JSON,
- required registry fields exist,
- `artifact_type` is `schema_registry`,
- schema versions use `MAJOR.MINOR.PATCH`,
- each schema record has required fields,
- schema IDs are unique and use a safe identifier pattern,
- statuses are one of `planned`, `draft`, `active`, `deprecated`, or `retired`,
- non-planned schema paths exist,
- planned schemas may point to missing future paths,
- active schemas include examples,
- example paths exist when required,
- migration notes are present.
- metadata fields have the required basic string/list types, including unique string lists,
- registry, schema and example paths stay inside the repository after resolving links; directories, absolute paths and traversal are rejected,
- malformed JSON, encoding errors and unreadable files return structured errors without a traceback.

## Required, optional, and warning-only checks

| Check | Current level | Notes |
|---|---|---|
| Registry JSON parses | required | Invalid JSON is an error. |
| Required registry fields exist | required | Missing fields are errors. |
| Duplicate schema IDs | required | Duplicate IDs are errors. |
| Non-planned schema path exists | required | Draft/active/deprecated/retired schemas must exist. |
| Planned schema path exists | info | Planned paths may be future files. |
| Active schema has example path | required | Active schemas need examples. |
| Planned schema example missing | warning | Planned schemas may reference future examples. |
| Migration notes present | required | Every record needs non-empty migration notes. |

## Commands

Text output:

```sh
python scripts/validate_repo_contracts.py
```

JSON output:

```sh
python scripts/validate_repo_contracts.py --format json --out reports/validation/latest.json
```

Use `--quiet` to omit routine informational text while retaining all warnings,
errors, counts and exit status. JSON output is always complete. `--schema-registry`
accepts a path relative to `--root`; escaping links and external files are rejected.

The script returns nonzero if errors are found.

## Registered schema content and examples

`python scripts/validate_repo_contracts.py --schemas` additionally uses the pinned
development tools `jsonschema` and `referencing` to check implemented registered
schema definitions, reference targets and their registered examples. Resources are
preloaded from validated repository paths; remote and arbitrary file retrieval
are disabled. Missing development tools fail explicitly. Planned entries remain
planned; unregistered files are outside this check's coverage. JSON Schema format
annotations are not additional format assertions.

Errors identify the schema/constraint without serializing example values.
Reports include actual schema/example/reference counts. Metadata-only invocation
still uses only the standard library for constrained environments.

## CI integration

`scripts/verify.sh` should run the validation gate before pytest:

```sh
python scripts/validate_repo_contracts.py --schemas
```

This keeps schema registry drift visible in local and CI verification.
The shared verification script also runs pinned Ruff checks for Python correctness
errors before pytest. Install development dependencies with `pip install -e '.[dev]'`.

## Non-goals

This gate does not yet:

- validate every schema in the repository,
- validate unregistered examples against inferred target schemas,
- check Markdown links,
- scan for real secrets,
- generate the deterministic dashboard,
- mutate files,
- access the network.

Those checks can be added later as the schema registry and dashboard mature.

## Agent rules

Agents should run the validation gate after changing:

- `schemas/registry.schema.json`,
- `schemas/schema-registry.json`,
- schema-governed example files,
- dashboard projection contracts,
- workflow state contracts,
- evidence/handoff contracts.

Agents must stop and create a handoff if validation fails and the failure cannot be fixed without changing task scope, altering a protected boundary, or breaking compatibility without migration notes.

## Review checklist

A reviewer should ask:

- Does the validation script run without network access?
- Does it fail on real errors?
- Does it distinguish planned future schema paths from missing implemented schemas?
- Does it produce a clear SUMMARY line?
- Is it wired into `scripts/verify.sh`?
- Are future checks documented as non-goals instead of silently implied?
