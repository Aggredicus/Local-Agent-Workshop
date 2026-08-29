# Publish Protocol

`/publish` is the safe release/save-file workflow for a reviewed `main` state in Local Agent Workshop.

It does not replace the normal pull-request review boundary and it does not exist to shuttle work through a separate integration branch.

## Branch meaning

The active branch model is:

```text
main          reviewed stable trunk, normal PR target, released/client-safe baseline
experimental  sandbox and lab branch
agent/*       autonomous work branches
release/*     exceptional release staging when actually needed
rc/*          exceptional release-candidate staging when actually needed
```

`develop` is a legacy historical branch retained temporarily for history and rollback reference. It is not an active integration branch and is not a normal pull-request target.

## Purpose

`/publish` should make a reviewed `main` state feel like a safe save point:

```text
finish bounded work on a short-lived branch
verify and review the pull request
human approves merge to main
merge to main
verify the resulting main state
capture incidents and follow-up work
prepare a stable release/save-file packet
perform any separately approved release action
leave a resume-ready baseline
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

Normal implementation pull requests target `main`. Human approval to merge into `main` remains a separate protected-branch decision.

`/publish` starts only when a human explicitly asks to finalize the reviewed `main` state as a stable release/save point or authorizes a separate release action.

Suggested publish loop:

```text
human requests publish of reviewed main
→ /publish preflight
→ verify main and publish approval profile
→ release/save-file packet
→ incident/follow-up review
→ optional release/tag/deploy proposal
→ explicit human approval for any live/protected effect
→ publish closeout
→ next-session resume notes
```

## Quality gate dependency

`/publish` depends on a successful `/quality-analysis final review gate` and verification of the `main` state being published.

Publishing should not happen merely because work ended or because the day ended.

Example approval profile:

```json
{
  "profile": "stable_main_publish",
  "source_branch": "main",
  "requires": {
    "cleanup_closeout": "passed",
    "quality_analysis_final": "passed",
    "verification": "passed",
    "hyperkanban_sync": "passed",
    "unresolved_blockers": 0,
    "high_risk_items": "human_approved",
    "incident_handling": "documented_or_none",
    "followup_issues": "created_or_intentionally_skipped",
    "resume_note": "present"
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

Before publishing, verify:

- the human request is explicit,
- the source state is the intended reviewed `main` commit,
- cleanup closeout passed,
- final quality analysis passed,
- verification passed on the state being published,
- incidents are documented or absent,
- unresolved blockers are zero,
- high-risk items have human approval,
- follow-up issues are created or intentionally skipped,
- a resume note exists or will be generated,
- the publish packet will be reviewable.

If the requested action includes creating a tag, GitHub release, deployment, release branch, or other live/protected effect, that action requires its own explicit authorization when repository policy says so.

## Publish packet

A publish packet is the reviewable evidence bundle for the stable state.

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

- source `main` commit,
- previous published baseline when known,
- commit range,
- merged PRs since the previous publish,
- issues completed,
- tests and verification run,
- cleanup result,
- quality-analysis result,
- incident reports,
- known limitations,
- follow-up issues,
- human approval status,
- any proposed release/tag/deploy action,
- rollback or reversal notes,
- next-session starting point.

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

## Human approval boundary

Agents may prepare:

- publish packets,
- incident summaries,
- quality summaries,
- changelog summaries,
- release/tag/deploy proposals,
- merge or release readiness recommendations.

Agents must not silently:

- merge into `main`,
- bypass branch protection or repository policy,
- ignore failed verification,
- hide incidents,
- erase audit history,
- create tags/releases/deployments with live effect when approval is required,
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
- the requested source is not the intended reviewed `main` state,
- the human did not explicitly approve publishing.

## Future CLI direction

Initial automation should remain local-first and evidence-first.

Possible future commands:

```sh
workshop publish preflight --source main
workshop publish packet --source main --out reports/publish/latest.json
workshop publish ready --require-human-approval
workshop publish propose-release --source main
workshop publish closeout --source main
```

Routine feature integration belongs to normal `branch -> PR -> human-approved merge to main` workflow, not to `/publish`.
