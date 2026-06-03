# /merge-review Improvement Log

This file records compact post-use artifact updates for `/merge-review` when no `SKILL.md` behavior patch is required.

Use the format from `skills/README.md`.

## 2026-06-02 — Establish mandatory artifact trail

Skill used: /merge-review
Used for: #160 governance update
Outcome: behavior updated
Observation: The project now requires every skill use to create both an improvement issue and a durable skill artifact update.
Decision: `/merge-review` was patched to explicitly require a post-use improvement issue and either a `SKILL.md` behavior patch or this log entry after every run.
Links: #160

## 2026-06-02 — PR #161 merge review

Skill used: /merge-review
Used for: PR #161
Outcome: log-only update
Observation: Merge review found no new behavior change after the PR body was corrected; CI passed, mergeability was true, and no review threads were open.
Decision: No `SKILL.md` behavior change recommended beyond the #160 artifact-trail rule already included in PR #161.
Links: #160, #161, #164
