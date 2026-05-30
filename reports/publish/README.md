# Publish Reports

This directory is reserved for generated `/publish` reports and release/save-file packets.

Planned files:

```text
publish-packet.<date>.md
publish-packet.<date>.json
latest.json
```

Publish packets should summarize source branch, target branch, commit range, verification evidence, cleanup result, final quality-analysis result, incidents, known limitations, follow-up issues, human approval status, rollback notes, and next-day resume notes.

Generated publish reports are evidence artifacts. They should inform review, Chronicle events, HyperKanban proposals, and human release decisions, but they must not silently merge protected branches.
