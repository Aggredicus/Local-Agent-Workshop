# Pass 3: maintained verification tools and final USB publication

Added pinned development-only Ruff, jsonschema and referencing tools. The installed workshop runtime still has no third-party dependencies. Shared verification now runs Python correctness lint and actual registered schema/example checks before pytest, in both output modes. Plain metadata-only contract validation remains standard-library-only for constrained machines.

The schema extension checks implemented registered schema definitions, duplicate IDs, reference targets and registered examples. A deny-retrieval registry permits only preloaded resources; no arbitrary file or HTTP retrieval occurs. Maintained schema traversal distinguishes actual schema references from reference-like annotation data. Evaluation errors omit example values. Unsupported dialects, missing tools, cyclic evaluation and excessive parser nesting fail explicitly. Format annotations are not additional format assertions; unregistered files remain outside coverage.

Evidence: **188 local tests pass**, including new extension acceptance cases and failure injection through the lint gate; selected Ruff checks and dependency compatibility checks pass. Canonical registry result: schema-content-validation.json. Current development environment advisory audit covers 13 packages and reports no known vulnerabilities: development-tool-advisories.json. This does not cover the OS, isolated build backend or every supported interpreter's dependency variant. New remote Python-matrix/Windows CI must pass before this slice is integrated.

The corrected USB candidate from source 849445738b19663e30bc6dbae0d4d6fae98f73ae was published by run 43716290683 after shared native Windows startup/compilation/synthetic crypto, source and Debian offline gates passed. Downloaded the public ZIP and verified its SHA256, CRC, all 223 manifest entries, every one of its 30 packaged source files against that exact commit, and the pinned age.exe digest. Delivery evidence: ../publish/usb-overnight-download-2026-11-15.json. Existing releases were preserved.

Hardware limits remain: real Wi-Fi/firmware, restricted Windows ACLs, USB/Secure Boot and physical network rollback need powered-on machines. Existing staged Windows tools can be preserved and restaged using the guide's upgrade instructions. No real credentials or device configuration were used in these checks.

Closeout hardening adds explicit failure for malformed legacy skill indexes,
non-finite JSON literals, malformed schema metadata and invalid resource IDs.
Legacy reports now name the JSON index files actually checked. Source CI has a
15-minute timeout. The final local suite is **202 passing tests**; the prior
188-test source passed CI 43718034591 and a fresh no-Git ZIP installation in a
folder containing spaces, an apostrophe and brackets. Compact fresh-install
evidence is in clean-zip-install.json and clean-zip-verify.txt.
