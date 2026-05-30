# Quality Analysis Protocol

Quality analysis is a required quality-intelligence gate for meaningful automation cycles.

It is distinct from repository cleanup.

```text
/cleanup asks: is the repository tidy, synchronized, and safe to proceed?
/quality-analysis asks: is the work high-quality, scoped, tested, documented, evidenced, and reviewable?
```

## Lifecycle placement

Quality analysis runs twice in the canonical automation loop:

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

## Baseline quality analysis

Run after cleanup preflight and before issue/start-work decisions.

Purpose:

- identify current quality risks before starting work,
- verify that intended work is clear and scoped,
- check for acceptance criteria,
- identify expected tests and documentation updates,
- classify risk,
- decide whether to proceed, simplify, split, or escalate.

Baseline questions:

```text
Is the issue/card clear?
Are acceptance criteria present?
Is scope bounded?
Is the expected branch strategy safe?
Are expected tests known?
Are expected docs known?
Is the risk level understood?
Are cleanup findings blocking work?
```

## Final review quality analysis

Run after closeout issue generation and cleanup closeout, immediately before review/human decision.

Purpose:

- evaluate the complete closeout package,
- check acceptance criteria against evidence,
- verify test and cleanup claims,
- detect scope creep,
- identify missing documentation or risk notes,
- decide whether the work is ready for human review,
- decide whether the work can satisfy a publish-readiness profile when `/publish` is requested.

Final review questions:

```text
Did the work meet acceptance criteria?
Are tests actually run and named?
Are unrun tests explicitly explained?
Did cleanup closeout pass?
Are follow-up issue decisions complete?
Are risks and limitations documented?
Do changed files match stated scope?
Is rollback or reversal clear?
Is the package ready for review/human decision?
Is the package ready for a /publish approval profile, if publishing is requested?
```

## Inputs

Quality analysis may consume:

- cleanup report JSON,
- Git diff or changed-file list,
- issue body,
- PR body,
- HyperKanban card state,
- Chronicle events,
- review cards,
- self-improvement inbox artifacts,
- test output summaries,
- verification command output,
- `me.md`,
- governance and protocol docs.

## Outputs

Quality analysis should produce machine-ingestible reports over time.

Suggested output path:

```text
reports/quality-analysis/
```

Suggested report names:

```text
baseline.<run-id>.json
final-review.<run-id>.json
latest.json
```

A report should include:

```json
{
  "artifact_type": "quality_analysis",
  "schema_version": "0.1.0",
  "phase": "baseline",
  "summary": {
    "blockers": 0,
    "warnings": 1,
    "info": 3,
    "recommendation": "proceed"
  },
  "findings": []
}
```

## Finding fields

Each finding should eventually include:

```text
category
severity
confidence
message
evidence
recommended_action
destination
```

## Categories

Initial categories:

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

## Severity levels

```text
INFO      useful observation
WARN      quality gap that should be addressed or tracked
BLOCKER   must be fixed or explicitly waived before merge/closeout
ESCALATE  human decision required
```

## Stop and simplify rules

Quality analysis should not become expensive ritual.

Stop or simplify when:

- the change is documentation-only and low-risk,
- the issue already has adequate acceptance criteria,
- no code, config, runtime behavior, schema, CI, or governance changed,
- the finding is too vague to act on,
- a short PR note is enough,
- deeper analysis would cost more than expected benefit.

Commit more quality-analysis effort when:

- governance changes,
- CI changes,
- security boundaries change,
- HyperKanban or Chronicle changes,
- automation or agent behavior changes,
- test evidence is missing,
- scope expanded,
- high-concurrency safety could be affected.

## Handoff to `/generate-issue`

Quality analysis should not create GitHub issues directly in early versions.

It should produce issue candidates for `/generate-issue` to classify.

```text
quality finding
→ issue candidate if valuable
→ duplicate search
→ create / simplify / skip / review-card
```

## Handoff to `/self-improvement`

The timing of this handoff depends on which quality-analysis gate produced the finding.

Baseline quality analysis happens before `/self-improvement` in the same cycle, so its findings may inform same-cycle grind planning and self-improvement context.

Final review quality analysis happens after `/self-improvement` in the canonical loop. Therefore final-review findings should normally become **next-cycle** self-improvement inputs, publish-readiness inputs, review-card notes, Chronicle candidates, or `/generate-issue` candidates.

Do not imply that final review quality analysis feeds same-cycle `/self-improvement` unless an explicit extra reflection pass is requested and documented.

Repeated quality findings should become lessons, skill proposals, test-gap proposals, or HyperKanban card proposals through the next appropriate cycle.

## Handoff to `/publish`

Final review quality analysis is the primary quality gate for `/publish`.

A publish attempt should consume the final quality-analysis report and compare it against a configurable publish approval profile before preparing or recommending a `develop` → `main` publish.

Publish should be blocked when final quality analysis has unresolved `BLOCKER` findings, unresolved `ESCALATE` findings without a human decision, missing verification evidence, failed cleanup closeout, undocumented incidents, unapproved high-risk changes, or a missing publish packet.

## HyperKanban hooks

Quality findings may propose updates to:

- test contracts,
- doc contracts,
- risk flags,
- review flags,
- evidence paths,
- open exceptions,
- follow-up cards,
- blocked reasons.

No automatic mutation is allowed in the first implementation.

## Chronicle hooks

Future event types may include:

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

Quality analysis may recommend readiness, request changes, or escalate.

It must not replace human review for high-risk changes or protected branch decisions.
