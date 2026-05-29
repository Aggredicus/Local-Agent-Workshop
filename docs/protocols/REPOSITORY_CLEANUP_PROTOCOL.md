# Repository Cleanup Protocol

Repository cleanup is not a one-time chore. It is a required boundary around every meaningful work session.

```text
clean before work
work in a bounded branch
clean after work
leave evidence
```

## Purpose

The cleanup protocol keeps Local Agent Workshop reviewable, resumable, and safe for multi-agent work.

It prevents:

- stale PR confusion,
- superseded branch clutter,
- outdated status files,
- drift between state and packets,
- local verification breakage,
- hidden pending review obligations,
- and agents starting work from stale assumptions.

## Core rule

Every meaningful work session has two cleanup gates:

```text
Preflight cleanup gate  = before changing files
Closeout cleanup gate   = before opening/merging/ending work
```

Agents must not treat cleanup as optional.

## Preflight cleanup gate

Before work, an agent should:

1. Read `me.md`.
2. Confirm the target branch and protected-branch rules.
3. Check open PRs and identify stale, superseded, or blocked work.
4. Confirm the intended issue/card is not already owned by another active branch or PR.
5. Run the repository cleanup audit script in check mode.
6. Run local verification if practical.
7. Record known blockers before starting implementation.

Suggested command:

```sh
python scripts/repo_cleanup.py --phase before
```

## Closeout cleanup gate

After work, an agent should:

1. Run local verification.
2. Run the repository cleanup audit script in after-work mode.
3. Confirm generated artifacts are synchronized.
4. Confirm no superseded PR was left open without explanation.
5. Confirm the PR body lists evidence and next steps.
6. Record any follow-up cleanup issue if something cannot be safely fixed now.

Suggested command:

```sh
python scripts/repo_cleanup.py --phase after
```

## Cleanup categories

### Pull request hygiene

Check for:

- open PRs superseded by replacements,
- stacked PRs whose base already merged,
- PRs targeting stale feature branches,
- duplicate PRs for the same card or issue,
- open PRs with failed CI and no follow-up,
- stale review comments that have been addressed elsewhere.

### Branch hygiene

Check for:

- old `agent/*` branches whose PRs are merged or closed,
- branches with no linked issue, card, or PR,
- branches that should become `spike/*` instead of `agent/*`,
- work branches that should be rebased or replaced.

Branch deletion should be human-approved unless the branch is obviously superseded and safe to delete.

### State hygiene

Check for:

- HyperKanban `state.json` / `packet.txt` drift,
- done cards without evidence,
- blocked cards without reason,
- high-risk cards without review gate,
- Chronicle events missing for meaningful work,
- review cards missing for medium/high-risk changes.

### Verification hygiene

Check for:

- `scripts/verify.sh` still passing,
- test suite still passing,
- CLI entrypoint still usable,
- cleanup audit script returning success or actionable warnings.

### Documentation hygiene

Check for:

- README status matching current project state,
- `plan/STATUS.md` not contradicting README,
- protocol docs updated when behavior changes,
- PR body listing evidence and follow-up work.

## Severity levels

```text
INFO      = useful context; does not block work
WARN      = should be fixed or recorded before closeout
BLOCKER   = must be fixed or explicitly waived before merge/closeout
```

Examples:

```text
INFO: open enhancement issue exists for next feature
WARN: superseded PR remains open
WARN: status file may be stale
BLOCKER: verification fails
BLOCKER: HyperKanban packet drift
BLOCKER: done card lacks required evidence
```

## Human approval boundaries

Cleanup agents may propose:

- closing superseded PRs,
- archiving import files,
- deleting stale branches,
- updating status docs,
- adding cleanup issues.

Cleanup agents must not silently:

- delete branches with ambiguous ownership,
- remove files that may be needed for audit/history,
- close high-risk review cards,
- alter protected branches,
- rewrite Chronicle events,
- bypass human approval gates.

## Relationship to high-concurrency work

High-concurrency work depends on cleanup.

Before many agents start, cleanup establishes the current truth:

```text
which PRs are active
which PRs are superseded
which cards are blocked
which branches are safe bases
which artifacts are synchronized
```

After many agents finish, cleanup prevents swarm residue:

```text
orphan branches
obsolete PRs
stale packets
duplicate cards
unclear review obligations
```

## Recommended workflow

```sh
python scripts/repo_cleanup.py --phase before
bash scripts/verify.sh
# perform scoped work
bash scripts/verify.sh
python scripts/repo_cleanup.py --phase after
```

If cleanup finds a blocker, stop and resolve it or create a review card / issue describing why it remains unresolved.
