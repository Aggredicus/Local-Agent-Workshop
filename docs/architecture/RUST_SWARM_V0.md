# LAW independent Rust swarm — implementation record

## Decision / authorship scope

LAW v0.1 is an independent implementation of general event-driven system patterns: messages, state reconstruction, parallel workers, deduplicated input, and independent tool execution. It is **not** derived from Infinity code, does not use its traits or wire formats, and adds no dependency on Infinity's crates. The original code is in `rust/law-swarm/`, with no third-party Cargo dependencies. Rust std APIs and common systems algorithms are not exclusive to this project. This development process examined architectural concepts before writing original code; it should not be called a formal clean-room procedure.

## Requirements and observable acceptance tests

1. `submit` writes a checksum-verified, fsynced event before reporting success.
2. Repeated identical `submit` calls do not create duplicate jobs; conflicting IDs fail.
3. `drive` executes safe built-in operations; terminal jobs do not re-execute.
4. Events within one conversation stay in acceptance order. Different conversations may run in parallel when their targets differ.
5. One SSH worker can process an explicitly assigned job using an existing, validated host-key trust relationship. The worker never starts a TCP listener.
6. A process restart replays persisted state. Interrupted attempts are retried, bounded to three attempts.
7. A malformed record fails closed; an incomplete final record is discarded.
8. No shell, filesystem mutation, package installation, network probing, secret access, or model API tool can be invoked through an untrusted task.
9. Original Rust unit and CLI integration tests run in the Rust CI job.

## Modules

- `protocol.rs`: validated identities, compact hex/UTF-8 worker request/response, fixed tool enum.
- `runtime.rs`: original event journal, in-memory projection, per-thread serialization, bounded fan-out and replay.
- `transport.rs`: safe built-in tools and fixed-command SSH standard I/O transport.
- `main.rs`: CLI with explicit state and target selection.

## Design trade-offs

The v0.1 transport uses SSH and a fixed command instead of unauthenticated HTTP. This inherits mature host-key, encryption, and account authentication features without shipping our own cryptography. Each worker is one process per job. The worker cannot receive arbitrary remote commands. The coordinator has no continuously running scheduler: operators explicitly call `drive` to dispatch queued work. No GPU, LLM, Docker, or general-purpose tool use is included yet.

The journal is single-writer and append-only with CRC32 integrity checks, not a transactional database. It uses `writer.lock` as a sentinel; after an abnormal exit, human inspection is needed to clear a stale sentinel. A crash after remote execution but before the outcome is recorded can repeat a job; all v0.1 tools are deterministic and free of external side effects. We must NOT extend the tool list to mutating effects before implementing durable leases, authorizations, outbox/inbox delivery, external idempotency, and sandboxing.

## Independent functional and security review checklist

- **Functional:** replay, duplicate-ID behavior, ordered thread work, budget bounds, concurrent distinct targets, stdout framing, remote error propagation, interruption handling, and incomplete journal tails.
- **Security:** reject malicious host arguments, reject unknown tool IDs, reject malformed wire frames, deny shell commands, validate length limits, disallow unauthenticated network servers, ensure GitHub secrets are never sent to workers, and never execute code from job payload.
- **Deployment:** SSH fingerprints must be verified out-of-band before use, and remote worker PATH must be set explicitly. Never disable host-key verification.

## Rollback

Delete the feature branch or revert the Rust crate/CI/doc additions. No prior LAW operational source files, schema registries, state artifacts, or protected branches are modified by the initial implementation.

## Next release increments

1. Wire a Rust facade into `workshop` CLI and Chronicle / HyperKanban, emitting evidence-linked job events.
2. Replace manual peer target selection with signed or SSH-attested node capability reports and deterministic scheduling.
3. Replace the sentinel and append log with transactionally durable storage and lease fencing; introduce bounded per-node resource reservations.
4. Add local `ModelProvider` adapters, first with a mock model and then real local inference, without introducing a cloud requirement.
5. Add sandboxed, human-governed tools in isolated worktrees; preserve the approval boundary before each side effect.
6. Build a responsive visualization/dashboard with read-only access before permitting browser control of jobs.
