# Grind Protocol

A grind run is a long-duration autonomous work session.

## Required steps

1. Read `me.md`.
2. Load branch policy.
3. Load roadmap, blockers, and pending review cards.
4. Select a task using value/risk scoring.
5. Create or use an isolated `agent/*` branch/worktree.
6. Perform scoped work.
7. Run verification.
8. Write Chronicle events.
9. Generate a review card.
10. Check whether to continue, pause, escalate, or stop.

## Grind should be resumable

Every grind run needs a run-state file under `.grind/state/`.

## Review bundles are artifacts, not always hard stops

A long-running grind may keep working on unrelated low-risk tasks after creating a review bundle, unless the next step depends on human input.
