# Morning report — 2026-11-15

The completed changes are on **main**. Use main for normal work; old branches are not needed to run the accepted tools.

## USB download

[Download LAW-USB-Tools.zip](https://github.com/Aggredicus/Local-Agent-Workshop/releases/download/usb-recovery-c61153454d53/LAW-USB-Tools.zip).
Extract anywhere, open `LAW`, double-click `START-USB.cmd`, and approve startup.
The launcher uses a process-only policy, honors enforced policy, and locates its scripts relative to itself. Saved execution policies are unchanged; its prompt discloses the persistent unblock of the three included script files.

The native Windows checks cover startup, real staging into a disposable child profile, private current-user ACLs, existing-install preservation, the staged menu, C# compilation, and synthetic UTF-8 age encryption/decryption. They caught and fixed the Windows framework reference problem before final delivery. [USB guide](../../setup/usb/README.md) · [final delivery verification](../publish/usb-final-download-2026-11-15.json).

If tools were staged from an earlier ZIP, follow the guide's backup-and-restage instructions. The ZIP supplies LAW tools and Debian offline recovery packages. Ventoy and an independently verified Debian installer ISO are separate downloads.

## Repository results

| Area | Result |
|---|---|
| Branch clarity | 56 original remote branches reduced to 14. Removed 42 fully merged obsolete refs, saved their exact heads, and removed the temporary overnight branch after integration. All 11 unique-work branches and four open PR heads were preserved. No history was rewritten. |
| Routine output | Verification output reduced from 2,997 to 544 characters: **81.8% less**, with the same checks, warnings, failures and exit semantics. Doctor also has an opt-in summary. These are character measurements, not tokenizer measurements. |
| Security/correctness | Rejected unsafe linked/special-file reads, invalid encodings, escaping registry paths and malformed indexes; improved error reporting without echoing private example values. |
| State quality | Shared validated snapshots replace duplicate cleanup parsing; iterative graph validation handles 2,000-node chains and was checked against all 512 three-node directed graphs. |
| Verification | **206 Python tests pass** across CI's Python 3.11–3.14 matrix, plus shared native Windows PowerShell 5.1 acceptance. Pinned Ruff and offline schema checks run before pytest. |
| Contracts | Three implemented registered schemas, one registered example and 29 references checked offline using maintained libraries. Unregistered artifacts and additional format assertions are outside that coverage. |
| Supply chain | Pinned CI actions and development tools; read-only test tokens and no persisted checkout credentials. Advisory audit found no known vulnerabilities among 13 installed development packages; OS/build-backend and other interpreter variants are outside that audit. |
| Portability | Fresh no-Git source-ZIP installation passed in a folder containing spaces, an apostrophe and brackets. The workshop runtime still has no third-party dependencies. |
| Documentation | Replaced stale setup-branch status, corrected navigation, and aligned remaining develop/main routing with the existing canonical branch policy. Approval requirements were preserved. |

Evidence: [pass 1](PASS-1.md), [pass 2](PASS-2.md), [pass 3](PASS-3.md), [branch inventory](branches-before.json), [final branches](branches-final.json), [output measurement](final-output-size.json), [ZIP installation](clean-zip-install.json).

## What still needs the machines

Physical USB/Secure Boot, actual Wi-Fi adapters and firmware, Windows machine-specific policy/permissions, and Debian association/reconnection/rollback need hands-on tests. The CI crypto tests used synthetic data and invoked no Wi-Fi APIs. No live credentials or real device configuration were used.

Complete security/release qualification is not claimed: the explicitly unavailable broad acceptance scripts still fail rather than reporting false success. Existing unmerged experiments and historical evidence were preserved. GitHub API access remained blocked here, so skill-improvement issue drafts are recorded locally rather than claimed as remote issues.

Source CI: [43746969700](https://github.com/Aggredicus/Local-Agent-Workshop/actions/runs/43746969700). Full USB build/publication: [43746969701](https://github.com/Aggredicus/Local-Agent-Workshop/actions/runs/43746969701). Both passed. The public ZIP was downloaded and checked against its SHA256, ZIP CRC, all 223 manifest entries, every packaged source file at the exact source commit, and the pinned age.exe digest.

ZIP SHA256: `dd1b93c1897662d5f460365632edb1cef2d84b8c663d2d3fc541fd708c8a0cf3`.

The next operator action is the USB guide, starting with the newly downloaded Windows tools and powering on Debian for pairing and adapter checks.
