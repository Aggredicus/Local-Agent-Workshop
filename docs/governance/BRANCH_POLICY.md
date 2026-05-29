# Branch Policy

## Long-lived branches

- `main`: stable, released, client-safe code.
- `develop`: reviewed integration branch.
- `experimental`: sandbox and lab branch.

## Short-lived branch prefixes

- `agent/*`
- `feature/*`
- `fix/*`
- `hotfix/*`
- `refactor/*`
- `docs/*`
- `test/*`
- `chore/*`
- `spike/*`
- `release/*`
- `rc/*`

## Protected branches

Protected branches require explicit human approval before merge:

- `main`
- `develop`
- `release/*`
- `rc/*`

## Agent rule

Agents may create branches, commits, diffs, reports, tests, and suggested PRs.

Agents may not merge into protected branches without explicit human approval.
