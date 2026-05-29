# /repo-cleanup

Use this skill before and after meaningful repository work.

The goal is to keep Local Agent Workshop clean, reviewable, resumable, and safe for multi-agent concurrency.

## When to use

Use `/repo-cleanup`:

- before starting a new implementation branch,
- before running a long autonomous grind,
- before opening a PR,
- after merging or closing PRs,
- after stacked PR delivery,
- before beginning high-concurrency/multi-agent work,
- when stale PRs, branches, packets, review cards, or status docs may exist.

## Core rule

```text
clean before work
work in a bounded branch
clean after work
leave evidence
```

## Preflight checklist

Before work:

1. Read `me.md`.
2. Read `docs/protocols/REPOSITORY_CLEANUP_PROTOCOL.md`.
3. Confirm target branch and branch protection rules.
4. Check open PRs for stale or superseded work.
5. Confirm the intended card/issue is not already owned.
6. Run:

```sh
python scripts/repo_cleanup.py --phase before
```

7. Run verification if practical:

```sh
bash scripts/verify.sh
```

8. Record blockers before editing.

## Closeout checklist

After work:

1. Run local verification:

```sh
bash scripts/verify.sh
```

2. Run:

```sh
python scripts/repo_cleanup.py --phase after
```

3. Confirm generated state is synchronized.
4. Confirm PR body includes evidence, risks, and next steps.
5. Close or mark superseded PRs only with clear evidence and human-safe reasoning.
6. Create a follow-up issue for unresolved cleanup.

## Script behavior

`repo_cleanup.py` is intentionally non-destructive.

It may report:

- INFO items,
- WARN items,
- BLOCKER items.

It must not delete branches, close PRs, rewrite events, or mutate protected branches.

## Escalation

Stop and request review if cleanup finds:

- failing verification,
- HyperKanban packet drift,
- done cards without evidence,
- high-risk work without review gate,
- ambiguous stale branches,
- conflicting active work,
- or anything requiring protected-branch changes.

## Output expectation

A good cleanup run should leave a short trace in the PR body or review card:

```text
Cleanup before: passed with 0 blockers, 1 warning.
Cleanup after: passed with 0 blockers.
Verification: passed.
Follow-up: #NN for non-blocking cleanup.
```
