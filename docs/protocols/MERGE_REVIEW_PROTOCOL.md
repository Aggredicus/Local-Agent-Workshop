# Merge Review Protocol

The merge review protocol defines how Local Agent Workshop evaluates PRs and PR stacks before human approval or merge.

It complements the branch policy, human approval boundaries, review workflow, cleanup protocol, and publish protocol.

## Principle

Merging is a protected decision point.

Agents may inspect, summarize, recommend, and prepare evidence, but they must not merge or approve high-risk changes without explicit human authorization.

When merge is authorized, prefer the smallest normal merge action supported by the tool.

## Relationship to other policies

Read alongside:

- `me.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/governance/HUMAN_APPROVAL_BOUNDARIES.md`
- `docs/governance/RISK_POLICY.md`
- `docs/protocols/REVIEW_WORKFLOW.md`
- `docs/protocols/PUBLISH_PROTOCOL.md`
- `skills/merge-review/SKILL.md`

## Review states

| State | Meaning |
|---|---|
| `ready_for_human_approval` | Evidence and checks are sufficient for a human to decide. |
| `needs_ci` | CI or verification is missing, failed, or pending. |
| `needs_review` | Human review or requested reviewer response is missing. |
| `blocked` | Dependency, stack order, conflict, requested changes, or evidence problem blocks merge. |
| `do_not_merge` | Safety, authority, or branch policy boundary is violated. |
| `stack_wait` | PR is acceptable only after an earlier stacked PR merges and the branch is retargeted/rechecked. |

## Required checks

A merge-review should inspect:

1. PR title and body.
2. Linked issue or reason for no linked issue.
3. Base and head branches.
4. Draft/open/closed/merged state.
5. Mergeability.
6. Changed files.
7. CI or workflow runs when available.
8. Review submissions and requested reviewers when available.
9. Evidence paths and skipped checks.
10. Risk notes and non-goals.
11. Stack order and dependency PRs.

## Stacked PR protocol

For a stack such as:

```text
PR A → PR B → PR C
```

Use this process:

1. Review PR A against its base branch.
2. Review PR B against PR A's branch.
3. Review PR C against PR B's branch.
4. Mark PR B and PR C as `stack_wait` until their bases merge.
5. After PR A merges, retarget PR B to the new integration branch.
6. Re-check CI, mergeability, and diff shape.
7. Repeat for the rest of the stack.

## Merge gates

Do not recommend merge if:

- the PR is draft,
- mergeability is false or unknown and cannot be resolved,
- required CI failed or is missing for code/validation changes,
- human review is required and absent,
- requested changes are unresolved,
- the PR changes protected branch policy without explicit human approval,
- the PR includes secrets or private credentials,
- the PR exposes local endpoints publicly,
- the PR performs Proxmox or host mutation without explicit approval,
- the PR changes generated projections as if they were source of truth,
- the PR lacks evidence for its acceptance criteria.

## Merge action payload

After a human explicitly authorizes a merge and all gates pass, prefer the minimal normal merge payload:

```text
repository_full_name
pr_number
```

Avoid optional merge fields unless specifically required:

- custom commit title,
- custom commit message,
- expected head SHA,
- explicit merge method,
- long generated summaries.

Long or highly customized merge payloads may hit tool-layer limits or safety checks even when the PR itself is safe and approved. If an optional-field merge attempt is blocked by the tool layer, re-check authorization and retry only with the minimal normal merge payload.

## Evidence expectations

Every merge-review packet should include:

- what was checked,
- what could not be checked,
- current PR state,
- mergeability,
- CI status,
- review status,
- changed files,
- evidence paths,
- risk notes,
- verdict,
- next action,
- human decision needed.

## Current stack example

For the current #118 preparation sprint, the expected review stack is:

```text
#119 — standard execution contract
#121 — repository self-model roadmap
#122 — schema registry and compatibility policy
#123 — repo contract validation gate
#124 — documentation map and navigation index
#125 — minimal hello workflow reference implementation
```

PRs that are based on another PR branch should not be treated as merge-ready to `main` until their parent PR has merged, they are retargeted or rebased as needed, and CI/mergeability are checked again.

## Output example

```text
repo: Aggredicus/Local-Agent-Workshop
reviewed_at: 2026-06-01
recommended_order: #119, #121, #122, #123, #124, #125

PR #119:
  verdict: ready_for_human_approval
  next_action: human reviews and decides whether to merge

PR #123:
  verdict: stack_wait
  next_action: wait for #122, then retarget/recheck

human_decision_needed:
  approve merge order or request changes
```

## Non-goals

This protocol does not implement automatic merge, auto-approval, branch-protection changes, or deployment.
