# Schema Registry and Compatibility Policy

The schema registry is the discoverability and compatibility layer for JSON artifacts in Local Agent Workshop.

It exists so agents can find canonical contracts without relying on prior chat history, issue-memory, or dashboard prose.

## Source-of-truth status

The registry file is:

```text
schemas/schema-registry.json
```

The registry schema is:

```text
schemas/registry.schema.json
```

The registry is a source-of-truth index for schema metadata, but it does not make planned schemas real. A registry entry with `status: planned` may point to a future path that does not exist yet.

## Status values

| Status | Meaning |
|---|---|
| `planned` | The schema is designed or expected but its file may not exist yet. |
| `draft` | The schema file exists and may be used for early validation, but breaking changes are allowed with notes. |
| `active` | The schema is ready for regular validation and should have examples. |
| `deprecated` | The schema remains readable but should not be used for new artifacts. |
| `retired` | The schema is no longer supported except for historical interpretation. |

## Versioning policy

Schema versions use a semver-like pattern:

```text
MAJOR.MINOR.PATCH
```

Use:

- patch changes for clarifications, descriptions, typo fixes, or compatible examples,
- minor changes for compatible optional fields, new examples, or compatible enum additions,
- major changes for breaking shape changes, required field changes, semantic meaning changes, or incompatible enum removals.

## Breaking changes

A breaking schema change requires migration notes.

Breaking changes include:

- removing a field,
- renaming a field,
- making an optional field required,
- changing the meaning of a field,
- changing enum values in a way that invalidates existing artifacts,
- moving canonical artifact paths,
- changing artifact source-of-truth status.

The registry record should update:

```text
version
compatible_versions
migration_notes
last_reviewed_at
```

## Non-breaking changes

Non-breaking changes include:

- improving descriptions,
- adding optional fields,
- adding examples,
- adding compatible enum values,
- clarifying validation commands,
- adding notes.

Non-breaking changes should still update migration notes when they affect agent behavior.

## Example requirements

Active schemas should have at least one example path in the registry.

Draft schemas should have examples when practical.

Planned schemas may have no examples yet.

## Validation expectations

Before #111 exists, validation may be manual or review-based.

After #111, validation should run through:

```text
scripts/validate_repo_contracts.py
```

The first expected validation target is:

```text
schemas/schema-registry.json
```

The validation gate should eventually check:

- registry file validates against `schemas/registry.schema.json`,
- every non-planned schema path exists,
- active schemas have examples,
- example files exist,
- migration notes exist for breaking changes,
- duplicate schema IDs do not exist,
- planned schema entries are clearly marked as planned.

## Agent rules

Agents should:

- check the registry before creating a new JSON artifact type,
- add a registry entry when proposing a new schema,
- mark future schemas as `planned`, not `active`,
- avoid treating planned schema paths as existing files,
- include migration notes for breaking changes,
- avoid silently renaming schema IDs,
- stop and create a handoff if two schemas appear to govern the same artifact type.

Agents must not:

- treat dashboard projections as schema authority,
- treat example seeds as canonical runtime state,
- mark a schema active without examples unless a human explicitly approves an exception,
- break existing examples without migration notes,
- remove historical schema entries without review.

## Relationship to repository self-model

The repository self-model seed currently lives under:

```text
examples/self-model/repo_self_model_seed.json
```

That file is an example seed, not canonical runtime state. It should become schema-governed only after `schemas/repo_self_model.schema.json` exists and validation is wired.

## Relationship to HyperKanban and dashboard projections

HyperKanban and dashboard artifacts may use schema-governed JSON views, but they remain projections unless explicitly designated otherwise.

The registry should help agents distinguish:

```text
source artifact
projection
report
draft example
planned contract
```

## Initial registry scope

The first registry includes:

- the registry schema itself as `draft`,
- planned local model provider schema,
- planned agent intake/budget/evidence/handoff schemas,
- planned workflow/trace/event schemas,
- planned dashboard/dependency graph schemas,
- planned repository self-model schema.

This is intentionally lightweight. The goal is not to finish every schema in #109; the goal is to create the map and compatibility rules that make future schema work safe.

## Review checklist

A reviewer should ask:

- Does `schemas/schema-registry.json` validate against `schemas/registry.schema.json`?
- Are planned schemas clearly marked as planned?
- Is the registry honest about missing future paths?
- Are active/draft schemas linked to examples when possible?
- Are migration notes present for breaking changes?
- Does the policy prevent schema drift and source-of-truth confusion?
