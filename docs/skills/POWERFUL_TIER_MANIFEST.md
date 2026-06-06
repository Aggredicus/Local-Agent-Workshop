# POWERFUL Tier Skills Manifest

This manifest tracks the 25 requested POWERFUL-tier skills and their staged import status.

Source archive SHA-256: `c8e1df8a6c3748a73a51d61fdd56c67d91138ddd278cca5f59a156d960b9c9fc`

## Status values

- `planned` — not started.
- `scaffolded` — repo-native skill wrapper exists, but executable implementation is not complete.
- `implemented` — skill has docs, attribution, schema, fixtures, validation, and review packet.
- `blocked` — waiting on source, design, or approval.

## Manifest

| Phase | Skill | Source path | Import mode | Maturity | Status |
|---:|---|---|---|---|---|
| 1 | `skill-security-auditor` | `engineering/skills/skill-security-auditor/` | script-suite + workshop wrapper | B / 7.8 | scaffolded |
| 1 | `dependency-auditor` | `engineering/skills/dependency-auditor/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 1 | `env-secrets-manager` | `engineering/skills/env-secrets-manager/` | script + normalized report | C / 6.9 | planned |
| 2 | `agent-designer` | `engineering/skills/agent-designer/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 2 | `agent-workflow-designer` | `engineering/skills/agent-workflow-designer/` | script + normalized report | C / 6.6 | planned |
| 2 | `git-worktree-manager` | `engineering/skills/git-worktree-manager/` | script + normalized report | C / 6.9 | planned |
| 2 | `monorepo-navigator` | `engineering/skills/monorepo-navigator/` | script + normalized report | C / 6.9 | planned |
| 2 | `mcp-server-builder` | `engineering/skills/mcp-server-builder/` | script + normalized report | C / 7.0 | planned |
| 3 | `pr-review-expert` | `engineering/skills/pr-review-expert/` | markdown protocol + thin executor | C / 5.5 | planned |
| 3 | `api-design-reviewer` | `engineering/skills/api-design-reviewer/` | script-suite + workshop wrapper | B / 8.3 | planned |
| 3 | `api-test-suite-builder` | `engineering/skills/api-test-suite-builder/` | markdown protocol + thin executor | C / 5.5 | planned |
| 3 | `performance-profiler` | `engineering/skills/performance-profiler/` | script + normalized report | C / 6.9 | planned |
| 3 | `tech-debt-tracker` | `engineering/skills/tech-debt-tracker/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 3 | `codebase-onboarding` | `engineering/skills/codebase-onboarding/` | script + normalized report | C / 6.6 | planned |
| 4 | `rag-architect` | `engineering/skills/rag-architect/` | script-suite + workshop wrapper | B / 7.9 | planned |
| 4 | `database-designer` | `engineering/skills/database-designer/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 4 | `database-schema-designer` | `engineering/skills/database-schema-designer/` | markdown protocol + thin executor | C / 5.5 | planned |
| 4 | `migration-architect` | `engineering/skills/migration-architect/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 5 | `ci-cd-pipeline-builder` | `engineering/skills/ci-cd-pipeline-builder/` | script + normalized report | C / 7.3 | planned |
| 5 | `changelog-generator` | `engineering/skills/changelog-generator/` | script + normalized report | C / 7.3 | planned |
| 5 | `release-manager` | `engineering/skills/release-manager/` | script-suite + workshop wrapper | A / 8.9 | planned |
| 5 | `observability-designer` | `engineering/skills/observability-designer/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 5 | `runbook-generator` | `engineering/skills/runbook-generator/` | script + normalized report | C / 6.6 | planned |
| 5 | `incident-commander` | `engineering-team/skills/incident-commander/` | script-suite + workshop wrapper + fixtures | A / 9.2 | planned |
| 6 | `interview-system-designer` | `engineering/skills/interview-system-designer/` | script-suite + workshop wrapper + fixtures | A / 9.1 | planned |

## Notes

- Source paths come from the implementation-grade analysis.
- `incident-commander` intentionally uses the `engineering-team/skills/` path.
- Each skill should move through the status values in reviewable patches.
