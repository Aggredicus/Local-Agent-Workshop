# Authorized main integration and downloadable test candidate

User explicitly requested all today's work on GitHub, authorized a release-asset download, then said: "Lets actually change main."

Fetched main: 22fc0e72f55fa68f98f5f9ffa92127e96c7b9913; usb-recovery is four commits ahead with no divergence. Integrate by fast-forward, preserving history and all existing main content. No forced push or branch-protection bypass is authorized.

Verification: 109 tests pass; selected Ruff checks pass; workflow YAML/action pins/branch permissions and embedded shell syntax checked. New offline test driver exercises fresh and repeated installs in network-disabled Debian 12/13 containers. Existing GitHub CI for USB source commit 4e5cc16 completed successfully. Results of the new GitHub build/publish workflow must be checked independently before claiming a download exists.

Workaround for the environment's failed reapply UI: native Git transport can push code. A narrowly scoped main-push workflow uses read permission for testing/building and a separate write-permission job only for release publication. No secrets are passed into package-builder containers. GitHub's own job token is used only in the publish step; no personal token is requested or stored.

The workflow rebuilds signed package closures, tests installation and repetition without networking, pins/verifies the Windows age tool, packs one ZIP, verifies its CRC/SHA256, uploads to a draft prerelease, downloads the uploaded ZIP and verifies it before making the prerelease visible. Source commit and test records accompany the asset. It never edits an existing release or marks the candidate as latest/stable.

Known limits remain explicit: native Windows WLAN/ACL behavior, real USB/Secure Boot, firmware and physical Wi-Fi recovery are not qualified. This is a testing download, not a production-ready server deployment or bootable ISO. The environment recovery UI itself is not repaired by this workaround.

Rollback: revert the delivery workflow commit through normal reviewed Git history if required; do not erase existing source commits or user work. No real server or physical USB writes occur.
