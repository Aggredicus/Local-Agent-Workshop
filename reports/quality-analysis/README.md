# Quality Analysis Reports

This directory is reserved for generated quality analysis reports.

Planned report types:

```text
baseline.<run-id>.json
final-review.<run-id>.json
latest.json
```

Quality reports should be treated as generated evidence artifacts. They can inform review cards, HyperKanban proposals, Chronicle events, and `/generate-issue` candidates, but they should not silently mutate repository governance.
