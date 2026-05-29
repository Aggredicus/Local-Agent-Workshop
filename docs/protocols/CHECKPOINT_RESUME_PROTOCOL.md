# Checkpoint and Resume Protocol

Long-running work must be checkpointed.

A checkpoint should include:

- run ID,
- task ID,
- branch,
- worktree,
- current status,
- files changed,
- tests run,
- pending decisions,
- next safe action,
- and resume command.

Example:

```sh
workshop grind resume <run-id>
```

Review bundles are artifacts, not always hard stops. The agent may continue unrelated low-risk work unless the next step depends on human input.
