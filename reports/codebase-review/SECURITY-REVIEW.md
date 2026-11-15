# Independent security review

Scope: baseline security-relevant Python tools plus the unfinished new deployment code. Performed by a separate review agent at the user's requested independent-review step. Temporary synthetic fixtures only; no live system changes or repository edits by the reviewer.

## Baseline findings independently confirmed

- **High:** `scripts/skills/env_secrets_manager.py:114–115` reproduces credential material from malformed keys in supposedly redacted report JSON.
- **High:** `src/workshop/skills.py:224–226` writes outside its designated target through a destination symlink. Source symlinks are dereferenced as well.
- **Medium:** `scripts/skills/dependency_auditor.py:122–129` ignores valid inline TOML dependencies and can report zero dependencies with `pass`.
- **Medium:** `scripts/skills/skill_security_auditor.py:28–31,77–84` omits PowerShell/CMD from its scan and can report `pass` without reviewing the Windows payload.

Additional observations: generated skill-cache freshness is count-based; removed helpers remain after sync; four named test/security/release scripts are no-ops; stale develop/publication language persists; mandatory per-skill issues impose avoidable process overhead. The primary reviewer clarified that `ci-local.sh` runs the real suite despite its placeholder banner.

## Separate unfinished deployment experiment

The following files are untracked WIP from before the user paused deployment. These findings are not attributed to the baseline:

1. `src/workshop/provisioning/core.py`: `plan()` does not record `helper_sha256`, but `apply()` requires it. Generated plans cannot be applied.
2. `core.py`: sending mutable script text to `sudo -n bash -s -- packages` is not an enforceable root action allowlist. A fixed root-owned helper or explicit interactive administrative session is required; broad passwordless root is unsuitable.
3. `setup/linux/docker-rootless.sh`: setuptool starts Docker before daemon configuration is written; `enable --now` does not reload that daemon.
4. `setup/offline/install.sh`: package files are verified in a caller-controlled directory, then later installed as root. Verified payloads need protected staging to prevent replacement between verification and installation; signed-entry matching also needs exact-path semantics.
5. Wi-Fi `KEEP` confirmation is local text input, not independent SSH reconnect verification. No hardware recovery test exists.

**Disposition:** do not deploy or promote this experiment. The Python language is not the underlying problem; repair the small baseline and validate privileged architecture before resuming infrastructure implementation.
