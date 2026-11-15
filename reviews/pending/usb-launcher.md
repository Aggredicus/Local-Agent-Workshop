# USB launcher: explicit consent and location-independent startup

User requested a launcher to handle the scripts-disabled error from any extraction folder, then asked whether copy/paste instructions were necessary. They are not: a CMD entry point can start a single PowerShell process after approval. Existing authorization covers main updates and the GitHub ZIP download; no environment configuration or stable release is being published.

Inputs: START-USB.cmd, setup/usb/Prepare-USB.ps1, setup/usb/README.md, USB download workflow. Scope: launcher, local staging, instructions, Windows integration test and the ZIP delivery gate. Implement on agent/usb-launcher; integrate into main only after Windows validation. No Wi-Fi credential use, policy persistence, physical disk writes or hardware changes.

Acceptance criteria:

- Double-click startup asks permission; declining runs no scripts and leaves file blocks intact.
- Approval uses process-only RemoteSigned, honors enforced policy, unblocks only the three included PS1 files, and preserves saved policies.
- Extraction paths with spaces, apostrophes, brackets, ampersands and exclamation marks work from a different current directory.
- Missing required scripts fail before the menu runs; unrelated scripts remain blocked.
- Locally staged tools include the launcher for later trusted Wi-Fi entry.
- Native Windows tests gate the rebuilt GitHub ZIP; source checks pass; the public asset is downloaded and checked before offering its link.

Baseline: cleanup reports 0 blockers, 1 warning for main, explicitly authorized by the user. Medium risk because downloaded script approval behavior changes; keep consent and file unblocking visible. GitHub API access remains blocked here; Actions and public HTML/downloads supply build and delivery evidence. Hardware/WLAN/ACL qualification remains outside this launcher test.

Stop if source/native launcher tests fail, saved policy changes, or release verification fails. Reversal: revert this focused commit through normal Git history; existing releases remain intact. Final evidence and follow-up decisions will be recorded below after validation.

Final source gate: 109 tests and lint pass; native Windows approval, cancellation, special-character paths, downloaded-file handling, missing-file rejection and policy-preservation checks pass in run 43711812696 on 7df6a75. Initial Windows missing-file failures were corrected before main integration. Branch cleanup: 0 blockers, 0 warnings. Evidence and blocked-API skill issue drafts: reports/usb-recovery/launcher-validation.md. Ready for the already-authorized main update and rebuilt test-candidate download; public asset verification remains required before claiming delivery. No new human decision is needed for that authorized scope.
