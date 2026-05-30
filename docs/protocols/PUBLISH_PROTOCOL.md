# Publish Protocol

`/publish` is the safe end-of-day release and save-file workflow for Local Agent Workshop.

It prepares reviewed `develop` work for promotion into `main`, but it must not bypass quality gates, branch protection, incident visibility, or human approval.

## Branch meaning

The branch policy defines:

```text
main     stable, released, client-safe code
develop  reviewed integration branch
```

Do not rename `main` to `stable`. Use `main` as the branch name and describe it as stable, released, and client-safe.

## Purpose

`/publish` should make the end of a work session feel like a safe save point:

```text
finish work
verify quality
capture incidents
record improvement opportunities
prepare stable state
walk away with a clean save file
resume tomorrow from a known-good baseline
```

## Relationship to the automation loop

The normal work loop is:

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

`/publish` starts only after review/human decision approves a publish attempt.

Suggested publish loop:

```text
review/human decision approves publish
→ /publish preflight
→ publish approval profile check
→ release/save-file packet
→ develop→main PR
→ explicit human approval
→ merge to main
→ publish closeout
→ next-day resume notes
```

## Quality gate dependency

`/publish` depends on a successful `/quality-analysis final review gate` pass.

Publishing should not happen merely because work ended or because the day ended.

Publishing is allowed only when the final quality-analysis report satisfies a configurable publish approval profile.

Example approval profile:

```json
{
  "profile": "end_of_day_publish",
  "source_branch": "develop",
  "target_branch": "main",
  "requires": {
    "cleanup_closeout": "passed",
    "quality_analysis_final": "passed",
    "verification": "passed",
    "hyperkanban_sync": "passed",
    "unresolved_blockers": 0,
    "high_risk_items": "human_approved",
    "incident_handling": "documented_or_none",
    "followup_issues": "created_or_intentionally_skipped",
    "next_day_resume_note": "present"
  },
  "blocks_publish_if": [
    "quality_analysis_has_BLOCKER",
    "quality_analysis_has_ESCALATE_without_human_decision",
    "verification_failed",
    "cleanup_closeout_failed",
    "undocumented_incident",
    "unapproved_high_risk_change",
    "missing_publish_packet"
  ]
}
```

## Publish preflight

Before preparing a `develop` → `main` publish, verify:

- the request is explicit,
- `develop` is the intended source branch,
- `main` is the intended target branch,
- cleanup closeout passed,
- final quality analysis passed,
- verification passed,
- incidents are documented or absent,
- unresolved blockers are zero,
- high-risk items have human approval,
- follow-up issues are created or intentionally skipped,
- a next-day resume note exists or will be generated,
- the publish packet will be reviewable.

## Publish packet

A publish packet is the reviewable evidence bundle for the release/save-file state.

Suggested path:

```text
reports/publish/
```

Suggested files:

```text
reports/publish/publish-packet.<date>.md
reports/publish/publish-packet.<date>.json
reports/publish/latest.json
```

A publish packet should include:

- source branch,
- target branch,
- commit range,
- merged PRs since last publish,
- issues completed,
- tests and verification run,
- cleanup result,
- quality-analysis result,
- incident reports,
- known limitations,
- follow-up issues,
- human approval status,
- rollback or reversal notes,
- next-day starting point.

## Incident and improvement handling

Incidents must remain visible.

Incident handling should record:

- incident summary,
- severity,
- linked bug/issue/card,
- workaround or rollback,
- whether the incident blocks publish,
- whether publish is approved despite the incident and why.

Improvement opportunities should route through:

```text
/quality-analysis finding
→ /generate-issue candidate
→ HyperKanban card proposal
→ Chronicle or self-improvement record
```

## Ethics and safety values

`/publish` should encode safety-first governance.

Values:

```text
Safety before speed.
Evidence before confidence.
Human review before irreversible action.
Mental health and burnout risks matter.
Secure software protects people.
Physical safety of humanity and nature matters.
AI cooperation must remain accountable to human and ecological well-being.
Automation should reduce harm, not accelerate unsafe work.
```

## Human approval boundary

Agents may prepare:

- publish packets,
- incident summaries,
- quality summaries,
- changelog summaries,
- `develop` → `main` PRs,
- merge readiness recommendations.

Agents must not silently:

- merge into `main`,
- bypass branch protection,
- ignore failed verification,
- hide incidents,
- erase audit history,
- publish without explicit human approval.

## Stop rules

Stop publish when:

- final quality analysis has unresolved `BLOCKER` findings,
- final quality analysis has unresolved `ESCALATE` findings without human decision,
- verification failed,
- cleanup closeout failed,
- incidents are undocumented,
- high-risk changes lack approval,
- publish packet is missing,
- the human did not explicitly approve publishing.

## Future CLI direction

Initial automation should be dry-run and local-first.

Possible future commands:

```sh
workshop publish preflight --source develop --target main
workshop publish packet --out reports/publish/latest.json
workshop publish ready --require-human-approval
workshop publish create-pr --source develop --target main
workshop publish closeout --publish-pr <number>
```

Actual merge to `main` must remain explicitly human-approved.
