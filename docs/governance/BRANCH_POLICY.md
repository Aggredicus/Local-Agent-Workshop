# Branch Policy

## Active branch model

Local Agent Workshop uses a trunk-based workflow centered on `main`.

- `main`: reviewed stable trunk, normal pull-request target, released/client-safe baseline.
- `experimental`: sandbox and lab branch.
- `develop`: legacy historical branch retained temporarily for history/rollback reference. It is not an active integration branch or normal pull-request target.

The machine-readable policy keeps `integration: main` so tools that expect an integration key continue to resolve the active reviewed integration target without requiring a separate long-lived branch.

## Short-lived branch prefixes

Normal work should happen on short-lived branches targeting `main`:

- `agent/*`
- `feature/*`
- `fix/*`
- `hotfix/*`
- `refactor/*`
- `docs/*`
- `test/*`
- `chore/*`
- `spike/*`

Exceptional release staging may use:

- `release/*`
- `rc/*`

## Policy-protected branches

These branches are treated as protected by repository policy and require explicit human approval before merge or direct mutation:

- `main`
- `develop` — legacy freeze while it is retained
- `release/*`
- `rc/*`

`develop` remains on the deny/protected lists only to preserve its historical state during migration. It must not be used as the normal integration branch.

## Agent rule

Agents may create branches, commits, diffs, reports, tests, and suggested pull requests.

Normal agent pull requests should target `main`.

Agents may not merge into policy-protected branches without explicit human approval. They may not move, delete, or repurpose the legacy `develop` branch without a separate explicit human decision.

## GitHub enforcement note

Repository policy and GitHub-hosted branch-protection settings are separate enforcement layers.

During the 2026-08-28 convergence audit, GitHub reported `main` branch protection as disabled even though repository policy treats `main` as human-gated. Until GitHub settings are aligned, this repository policy remains binding on agents and human workflow, and the missing hosted enforcement should be treated as a governance gap rather than permission to bypass review.
