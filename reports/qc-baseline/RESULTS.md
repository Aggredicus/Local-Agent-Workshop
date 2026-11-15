# Selective rebuild: first baseline slice

Branch: `agent/qc-baseline`. Reviewed base: `22fc0e72f55fa68f98f5f9ffa92127e96c7b9913`.
Implementation reviewed/tested at `ce3e030`; subsequent changes document results, installer guidance and skill audit records.

## Component acceptance

| Component | Explicit criterion | Evidence/outcome |
|---|---|---|
| Env report diagnostics | Malformed credential-bearing keys never reproduce the synthetic secret | Canary regression passes; independent redaction review found no remaining reported issue |
| Skill cache | Reject containment escapes, preserve unrelated/operator files, remove obsolete owned files, preserve executable bits, report ambiguous legacy content, recover normal failed swaps | 20 skill tests pass, including storage-failure injection and mocked Windows reparse-point rejection |
| Cache health | Inventory, hashes and POSIX modes determine currentness | Corrupt generated skill regression passes; doctor and two sync invocations pass |
| Shared state validation | CLI, doctor, cleanup and CI use the same semantic rules | One validation module replaces script/runtime duplication; cycles, bad values, typed fields and evidence presence tested |
| Canonical state updates | Reject stale/deleted snapshots and state/packet aliases; retain valid JSON after replace failure | Fault/stale-write/alias tests pass; explicit packet repair tested without changing canonical state |
| Completion artifacts | New artifact paths exist inside evidence root and receive SHA-256 identity | Missing/escaping artifacts rejected without mutating state; exception annotations explicitly remain unverified metadata |
| Dependency inventory | Parse ordinary TOML arrays, optional groups and build dependencies; malformed containers produce structured findings | Five dependency tests pass; unsupported/dynamic formats reported for review |
| Heuristic security inventory | Omitted/unreadable content cannot appear completely reviewed | Five scanner tests pass, including real POSIX unreadable-directory fixture; unsupported Windows payload reported unreviewed |
| Named check scripts | Test scripts execute tests; unavailable security/release gates cannot return success | Fast and full scripts execute their named suites; unavailable-gate exit-code tests pass |
| Installer environment | Audited current installer replaces reviewed vulnerable version | Local project pip updated to 26.3; advisory service returned no known advisories for the six resolved installer/development packages |

These are acceptance results for local helper behavior, not production/deployment authorization.

## Verification actually executed

- Before repairs: original 47-test suite passed. New redaction/cache regression run produced 9 failures; scanner regression run produced 4 failures; state fault/evidence tests exposed additional missing safety behavior. Some tests exercise newly specified interfaces; baseline missing-interface failures are not misrepresented as exploit reproductions.
- After repairs: `bash scripts/verify.sh`: **88 collected, 88 passed**, Python 3.12.14 / pytest 9.2.0. Existing test behavior retained.
- Independent final recheck: **50 focused tests passed** across skills, state safety, and three scanners. No remaining concrete blocker from the independent review's reported defects.
- `ruff check --select E4,E7,E9,F src scripts tests`: passed. Historical basic unused-import/import-bootstrap findings removed; no formatter or broad style rewrite.
- `workshop skills sync`, `workshop doctor`, `python -m pip check`, `git diff --check`: passed.
- Exported `git archive ce3e030` and extracted it to `/tmp/law-qc-zip-aodmjj6b/Extracted LAW With Spaces`; confirmed no `.git`, `setup/`, or experimental provisioning package. Fresh venv, pip 26.3, editable development installation, skill sync, doctor, full verification and dependency compatibility check all passed. **88 tests passed from this ZIP export.** Internet and a Git executable were available; this is Linux ZIP compatibility, not offline/Windows qualification.
- Invoked `scripts/test-fast.sh` by absolute path from `/tmp` with the project venv active, verifying directory-independent script behavior; 39 tests passed.
- `pip-audit --disable-pip --no-deps --cache-dir /tmp/law-review-audit-cache -r /tmp/law-qc-toolchain.txt --format json`: returned no known advisories. Raw evidence: [toolchain-audit.json](toolchain-audit.json). This excludes the OS, standard library, isolated build backend and future dependency resolutions; it is not a security guarantee.

## Independent review closure

The reviewer found unreadable inventory directories, stale writes after deletion, packet writes from uncommitted memory, invalid TOML container crashes, lost executable modes, ambiguous legacy cache adoption, missing Windows 3.11 junction detection, incomplete lock recovery documentation and state/packet alias data loss. All received code/documentation corrections and regression coverage before final recheck. Native Windows remains untested; the reparse compatibility check is static/mocked only.

## Preserved work and traceability

The unfinished deployment experiment was copied outside the checkout to `/workspace/law-paused-deployment-qsz8xcl4`, with all nine files hash-verified before removing the experimental source from the active tree. Its preservation record and historical run state are retained. This is preservation in the current workspace, not a claim of remote backup/publication.

Baseline review findings and their original reproduction script are historical evidence. That script intentionally asserted old defects at the reviewed baseline; use the regression tests for current code, rather than treating the historical script as a current acceptance suite.

Skill audit entries were appended to design-first, repo-cleanup and quality-analysis logs without changing their behavior. GitHub API still returns 403; required issue candidates are saved locally in SKILL-ISSUES.md and are not falsely described as created remotely.

## Deferred findings and limits

- R05: stronger human exception authorization is not implemented; compatible annotations remain unverified. Neither HyperKanban nor its hashes authorizes deployments.
- R09: registry validation remains metadata-only. Full schema/example enforcement needs its own acceptance slice.
- R10: complete security/release gates remain unavailable and return nonzero; they have not been replaced with superficial passing checks.
- R11/R12: conflicting merge policy, old tool workarounds and mandatory issue churn require a separate governance refresh. No policy relaxation was made.
- R14: full locked/hashes-based release toolchain, action pinning, license/notice decisions and historical distribution curation remain outstanding.
- R15: current local pip and documented installer guidance are repaired. The published cloud draft/install script was not edited, reapplied or published; future cloud tasks may still inherit its old installer unless separately updated.
- Windows-native tests, other CI Python versions, VM/physical network recovery, firmware, firewall, reboot, backups and offline deployment bundles were not qualified. No real server was contacted or changed.

Local commits and a PR body are prepared for review. GitHub API access is denied, so no remote PR, push, merge or publication is claimed. The foundation has a verified first repair slice; the entire deployment mission is not complete.
