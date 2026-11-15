# Proposed follow-ups — not GitHub issues

These are review candidates, not approved changes. GitHub API access returned 403, so no issue creation, live deduplication, or PR ownership verification was possible. Review-first instruction takes precedence over continuing feature implementation.

| Order | Candidate | Evidence | Acceptance |
|---|---|---|---|
| 1 | Remove untrusted input from redacted env diagnostics | R01 | Synthetic canaries absent from all outputs |
| 1 | Constrain skill synchronization and make generated state accurate | R02, R03 | No symlink escape, stale generated files or false freshness passes |
| 2 | Share HyperKanban validators and define safe evidence semantics | R04, R05 | Same verdicts across CLI/doctor/CI/cleanup; evidence is accurately described |
| 2 | Make canonical state writes recoverable | R06 | Interrupted writes recover; competing revisions cannot silently overwrite |
| 2 | Replace heuristic parsing and expose scan coverage | R07, R08 | TOML correctly parsed; omitted/unsupported files never appear fully reviewed |
| 3 | Implement honest quality/security/release gates | R09, R10, R13, R15 | Real checks, locked audited tools, explicit unavailable checks and supported platform matrix |
| 3 | Reconcile governance and refresh skills | R11, R12 | Single approval contract; reviewed-SHA binding; proportionate audit duties; current commands |
| 4 | Review reproducibility, licenses and historical distributions | R14 | Traceable toolchain/artifacts, notices and clearly labeled history |
| 5 | Reassess deployment architecture against the corrected baseline | Review component table | Reviewed threat model, smallest privileged surface, disposable VM evidence before real-server use |

## Skill-use improvement audit hook

The repository currently requires an improvement issue and durable skill artifact update after every invocation. The earlier deployment step invoked `/design-first`, `/repo-cleanup`, and `/quality-analysis`. Reading other skills for this review is inspection, not execution of their workflows.

Suggested improvement records for those invocations:

- `/design-first`: measure infrastructure risk by enforceable privilege boundaries and verified platform evidence, not the presence of a design report. Link this review and the paused experiment.
- `/repo-cleanup`: distinguish fresh checkout/intentional review artifacts from unsafe residue; share state validation rather than growing a third partial validator.
- `/quality-analysis`: report actual check coverage and unrun platform tests; detect successful placeholder checks and stale branch instructions.

No skill behavior/log file was modified during the user's requested review-first assessment. Artifact changes are deferred to the proposed governance/remediation review; this report records that outstanding protocol obligation explicitly rather than claiming it was completed. Existing logs and history are preserved. Do not create recursive no-change issues merely to close this review package; any exception to current policy needs the appropriate reviewed governance change.
