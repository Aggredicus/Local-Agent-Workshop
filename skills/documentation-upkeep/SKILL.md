# /documentation-upkeep

Use this skill to audit project-management documentation upkeep needs after repository changes.

The goal is to detect documentation drift, append evidence, and create bounded follow-up work without silently rewriting history or treating generated projections as source of truth.

## Core rule

```text
append evidence before changing docs
prefer follow-up issues over silent edits
reports are evidence, not authority
Chronicle-style history is append-only
HyperKanban and dashboards are projections, not source of truth
issues are work-tracking interfaces, not proof of truth
no deletion by default
no historical rewrite by default
no issue state mutation by default
no HyperKanban mutation by default
no source-of-truth promotion
create a follow-up improvement issue after every use
update the /documentation-upkeep artifact trail after every use
```

## When to use

Use `/documentation-upkeep`:

- after merging governance, protocol, skill, schema, report, or project-management documentation changes,
- after a repo quality audit finds state-truth drift,
- after adding a new skill, schema, report directory, project-management doc, or protocol doc,
- when navigation docs may be stale,
- when an issue appears closed but not complete,
- when an issue appears complete but remains open,
- when a project-management rule changes and related docs may need additive updates,
- before making broad documentation maintenance changes,
- when a fresh agent may need better discovery paths.

## Non-goals

This skill does not:

- edit project-management docs directly unless an issue explicitly authorizes that edit,
- delete files,
- rewrite historical records,
- silently change issue state,
- close or reopen issues,
- mutate HyperKanban state,
- mutate Chronicle history except by append-only record,
- promote dashboards, reports, generated docs, or model summaries to source of truth,
- replace `/close-issue`, `/merge-review`, `/quality-analysis`, or repo validation,
- create automatic issue-closing behavior,
- implement documentation-audit scripts unless a separate issue authorizes scripts.

## Inputs

Collect as available:

- repository name,
- triggering issue, PR, report, audit, or user request,
- current branch and target branch,
- recent merged PRs,
- recent open and closed issues,
- project-management docs,
- navigation/index docs,
- protocol docs,
- skill docs and skill improvement logs,
- schema registry files,
- report directories,
- validation outputs,
- Chronicle-style append paths if present,
- HyperKanban/dashboard projection paths if present,
- known stale status references,
- known source-of-truth boundaries,
- human authorization context for governance-relevant documentation changes.

Minimum context for a normal run:

```text
me.md
skills/README.md
skills/*/SKILL.md
skills/*/IMPROVEMENT_LOG.md
docs/README.md if present
docs/NAVIGATION_INDEX.md if present
docs/project-management/** if present
docs/protocols/** if present
schema registry files if present
reports/** structure if present
recent issues and PRs related to the upkeep trigger
```

## Append-only posture

Default allowed actions are additive:

- create or append a documentation-upkeep report,
- create or append an improvement log entry,
- create a bounded follow-up issue,
- add an issue comment explaining detected drift,
- add a new placeholder directory such as `.gitkeep`,
- propose a patch without applying it,
- add a new supersession/correction note when explicitly authorized.

Default forbidden actions are destructive or silently corrective:

- delete files,
- rewrite historical records,
- remove old statements without preserving supersession context,
- reorder or restructure docs without a dedicated issue,
- silently change issue state,
- close or reopen issues,
- mutate HyperKanban state,
- mutate generated dashboard state as if it were authority,
- overwrite Chronicle-style history instead of appending,
- edit source-of-truth governance docs without explicit authorization.

When a historical statement is stale, prefer an additive note:

```text
This status was accurate as of <date>.
Superseded by <issue/PR/report> on <date>.
```

## Inspection checklist

### 1. Navigation drift

Check whether important files are discoverable from navigation docs:

- new skills,
- project-management docs,
- protocol docs,
- schema docs,
- validation reports,
- dashboard docs,
- architecture docs,
- report directories.

Look for stale navigation language such as:

```text
active PR
planned
pending
TODO
coming soon
not yet implemented
```

Do not edit navigation automatically unless the issue explicitly authorizes it. Prefer a follow-up issue with evidence.

### 2. Issue-status drift

Check for:

- closed issues that still contain real remaining work,
- closed epics whose body still lists unfinished outputs,
- closed issues whose linked PR completed only a slice,
- closed issues without public closeout evidence,
- open issues whose linked PRs merged and appear complete,
- duplicate terminal audit issues,
- issues that should be superseded, restored, split, or corrected.

Do not close or reopen issues. Produce a report or follow-up issue for `/close-issue` or human review.

### 3. Project-management documentation gaps

Check whether new repository behavior should be reflected in:

```text
docs/project-management/**
docs/protocols/**
docs/NAVIGATION_INDEX.md
docs/README.md
skills/README.md
```

Examples:

- new governance rules,
- new skill-use requirements,
- new issue taxonomy behavior,
- new milestone or roadmap behavior,
- new validation/report conventions,
- new schema or workflow conventions,
- new release/readiness rules.

### 4. Skill documentation drift

Check:

- every `skills/*/SKILL.md` has an `IMPROVEMENT_LOG.md`,
- skill docs do not conflict with `skills/README.md`,
- post-use improvement issue and artifact update obligations are represented where needed,
- new skills have report/log directories if required,
- new skills need navigation/index follow-up,
- terminal audit issues do not create infinite recursion.

### 5. Schema and report discoverability

Check:

- new schemas are discoverable or have registry follow-up issues,
- schema registry status is not stale,
- new report directories have placeholders,
- report paths are mentioned in the relevant docs or follow-up issues,
- generated reports are not promoted to source of truth,
- validation outputs are linked or tracked.

### 6. Chronicle-style append needs

Check whether a change should produce an append-only history record:

- governance change,
- policy change,
- issue-state correction,
- premature closure restoration,
- major roadmap split,
- skill behavior change,
- source-of-truth boundary clarification.

If Chronicle writer support or a canonical Chronicle path is unavailable, create a documentation-upkeep report and/or follow-up issue instead of inventing a new source-of-truth path.

## Verdicts

Use one or more verdicts.

| Verdict | Meaning |
|---|---|
| `upkeep_clean` | No documentation upkeep action is needed. |
| `append_report_only` | Record findings in an append-only report; no follow-up issue required. |
| `needs_documentation_issue` | A bounded documentation issue should be created. |
| `needs_navigation_issue` | A navigation/index update is needed, but should be tracked separately. |
| `needs_status_correction` | Issue/doc status appears misleading and needs correction or restoration tracking. |
| `needs_chronicle_append` | An append-only Chronicle-style event should be created when a canonical path/writer is available. |
| `needs_project_management_doc` | Project-management docs should be updated by a dedicated issue/PR. |
| `needs_skill_doc_update` | A skill or skills protocol doc needs a behavior or discoverability update. |
| `needs_schema_registry_issue` | Schema registry or schema documentation follow-up is needed. |
| `blocked_missing_context` | Required repository context could not be inspected. |
| `do_not_modify` | A proposed change would delete, rewrite, mutate state, or promote projections to source of truth. |

## Report format

A documentation-upkeep report should be append-only and compact.

Preferred Markdown report:

```text
# Documentation Upkeep Report — YYYY-MM-DD — <context>

repo:
trigger:
reviewed_at:
reviewer:
source_refs:

## Summary

## Findings

### Finding <n>: <title>
category:
severity: low | medium | high
source:
evidence:
recommended_action:
follow_up_issue:
verdict:

## Non-actions

## Stop conditions

## Suggested issues
```

Preferred JSON shape for future scripts:

```json
{
  "report_type": "documentation_upkeep",
  "version": "0.1",
  "repo": "owner/name",
  "trigger": "issue|pr|audit|manual",
  "reviewed_at": "ISO-8601",
  "findings": [
    {
      "id": "DU-001",
      "category": "navigation_drift|issue_status_drift|project_management_gap|skill_doc_drift|schema_report_discoverability|chronicle_append_need",
      "severity": "low|medium|high",
      "source": "issue/pr/path/report",
      "evidence": "short evidence string",
      "recommended_action": "append_report|create_issue|add_comment|do_not_modify|needs_human_review",
      "verdict": "needs_documentation_issue"
    }
  ]
}
```

## Follow-up issue guidance

When creating follow-up issues:

- keep them bounded,
- include exact evidence paths or issue/PR numbers,
- state whether the fix should be append-only or may modify a specific doc,
- include non-goals,
- include acceptance criteria,
- avoid bundling unrelated drift categories.

Example issue title patterns:

```text
Link <new doc/skill> from navigation index
Add project-management note for <new governance rule>
Append status correction for <issue/doc drift>
Split restored <epic> work into bounded dashboard issues
Add schema registry follow-up for <schema>
```

## Future scripts

Useful scripts to create under separate issues:

```text
scripts/audit_documentation_upkeep.py
scripts/check_closed_issue_authenticity.py
scripts/check_project_management_doc_gaps.py
scripts/check_navigation_index_drift.py
scripts/check_skill_artifact_trails.py
scripts/append_documentation_upkeep_log.py
scripts/suggest_documentation_issues.py
```

The first version of `/documentation-upkeep` should mention these scripts but not implement them unless the issue explicitly authorizes scripts.

## Safe flow

1. Read required repository context.
2. Identify the trigger and scope.
3. Check navigation drift.
4. Check issue-status drift.
5. Check project-management documentation gaps.
6. Check skill documentation drift.
7. Check schema/report discoverability.
8. Check Chronicle-style append needs.
9. Produce findings and verdicts.
10. Prefer append-only report output.
11. Create bounded follow-up issues only when authorized or clearly requested.
12. Do not edit source-of-truth docs directly unless explicitly authorized.
13. Do not close or reopen issues.
14. Record post-use improvement issue and artifact update for `/documentation-upkeep`.

## Stop conditions

Stop and create a handoff if:

- required context cannot be inspected,
- the only apparent fix requires deletion,
- the only apparent fix requires rewriting history,
- source-of-truth authority is unclear,
- a generated projection would be treated as source of truth,
- a proposed action would close or reopen issues,
- a proposed action would mutate HyperKanban state,
- a proposed action would mutate Chronicle history rather than append,
- project-management docs need direct modification but no issue authorizes it,
- governance-relevant documentation changes lack human authorization,
- multiple unrelated drift categories would be bundled into one oversized PR.

## Mandatory post-use improvement

After every `/documentation-upkeep` run:

1. Create the required follow-up improvement issue for `/documentation-upkeep`.
2. If the run found a reusable behavior lesson, patch `skills/documentation-upkeep/SKILL.md`.
3. If the run found no behavior change, append a compact entry to `skills/documentation-upkeep/IMPROVEMENT_LOG.md`.
4. Link the triggering issue, PR, or report when practical.
5. Apply the global `skills/README.md` recursion breaker only for terminal no-change audit issues.

## Good documentation-upkeep behavior

A good run should say:

- what repository context was inspected,
- what drift categories were checked,
- what evidence was found,
- which docs should be linked or updated,
- which issues appear stale, incomplete, or complete-but-open,
- what should be appended rather than rewritten,
- what follow-up issues should be created,
- what must not be modified,
- whether Chronicle-style append support exists,
- what verdicts apply,
- and what post-use improvement issue/artifact update was created.
