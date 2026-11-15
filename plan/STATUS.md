# Current status

Use **main** for the accepted code and normal downloads. Work happens on one short-lived task branch and returns to main after its authorized checks. `develop` is retained historical state; `experimental` is the sandbox.

- **USB download:** [LAW-USB-Tools.zip](https://github.com/Aggredicus/Local-Agent-Workshop/releases/download/usb-recovery-f164824e23fd/LAW-USB-Tools.zip). Extract, open `LAW`, double-click `START-USB.cmd`, approve startup. Works relative to its folder without manual policy commands. [Guide](../setup/usb/README.md) · [verified delivery](../reports/publish/usb-launcher-download-2026-11-15.json).
- **Accepted tools:** Python 3.11+ CLI, canonical skills and generated client cache, deterministic skill selection, shared HyperKanban validation, recoverable state updates, explicit offline package verification and encrypted Wi-Fi transfer.
- **Verified:** source tests/CI, native Windows PowerShell 5.1 launcher, signed Debian 12/13 package closure and network-disabled install/repetition. These are distinct test scopes.
- **Still physical:** USB/Secure Boot, adapter firmware, Windows WLAN/ACLs, Debian networking and timed rollback on the real machines. No installer ISO is included.
- **Separate work:** open deployment, Rust swarm, runtime adapter and recursive-QA PRs retain their unique code; they are not prerequisites for the USB tools. Historical branch cleanup is recorded under [overnight quality](../reports/overnight-quality/).

For a compact health check:

```sh
workshop doctor --summary
bash scripts/verify.sh --quiet
```

Agents start with [me.md](../me.md). Use [docs navigation](../docs/NAVIGATION_INDEX.md) for the task's relevant contracts and [baseline recovery](../docs/operations/BASELINE_QA.md) for cache/state recovery. Historical reports describe their original commits and may not represent current status.
