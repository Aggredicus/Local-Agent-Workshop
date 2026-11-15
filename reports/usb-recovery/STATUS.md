# USB recovery handoff

Current download: [updated USB tools ZIP](https://github.com/Aggredicus/Local-Agent-Workshop/releases/download/usb-recovery-849445738b19/LAW-USB-Tools.zip). Extract the ZIP, open `LAW`, double-click `START-USB.cmd`, and approve startup. The launcher works from the extracted folder without manual PowerShell commands or saved policy changes. Native Windows PowerShell 5.1 launcher, C# compilation and synthetic encrypted credential round-trip checks and the rebuilt Debian offline checks pass. Delivery/hash evidence: [published result](../publish/usb-overnight-download-2026-11-15.json). This supersedes the original workspace artifact below; Wi-Fi/ACL and physical boot qualification remain outstanding.

## Original build record

Branch: agent/usb-recovery, based on the repaired qc-baseline.

Prepared artifact: /workspace/artifacts/LAW-USB-Tools.zip (112,418,470 bytes).
SHA256: bc1b13aea251d09857088bf357e7d5070d0d427a298bc02f7a7ea58786626aca

Contains Windows per-user staging/credential entry, pinned age 1.3.2 executable/license, Debian 12/13 amd64 authenticated offline recovery packages, read-only inspection, root-local controller, device-paired encrypted credential transfer, explicit configuration approval, timed file recovery and a single operator guide. Does not contain an ISO, private key or operator credentials. This data ZIP is not bootable by itself. Use operator-prepared Ventoy plus an independently verified official Debian DVD-1 ISO.

Verification: 109 pytest tests passed; selected Ruff checks passed; real PowerShell 7.6.10/Linux C# compilation and synthetic UTF-8 credential encryption/decryption round trip passed. Both bundles' InRelease->Packages->deb chains and complete recovery dependency closure reverified during packaging with networking disabled. Offline installation/repetition evidence is in offline-tests.json. Installer uses fixed roots, never installs arbitrary extra cached packages, does not install SSH server/Docker/NetworkManager, and never removes existing packages.

Independent security review identified package-set/completeness, code-integrity, sender-substitution, output-race, expiry, scope, concurrency and old-association issues; corrections and regression tests were added. The review agent hit its usage limit before a complete final re-review, so no complete independent sign-off is claimed.

Not tested: native Windows 5.1 execution/ACLs/WLAN API, physical USB boot, Secure Boot, live Wi-Fi adapters/firmware, systemd timer firing on a real host, or real network deactivation/boot persistence. Timed rollback has tested file-restoration behavior and requests disconnection; network stop remains unverified. No real server or physical USB was modified.

cdimage.debian.org returned proxy 403, so no ISO was downloaded, signature-verified or boot-tested here. The guide directs Windows-side download and authenticated upstream verification. Firmware is not guessed; identify the actual adapter when ThinkCentre2 is powered on.

User wants to conserve tokens after the usage limit. Stop expanding scope. Next physical steps: verify/extract ZIP on Windows, stage trusted tools locally, prepare Ventoy/verified Debian ISO if boot media is needed, copy LAW data folder, then use installed Debian normally for recovery. First Debian trip installs verified tools/controller and exports only a public pairing request. Windows enters credentials locally and exports only encrypted data. Returning USB code is not executed: use the root-owned Debian controller and locally staged Windows helper. Do not paste credentials into chat.
