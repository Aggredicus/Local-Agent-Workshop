# skill-security-auditor Implementation Review Packet

issue: #174
role: implementation scaffold plus read-only wrapper
branch/worktree: `agent/powerful-tier-skills-scaffold`

## Summary

This patch begins POWERFUL-tier skill import development by adding the staged import plan, porting standard, manifest, shared schemas, and a repo-native implementation slice for `/skill-security-auditor`.

The patch does not copy or execute the upstream scanner script. It adds a conservative Local Agent Workshop wrapper inspired by the upstream design and constrained to local read-only directory review.

## Changed files

- `docs/skills/POWERFUL_TIER_IMPORT_PLAN.md`
- `docs/skills/SKILL_PORTING_STANDARD.md`
- `docs/skills/POWERFUL_TIER_MANIFEST.md`
- `schemas/skills/skill-report.schema.json`
- `schemas/skills/powerful-tier-manifest.schema.json`
- `skills/skill-security-auditor/SKILL.md`
- `skills/skill-security-auditor/README.md`
- `skills/skill-security-auditor/IMPROVEMENT_LOG.md`
- `skills/skill-security-auditor/upstream.json`
- `scripts/skills/skill_security_auditor.py`
- `tests/fixtures/skills/skill-security-auditor/README.md`
- `tests/fixtures/skills/skill-security-auditor/safe-skill/SKILL.md`
- `tests/skills/test_skill_security_auditor.py`
- `reviews/pending/skill-security-auditor-implementation-review.md`

## Evidence paths

- Manifest: `docs/skills/POWERFUL_TIER_MANIFEST.md`
- Porting standard: `docs/skills/SKILL_PORTING_STANDARD.md`
- Source metadata: `skills/skill-security-auditor/upstream.json`
- Shared report schema: `schemas/skills/skill-report.schema.json`
- Wrapper: `scripts/skills/skill_security_auditor.py`
- Safe fixture: `tests/fixtures/skills/skill-security-auditor/safe-skill/SKILL.md`
- Tests: `tests/skills/test_skill_security_auditor.py`

## Checks run

Local check outside the repo connector, using the same file contents before GitHub commit:

```sh
python -m pytest -q tests/skills/test_skill_security_auditor.py
```

Result:

```text
2 passed
```

Additional evidence:

- The wrapper is local-directory only.
- No upstream script was executed.
- No external repository cloning is implemented in the wrapper.
- The manifest records all 25 requested skills and the special `incident-commander` source path.

## Skipped checks

- JSON schema validation was not run in the repository environment.
- Full repository test suite was not run through the GitHub connector.
- Source archive extraction was not performed inside the repository.

## Risks

- The scanner is heuristic and can produce false positives or false negatives.
- It does not perform dependency advisory lookups.
- It should be treated as a first-pass review gate, not a complete security guarantee.
- The Markdown manifest should eventually gain a machine-readable manifest JSON if automation depends on it.

## Next recommended action

Review this PR, then either merge the scaffold plus read-only wrapper or request changes before continuing with the remaining security-gate skills.

## Human decision needed

Decide whether the first import slice is ready to move from draft to review or needs more validation first.
