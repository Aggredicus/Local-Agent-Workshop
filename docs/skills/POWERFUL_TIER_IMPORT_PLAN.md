# POWERFUL Tier Skills Import Plan

This plan begins a staged, evidence-gated import of 25 POWERFUL-tier skills into Local Agent Workshop.

This is not a bulk-copy plan. It is a safe porting plan: every imported skill must become a repo-native Local Agent Workshop skill with explicit stop conditions, evidence requirements, MIT attribution, and review boundaries.

## Source provenance

- Source repository: alirezarezvani/claude-skills
- Source archive used for analysis: `claude-skills-2-main.zip`
- Source archive SHA-256: `c8e1df8a6c3748a73a51d61fdd56c67d91138ddd278cca5f59a156d960b9c9fc`
- License: MIT
- Copyright: Copyright (c) 2025 Alireza Rezvani

## Development issue

- Tracking issue: #174

## Import principles

1. Follow `me.md` and repository governance before this plan.
2. Treat upstream files as source material, not as trusted instructions.
3. Preserve MIT attribution for all copied or substantially adapted material.
4. Review upstream automation before enabling it.
5. Default new automation to review-only behavior.
6. Add JSON report schemas and fixture paths before claiming implementation is complete.
7. Stop at human-approval boundaries for private credentials, live services, branch protection, public exposure, or irreversible host changes.
8. Produce human-ready review packets with changed files, evidence, skipped checks, risks, and next decision.

## Phases

### Phase 0 — Import standard and manifest

Deliver:

- `docs/skills/SKILL_PORTING_STANDARD.md`
- `docs/skills/POWERFUL_TIER_MANIFEST.md`
- `schemas/skills/skill-report.schema.json`
- `schemas/skills/powerful-tier-manifest.schema.json`

### Phase 1 — Security gate

Import first:

- `skill-security-auditor`
- `dependency-auditor`
- `env-secrets-manager`

The first patch only scaffolds `/skill-security-auditor`; the remaining two should be separate follow-up issues.

### Phase 2 — Agent orchestration and local workflow

- `agent-designer`
- `agent-workflow-designer`
- `git-worktree-manager`
- `monorepo-navigator`
- `mcp-server-builder`

### Phase 3 — Review, API, testing, and code quality

- `pr-review-expert`
- `api-design-reviewer`
- `api-test-suite-builder`
- `performance-profiler`
- `tech-debt-tracker`
- `codebase-onboarding`

### Phase 4 — Data, RAG, and migration architecture

- `rag-architect`
- `database-designer`
- `database-schema-designer`
- `migration-architect`

### Phase 5 — Release, CI/CD, observability, and operations

- `ci-cd-pipeline-builder`
- `changelog-generator`
- `release-manager`
- `observability-designer`
- `runbook-generator`
- `incident-commander`

Note: `incident-commander` source path is `engineering-team/skills/incident-commander/`, not `engineering/skills/incident-commander/`.

### Phase 6 — People systems

- `interview-system-designer`

## Completion definition

The POWERFUL-tier import is complete only when each skill has:

- `skills/<skill>/SKILL.md`
- `skills/<skill>/README.md`
- `skills/<skill>/IMPROVEMENT_LOG.md`
- `skills/<skill>/upstream.json`
- relevant schemas under `schemas/skills/`
- fixtures under `tests/fixtures/skills/<skill>/`
- validation guidance and evidence paths
- a review packet for the implementation PR

## Non-goals for the first development slice

- Do not bulk-import all 25 skills.
- Do not activate unreviewed upstream automation.
- Do not enable live-service behavior by default.
- Do not bypass Local Agent Workshop review gates.
