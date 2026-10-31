# Roadmap

## v0.1 — CLI + Markdown review loop

- Repo initializer.
- Branch policy.
- Chronicle events.
- Review cards.
- Morning report.

## v0.2 — Branch-aware sandbox runner

- Worktree management.
- Branch guards.
- Verification routing.

## v0.3 — Repo graph + risk scoring

- GraphML/JSON graph export.
- File impact analysis.
- Risk-zone detection.

## v0.4 — Resumable grind engine

- Checkpointing.
- Pause/resume.
- Long-duration run state.

## v0.5 — Local dashboard

- Morning cockpit.
- Patch cards.
- Beginner/advanced modes.

## v0.6 — Telegram/Signal escalation

- Quiet-by-default escalation.
- Decision replies.
- Rate limits.

## v1.0 — Stable Local Agent Workshop

- Production-quality local-first agentic development harness.

## v0.2 integration increment — CAW / LAW boundary

- [x] Introduce private serverless SQLite node state with stable pseudonymous installation/agent IDs.
- [x] Preserve agent source/version/digest history and invalidate pending capability proposals on changes.
- [x] Support locally validated CAW work packets via one canonical CAW contract JSON.
- [x] Produce default-deny execution plans without claiming to run an enforceable sandbox.
- [ ] Implement and adversarially verify an actual restricted runner (filesystem, secret, network and host controls).
- [ ] Implement hardware capability probes and local model-provider adapters, privacy-first.
- [ ] Integrate authenticated GitHub review claims with least-privilege runtime credentials.
- [ ] Validate a cross-repo integration fixture from a pinned CAW version, then roll out to more than one physical host.

The runtime stays in LAW. Human/agent skill policy, contributor matching, PM and governance live in CAW. GitHub retains final merge authority.
