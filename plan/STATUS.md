# Status

Initial normalization branch is in progress.

## Current branch

```text
agent/0001-normalize-repo-structure
```

## Current focus

Issue #1: normalize the repository structure from uploaded zip assets and establish the canonical Local Agent Workshop scaffold.

## Known cleanup item

The connector blocked deletion of the temporary `src/workshop_core/` package marker and blocked creating Python files directly under `src/workshop/`.

The intended final active package path remains:

```text
src/workshop/
```

The intended CLI entrypoint remains:

```toml
workshop = "workshop.cli:main"
```
