# Quality Observation Inbox

This inbox stores machine-ingestible quality observations produced by QC agents.

Files in this directory are reviewable inputs for:

```text
/quality-analysis
/self-improvement
/generate-issue
Chronicle candidate events
HyperKanban card proposals
```

Recommended naming:

```text
qc-agent-<id>-<short-test-name>-YYYY-MM-DD.json
```

Each observation should include evidence, severity, confidence, recommended destination, and whether it should create an issue, update a card, become a Chronicle event, or be ignored/deferred.

Observation artifacts are not automatically accepted as facts. They are evidence packets that should be reviewed, classified, and routed through the project governance loop.
