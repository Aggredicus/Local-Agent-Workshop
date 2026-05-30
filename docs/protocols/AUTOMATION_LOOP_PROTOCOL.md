# Automation Loop Protocol

This protocol defines the canonical order for meaningful Local Agent Workshop automation cycles.

It coordinates cleanup, quality analysis, issue generation, grind execution, self-improvement, and human review.

## Canonical loop

```text
/cleanup preflight
→ /quality-analysis baseline
→ /generate-issue start-check
→ /grind
→ /self-improvement
→ /generate-issue closeout-check
→ /cleanup closeout
→ /quality-analysis final review gate
→ review/human decision
```

## Why this order matters

The loop is intentionally nested.

Cleanup creates a safe workspace boundary. Quality analysis checks whether the work is worth doing and whether the final package is ready. Issue generation prevents untracked work and captures valuable follow-up. Grind performs the bounded work. Self-improvement learns from the run without silently mutating governance.

## Step responsibilities

### 1. `/cleanup preflight`

Confirms the repository is tidy, synchronized, and safe to work in.

Primary questions:

- Are there cleanup blockers?
- Is the current branch appropriate?
- Are generated artifacts synchronized?
- Are there stale or superseded work items to consider?

### 2. `/quality-analysis baseline`

Checks the quality posture before work begins.

Primary questions:

- Is the issue/card clear?
- Is the scope bounded?
- Are acceptance criteria present?
- Are expected tests and docs known?
- Is risk understood?
- Should the work proceed, split, simplify, or escalate?

### 3. `/generate-issue start-check`

Confirms the work is tracked by a valid issue or HyperKanban card.

Primary questions:

- Does a suitable issue already exist?
- Should the proposed work be added to an existing issue?
- Should a new issue be created?
- Should the work be skipped because value is too low?

### 4. `/grind`

Performs bounded work.

Every grind run must preserve:

- run ID,
- branch/worktree,
- current task,
- checkpoint state,
- verification evidence,
- review card,
- resume command.

### 5. `/self-improvement`

Reflects on the run and writes bounded machine-ingestible proposals.

Primary outputs may include:

- run reflections,
- lessons,
- issue candidates,
- HyperKanban card proposals,
- harness patch proposals,
- risk findings,
- test gaps,
- doc gaps.

Self-improvement must not silently rewrite governance or mutate protected branches.

### 6. `/generate-issue closeout-check`

Decides what follow-up issues, checklists, notes, review cards, or Chronicle events are needed.

It should avoid issue spam by applying duplicate checks, value/cost classification, and stop/simplify rules.

### 7. `/cleanup closeout`

Leaves the repo in a clean and reviewable state.

Primary questions:

- Did verification run?
- Are cleanup blockers resolved or explicitly documented?
- Are generated artifacts synchronized?
- Are unresolved follow-ups captured?

### 8. `/quality-analysis final review gate`

Evaluates the complete closeout package before human review.

This happens after closeout issue generation and cleanup so it can evaluate the final evidence package.

Primary questions:

- Did the work meet acceptance criteria?
- Is evidence specific and truthful?
- Did cleanup closeout pass?
- Are risks and limitations documented?
- Are follow-up decisions complete?
- Is the package ready for review/human decision?

### 9. `review/human decision`

The human or maintainer decides whether to approve, modify, reject, merge, defer, or redirect the work.

Agents may prepare evidence and recommendations, but protected branch merges and high-risk decisions remain human-governed.

## Skip rule

A step may be skipped only when the agent records a reason.

Acceptable examples:

```text
Skipped self-improvement: documentation-only typo fix with no meaningful lesson.
Skipped generate-issue closeout: no unresolved findings and no high-value follow-up.
Skipped expensive quality analysis: no runtime, CI, schema, governance, or behavior change.
```

Unacceptable examples:

```text
Skipped cleanup because it was inconvenient.
Skipped quality analysis but changed CI behavior.
Skipped issue generation while adding untracked feature scope.
```

## Cost control

The loop should stay useful without becoming ritual overhead.

Rules:

```text
Analyze only enough.
Create only bounded follow-up work.
Prefer checklist items over new issues when appropriate.
Prefer Chronicle notes over issues for low-actionability lessons.
Stop when value drops below cost.
Escalate only at risk boundaries.
```

## Safety boundaries

The automation loop must not:

- mutate protected branches without approval,
- silently rewrite governance,
- create recursive issue spam,
- treat self-improvement proposals as accepted facts,
- bypass cleanup,
- bypass quality gates for high-risk changes,
- claim tests passed without evidence.

## Relationship to `me.md`

`me.md` is the instruction spine. This protocol explains the automation loop referenced there.

If this protocol and `me.md` disagree, stop and create a follow-up issue to reconcile the governance files.
