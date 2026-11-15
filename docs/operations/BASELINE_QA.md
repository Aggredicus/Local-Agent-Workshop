# Baseline component acceptance and recovery

This branch repairs the existing local CLI. It does not install Debian/Docker or qualify a release. Production deployment, policy changes and protected merges remain separately reviewed work.

## Checks

The tested installer baseline is pip 26.3. Refresh it inside the project virtual
environment with `python -m pip install --upgrade "pip==26.3"`; this does not
change the published cloud configuration or constitute a fully locked toolchain.

Activate the repository virtual environment and run:

```sh
bash scripts/test-fast.sh
bash scripts/test-full.sh
workshop skills sync
workshop doctor
```

Fast tests cover CLI, skill-cache safety and state fault handling. Full tests run the real repository validators and complete pytest suite. The scripts resolve their repository directory, so they can be invoked from elsewhere. `scripts/ci-local.sh` delegates to full verification.

`security-scan.sh` and `release-check.sh` now return **2 (unavailable)** until complete acceptance gates exist. They never report success based on placeholder output. Heuristic skill scanning and unit tests do not certify repository security or release readiness. Ruff/advisory checks remain separate development checks; this slice does not add a locked release toolchain or hardware qualification.

## Skill cache

Sync validates filesystem containment before copying. Symlinks, Windows reparse points/junctions, special files, unreadable directories and overlapping source/target trees are rejected. POSIX file permissions, including helper executable bits, are preserved. The parent directory must be controlled by the operator; this is not a sandbox against another process with the same OS account.

`.workshop-generated.json` identifies owned files, checksums and modes. Only previously owned, unmodified files can be removed as obsolete. Unrelated files are preserved. Manually modified generated files stop synchronization; copy that work aside and reconcile it with canonical `skills/` first. Unknown files inside a generated skill, or unknown discoverable skills, prevent doctor from claiming the cache is current.

A legacy `.workshop-generated` cache without an ownership manifest can be adopted only when existing canonical files match and no ambiguous legacy helper/skill content exists. Otherwise preserve the entire old cache outside `.agents/skills`, sync into a fresh directory, and review any custom content before reinstating it. Never delete unknown content merely to make doctor pass.

Sync stages a full next generation before swapping directories. A normal swap failure restores the previous generation. Hard interruption can leave `.<target>.workshop-lock`, `.<target>.workshop-backup`, or a `.<target>.stage-*` directory beside the target. Verify no sync process is active, preserve these paths, then remove only the stale lock. If the target is absent and a backup exists, the next invocation restores it before syncing. If both target and backup exist, sync stops for operator review; it does not delete an ambiguous backup. Disk-space exhaustion can make staging fail without replacing the current cache. Atomic rename behavior is filesystem-dependent; do not run this across filesystems or under a shared writable parent.

## HyperKanban

CLI, doctor, cleanup and standalone verification share semantic validation. Contradictory completion flags, bad coordinate types, cycles and required-evidence omissions fail consistently. A derived packet mismatch is also reported by validation/doctor.

State is canonical; `packet.txt` is a derived view. Writers use an exclusive lock, an expected content revision, and an atomic file replacement. Reload before changing/saving an existing state. A deleted or externally modified state invalidates a loaded revision. A packet-write failure reports that state was committed; recover the projection with:

```sh
workshop hk --state orchestration/hyperkanban/state.json repair-packet
workshop hk validate
```

Packet repair leaves canonical state unchanged and refuses an in-memory snapshot with uncommitted changes. A hard interruption may leave `.state.json.lock`; confirm no writer is active before removing a stale lock. No automatic lock eviction is attempted. This is single-host filesystem coordination, not a distributed transaction or a power-loss durability guarantee.

`hk complete --evidence PATH` resolves files relative to the current working directory, rejects missing/escaping paths, and records SHA-256 hashes. A hash identifies bytes; it does not prove the report is truthful, that a command succeeded, or that a human approved deployment. Existing `--exception` annotations remain compatible **unverified metadata**, and the CLI says so. HyperKanban never grants production authorization. Stronger exception verification requires its own reviewed contract; it is not silently introduced here.

## Manifest/security reports

Dependency inventory parses supported `project.dependencies`, optional groups and build requirements with Python's `tomllib`. Malformed or unsupported/dynamic declarations produce review findings. This remains a manifest inventory; use maintained package-manager/advisory tooling for a resolved environment and transitive dependencies.

The heuristic security scanner inventories unreviewed files, including Windows scripts it cannot analyze, oversized files, symlinks and unreadable directories. Incomplete coverage produces `review`, and `--strict` returns nonzero. Even complete heuristic coverage is not proof of safety. Reports omit malformed dotenv key contents so diagnostics do not reproduce credential-bearing input.

## Platform evidence

The local verification report names exactly what ran. POSIX mode/permission fixtures do not establish Windows execution-policy behavior; simulated reparse-point checks are not a Windows-native qualification. The existing CI matrix runs Linux Python versions. Windows CI, actual Windows launcher tests, VM firewall/reboot checks, physical Wi-Fi and offline bundle acceptance remain future deployment gates.
