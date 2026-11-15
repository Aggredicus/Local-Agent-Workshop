Title: Repair reviewed CLI safety defects before rebuilding deployment
Base: main
Head: agent/qc-baseline

The foundation review found that malformed env diagnostics could leak credential material, skill sync could escape its cache and retain obsolete code, state validators disagreed, and several named checks reported success without performing validation.

This change preserves the existing CLI and history while adding manifest-owned staged skill synchronization, accurate cache checks, shared state validation, revision-checked atomic canonical writes with explicit packet recovery, contained artifact identity checks, TOML parsing, and honest heuristic scan coverage. Fast/full scripts now execute tests; unavailable security/release qualification returns nonzero. Regression tests cover the identified failure cases and additional defects caught by independent review.

Validation: 88 tests pass locally and from a fresh no-.git ZIP under a path containing spaces; selected Ruff checks pass; doctor, skill sync and dependency compatibility pass. Independent recheck ran 50 focused tests with no remaining blocker from its reported defects. Updated local pip 26.3 and the resolved development packages return no known advisories.

Scope and limitations: no deployment code, real-server changes, policy relaxation or cloud publication. Windows handling is mocked/static rather than natively qualified. HyperKanban exceptions and evidence hashes never establish human authorization. Complete schema/example validation, security/release qualification, governance refresh, and fully locked release tooling remain separate work. See reports/qc-baseline/RESULTS.md and docs/operations/BASELINE_QA.md.

GitHub API returned 403 in this environment; this is a local PR packet, not an opened PR. Human approval remains required before merging into main.
