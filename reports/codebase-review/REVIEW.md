# LAW foundation review and rebuild recommendation

Reviewed 2026-11-15. Baseline: `22fc0e72f55fa68f98f5f9ffa92127e96c7b9913` (latest local published checkout; commit dated 2026-08-29). Branch used for the session: `agent/debian-deployment`.

**Decision: selectively reuse LAW after baseline repairs. Do not accept it as an existing deployment or security enforcement platform.** Keep the small Python CLI, canonical instruction entrypoint, and useful tests. Repair state validation, cache handling, and diagnostic safety before adding operational authority. Simplify the skills through a separately reviewed governance change. Build infrastructure features around maintained tools and explicit platform acceptance tests.

The age of the code is not the deciding factor. The review found specific problems in correctness, assurance, and policy consistency. A language or framework rewrite alone would preserve those problems in a new form.

## Scope and method

The user redirected the original deployment task to a full foundation review. Deployment implementation is paused. No provisioning, SSH pairing, firewall change, publication, push, or merge was performed. No tracked application, test, dependency, lockfile, or governance file was changed during this review.

The baseline contains 163 tracked files, 2,606 lines of Python application/helper code, and 739 test lines. The installed CLI implements only `doctor`, `skills`, and `hk`. There is no baseline Windows launcher, SSH controller, Docker installer, application deployment service, operational dashboard, backup engine, or offline release pipeline.

Reviewed the active CLI and all Python/shell helpers, their test suite, packaging and CI, schemas and registry, canonical instructions, branch/review/skill contracts, documentation consistency, and runtime capability claims. Executed clean-source installation and adversarial probes. An independent agent reviewed security-relevant baseline code and the unfinished deployment experiment. Archived ZIPs were inventoried as historical artifacts; their embedded code was not executed or certified. This is a code and readiness review, not a penetration test or formal security certification.

Evidence:

- [Inventory](inventory.json)
- [Repeatable adversarial probes](reproduce.py) and [observed results](reproductions.json)
- [Schema checks](schema-audit.json)
- [Static analysis](lint.json)
- [Resolved development dependency audit](dependency-audit.json)
- [Installer/toolchain audit](toolchain-audit.json)
- [Independent security review](SECURITY-REVIEW.md)
- [Commands and outcomes](VALIDATION.md)

## Findings requiring repair before operational reuse

Severity reflects the prospective deployment role. The current CLI does not expose a network service; these findings do not establish remote compromise of a deployed LAW server.

### R01 — High: a redacted report can disclose credential material

**Source:** [env_secrets_manager.py](../../scripts/skills/env_secrets_manager.py#L111), especially lines 114–115.

Malformed dotenv input is split at the first `=`. An invalid key is interpolated verbatim into the report finding. A connection URL such as `https://operator:SYNTHETIC-CANARY-NOT-A-SECRET@example.invalid/key=value` therefore copies the synthetic password into JSON, despite the normal value field being redacted.

**Evidence:** `env-report-redaction` reproduced; independently confirmed. No live credential was used.

**Repair/acceptance:** Never reproduce arbitrary malformed input in diagnostics. Emit category, file and line only. Test URLs, multiline input, malformed keys, parser exceptions, reports and stderr with synthetic canaries. Apply redaction across the report path rather than just valid values.

### R02 — High: skill sync escapes its designated filesystem boundary

**Source:** [skills.py](../../src/workshop/skills.py#L220), lines 224–226.

`copytree(..., dirs_exist_ok=True)` follows an existing destination directory symlink. Sync writes outside its requested target. Source symlinks are dereferenced and can copy external file contents into the agent discovery cache. This matters when processing externally supplied skill trees or a cache writable by another local process. It is not evidence that a remote attacker currently controls either directory.

**Evidence:** `sync-destination-symlink` and `sync-source-symlink` reproduced with temporary canaries; destination escape independently confirmed.

**Repair/acceptance:** Reject symlinks and source/target overlap, resolve and enforce containment, validate the complete source tree before copying, and stage an owned generation. Tests must demonstrate that no out-of-tree canary is read, copied or overwritten. Do not treat imported skills as trusted merely because their metadata validates.

### R03 — Medium: sync retains removed code and doctor gives false assurance

**Source:** [skills.py](../../src/workshop/skills.py#L204); [doctor.py](../../src/workshop/doctor.py#L50).

Sync overlays the target; deleting a canonical helper does not remove its generated copy. Entire removed skills can also remain. Doctor equates equal inventory counts with synchronization, without comparing names, validity or contents. An invalid generated skill with the correct count receives `PASS`.

**Evidence:** `stale-generated-helper`, `doctor-count-only-cache-check` reproduced.

**Repair/acceptance:** Track tool-owned files in a generation manifest, replace only owned content, preserve unrelated user content, and compare validated inventories/hashes. Test deletion, rename, changed metadata, stale files and interrupted synchronization.

### R04 — Medium: different entrypoints disagree about valid project state

**Source:** [runtime validator](../../src/workshop/hyperkanban/state.py#L67), [CI validator](../../scripts/validate_hyperkanban.py#L164), [cleanup checks](../../scripts/repo_cleanup.py#L127).

Runtime validation omits axis value/type and dependency-cycle checks that CI performs. CI omits completion-evidence checks that runtime performs. Cleanup adds another partial interpretation. A self-cycle and invalid coordinate pass runtime validation; done-without-required-evidence passes the standalone CI validator.

**Evidence:** Three `validator-disagreement-*` probes reproduced. These are isolated entrypoint checks; the report does not claim every malformed fixture also passes the whole test suite.

**Repair/acceptance:** One validation implementation shared by CLI, doctor, cleanup and CI. Add table-driven malformed input tests and require identical verdicts. Define consistency between flags and coordinate state, typed dependencies, cycles, supported schema versions, and packet derivation.

### R05 — Medium: completion evidence is metadata presence, not verification

**Source:** [state.py](../../src/workshop/hyperkanban/state.py#L125), especially `completion_has_evidence_or_exception` and `complete_card`.

Any nonempty evidence list or exception list satisfies the gate. A nonexistent path completes a contracted card. An arbitrary exception string does not establish that a human approved it. This lightweight metadata model must not authorize a deployment, release or security-sensitive transition.

**Evidence:** `nonexistent-completion-evidence` reproduced; existing tests intentionally permit string-only review exceptions.

**Repair/acceptance:** Define what evidence proves: existing contained artifact, command/result, reviewed commit and target identity as appropriate. Bind exceptions to an independently reviewed record. Keep HyperKanban a projection; it must not become an authorization database. Mere path existence would still not prove test success.

### R06 — Medium: state writes are not recoverable transactions

**Source:** [state.py](../../src/workshop/hyperkanban/state.py#L52), lines 52–64.

State JSON is overwritten, then packet.txt is overwritten separately. A storage failure between them leaves a committed state and stale packet. There is no lock or optimistic revision check for competing writers. Concurrency loss is a code-level risk; only the partial-write scenario was exercised here.

**Evidence:** `partial-state-commit` reproduced by injecting a packet-write failure into temporary fixtures.

**Repair/acceptance:** Make one artifact canonical and regenerate its projection; atomically replace canonical state with a revision check/lock and a clear recovery procedure. Test interruption, failed writes and two competing writers before runtime orchestration uses this state.

### R07 — Medium: dependency auditing silently misses valid TOML

**Source:** [dependency_auditor.py](../../scripts/skills/dependency_auditor.py#L115), lines 122–129.

Line-oriented regular expressions miss standard `dependencies=["requests"]` declarations. A valid project with this declaration and license metadata reports zero dependencies and `pass`. Nested requirements and lockfiles are also not resolved; these latter limitations are partially documented.

**Evidence:** `inline-toml-dependencies` reproduced and independently confirmed. LAW's own inline dev-dependency declaration is outside this parser's supported pattern.

**Repair/acceptance:** Use Python 3.11's `tomllib`, supported requirement parsing, and explicit coverage/unsupported-format reporting. Use maintained ecosystem advisory tools for resolved dependencies. Test inline/multiline arrays, optional groups, build dependencies, direct references, nested files and malformed manifests. Keep a manifest inventory if useful; do not present it as a vulnerability audit.

### R08 — Medium: security auditing silently excludes Windows scripts

**Source:** [skill_security_auditor.py](../../scripts/skills/skill_security_auditor.py#L28), lines 28–34 and 77–84.

`.ps1`, `.cmd`, `.bat`, extensionless files and files above the size limit can be omitted without a skipped-file inventory. A directory containing SKILL.md and a PowerShell `Invoke-Expression` fixture receives `pass` while only SKILL.md is scanned. The documented heuristic disclaimer does not make this acceptable evidence for the proposed Windows launcher.

**Evidence:** `powershell-omitted` reproduced and independently confirmed.

**Repair/acceptance:** Inventory every file, report unreviewed content explicitly, and make incomplete security coverage distinct from pass. Use maintained language-aware checks where possible. Preserve manual security review; a handful of regexes cannot certify imported code or prompt-injection resistance.

## Assurance and process gaps

### R09 — Documented scope gap: registry validation does not validate contracts

**Source:** [validate_repo_contracts.py](../../scripts/validate_repo_contracts.py#L175), [validation-gate non-goals](../../docs/protocols/REPO_VALIDATION_GATE.md).

The gate checks registry metadata and referenced path existence, not the syntax of schema files or the validity of their examples. A referenced file containing `not JSON at all` passes the metadata checks. **This limitation is explicitly documented; it is not an undisclosed implementation defect.** It becomes a blocker if used as proof of deployment-manifest validation.

**Evidence:** `unparsed-schema-file` demonstrates the limitation. Separately, an independent Draft 2020-12 validator accepted all nine current schema documents and validated the current registry and HyperKanban state. Those checks are not currently integrated into CI. 6 of the nine schema documents have no corresponding non-planned registry entry.

**Recommendation:** Keep the offline metadata check, add actual schema/example validation with a local reference registry, and name each check accurately. Do not reject deliberately planned missing schemas as implementation bugs.

### R10 — High assurance gap: successful placeholder security/release checks

**Source:** [security-scan.sh](../../scripts/security-scan.sh), [release-check.sh](../../scripts/release-check.sh), [test-fast.sh](../../scripts/test-fast.sh), [test-full.sh](../../scripts/test-full.sh).

These scripts print placeholder text and return zero without executing their named checks. `verify.sh` is real and runs validation plus pytest. `ci-local.sh` has a placeholder banner **but delegates to real verification**; it must not be grouped with the four no-op checks.

**Recommendation:** Implement a meaningful gate or return a clearly unavailable/non-success result. A production release must not interpret a placeholder's exit code as acceptance evidence.

### R11 — High policy risk: instructions conflict and discourage commit-bound review

**Source:** [me.md](../../me.md), [branch policy](../../docs/governance/BRANCH_POLICY.md), [merge-review protocol](../../docs/protocols/MERGE_REVIEW_PROTOCOL.md), [merge-review skill](../../skills/merge-review/SKILL.md).

The spine/branch policy requires human approval for protected-branch merges, while merge-review instructions describe an autonomous low-risk lane targeting an allowed integration branch. Current integration is protected `main`. The restrictive canonical rule remains binding; the overlapping exception should be resolved explicitly.

Merge instructions also recommend omitting an expected head SHA to avoid historical tool-layer problems. That weakens the binding between the reviewed commit and a later merge if the PR changes. This is a procedural TOCTOU risk, not a reproduced unauthorized merge.

Quality-analysis still references `develop → main` publication and review workflow retains `promote to develop`, contradicting the trunk migration. Correct authority is available, but agents should not repeatedly arbitrate stale rules.

**Recommendation:** One authoritative merge/approval contract, explicit handling of standing authorization, and expected-commit checks where supported. Preserve human approval for this project's infrastructure and protected branches. Changes require a reviewed governance patch; none were made here. Current hosted branch-protection settings could not be checked because GitHub API access returned 403; historical documentation does not establish today's enforcement.

### R12 — Medium process cost: skill invocation causes mandatory issue churn

**Source:** [skills/README.md](../../skills/README.md#L5), lines 7–42; [automation-loop cost controls](../../docs/protocols/AUTOMATION_LOOP_PROTOCOL.md).

Every invocation requires both an improvement issue and a durable skill edit/log update, even when nothing needs improving. The loop elsewhere says to avoid low-value issue spam. This adds GitHub dependence to a local-first workflow and makes a read-only review generate maintenance work unrelated to its findings.

**Recommendation:** Propose one compact run audit record; create issues only for actionable lessons after deduplication. Keep skills as concise task-specific guidance over current agent tools. Retain the canonical instruction spine and meaningful approvals. This is a proposed governance change, not permission to ignore the existing rule.

### R13 — Medium quality gap: green tests do not cover the proposed safety boundary

**Source:** [tests](../../tests), [CI](../../.github/workflows/ci.yml), [pyproject.toml](../../pyproject.toml).

All 47 tests pass and many are useful functional/negative checks. However, doctor has one missing-repository test; cleanup tests mostly validate reporting with the collector mocked; there is no dedicated test module for the registry validator. Existing cache tests exercise additive copying, not deletion/containment/interruption. No Windows runner, source-ZIP job, package-distribution smoke job, static-analysis gate, advisory audit, or real security scan is configured. Linux CI declares four Python versions, but only 3.12 was run in this session.

Ruff found seven basic diagnostics: two unused imports and five import-order findings caused by test path bootstrapping. These are low-priority cleanup, not the reason to rebuild.

**Recommendation:** Keep the real tests and add failure-focused acceptance tests. Test evidence must name the target/platform and distinguish unit, integration, VM and hardware checks. No coverage percentage or mutation-testing result is claimed.

### R14 — Medium reproducibility/distribution gap

**Source:** [pyproject.toml](../../pyproject.toml), [CI](../../.github/workflows/ci.yml), imported skill provenance and tracked root ZIPs.

Runtime has no third-party Python dependencies, a valuable property. Development/build requirements are open ranges (`pytest>=8`, `setuptools>=68`), with no locked resolved toolchain/hashes. CI action tags are mutable and workflow token permissions are not declared explicitly. Three historical source ZIPs coexist with the active source; they are small historical artifacts, not verified offline distributions. Project license metadata/full license file is absent, while adapted wrappers contain upstream attribution and declare MIT provenance. That is a redistribution review gap, not a legal conclusion.

**Recommendation:** Keep flexible library metadata where appropriate, but lock and audit the reproducible developer/release toolchain. Declare least-privilege CI permissions, pin actions to reviewed SHAs, establish license/notice handling, and label historical archives. Preserve audit/history artifacts until a separate cleanup decision; do not delete them as a cosmetic cleanup.

### R15 — Environment finding: bundled pip has reported advisories

The prepared virtual environment uses pip 25.0.1, inherited from venv bootstrapping. The five resolved development packages (pytest, iniconfig, packaging, pluggy, pygments) returned no known advisories. Including the installer produced 12 advisory records for pip, representing **six distinct advisory IDs**, with overlapping/duplicate records. They include CVE-2025-8869, CVE-2026-1703, CVE-2026-3219, CVE-2026-6357, CVE-2026-8643 and CVE-2026-13346. Reported fixes range through pip 26.2/26.2.0. Some require malicious archives/indexes or other preconditions; no exploitation was attempted or established.

**Recommendation:** Update and pin the installer toolchain in the later setup/remediation change, then rerun the audit. This review did not silently upgrade the published environment or reapply its configuration. The runtime standard library, OS, build-isolation setuptools download, archived code and all possible future dependency resolutions are outside this audit result. An empty advisory result is not a security guarantee.

## What to keep, repair, replace or retire

| Component | Decision | Acceptance before reuse |
|---|---|---|
| Python 3.11+ and `workshop` CLI shell | Keep and reshape | Preserve compatible commands; ZIP and wheel smoke; predictable errors/exit codes |
| `me.md` canonical entrypoint and thin agent adapters | Keep | One coherent approval policy; no duplication of operational authority |
| Existing 47 tests | Keep and expand | Add adversarial regression cases; platform-specific CI |
| Skill discovery and generated cache | Repair | Containment, complete inventory, safe owned replacement, accurate freshness |
| Duplicate skill selectors | Consolidate | One tested implementation; thin compatibility wrappers for scripts; consistent metadata parsing |
| HyperKanban read-only views | Keep after validation repair | Shared validator, malformed input parity, projection stays advisory |
| HyperKanban mutations/evidence gate | Redesign narrowly | Recoverable writes, revision checks, explicit evidence semantics; no deployment authority |
| Dependency/security regex scanners | Retain only as labeled hints, or replace | Structured parsing; maintained audits; honest coverage/unsupported states |
| Placeholder test/security/release checks | Replace or mark unavailable | A positive outcome must prove a meaningful executed check |
| Design/review/cleanup skills | Simplify through review | Concise risk-based guidance using current tools; actionable findings rather than mandatory issue churn |
| Chronicle, review cards and examples | Keep the concepts | Define minimal validated records; historic examples remain examples, not executed runtime evidence |
| Planned supervisor/grind/dashboard systems | Defer until independently justified | Demonstrated need beyond the agent platform; explicit supported commands |
| Historical ZIPs and duplicated root docs | Label and reconcile | Preserve history; a single current source/install guide |
| New deployment experiment from this session | Preserve as unfinished reference | Reassess after the foundation review; no direct promotion to production |

## Recommended branch and implementation strategy

Use a fresh short-lived branch from the **exact reviewed baseline commit**, preserving ordinary Git history. A branch starts with the baseline's files; cleanliness comes from deliberate reviewed changes, not an empty orphan branch or a mass deletion.

1. **Review package:** this report and reproductions; no feature rollout. Keep the current untracked deployment experiment separate from the change selected for any review PR. No new branch, commit or PR was created in response to the user's recommendation question.
2. **`agent/qc-baseline`:** regression tests for R01–R08, then fixes; shared validators; meaningful check outcomes; installer/dependency audit and CI. Each fix is a small reviewable commit. Require zero new regressions and explicit passing negative tests.
3. **`agent/governance-refresh`:** reconcile approval rules, remove obsolete tool workarounds and unsupported-command claims, propose proportionate skill audit requirements. Human review is required for these policy changes.
4. **Deployment design decision:** compare a thin LAW orchestration layer against maintained declarative provisioning tooling, measuring Windows startup burden, offline packaging, privileged code size, recovery, repeatability and maintenance cost. Ansible is a candidate backend to evaluate, not a dependency selected merely by habit. Do not invent a general orchestration framework.
5. **Independent deployment slices:** Windows ZIP launcher/inspection → SSH trust/pairing → rootless Docker → one restricted application → backup/rollback → USB/network recovery → offline packaging. Each slice has tests and a review boundary. The original mission remains the destination; it is not declared complete by this review.

Suggested acceptance policy: no acceptance without an identified owner, supported platforms, failure/rollback behavior, actual test evidence, known limitations and a clear privilege boundary. Skills advise agents; executable controls enforce security. Model/tool improvements should reduce repetitive scaffolding, not replace reproducible local operations or OS access control.

## Unfinished work and external limits

New untracked files in `src/workshop/provisioning/` and `setup/` were written before the user requested review-first. They are excluded from baseline findings and not integrated into the CLI. Independent inspection found a plan/helper-hash mismatch, unconstrained root-shell escalation, Docker startup/configuration ordering, and offline verification race issues. They have no acceptance tests yet and must not be used on ThinkCentre2. See the separate security review. Preserve them as reference, not as a reusable engine.

No Windows-native test, physical network/Wi-Fi/firmware test, reboot recovery test, Docker firewall test, or offline provisioning acceptance test was performed. A disposable Debian 12 image was pulled and its version read before deployment was paused; that is not provisioning evidence. GitHub API access was denied, so open-PR ownership, live protections, and issue creation could not be verified. Git read access worked. No GitHub account or token is requested for finishing this local review.

No fixes, policy relaxations, deployment, environment configuration changes or publication are implied by accepting this report. The next decision is the remediation/rebuild scope, informed by the component table above.
