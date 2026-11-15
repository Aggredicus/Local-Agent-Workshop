# Selective baseline rebuild — first repair slice

Branch: agent/qc-baseline, from reviewed 22fc0e72f55fa68f98f5f9ffa92127e96c7b9913.

[Acceptance results](../../reports/qc-baseline/RESULTS.md) · [PR packet](../../reports/qc-baseline/PR.md) · [Recovery guide](../../docs/operations/BASELINE_QA.md)

Changes: safe redaction; staged/owned cache with containment and mode preservation; shared state validator; atomic revision-checked canonical writes and explicit packet repair; contained artifact hashes; TOML parsing and honest scan coverage; real fast/full checks; unavailable security/release gates fail closed.

Evidence: 88 local tests pass; 88 from clean source ZIP with spaces/no .git; independent focused recheck 50 pass; selected Ruff, doctor, sync, pip check and current resolved dependency advisory audit pass.

Known limits: no native Windows/hardware/production tests; state/packet remain separate writes with recovery; same-account hostile processes are outside filesystem-lock guarantees; hashes/exceptions are not authorization; full release/security gates and schema-example enforcement remain unavailable. Governance and release-toolchain work is deferred explicitly.

GitHub API access returned 403; no remote PR or publication. Existing protected branches unchanged. Review source before any main merge. The unfinished provisioning experiment is preserved outside the checkout and not included in application source.
