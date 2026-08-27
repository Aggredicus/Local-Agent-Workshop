# Local Agent Workshop

**Local Agent Workshop** is a local-first, human-governed workspace for agent-assisted software development: reusable Agent Skills, reviewable branches, deterministic project state, evidence-backed verification, and explicit human approval at risk boundaries.

## Get running again

Requirements: Python 3.11+ and Git.

```bash
git clone https://github.com/Aggredicus/Local-Agent-Workshop.git
cd Local-Agent-Workshop
python -m venv .venv
```

Activate the virtual environment, then:

```bash
python -m pip install -e ".[dev]"
workshop skills validate
workshop skills sync
workshop doctor
bash scripts/verify.sh
```

`workshop skills sync` materializes the canonical `skills/` library into `.agents/skills/`, the modern project-level Agent Skills discovery location used by Cursor and other compatible clients. Older first-party skills are normalized to current Agent Skills frontmatter in the generated cache, while newer standards-compliant skills are copied as-is. The generated copy is gitignored: **edit `skills/<name>/` and sync again**, rather than editing `.agents/skills/`.

After syncing, reopen or reload your agent client so its skill inventory refreshes.

## Useful commands

```text
workshop --version
workshop doctor
workshop skills list
workshop skills validate
workshop skills sync
workshop hk validate
workshop hk next
workshop hk list
workshop hk show HK-001
```

`workshop doctor` checks the local Python/Git environment, core repository files, Agent Skill validity/discovery, and HyperKanban state. Warnings are actionable but non-fatal; hard readiness failures return a non-zero exit code.

## What is canonical?

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ↓
me.md                         canonical instruction spine
  ↓
skills/                      canonical reusable Agent Skills source
schemas/ + docs/ + scripts/  contracts, protocols, verification
  ↓
chronicle/                    historical event memory
orchestration/hyperkanban/    operational project-state projection
reviews/ + reports/           review/evidence artifacts
```

`.agents/skills/` is a generated compatibility/discovery cache, not a second source of truth.

## Core loop

```text
repo → preflight → task selection → isolated agent branch/worktree
→ work → verify → closeout → review card → human decision → resume
```

The branch policy is intentionally conservative: agents work on `agent/*` (or other explicitly allowed non-protected branches), while protected-branch merges and other consequential actions remain human-gated.

## Development workflow

Before changing code:

```bash
workshop doctor
bash scripts/verify.sh
```

During development, keep changes on an isolated branch and add tests alongside behavior. Before opening or updating a PR:

```bash
workshop skills validate
bash scripts/verify.sh
python scripts/repo_cleanup.py --phase after
```

CI tests supported Python versions and runs the same local verification path.

## HyperKanban

HyperKanban is a deterministic operational projection, not the sole source of truth. The current CLI supports validation, compact packets, card inspection, next-card selection, and evidence-gated completion.

```bash
workshop hk validate
workshop hk next
workshop hk show HK-002
```

## Repository instruction entrypoint

Start with `me.md`. Tool-specific instruction files such as `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, and Cursor rules are intentionally thin adapters that route back to it.

## Status

The August 2026 revival sprint focuses on restoring a trustworthy cold start: standards-compliant Agent Skills, native project skill discovery, a useful `workshop` health surface, explicit Python packaging, and multi-version CI. Larger orchestration/dashboard/runtime work remains separate from this recovery layer.
