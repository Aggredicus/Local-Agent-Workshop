# /close-issue

Use this skill before closing a GitHub issue, marking an issue as completed, marking an issue as not planned, or deciding that an issue should remain open.

The goal is to prevent premature closure by making issue closeout evidence-linked, acceptance-criteria-driven, and human-governed at risk boundaries.

## Core rule

```text
close only with evidence
merged PR is not enough
acceptance criteria must be checked
non-goals must be preserved
epics wait for child status
human-gated work needs human review
leave a closure packet
use compact public comments when needed
prefer minimal close mutations after evidence is posted
capture reusable friction for /improve-skill
```

## When to use

Use `/close-issue`:

- after a PR claims to implement an issue,
- after a docs-only or cleanup PR merges,
- before closing stale or superseded issues,
- before marking an issue `completed`, `not_planned`, or `duplicate`,
- during `/generate-issue closeout-check`,
- during `/cleanup closeout`,
- before closing parent epics,
- whenever issue state, PR state, evidence, labels, or dashboard projections disagree.

## Non-goals

This skill does not:

- close issues merely because a PR merged,
- close parent epics while child issues remain unresolved,
- bypass `/merge-review`, `/quality-analysis`, cleanup closeout, CI, or human approval,
- authorize closure of medium-risk or high-risk work without review,
- treat HyperKanban, dashboards, generated reports, or model prose as source-of-truth by themselves,
- mutate protected branches, secrets, infrastructure, public endpoints, Proxmox runtime, or generated source-of-truth status,
- replace human judgment for governance, security, release, schema, script, CI, infrastructure, or source-of-truth changes.

## Inputs

Collect:

- repository name,
- target issue number,
- issue title and body,
- issue labels and milestone,
- acceptance criteria,
- non-goals,
- stop conditions,
- linked PRs and their merge state,
- PR bodies and changed files,
- CI/workflow state when available,
- review state and unresolved review comments when available,
- linked child issues or parent epic relationship,
- linked duplicate/superseding issue if any,
- evidence paths listed in PRs, comments, review cards, reports, or issue body,
- cleanup and quality-analysis evidence when available,
- risk level and human-review boundaries,
- any tool-layer failure or friction from the closeout attempt.

## Inspection checklist

For each issue, inspect:

1. **Issue state** — open, closed, duplicate, superseded, or already resolved.
2. **Issue type** — normal issue, parent epic, duplicate, abandoned idea, cleanup item, or follow-up.
3. **Acceptance criteria** — every checkbox or explicit requirement is satisfied, intentionally deferred, or still open.
4. **Outputs** — files, docs, schemas, scripts, reports, or artifacts named by the issue exist or were intentionally deferred.
5. **Evidence** — tests, validation, CI, reports, review cards, or explicit comments support completion.
6. **Linked PRs** — implementation PRs are merged, intentionally abandoned, or not required.
7. **CI and validation** — relevant checks passed or skipped checks are explained.
8. **Review state** — requested changes and unresolved review threads are absent or explicitly handled.
9. **Non-goals** — implementation did not violate the issue boundary.
10. **Stop conditions** — no unresolved stop condition remains.
11. **Risk** — medium/high-risk closure has human review or explicit approval where required.
12. **Children** — child issues of an epic are complete, superseded, duplicate, or explicitly deferred.
13. **Status drift** — docs, labels, dashboard, HyperKanban, and issue body do not conflict in a way that affects closure.
14. **Tool safety** — closeout evidence can be posted in a compact, safe form before mutation.

## Closure states

Use one of these verdicts.

| Verdict | Meaning |
|---|---|
| `ready_to_close_completed` | Acceptance criteria are satisfied, evidence exists, linked PRs are merged or unnecessary, and no stop condition remains. |
| `ready_to_close_not_planned` | The issue should be closed as not planned because the work is intentionally deferred, rejected, obsolete, out of scope, or no longer valuable. |
| `ready_to_close_duplicate` | The issue duplicates another issue or PR and the canonical successor is linked. |
| `needs_evidence` | Work may be complete, but evidence is missing, vague, stale, or not linked. |
| `needs_review` | Review, human approval, CI, or requested-change resolution is missing. |
| `blocked` | A dependency, child issue, failed check, unresolved comment, or risk boundary blocks closure. |
| `epic_wait` | A parent issue or epic still has unresolved children or incomplete closeout evidence. |
| `do_not_close` | Closure would hide active work, violate policy, erase audit value, bypass human approval, or falsely claim completion. |

## GitHub state reason guidance

Use GitHub closure state reasons carefully:

| State reason | Use when |
|---|---|
| `completed` | The issue acceptance criteria are satisfied and evidence is linked. |
| `not_planned` | The issue is intentionally not being pursued, is obsolete, out of scope, or safely deferred. |
| `duplicate` | The issue duplicates another issue and the canonical issue is linked. |
| leave open | Evidence, review, CI, dependency, child issue, or risk-boundary questions remain. |

Do not use `completed` just because a PR merged.

When using a tool to close an issue, prefer the minimal safe mutation after evidence has already been posted. If an optional `state_reason` field causes the close action to fail, retry only after confirming the evidence comment exists, and use the smallest supported close payload.

## Parent epic rules

For parent epics:

1. List every child issue mentioned in the body, checklist, comments, or linked PRs.
2. Check each child state and evidence.
3. Close the epic only when children are complete, duplicate, superseded, or explicitly deferred with a reason.
4. If a child is still active, use `epic_wait`.
5. If the epic goal changed, create or link a successor before closing as `not_planned` or `superseded`.

## Acceptance criteria rules

Before `ready_to_close_completed`, answer:

```text
For each acceptance criterion:
  status: satisfied | deferred | not satisfied | unclear
  evidence: PR, file path, report, CI run, comment, or review card
  notes: why this satisfies the issue
```

If any criterion is `not satisfied` or `unclear`, the issue is not ready to close unless a human explicitly approves narrowing, deferring, or closing as not planned.

## Evidence requirements

Good evidence includes:

- merged PR number,
- changed files,
- successful CI or validation run,
- relevant report path,
- review card or PR body summary,
- explicit comment explaining intentionally skipped work,
- successor issue for deferred or superseded work,
- duplicate issue link when closing as duplicate.

Weak evidence includes:

- “looks done,”
- dashboard says done,
- model says done,
- one PR merged but acceptance criteria were not checked,
- no link to the changed files or checks,
- stale status docs without current PR/CI evidence.

Weak evidence should produce `needs_evidence`, not closure.

## Closure packet

Before closing, leave or prepare a closure packet in the issue or PR handoff.

```text
/close-issue packet
repo:
issue:
title:
reviewed_at:
reviewer:
issue_type:
linked_prs:
linked_children:
risk_level:
acceptance_criteria:
  - criterion:
    status:
    evidence:
non_goals_checked:
stop_conditions_checked:
ci_or_validation:
review_state:
cleanup_or_quality_evidence:
closure_verdict:
state_reason:
blockers:
follow_up_issues:
human_decision_needed:
```

## Tool-safe closure comments

A full closure packet is preferred, but tool layers or public issue threads may reject or poorly display long structured comments. If that happens:

1. Keep the full packet in the PR body, review card, handoff note, or local report when available.
2. Post a compact public closeout comment that includes only the essential proof:

```text
Closeout: PR #NN merged; evidence checked; acceptance criteria satisfied; CI passed or skipped with reason; verdict ready_to_close_completed; blockers none.
```

3. Avoid repeatedly submitting large failing comments.
4. Do not close the issue until at least a compact evidence comment is posted or the failure is documented in a handoff.
5. If even the compact comment fails, leave the issue open and create a handoff.

## Safe closure flow

1. Read `me.md` and the target issue.
2. Collect linked PRs, comments, children, and evidence.
3. Check acceptance criteria one by one.
4. Check non-goals and stop conditions.
5. Check CI, review state, and human approval boundaries.
6. For epics, check child issue status.
7. Produce a closure packet.
8. Post the full packet, or use the compact comment fallback if the full packet is blocked.
9. Close only when the verdict supports closure and evidence has been posted or safely handed off.
10. Use the correct state reason when supported.
11. If an optional close field fails, retry with a minimal close mutation only after evidence is posted.
12. Leave the issue open if evidence or review is incomplete.
13. Record reusable closeout friction as a future `/improve-skill` follow-up.

## Stop conditions

Stop and create a handoff instead of closing if:

- acceptance criteria are missing, ambiguous, unchecked, or partially satisfied,
- evidence cannot be found,
- linked PRs are open, draft, failed, conflicted, or not merged,
- CI status is missing for code, schema, script, CI, validation, or runtime changes,
- requested changes or unresolved review threads remain,
- child issues are unresolved,
- the issue affects governance, security, schemas, scripts, source code, CI/workflows, Proxmox/local infrastructure, public endpoints, migrations, source-of-truth promotions, or merge policy without human review,
- closure would hide known follow-up work,
- issue body and implementation disagree,
- state reason is unclear,
- the evidence comment cannot be posted and no handoff captures the closure packet.

## Improvement hook

At the end of every `/close-issue` run, ask:

```text
Did this closeout reveal a reusable failure mode, ambiguity, tool friction, missing checklist item, or governance boundary?
```

If yes, create or recommend a small `/improve-skill` follow-up. Prefer a docs-only patch to this skill unless the lesson requires a script, schema, or governance change.

## Good close-issue behavior

A good `/close-issue` run should not merely say “done.” It should say:

- what was checked,
- what evidence proves completion,
- which acceptance criteria are satisfied,
- what was intentionally deferred,
- what risks remain,
- which state reason is appropriate,
- whether human approval is needed,
- whether the issue should close now or remain open,
- and whether the run produced a reusable lesson for `/improve-skill`.
