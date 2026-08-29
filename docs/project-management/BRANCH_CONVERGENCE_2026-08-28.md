# Branch Convergence Review — 2026-08-28

## Verdict

`develop` is no longer functioning as Local Agent Workshop's integration branch in repository history.

After PR #185 merged, the measured state is:

```text
develop: 429753320520bb96907a3b6a887f333c9648c5ec
main:    ed5e571ac90252d94655152f566fc34c0e5221d5
main ahead of develop: 127 commits
develop ahead of main: 0 commits
```

The merge base is the current `develop` tip itself. Every commit on `develop` is already contained in `main`; `develop` has no unique work to integrate.

## Policy drift found

Before this governance migration, the repository still described `develop` as the reviewed integration branch in:

- `.branch-policy.yaml`
- `docs/governance/BRANCH_POLICY.md`
- `me.md`
- `docs/protocols/PUBLISH_PROTOCOL.md`
- `skills/publish/SKILL.md`
- CI push-branch configuration

That written model no longer matched observed repository operation.

## Hosted enforcement gap

The same audit found that GitHub currently reports the `main` branch with branch protection disabled.

This does not change repository policy: `main` remains human-gated. It means the hosted enforcement layer is weaker than the repository's declared governance and should be aligned through an explicit repository-settings decision rather than silently changed inside this source-only migration.

## Adopted branch model in this PR

```text
main          reviewed stable trunk and normal PR target
agent/*       autonomous/agent work branches
feature/*     optional human feature branches
fix/*         optional bug-fix branches
experimental  sandbox/lab branch
release/*     exceptional release-staging branches when actually needed
rc/*          exceptional release-candidate branches when actually needed
develop       frozen legacy history; not active integration
```

Normal development uses short-lived branches targeting `main`. Human approval and CI remain the merge gates for `main`; removing `develop` from the normal path does not weaken those boundaries.

For compatibility with tooling that expects an `integration` key, `.branch-policy.yaml` resolves `integration: main` rather than inventing a second active long-lived branch.

## Publish lifecycle

`/publish` no longer means `develop -> main` promotion.

The normal sequence is:

```text
short-lived branch
→ PR targeting main
→ CI/review
→ explicit human approval
→ merge to main
→ verify reviewed main state
→ /publish packet / stable save point
→ optional separately approved release action
```

## Legacy develop handling

This migration deliberately does not delete, move, fast-forward, or repurpose `develop`.

`develop` remains on policy-protected / agent-deny lists while retained so its historical state cannot be casually mutated. A later decision may archive or delete the remote branch only with explicit human approval.

## CI handling

CI continues to run on all pull requests and on pushes to active branches. The explicit `develop` push trigger is removed because `develop` is no longer an active integration destination.

## Non-goals

This migration does not:

- delete or move `develop`,
- weaken human approval for `main`,
- change GitHub branch-protection/ruleset settings directly,
- merge this governance PR automatically,
- rewrite repository history,
- create live release/deployment effects.

## Evidence source

GitHub compare result for `develop...main` after PR #185 merged reported:

```text
status: ahead
ahead_by: 127
behind_by: 0
merge_base: 429753320520bb96907a3b6a887f333c9648c5ec
```

GitHub branch metadata for `main` reported:

```text
main: ed5e571ac90252d94655152f566fc34c0e5221d5
protected: false
protection.enabled: false
```

This document records the evidence and the migration represented by the associated governance PR. GitHub-hosted protection settings remain a separate explicit governance action.
