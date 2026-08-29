# /publish

Use this skill when a human explicitly wants to finalize the current reviewed `main` state as a stable release/save-file baseline or prepare a separately approved release action.

`/publish` is not a shortcut around pull-request review, protected-branch approval, or verification.

## Branch target

```text
main          reviewed stable trunk, normal PR target, released/client-safe baseline
develop       legacy historical branch retained temporarily; not active integration
```

Routine work should use a short-lived branch and a pull request targeting `main`. A human-approved merge into `main` happens before `/publish` finalizes that stable state.

## When to use

Use `/publish` only after the normal work/review loop has produced a reviewed `main` state and the human explicitly asks to publish or create a stable save point.

```text
short-lived branch
→ verification and review
→ main-targeted PR
→ explicit human approval
→ merge to main
→ /publish preflight
→ publish packet
→ optional separately approved release action
→ publish closeout
```

## Quality gate dependency

`/publish` depends on a successful `/quality-analysis final review gate` and verification of the `main` commit being published.

Do not publish simply because the day ended.

Minimum approval criteria:

```text
source is reviewed main
cleanup closeout passed
quality-analysis final passed
verification passed
HyperKanban synchronized
zero unresolved blockers
high-risk items human-approved
incidents documented or absent
follow-up issues created or intentionally skipped
resume note present
```

Block publish when:

```text
quality-analysis has BLOCKER
quality-analysis has ESCALATE without human decision
verification failed
cleanup closeout failed
incident is undocumented
high-risk change is unapproved
publish packet is missing
source is not the intended reviewed main state
human approval is missing
```

## Publish preflight

Before publishing, check:

- source state is the intended reviewed `main` commit,
- final quality-analysis result is acceptable,
- cleanup closeout passed,
- `scripts/verify.sh` passed for the state being published,
- incident reports are complete or not needed,
- unresolved risks are documented,
- follow-up issues are created or intentionally skipped,
- publish packet exists or will be generated,
- human approval is explicit.

If the requested action includes a tag, GitHub release, deployment, release branch, or other live/protected effect, require the additional approval demanded by repository policy.

## Publish packet

Generate or prepare a publish packet under:

```text
reports/publish/
```

The packet should include:

- source `main` commit,
- previous published baseline when known,
- commit range,
- merged PRs since the previous publish,
- issues completed,
- verification evidence,
- cleanup result,
- quality-analysis result,
- incident reports,
- known limitations,
- follow-up issues,
- human approval status,
- any proposed release/tag/deploy action,
- rollback or reversal notes,
- next-session starting point.

## Incident handling

Do not hide incidents.

For each incident, record:

- summary,
- severity,
- linked issue/card,
- workaround or rollback,
- publish blocking decision,
- reason if publish proceeds despite the incident.

## Agent permissions

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
- create live release effects without required approval,
- publish without explicit human approval.

## Stop rules

Stop when:

- final quality analysis does not pass,
- verification does not pass,
- cleanup closeout does not pass,
- incidents are undocumented,
- unresolved blockers exist,
- high-risk changes lack approval,
- publish packet is missing,
- source is not the intended reviewed `main` state,
- the human did not approve publishing.

## Future CLI direction

Future commands may include:

```sh
workshop publish preflight --source main
workshop publish packet --source main --out reports/publish/latest.json
workshop publish ready --require-human-approval
workshop publish propose-release --source main
workshop publish closeout --source main
```

Until those commands exist, follow this skill and `docs/protocols/PUBLISH_PROTOCOL.md` manually.
