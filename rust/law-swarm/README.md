# LAW Swarm — original Rust foundation (v0.1)

This is an independently authored event-driven worker prototype for **Local Agent Workshop**. It shares architectural ideas that are common to asynchronous systems (message inboxes, durable events, stateless workers, serialized per-conversation execution), **not source code, identifiers, or wire compatibility** with Infinity. This crate has **no third-party Cargo dependencies**.

**What works:** durable append-only event journal with CRC32 corruption detection; recoverable submitted jobs; replay-safe task IDs; ordered tasks per conversation; bounded, parallel dispatch across different targets; a strict three-tool worker; SSH stdio transport with host-key verification; no listening sockets or shell tools; Rust unit/integration tests.

**What is not built:** model inference, GPU scheduling, container isolation, distributed consensus, persistent distributed reservations, device discovery, authenticated worker capability attestations, skill/voting governance enforcement, headless 24/7 scheduler, or a live phone dashboard. This is not yet a production AI swarm. Input tools are intentionally side-effect-free so retry after coordinator crash is safe.

## Requirements

Rust 1.80+ and Cargo on the coordinator and each worker. For remote work: SSH installed, a pre-paired host key, key-based noninteractive login, and `law-swarm` on the remote worker's PATH. The coordinator invokes only the fixed remote command `law-swarm worker`.

```bash
cargo test --manifest-path rust/law-swarm/Cargo.toml
cargo build --release --manifest-path rust/law-swarm/Cargo.toml
# This path is relative to the repo root:
./rust/law-swarm/target/release/law-swarm init --state ~/.law-swarm-state
```

Set the program on each machine's PATH before using remote commands. For example, you can install locally using `cargo install --path rust/law-swarm --locked` (or copy the built release binary to a private `~/.local/bin/`).

## One-node demonstration

```bash
law-swarm submit --state ~/.law-swarm-state --id example1 --thread research --target local --tool word-count --input 'hello from a local agent'
law-swarm submit --state ~/.law-swarm-state --id example2 --thread reviewer --target local --tool sum --input '3, 7, 9'
law-swarm drive --state ~/.law-swarm-state --parallel 2 --budget 10
law-swarm status --state ~/.law-swarm-state
```

Re-running the same `submit` ID with exactly the same contents is a no-op. Re-running `drive` does not execute terminal jobs again.

## Two-node demonstration (pre-paired SSH)

1. Build or install `law-swarm` on both Linux computers.
2. Manually verify the remote host's SSH fingerprint using a trusted channel; establish SSH keys in advance. Do **not** set `StrictHostKeyChecking=no`.
3. Verify the fixed remote command: `ssh user@192.168.1.20 'law-swarm advertise'`.
4. On the coordinator, submit and dispatch:

```bash
law-swarm submit --state ~/.law-swarm-state --id remote1 --thread agentA --target ssh:user@192.168.1.20 --tool uppercase --input 'distributed hello'
law-swarm submit --state ~/.law-swarm-state --id local1 --thread agentB --target local --tool word-count --input 'hello from our second job'
law-swarm drive --state ~/.law-swarm-state --parallel 2 --budget 10
law-swarm status --state ~/.law-swarm-state
```

There is no public service. The remote worker consumes one validated request on stdin and emits one response on stdout. This prototype does **not** discover peers or schedule workloads based on hardware yet; targets are selected explicitly.

## Persistence and crash recovery

`events.lawlog` is an append-only, checksummed event journal under the selected state directory. Each write is flushed before the next action; replay rebuilds the in-memory task index. A torn final record is discarded; corruption of a completed record fails closed. The `writer.lock` sentinel prevents two cooperative coordinators from opening the same state. **After a hard crash, inspect that no writer process remains before manually deleting an orphaned `writer.lock`.** This sentinel is not a robust cross-host locking mechanism.

A crash between dispatch and callback may cause a job to execute again on restart. That is why v0.1 only permits side-effect-free builtins. This is *at-least-once execution with deduplicated terminal state*, not universal exactly-once semantics. After three interrupted attempts the job fails closed. Do not add filesystem, network mutation, shell, or credential tools without durable leases, idempotency controls, and LAW permission enforcement.

## Security boundary

- SSH is the only cross-machine transport; the caller enforces known-host verification and noninteractive authentication.
- Fixed allowlisted operations: `uppercase`, `word-count`, `sum`. No arbitrary command path can come from a job.
- Task, response, and journal records have byte limits and validated identities.
- The journal checksum detects corruption; it is **not cryptographic authentication**.
- State directory permissions depend on the host; protect this directory and avoid placing sensitive data in job inputs.
- Remote SSH account privileges are **not sandboxed by this program**. Use dedicated least-privilege accounts for future expansion.

## Design principles and authorship

All Rust source, tests, and wire formats in this crate were generated specifically for LAW from an original design. The implementation does not import or adapt source files from the Infinity repository. Rust standard library types and long-established concurrent-systems concepts are used. Copyright and exclusive human authorship have legal nuances for AI-assisted code; the project makes no claim to another project's source material.
