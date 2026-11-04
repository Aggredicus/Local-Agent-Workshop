# Rust Swarm Original Implementation — Review Packet

issue: independent Rust swarm architecture implementation requested in chat
role: implementation and independent review preparation
branch/worktree: `agent/rust-swarm-original-v0`
base branch: `main`
risk: medium (new executable and local/SSH coordination; no live deployment)

## Objective

Introduce a from-scratch Rust agent-execution foundation without importing or adapting Infinity source code. Demonstrate durable event records, per-conversation work order, bounded parallel tasks, an allowlisted worker, and authenticated transport by relying on pre-paired OpenSSH.

## Changed files

- `rust/law-swarm/{Cargo.toml,LICENSE,README.md}`
- `rust/law-swarm/src/{lib,main,protocol,runtime,transport}.rs`
- `rust/law-swarm/tests/cli.rs`
- `.github/workflows/rust-swarm.yml`
- `docs/architecture/RUST_SWARM_V0.md`
- `chronicle/events/event-rust-swarm-original-v0.json`

## Evidence required

- Rust CI: `cargo test --manifest-path rust/law-swarm/Cargo.toml --all-targets`
- Rust CI: `cargo clippy --manifest-path rust/law-swarm/Cargo.toml --all-targets -- -D warnings`
- Rust CI: `cargo fmt --manifest-path rust/law-swarm/Cargo.toml --all` (formatting pass in CI workspace)
- Manual security inspection: tool allowlist, SSH fixed command, no public network listener
- Existing LAW Python verification: `bash scripts/verify.sh` (unchanged by this patch)

## Risks and skipped verification

- A local Rust compiler is not installed in the authoring runtime, so local compilation and Rust tests could not be run prior to the commit. GitHub Actions is the planned test executor; do not claim passing results until they are observed.
- The initial coordinator is explicitly driven from CLI; agent LLM inference is not connected yet.
- The SSH user has ordinary account privileges on the target, so a later mutating tool would require a new sandbox and enforceable permissions.
- CRC32 detects corruption, not tampering. Journal directory permissions and backups are operator responsibilities.
- An orphan lock may remain after crashes; manual inspection is required for recovery.
- Consistent format is generated on the CI runner, but a future revision should commit `cargo fmt` changes before merge.

## Human decision needed

Review the technical boundaries and CI evidence, then decide whether to approve merging this **initial foundation**, rather than treating it as a finished autonomous swarm. Do not merge protected `main` automatically.
