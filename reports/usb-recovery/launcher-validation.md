# Location-independent Windows launcher

The user requested startup without manual policy commands or a Downloads-folder assumption. START-USB.cmd now asks Y/N approval before starting one native Windows PowerShell process with RemoteSigned. It unblocks exactly the bootstrap and two tool scripts, resolves paths literally, and retains administrator-enforced restrictions. Saved policy is unchanged; per-file unblocking persists and is disclosed. The staged Windows installation includes the same entry point for later Wi-Fi entry.

Local evidence: 109 pytest tests pass; selected Ruff checks pass; changed PS1 files and the CMD inline bootstrap parse successfully with PowerShell 7.6.10; workflow YAML and its Windows test dependency validate; git diff --check passes. Preflight cleanup: 0 blockers, 1 warning for authorized main; implementation moved to agent/usb-launcher. Native Windows tests, main integration and public ZIP verification are pending and must be recorded before a working download is claimed.

Windows test design: execute the real CMD/bootstrap against stub tools in a different current directory, with spaces, apostrophes, brackets, ampersands and exclamation marks in the extraction path; downloaded-file zone markers; inherited Restricted process policy. Check N leaves files untouched, Y runs with process RemoteSigned and preserves saved policies, unrelated scripts stay blocked, missing files fail before menu execution. No real WLAN, credentials or USB device is involved.

Follow-up: physical boot, WLAN and restricted ACL behavior remain unqualified. This launcher test is narrower than a complete Windows product acceptance test. Reversal uses a normal commit revert; no releases are overwritten.

Skill audit: GitHub API access is still unavailable in this running environment, so the following are durable local issue drafts, not remotely created issues. Corresponding no-change improvement logs were appended; no skill behavior changed.

- **Improve /repo-cleanup after USB launcher update.** Skill used for preflight/closeout. Observation: main warning is resolved by an implementation branch with explicitly authorized integration after checks. Action: log-only update. Artifact: skills/repo-cleanup/IMPROVEMENT_LOG.md. Scope: audit documentation, low risk.
- **Improve /quality-analysis after USB launcher update.** Skill used for baseline/final acceptance. Observation: Linux PowerShell parsing cannot qualify Windows execution policy; native Windows CI should gate the downloadable candidate. Action: log-only update. Artifact: skills/quality-analysis/IMPROVEMENT_LOG.md. Scope: audit documentation, low risk.
