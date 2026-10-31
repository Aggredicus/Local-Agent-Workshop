# CAW–LAW Architecture Split — QA Report

Status: **review-stage, NOT a production release**  
Date: 2026-10-31

## Traceability
- CAW collaborative/contract changes: https://github.com/Aggredicus/Codex-Agent-Workshop/pull/3
- LAW local runtime changes: https://github.com/Aggredicus/Local-Agent-Workshop/pull/192
- CAW canonical contract: `contracts/caw-law-work-packet.v1.json`
- LAW runtime: `src/workshop/local_registry.py`, `src/workshop/caw_contract.py`

## Verified by automated checks
| Environment | Evidence | Result |
|---|---|---|
| CAW Python 3.11–3.14 | CI run 41236116734 | All matrix jobs passed |
| LAW Python 3.11–3.14 | CI run 41236073067 | All matrix jobs passed |
| LAW ↔ CAW pinned contract and fixture | CI run 41236073065 | Passed |
| LAW version reset with real CAW taxonomy | CI run 41236073065 | Passed |
| Offline work packet | CI run 41236073065 | Validated; execution remains disabled |
| Privacy-scoped skill inventory consistency | CAW CI run 41236116734 | Passed |

## Positive invariants
- CAW has no duplicate active local SQLite registry.
- Only CAW has the canonical v1 contract schema and skill taxonomy. LAW loads reviewed file paths and has no runtime network dependency.
- LAW keeps node data in a Git-ignored SQLite database, and tracks agent origin/version digests.
- Changing a declared agent origin clears current skill claims and invalidates pending proposals.
- No claimed local role/identity translates into GitHub approval/merge rights.
- Work packet validation rejects unknown fields, unsupported schema versions, unsafe paths, and self-declared approval states.
- All LAW execution plans are data-only and explicitly deny execution.
- Coarse hardware probing does not collect hostnames, serials, MAC addresses, IPs, or usernames.

## Unverified / outstanding
1. **High — licensing/provenance:** LAW's default branch has no detected LICENSE file; CAW code was relocated from a GPLv3-covered repository. Confirm compatible release licensing and preserve attribution before merge.
2. **High — enforceable sandbox:** No OS-level isolation runner exists in this PR. Current plan adapter must NEVER be described as enforcing filesystem, network, or credentials.
3. **High — authenticated agent identity:** Source/version/digest are self-declared, not cryptographically attested. Privileges remain denied pending trusted approval.
4. **Medium — human review:** Independent fresh-context functional review and separate security review are still needed.
5. **Medium — offline multi-host workflow:** No coordinated real-time state sync or conflict-resolution test across two physical computers; each SQLite database is local.
6. **Medium — mobile/browser:** Public gateway requires independent mobile, keyboard, screen-reader and file:// testing before publication.
7. **Medium — governance convergence:** LAW's skill invocation protocol generates improvement issues on every use, while CAW uses evidence-triggered improvements. Decide and implement a shared governance rule in a separate reviewed policy change.

## Rollback
Do not merge both PRs before reviewing the two-repo transition and license. To roll back a pre-merge proposal, close both PRs; no production runtime, credential policy, or public profile has been altered. After a hypothetical approved merge, use revert PRs with their related CI and data migration checks. Local SQLite files are private and unaffected by closing a PR.

## Review dispositions
- Functional smoke and CI: **passed** for checked features.
- Independent reviewer: **not completed**.
- Security boundary: **not complete**; execution intentionally disabled.
- Publication/merge: **blocked pending human review and licensing decision**.
