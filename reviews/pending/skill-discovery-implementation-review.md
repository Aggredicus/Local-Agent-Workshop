# skill-discovery Implementation Review Packet

issue: #181
role: implementation slice / deterministic local skill selection gate
branch/worktree: `agent/skill-discovery-gate`
base branch: `main`

## Summary

This patch implements `/skill-discovery` as a Local Agent Workshop meta-skill that prevents agents from missing existing local skills before choosing a workflow, creating a new skill, reviewing a PR, merging, or continuing a stacked PR sequence.

The motivating failure was missing the existing `/merge-review` skill because broad GitHub code search and memory were treated as enough. This skill makes local skill discovery deterministic by scanning `skills/*/SKILL.md`, checking direct paths for named skills, validating registry drift, and ranking candidate skills for a task summary.

## Changed files

- `skills/skill-discovery/SKILL.md`
- `skills/skill-discovery/README.md`
- `skills/skill-discovery/IMPROVEMENT_LOG.md`
- `scripts/skills/list_available_skills.py`
- `scripts/skills/select_skill.py`
- `tests/fixtures/skills/skill-discovery/repo/skills/merge-review/SKILL.md`
- `tests/fixtures/skills/skill-discovery/repo/skills/skill-security-auditor/SKILL.md`
- `tests/fixtures/skills/skill-discovery/repo/skills/dependency-auditor/SKILL.md`
- `tests/fixtures/skills/skill-discovery/repo/skills/env-secrets-manager/SKILL.md`
- `tests/fixtures/skills/skill-discovery/repo/skills/generic-helper/SKILL.md`
- `tests/fixtures/skills/skill-discovery/repo/skills/registry.json`
- `tests/skills/test_skill_discovery.py`
- `reviews/pending/skill-discovery-implementation-review.md`

## Evidence paths

- Skill contract: `skills/skill-discovery/SKILL.md`
- Inventory helper: `scripts/skills/list_available_skills.py`
- Selection helper: `scripts/skills/select_skill.py`
- Fixture repo: `tests/fixtures/skills/skill-discovery/repo/`
- Tests: `tests/skills/test_skill_discovery.py`

## Checks run

Local check outside the repo connector, using the same file contents before GitHub commit:

```sh
python -m pytest -q tests/skills/test_skill_discovery.py
```

Result:

```text
6 passed
```

Covered scenarios:

- direct path lookup finds `skills/merge-review/SKILL.md`,
- broad search failure is not treated as absence when a skill is named,
- registry drift is detected,
- merge task ranks `/merge-review`,
- external skill import ranks `/skill-security-auditor`,
- new dependency-skill proposal selects `/dependency-auditor` instead of recommending duplicate skill creation.

## Skipped checks

- Full repository test suite was not run through the GitHub connector.
- Live GitHub API skill-tree enumeration was not implemented in v1.0.
- Registry/index mutation was intentionally not implemented.
- Semantic embedding or LLM-based ranking was intentionally not implemented.

## Risks

- Skill selection is keyword/rule based, so it is a deterministic preflight rather than semantic certainty.
- Registry drift detection supports JSON registry/index files in v1.0, not Markdown table parsing.
- Branch/ref support is represented by the root path passed to the scripts; connector-specific branch fetching is not implemented inside the script.
- The selected skill still must be read and followed by the agent; this helper does not replace workflow-specific skills.

## Next recommended action

Review this PR, then consider adding `/skill-discovery` as a mandatory preflight in `me.md` or `skills/README.md` after the v1 implementation proves useful.

## Human decision needed

Decide whether this v1.0 skill is acceptable as a deterministic local skill-selection gate.
