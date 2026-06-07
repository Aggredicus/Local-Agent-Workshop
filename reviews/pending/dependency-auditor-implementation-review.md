# dependency-auditor Implementation Review Packet

issue: #176
role: implementation slice / dependency auditor skill
branch/worktree: `agent/dependency-auditor-skill`
base branch: `agent/powerful-tier-skills-scaffold`

## Summary

This patch implements `/dependency-auditor` as the next POWERFUL-tier skill using the Universal Agent Skill Creation Kit v2.7 pattern: one bounded skill, concrete model-facing trigger, gotchas, verification, stop conditions, fixture-backed tests, and a review packet.

The v1.0 wrapper is local and review-oriented. It reads supported dependency manifests, builds a dependency inventory, flags broad version specifiers, missing license metadata, and direct source references, and emits a Local Agent Workshop skill report.

## Changed files

- `skills/dependency-auditor/SKILL.md`
- `skills/dependency-auditor/README.md`
- `skills/dependency-auditor/IMPROVEMENT_LOG.md`
- `skills/dependency-auditor/upstream.json`
- `scripts/skills/dependency_auditor.py`
- `tests/fixtures/skills/dependency-auditor/clean-project/package.json`
- `tests/fixtures/skills/dependency-auditor/review-project/package.json`
- `tests/fixtures/skills/dependency-auditor/review-project/requirements.txt`
- `tests/skills/test_dependency_auditor.py`
- `reviews/pending/dependency-auditor-implementation-review.md`

## Evidence paths

- Skill contract: `skills/dependency-auditor/SKILL.md`
- Source metadata: `skills/dependency-auditor/upstream.json`
- Wrapper: `scripts/skills/dependency_auditor.py`
- Fixtures: `tests/fixtures/skills/dependency-auditor/`
- Tests: `tests/skills/test_dependency_auditor.py`

## Checks run

Local check outside the repo connector, using the same file contents before GitHub commit:

```sh
python -m pytest -q tests/skills/test_dependency_auditor.py
```

Result:

```text
2 passed
```

## Skipped checks

- Full repository test suite was not run through the GitHub connector.
- Live dependency advisory checks were intentionally not performed.
- Package-manager commands were intentionally not run.
- Lockfile parsing is not implemented in v1.0.

## Risks

- Manifest-only review cannot prove transitive dependency safety.
- The scanner can miss ecosystem-specific dependency declarations.
- License metadata can be incomplete or misleading.
- The wrapper should be treated as first-pass review, not a complete release gate.

## Next recommended action

Review this PR after #175 lands or while stacked on #175. Future improvements should add lockfile parsing, ecosystem-specific advisory adapters, and richer license compatibility logic in separate issues.

## Human decision needed

Decide whether this v1.0 skill is acceptable as a local first-pass dependency audit skill.
