# /close-issue

Use this skill before closing a GitHub issue, marking an issue as completed, marking an issue as not planned, or deciding that an issue should remain open.

The goal is to prevent premature closure by making issue closeout evidence-linked, acceptance-criteria-driven, requirement-mapped, and human-governed at risk boundaries.

## Core rule

```text
close only with evidence
merged PR is not enough
CI is not enough
acceptance criteria must be checked
requirements must map to proof
non-goals must be proven preserved
epics wait for child status
human-gated work needs human review
leave a public closure packet or compact public evidence comment
private handoff is not enough to close
use compact public comments when needed
prefer minimal close mutations after public evidence is posted
if close mutation is blocked, leave blocked-close handoff
create a follow-up improvement issue after every skill use
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
- close issues merely because CI passed,
- close parent epics while child issues remain unresolved,
- bypass `/merge-review`, `/quality-analysis`, cleanup closeout, CI, or human approval,
- authorize closure of medium-risk or high-risk work without review,
- treat HyperKanban, dashboards, generated reports, or model prose as source-of-truth by themselves,
- mutate protected branches or generated source-of-truth status,
- replace human judgment for governance, release, schema, script, CI, or source-of-truth changes.

## Inputs

Collect:

- repository name,
- target issue number,
- issue title and body,
- issue labels and milestone,
- acceptance criteria,
- derived requirements when explicit criteria are missing,
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
3. **Definition of done** — explicit acceptance criteria exist, or a temporary definition of done is derived from the issue and linked artifacts.
4. **Satisfaction matrix** — every requirement has a row mapping source, proof, verification, status, and notes.
5. **Outputs** — files, docs, schemas, scripts, reports, or artifacts named by the issue exist or were intentionally deferred.
6. **Evidence** — tests, validation, CI, reports, review cards, or explicit comments support completion.
7. **Linked PRs** — implementation PRs are merged, intentionally abandoned, or not required.
8. **CI and validation** — relevant checks passed or skipped checks are explained.
9. **Review state** — requested changes and unresolved review threads are absent or explicitly handled.
10. **Non-goals** — implementation did not violate the issue boundary.
11. **Scope preservation** — forbidden paths and human-review boundaries were preserved.
12. **Stop conditions** — no unresolved stop condition remains.
13. **Risk** — medium/high-risk closure has human review or explicit approval where required.
14. **Children** — child issues of an epic are complete, superseded, duplicate, or explicitly deferred.
15. **Status drift** — docs, labels, dashboard, HyperKanban, and issue body do not conflict in a way that affects closure.
16. **Tool safety** — closeout evidence can be posted in a compact, safe form before mutation.
17. **Close mutation result** — if public evidence is posted but close mutation fails, record `blocked_close_mutation` instead of pretending closure succeeded.

## Closure states

Use one of these verdicts.

| Verdict | Meaning |
|---|---|
| `ready_to_close_completed` | Each requirement has a satisfied or explicitly deferred satisfaction row, evidence exists, linked PRs are merged or unnecessary, scope preservation is checked, public closeout evidence is posted, and no stop condition remains. |
| `ready_to_close_not_planned` | The issue should be closed as not planned because the work is intentionally deferred, rejected, obsolete, out of scope, or no longer valuable. |
| `ready_to_close_duplicate` | The issue duplicates another issue or PR and the canonical successor is linked. |
| `blocked_close_mutation` | Public closeout evidence is posted and closure is justified, but the GitHub close mutation failed or was blocked. Leave the issue open, create/keep a follow-up issue, and report the exact blocked state. |
| `needs_satisfaction_matrix` | Evidence may exist, but requirements have not been mapped to proof row by row. |
| `needs_evidence` | Work may be complete, but evidence is missing, vague, stale, or not linked. |
| `needs_review` | Review, human approval, CI, requested-change resolution, or definition-of-done clarification is missing. |
| `blocked` | A dependency, child issue, failed check, unresolved comment, or risk boundary blocks closure. |
| `epic_wait` | A parent issue or epic still has unresolved children or incomplete closeout evidence. |
| `do_not_close` | Closure would hide active work, violate policy, erase audit value, bypass human approval, or falsely claim completion. |

## GitHub state reason guidance

Use GitHub closure state reasons carefully:

| State reason | Use when |
|---|---|
| `completed` | The issue requirements are satisfied, the satisfaction matrix is complete, public closeout evidence is posted, and evidence is linked. |
| `not_planned` | The issue is intentionally not being pursued, is obsolete, out of scope, or safely deferred. |
| `duplicate` | The issue duplicates another issue and the canonical issue is linked. |
| leave open | Evidence, review, CI, dependency, child issue, satisfaction matrix, public closeout evidence, risk-boundary questions, or blocked close mutation remain. |

Do not use `completed` just because a PR merged or CI passed.

When using a tool to close an issue, prefer the minimal safe mutation after public evidence has already been posted. If an optional `state_reason` field causes the close action to fail, retry only after confirming the evidence comment exists, and use the smallest supported close payload. If the smallest supported close payload also fails, use `blocked_close_mutation` and stop retrying.

## Parent epic rules

For parent epics:

1. List every child issue mentioned in the body, checklist, comments, or linked PRs.
2. Check each child state and evidence.
3. Close the epic only when children are complete, duplicate, superseded, or explicitly deferred with a reason.
4. If a child is still active, use `epic_wait`.
5. If the epic goal changed, create or link a successor before closing as `not_planned` or `superseded`.

## Definition of done recovery

If an issue lacks explicit checkbox-style acceptance criteria, recover a temporary definition of done before evaluating closure.

Derive requirements from:

- issue title,
- issue summary/body,
- requested outputs,
- non-goals,
- stop conditions,
- linked PR body,
- linked comments,
- linked child issues,
- referenced files or paths.

If the recovered definition of done is ambiguous, incomplete, or controversial, do not close. Use `needs_satisfaction_matrix` when rows are missing, or `needs_review` when human clarification is required.

## Satisfaction matrix

Before `ready_to_close_completed`, produce a satisfaction matrix. Every explicit acceptance criterion must have its own row. If acceptance criteria are implicit, every recovered requirement must have its own row.

```text
requirement:
source:
implementation_proof:
validation_proof:
scope_proof:
risk_proof:
status: satisfied | deferred | not satisfied | unclear
notes:
```

If any row is `not satisfied` or `unclear`, the issue is not ready to close unless a human explicitly approves narrowing, deferring, or closing as not planned.

## Scope-preservation proof

Authentic satisfaction requires proving the PR did not violate the issue boundary.

Before closure, check:

```text
non_goals_preserved:
forbidden_paths_untouched:
human_gated_boundaries_preserved:
parent_child_status_checked:
generated_projections_not_source_of_truth:
hidden_followups_not_buried:
```

For docs-only issues, this can be brief. For schema, script, source, CI, or governance-related issues, it must be explicit and evidence-linked.

## Evidence requirements

Good evidence includes:

- satisfaction matrix rows,
- merged PR number,
- changed files,
- successful CI or validation run,
- relevant report path,
- review card or PR body summary,
- explicit public comment explaining intentionally skipped work,
- successor issue for deferred or superseded work,
- duplicate issue link when closing as duplicate.

Weak evidence includes:

- “looks done,”
- dashboard says done,
- model says done,
- one PR merged but requirements were not checked,
- CI passed but requirements were not mapped,
- no link to the changed files or checks,
- private handoff without public issue-thread evidence,
- stale status docs without current PR/CI evidence.

Weak evidence should produce `needs_satisfaction_matrix` or `needs_evidence`, not closure.

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
definition_of_done:
satisfaction_matrix:
  - requirement:
    source:
    implementation_proof:
    validation_proof:
    scope_proof:
    risk_proof:
    status:
scope_preservation:
non_goals_checked:
stop_conditions_checked:
ci_or_validation:
review_state:
cleanup_or_quality_evidence:
close_mutation_result:
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
Closeout: PR #NN merged; satisfaction matrix checked; requirements satisfied; CI passed or skipped with reason; scope preserved; verdict ready_to_close_completed; blockers none.
```

3. Avoid repeatedly submitting large failing comments.
4. Do not close the issue until at least a compact public evidence comment is posted.
5. If even the compact comment fails, leave the issue open and create a handoff.
6. A private handoff may preserve context, but it must not substitute for public issue-thread evidence when closing.

## Safe closure flow

1. Read `me.md` and the target issue.
2. Collect linked PRs, comments, children, and evidence.
3. Recover a definition of done if explicit acceptance criteria are missing.
4. Build a satisfaction matrix row for every explicit or recovered requirement.
5. Check non-goals, scope preservation, and stop conditions.
6. Check CI, review state, and human approval boundaries.
7. For epics, check child issue status.
8. Produce a closure packet.
9. Post the full packet, or use the compact public comment fallback if the full packet is blocked.
10. Close only when the verdict supports closure and public issue-thread evidence has been posted.
11. Use the correct state reason when supported.
12. If an optional close field fails, retry with a minimal close mutation only after public evidence is posted.
13. If the minimal close mutation fails, record `blocked_close_mutation`, leave the issue open, and stop retrying.
14. Leave the issue open if evidence, satisfaction matrix, scope preservation, public closeout comment, review, or close mutation is incomplete.
15. Create a follow-up improvement issue for `/close-issue` after every run, unless the recursion breaker in `skills/README.md` applies.

## Stop conditions

Stop and create a handoff instead of closing if:

- acceptance criteria are missing, ambiguous, unchecked, or partially satisfied,
- recovered definition of done is ambiguous,
- satisfaction matrix is missing or incomplete,
- any satisfaction row is `not satisfied` or `unclear`,
- evidence cannot be found,
- linked PRs are open, draft, failed, conflicted, or not merged,
- CI status is missing for code, schema, script, CI, validation, or runtime changes,
- requested changes or unresolved review threads remain,
- child issues are unresolved,
- scope preservation cannot be established,
- the issue affects governance, schemas, scripts, source code, CI/workflows, source-of-truth promotions, or merge policy without human review,
- closure would hide known follow-up work,
- issue body and implementation disagree,
- state reason is unclear,
- public evidence comment cannot be posted,
- close mutation is blocked after public evidence is posted.

## Mandatory improvement issue

At the end of every `/close-issue` run, create a follow-up improvement issue for `/close-issue`.

The issue may be tiny and may record `no change recommended`, but it must exist. This creates an audit trail for every skill invocation and lets the repository decide whether the lesson is actionable.

Use the global `skills/README.md` protocol for the improvement issue format. Apply the recursion breaker only for terminal no-change improvement issues as defined there.

## Good close-issue behavior

A good `/close-issue` run should not merely say “done.” It should say:

- what was checked,
- how the definition of done was identified or recovered,
- how each requirement maps to proof,
- what evidence proves completion,
- which requirements are satisfied,
- what was intentionally deferred,
- what scope-preservation proof was checked,
- what risks remain,
- which state reason is appropriate,
- whether human approval is needed,
- whether the issue should close now or remain open,
- what happened when the close mutation was attempted,
- and which mandatory follow-up improvement issue was created for `/close-issue`.
