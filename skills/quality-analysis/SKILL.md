# /quality-analysis

Use this skill near both ends of every meaningful Local Agent Workshop automation cycle.

`/quality-analysis` is distinct from `/cleanup`.

```text
/cleanup asks: is the repository tidy, synchronized, and safe to proceed?
/quality-analysis asks: is the work high-quality, scoped, tested, documented, evidenced, and reviewable?
```

## Lifecycle placement

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

## Baseline mode

Run baseline mode after cleanup preflight and before start-work issue decisions.

Ask:

- Is the work attached to a clear issue or HyperKanban card?
- Are acceptance criteria present?
- Is the scope bounded?
- Are expected tests and docs known?
- Is the risk level understood?
- Should the work proceed, split, simplify, or escalate?

Recommended output:

```text
Baseline quality analysis: proceed / split / simplify / escalate / stop
Key risks:
Expected tests:
Expected docs:
Issue/card readiness:
```

## Final review gate mode

Run final review gate mode after `/generate-issue closeout-check` and `/cleanup closeout`, immediately before review/human decision.

Ask:

- Did the work meet acceptance criteria?
- Are tests actually run and named?
- Are unrun tests explained?
- Did cleanup closeout pass?
- Are follow-up issue decisions complete?
- Are risks and limitations documented?
- Do changed files match stated scope?
- Is the package ready for review/human decision?
- Is the package ready for a `/publish` approval profile, if publishing is requested?

Recommended output:

```text
Final quality analysis: ready / needs changes / escalate / stop
Evidence:
Risks:
Follow-ups:
Cleanup closeout:
Publish readiness, if requested:
Human decision needed:
```

## Finding model

Quality findings should be specific and evidence-linked.

Suggested fields:

```text
category
severity
confidence
message
evidence
recommended_action
destination
```

Severity levels:

```text
INFO      useful observation
WARN      quality gap that should be addressed or tracked
BLOCKER   must be fixed or explicitly waived before merge/closeout
ESCALATE  human decision required
```

## Categories

Use categories such as:

```text
requirements
scope
architecture
tests
documentation
risk
security
maintainability
performance
accessibility
usability
observability
cleanup
HyperKanban
Chronicle
review-readiness
resource-cost
```

## Stop and simplify rules

Do not over-analyze trivial work.

Skip or simplify when:

- the change is documentation-only and low-risk,
- no code/config/runtime behavior changed,
- the issue already has clear acceptance criteria,
- a short PR note is sufficient,
- the finding is too vague to act on,
- deeper analysis would cost more than expected benefit.

Spend more effort when:

- governance changes,
- CI changes,
- security boundaries change,
- HyperKanban or Chronicle changes,
- automation or agent behavior changes,
- tests are missing,
- evidence is weak,
- scope expanded,
- high-concurrency safety could be affected.

## Handoff rules

### To `/generate-issue`

Quality analysis should produce issue candidates, not create issue spam.

```text
quality finding
→ issue candidate if valuable
→ /generate-issue duplicate search
→ create / simplify / skip / review-card
```

### To `/self-improvement`

Baseline quality findings can inform same-cycle planning because baseline mode happens before `/grind` and `/self-improvement`.

Final review quality analysis happens after `/self-improvement` in the canonical loop. Final-review findings should normally become next-cycle self-improvement inputs, review notes, Chronicle candidates, HyperKanban proposals, or `/generate-issue` candidates.

Do not treat final review quality findings as same-cycle `/self-improvement` input unless an explicit extra reflection pass is requested and documented.

### To `/publish`

Final review quality analysis is the primary quality gate for `/publish`.

`/publish` should consume the final quality-analysis report and compare it against a configurable publish approval profile before preparing or recommending a `develop` → `main` publish.

Block publish on unresolved `BLOCKER` findings, unresolved `ESCALATE` findings without human decision, failed verification, failed cleanup closeout, undocumented incidents, unapproved high-risk changes, or missing publish packet.

### To HyperKanban

Quality findings may propose updates to:

- test contracts,
- doc contracts,
- risk flags,
- review flags,
- evidence paths,
- open exceptions,
- follow-up cards,
- blocked reasons.

No automatic mutation in the first implementation.

### To Chronicle

Quality analysis may eventually emit or propose events such as:

```text
quality_analysis.started
quality_analysis.completed
quality_analysis.blocker_detected
quality_analysis.warning_detected
quality_analysis.escalation_requested
quality_analysis.issue_candidate_created
quality_analysis.waived_with_reason
```

## Human approval boundary

Agents may recommend readiness.

Agents must not replace human review for high-risk changes, protected branch decisions, destructive actions, live credentials, deployments, or governance changes.
