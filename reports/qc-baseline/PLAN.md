# Selective rebuild: baseline acceptance plan

Branch: agent/qc-baseline. Base: 22fc0e72f55fa68f98f5f9ffa92127e96c7b9913.
User authorized selective rebuild with history preserved and explicit component criteria.

Inputs: codebase-review/REVIEW.md and its reproductions, canonical instructions, baseline tests.
Risk: high security-sensitive code preparation; only local synthetic tests and source changes. No server changes, protected-branch mutation, publication, or credentials.

Chosen design: retain the public Python CLI and its offline standard-library core. Repair it in place behind compatible entrypoints; use regression tests and maintained parsing/validation libraries in development where appropriate. A wholesale framework rewrite would not address the reviewed defects and would enlarge the change surface.

Acceptance slices:
1. Env diagnostics never reproduce malformed input/credential canaries.
2. Skill sync rejects symlinks/overlap, owns only manifest-listed files, preserves unrelated user content, removes obsolete owned files, and can recover interrupted replacement. Doctor verifies generated content, not counts.
3. All HyperKanban entrypoints share semantic validation; completion checks existing contained evidence and clearly labels exceptions as unverified metadata. Canonical writes are atomic and guarded against stale revisions; packet is a recoverable derived view.
4. Dependency parser uses tomllib for supported TOML sections and reports incomplete/unparsed coverage. Security scanner inventories omissions including unsupported Windows scripts instead of passing them silently.
5. Placeholder named checks cannot report successful acceptance. Existing real verification continues to execute all tests.

Evidence: new regression tests must fail against the reviewed baseline and pass against repairs; full existing suite, CLI smoke, clean ZIP install, lint and advisory checks as applicable.
Stop conditions: genuine external access block, destructive/live effects, governance changes or incompatible evidence migration needing a separate decision.
Non-goals: new deployment runtime, broad policy changes, removal of historical artifacts, claims of Windows/hardware/offline production qualification.
Handoff: review card, Chronicle events, verification results and deferred findings. Governance refresh and production deployment remain separate review slices.
