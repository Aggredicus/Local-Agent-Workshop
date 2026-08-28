# Branch Convergence Review — 2026-08-28

## Verdict

`develop` is no longer functioning as Local Agent Workshop's integration branch in repository history.

At the start of this review:

```text
develop: 429753320520bb96907a3b6a887f333c9648c5ec
main:    054a64c6fbcbd005f9c3c6e18cf4086db3e24694
main ahead of develop: 120 commits
develop ahead of main: 0 commits
```

The merge base is the current `develop` tip itself. In other words, every commit on `develop` is already contained in `main`, and 120 additional commits have landed directly through `main`-targeted review since then.

## Current policy drift

The repository still describes `develop` as the reviewed integration branch in multiple authority surfaces, including:

- `.branch-policy.yaml`
- `docs/governance/BRANCH_POLICY.md`
- `me.md`
- `docs/protocols/PUBLISH_PROTOCOL.md`
- `skills/publish/SKILL.md`

That written model no longer matches observed repository operation.

## Recommended branch model

Adopt a simple trunk-based model:

```text
main          reviewed stable trunk and normal PR target
agent/*       autonomous/agent work branches
feature/*     optional human feature branches
fix/*         optional bug-fix branches
experimental  sandbox/lab branch
release/*     exceptional release-staging branches when actually needed
```

Normal development should use short-lived branches targeting `main`. Human approval and CI remain the merge gates for `main`; removing `develop` from the normal path does not weaken those boundaries.

## Migration recommendation

1. Update all branch-policy authority surfaces in one governance PR.
2. Change the machine-readable integration target from `develop` to `main` or remove the separate integration concept.
3. Update `/publish` so it describes release/save-point preparation from reviewed `main`, rather than a `develop -> main` promotion ritual.
4. Update examples and stale roadmap text that still prescribe `develop`.
5. Keep the existing `develop` branch untouched during the policy migration so rollback/history remains available.
6. After the policy PR is merged and verified, decide separately whether the stale remote `develop` branch should be archived or deleted.

## Non-goals

This review does not:

- delete or move `develop`,
- weaken human approval for `main`,
- change branch protection directly,
- merge a governance PR automatically,
- rewrite repository history.

## Evidence source

GitHub compare result for `develop...main` on 2026-08-28 reported:

```text
status: ahead
ahead_by: 120
behind_by: 0
merge_base: 429753320520bb96907a3b6a887f333c9648c5ec
```

This document is a review artifact and recommendation. Canonical branch governance remains unchanged until a dedicated governance PR is reviewed and merged.
