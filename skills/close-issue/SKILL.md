# /close-issue

Use this skill before closing a GitHub issue, marking an issue as completed, marking an issue as not planned, or deciding that an issue should remain open.

The goal is to prevent premature closure by making issue closeout evidence-linked, acceptance-criteria-driven, requirement-mapped, checklist-aware, output-aware, and human-governed at risk boundaries.

## Core rule

```text
close only with evidence
merged PR is not enough
CI is not enough
all checkboxes must be accounted for
all stated outputs must be accounted for
acceptance criteria must be checked
requirements must map to proof
non-goals must be proven preserved
epics require child and remaining-work proof
incomplete work needs successor tracking before closure
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
- close issues merely because one slice of a larger epic landed,
- close parent epics while child issues or issue-body tasks remain unresolved,
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
- explicit acceptance criteria,
- every checklist item in the issue body,
- every stated output/file/artifact/report/schema/script/workflow requested by the issue body,
- derived requirements when explicit criteria are missing,
- non-goals,
- stop conditions,
- linked PRs and their merge state,
- PR bodies and changed files,
- CI/workflow state when available,
- review state and unresolved review comments when available,
- linked child issues or parent epic relationship,
- linked duplicate/superseding issue if any,
- successor issue for incomplete, deferred, or carried-forward work,
- evidence paths listed in PRs, comments, review cards, reports, or issue body,
- cleanup and quality-analysis evidence when available,
- risk level and human-review boundaries,
- any tool-layer failure or friction from the closeout attempt.

## Hard pre-close completion gate

Before any issue can receive `ready_to_close_completed`, build a completion inventory from the issue body.

The inventory must include:

```text
unchecked_checkboxes:
checked_checkboxes:
stated_outputs:
missing_outputs:
explicit_acceptance_criteria:
unsatisfied_acceptance_criteria:
child_issues:
unresolved_child_issues:
remaining_work:
successor_issues:
```

Rules:

1. Every unchecked checkbox must become either `satisfied`, `deferred_with_successor`, `superseded_with_successor`, `not_applicable_with_reason`, or `not_satisfied`.
2. Every stated output must have implementation proof or an explicit successor issue.
3. Every acceptance criterion must have a satisfaction-matrix row.
4. Every child issue or referenced subtask must be complete, duplicate, superseded, explicitly deferred, or tracked by a successor issue.
5. Any remaining work hidden inside prose counts as `remaining_work` even if it is not written as a checkbox.
6. `ready_to_close_completed` is forbidden when any row is `not_satisfied`, `unclear`, or lacks proof.
7. `ready_to_close_completed` is forbidden when remaining work exists but no successor issue is linked.
8. For epics, landing one implementation slice is not enough. The epic can close as completed only when the whole epic inventory is complete.

If this gate fails, use `premature_closure_risk`, `epic_wait`, `needs_satisfaction_matrix`, or `needs_review`.

## Inspection checklist

For each issue, inspect:

1. **Issue state** — open, closed, duplicate, superseded, or already resolved.
2. **Issue type** — normal issue, parent epic, duplicate, abandoned idea, cleanup item, or follow-up.
3. **Completion inventory** — checkboxes, acceptance criteria, outputs, children, and remaining prose work are accounted for.
4. **Definition of done** — explicit acceptance criteria exist, or a temporary definition of done is derived from the issue and linked artifacts.
5. **Satisfaction matrix** — every requirement has a row mapping source, proof, verification, status, and notes.
6. **Outputs** — files, docs, schemas, scripts, reports, workflows, or artifacts named by the issue exist or are intentionally carried forward by successor issue.
7. **Evidence** — tests, validation, CI, reports, review cards, or explicit comments support completion.
8. **Linked PRs** — implementation PRs are merged, intentionally abandoned, or not required.
9. **CI and validation** — relevant checks passed or skipped checks are explained.
10. **Review state** — requested changes and unresolved review threads are absent or explicitly handled.
11. **Non-goals** — implementation did not violate the issue boundary.
12. **Scope preservation** — forbidden paths and human-review boundaries were preserved.
13. **Stop conditions** — no unresolved stop condition remains.
14. **Risk** — medium/high-risk closure has human review or explicit approval where required.
15. **Children** — child issues of an epic are complete, superseded, duplicate, or explicitly deferred with successor tracking.
16. **Status drift** — docs, labels, dashboard, HyperKanban, and issue body do not conflict in a way that affects closure.
17. **Tool safety** — closeout evidence can be posted in a compact, safe form before mutation.
18. **Close mutation result** — if public evidence is posted but close mutation fails, record `blocked_close_mutation` instead of pretending closure succeeded.

## Closure states

Use one of these verdicts.

| Verdict | Meaning |
|---|---|
| `ready_to_close_completed` | Completion inventory has no unresolved checkboxes, outputs, acceptance criteria, children, or hidden remaining work; each requirement has a satisfied or explicitly deferred satisfaction row; successor issues exist for any carried-forward work; evidence exists; linked PRs are merged or unnecessary; scope preservation is checked; public closeout evidence is posted; and no stop condition remains. |
| `ready_to_close_not_planned` | The issue should be closed as not planned because the work is intentionally deferred, rejected, obsolete, out of scope, or no longer valuable, and any important remaining work is explicitly carried forward or rejected with public rationale. |
| `ready_to_close_duplicate` | The issue duplicates another issue or PR and the canonical successor is linked. |
| `premature_closure_risk` | The issue appears closable at a glance, but unchecked requirements, missing outputs, incomplete child work, hidden remaining work, or missing successor tracking would make closure misleading. Do not close. |
| `blocked_close_mutation` | Public closeout evidence is posted and closure is justified, but the GitHub close mutation failed or was blocked. Leave the issue open, create/keep a follow-up issue, and report the exact blocked state. |
| `needs_satisfaction_matrix` | Evidence may exist, but requirements have not been mapped to proof row by row. |
| `needs_evidence` | Work may be complete, but evidence is missing, vague, stale, or not linked. |
| `needs_review` | Review, human approval, CI, requested-change resolution, or definition-of-done clarification is missing. |
| `blocked` | A dependency, child issue, failed check, unresolved comment, or risk boundary blocks closure. |
| `epic_wait` | A parent issue or epic still has unresolved children, unchecked issue-body work, missing outputs, or incomplete closeout evidence. |
| `do_not_close` | Closure would hide active work, violate policy, erase audit value, bypass human approval, or falsely claim completion. |

## GitHub state reason guidance

Use GitHub closure state reasons carefully:

| State reason | Use when |
|---|---|
| `completed` | The issue requirements are satisfied, the completion inventory is clean, the satisfaction matrix is complete, public closeout evidence is posted, and evidence is linked. |
| `not_planned` | The issue is intentionally not being pursued, is obsolete, out of scope, or safely deferred with public rationale and successor tracking when needed. |
| `duplicate` | The issue duplicates another issue and the canonical issue is linked. |
| leave open | Evidence, review, CI, dependency, child issue, completion inventory, satisfaction matrix, public closeout evidence, risk-boundary questions, or blocked close mutation remain. |

Do not use `completed` just because a PR merged or CI passed.

Do not use `completed` when the issue body still has unchecked acceptance criteria, unchecked task boxes, missing requested outputs, unresolved child issues, or untracked remaining work.

When using a tool to close an issue, prefer the minimal safe mutation after public evidence has already been posted. If an optional `state_reason` field causes the close action to fail, retry only after confirming the evidence comment exists, and use the smallest supported close payload. If the smallest supported close payload also fails, use `blocked_close_mutation` and stop retrying.

## Parent epic rules

For parent epics:

1. List every child issue mentioned in the body, checklist, comments, PRs, or issue relationships.
2. List every unchecked checkbox and every output named in the epic body.
3. Check each child state and evidence.
4. Check whether every epic-level output exists or has successor tracking.
5. Close the epic as completed only when children, checklist items, outputs, and acceptance criteria are complete.
6. If only one slice merged, keep the epic open or create a replacement epic before closing the original.
7. If a child is still active, use `epic_wait`.
8. If the epic goal changed, create or link a successor before closing as `not_planned` or `superseded`.
9. If an epic was previously closed while work remained, create a governance correction issue and do not treat the old epic as complete.

## Definition of done recovery

If an issue lacks explicit checkbox-style acceptance criteria, recover a temporary definition of done before evaluating closure.

Derive requirements from:

- issue title,
- issue summary/body,
- task checklists,
- requested outputs,
- file lists,
- non-goals,
- stop conditions,
- linked PR body,
- linked comments,
- linked child issues,
- referenced files or paths.

If the recovered definition of done is ambiguous, incomplete, or controversial, do not close. Use `needs_satisfaction_matrix`, `premature_closure_risk`, or `needs_review`.

## Satisfaction matrix

Before `ready_to_close_completed`, produce a satisfaction matrix. Every explicit acceptance criterion must have its own row. If acceptance criteria are implicit, every recovered requirement, stated output, and issue-body checkbox must have its own row.

```text
requirement:
source:
implementation_proof:
validation_proof:
scope_proof:
risk_proof:
status: satisfied | deferred_with_successor | superseded_with_successor | not_applicable_with_reason | not_satisfied | unclear
successor_issue:
notes:
```

If any row is `not_satisfied` or `unclear`, the issue is not ready to close as completed.

If any row is `deferred_with_successor` or `superseded_with_successor`, the successor issue must be linked before closure.

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

For docs-only issues, this can be brief. For schema, script, source, CI, workflow, or governance-related issues, it must be explicit and evidence-linked.

## Evidence requirements

Good evidence includes:

- completion inventory,
- satisfaction matrix rows,
- merged PR number,
- changed files,
- successful CI or validation run,
- relevant report path,
- review card or PR body summary,
- explicit public comment explaining intentionally skipped work,
- successor issue for deferred, superseded, or remaining work,
- duplicate issue link when closing as duplicate.

Weak evidence includes:

- “looks done,”
- dashboard says done,
- model says done,
- one PR merged but requirements were not checked,
- CI passed but requirements were not mapped,
- no link to the changed files or checks,
- private handoff without public issue-thread evidence,
- stale status docs without current PR/CI evidence,
- unchecked issue-body tasks ignored,
- missing requested outputs ignored,
- closing an epic after a single slice merged.

Weak evidence should produce `premature_closure_risk`, `needs_satisfaction_matrix`, or `needs_evidence`, not closure.

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
completion_inventory:
  unchecked_checkboxes:
  stated_outputs:
  missing_outputs:
  unsatisfied_acceptance_criteria:
  unresolved_child_issues:
  remaining_work:
  successor_issues:
definition_of_done:
satisfaction_matrix:
  - requirement:
    source:
    implementation_proof:
    validation_proof:
    scope_proof:
    risk_proof:
    status:
    successor_issue:
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
Closeout: PR #NN merged; completion inventory checked; satisfaction matrix checked; requirements satisfied; CI passed or skipped with reason; scope preserved; successor issues linked where needed; verdict ready_to_close_completed; blockers none.
```

3. Avoid repeatedly submitting large failing comments.
4. Do not close the issue until at least a compact public evidence comment is posted.
5. If even the compact comment fails, leave the issue open and create a handoff.
6. A private handoff may preserve context, but it must not substitute for public issue-thread evidence when closing.

## Safe closure flow

1. Read `me.md`, `skills/README.md`, and the target issue.
2. Collect linked PRs, comments, children, and evidence.
3. Build the hard completion inventory from checkboxes, requested outputs, acceptance criteria, child issues, and prose work.
4. Recover a definition of done if explicit acceptance criteria are missing.
5. Build a satisfaction matrix row for every explicit or recovered requirement.
6. Check non-goals, scope preservation, and stop conditions.
7. Check CI, review state, and human approval boundaries.
8. For epics, check child issue status and remaining epic-level work.
9. If remaining work exists, require successor tracking before any non-completed closure.
10. Produce a closure packet.
11. Post the full packet, or use the compact public comment fallback if the full packet is blocked.
12. Close only when the verdict supports closure and public issue-thread evidence has been posted.
13. Use the correct state reason when supported.
14. If an optional close field fails, retry with a minimal close mutation only after public evidence is posted.
15. If the minimal close mutation fails, record `blocked_close_mutation`, leave the issue open, and stop retrying.
16. Leave the issue open if evidence, completion inventory, satisfaction matrix, scope preservation, public closeout comment, review, successor tracking, or close mutation is incomplete.
17. Create a follow-up improvement issue for `/close-issue` after every run, unless the recursion breaker in `skills/README.md` applies.

## Stop conditions

Stop and create a handoff instead of closing if:

- acceptance criteria are missing, ambiguous, unchecked, or partially satisfied,
- any issue-body checkbox remains unchecked without status and proof,
- any stated output is missing without successor tracking,
- recovered definition of done is ambiguous,
- completion inventory is missing or incomplete,
- satisfaction matrix is missing or incomplete,
- any satisfaction row is `not_satisfied` or `unclear`,
- remaining work exists without successor issue,
- evidence cannot be found,
- linked PRs are open, draft, failed, conflicted, or not merged,
- CI status is missing for code, schema, script, CI, validation, workflow, or runtime changes,
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
- what issue-body checkboxes and outputs were inventoried,
- whether any unchecked or missing work remains,
- how the definition of done was identified or recovered,
- how each requirement maps to proof,
- what evidence proves completion,
- which requirements are satisfied,
- what was intentionally deferred and where it is tracked,
- what scope-preservation proof was checked,
- what risks remain,
- which state reason is appropriate,
- whether human approval is needed,
- whether the issue should close now or remain open,
- what happened when the close mutation was attempted,
- and which mandatory follow-up improvement issue was created for `/close-issue`.
