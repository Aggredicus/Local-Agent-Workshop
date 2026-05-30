# /publish

Use this skill when a human explicitly wants to promote reviewed `develop` work into `main` as a stable end-of-day release/save-file state.

`/publish` is not a shortcut around review. It is a quality-gated release workflow.

## Branch target

```text
main     stable, released, client-safe code
develop  reviewed integration branch
```

Use the branch name `main`. Do not rename it to `stable`.

## When to use

Use `/publish` only after:

```text
/cleanup preflight
→ /quality-analysis baseline
→ /generate-issue start-check
→ /grind
→ /self-improvement
→ /generate-issue closeout-check
→ /cleanup closeout
→ /quality-analysis final review gate
→ review/human decision approves publish
```

## Publish loop

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

Do not publish simply because the day ended.

Publish only when the final quality-analysis report satisfies a custom publish approval profile.

Minimum approval criteria:

```text
cleanup closeout passed
quality-analysis final passed
verification passed
HyperKanban synchronized
zero unresolved blockers
high-risk items human-approved
incidents documented or absent
follow-up issues created or intentionally skipped
next-day resume note present
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
human approval is missing
```

## Publish preflight

Before publishing, check:

- source branch is `develop`,
- target branch is `main`,
- final quality-analysis result is acceptable,
- cleanup closeout passed,
- `scripts/verify.sh` passed,
- incident reports are complete or not needed,
- unresolved risks are documented,
- follow-up issues are created or intentionally skipped,
- publish packet exists or will be generated,
- human approval is explicit.

## Publish packet

Generate or prepare a publish packet under:

```text
reports/publish/
```

The packet should include:

- source branch,
- target branch,
- commit range,
- merged PRs since last publish,
- issues completed,
- verification evidence,
- cleanup result,
- quality-analysis result,
- incident reports,
- known limitations,
- follow-up issues,
- human approval status,
- rollback or reversal notes,
- next-day starting point.

## Incident handling

Do not hide incidents.

For each incident, record:

- summary,
- severity,
- linked issue/card,
- workaround or rollback,
- publish blocking decision,
- reason if publish proceeds despite the incident.

## Ethics and safety values

`/publish` should express the project’s safety-first governance.

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

## Agent permissions

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

Stop when:

- final quality analysis does not pass,
- verification does not pass,
- cleanup closeout does not pass,
- incidents are undocumented,
- unresolved blockers exist,
- high-risk changes lack approval,
- publish packet is missing,
- the human did not approve publishing.

## Future CLI direction

Future commands may include:

```sh
workshop publish preflight --source develop --target main
workshop publish packet --out reports/publish/latest.json
workshop publish ready --require-human-approval
workshop publish create-pr --source develop --target main
workshop publish closeout --publish-pr <number>
```

Until those commands exist, follow this skill and `docs/protocols/PUBLISH_PROTOCOL.md` manually.
