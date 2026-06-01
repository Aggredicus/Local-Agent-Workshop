# Local Agent Workshop Documentation

This directory is the documentation map for Local Agent Workshop.

For agent orientation, read files in this order:

1. Repository root `README.md` for project purpose.
2. Repository root `me.md` for the canonical instruction spine.
3. `docs/NAVIGATION_INDEX.md` for the documentation map.
4. `docs/architecture/REPOSITORY_KNOWLEDGE_MAP.md` for the source-of-truth and projection model.

## Status legend

| Status | Meaning |
|---|---|
| implemented | File or directory exists in the repository or active PR stack. |
| planned | File is planned by an issue but may not exist yet. |
| generated | File should eventually be produced by scripts or CI. |
| example | File is a seed/example and not canonical runtime state. |

## Start here

| Topic | Path | Status |
|---|---|---|
| Canonical instruction spine | `../me.md` | implemented |
| Human-facing project overview | `../README.md` | implemented |
| Documentation navigation | `NAVIGATION_INDEX.md` | implemented |
| Repository knowledge map | `architecture/REPOSITORY_KNOWLEDGE_MAP.md` | implemented |
| Standard execution contract | `protocols/STANDARD_EXECUTION_CONTRACT.md` | in active PR #119 |
| Schema registry policy | `protocols/SCHEMA_REGISTRY_AND_COMPATIBILITY.md` | in active PR #122 |
| Repository validation gate | `protocols/REPO_VALIDATION_GATE.md` | in active PR #123 |

## Source-of-truth reminder

```text
GitHub Issues = planned work and coordination
Pull Requests = review boundary
CI = validation proof
Chronicle = historical event memory
HyperKanban = operational projection
Reports = evidence artifacts
Dashboard = generated visual projection, not authority
```

Do not treat planned docs, dashboards, or example seeds as canonical runtime state until they are schema-governed and validated.
