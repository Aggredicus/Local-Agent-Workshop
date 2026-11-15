# Validation record

Baseline commit: `22fc0e72f55fa68f98f5f9ffa92127e96c7b9913`.
Host Python: 3.12.14. Project pytest: 9.2.0. Audit tools installed separately in `/tmp/law-review-tools`: Ruff 0.17.5, pip-audit 2.10.1, jsonschema 4.26.0. Review tools were not added to project dependencies.

## Commands executed and actual outcomes

From `/workspace/Local-Agent-Workshop`, with `.venv` activated:

```sh
workshop doctor
python scripts/repo_cleanup.py --phase before
bash scripts/verify.sh
```

Doctor passed. Initial checkout was clean; cleanup: 0 blockers, 0 warnings. Verification: HyperKanban validation passed; registry metadata check reported 0 errors, 0 warnings, 9 planned-path informational messages; pytest executed **47 tests, all passed**.

Exported the baseline with `git archive --format=zip HEAD`, then extracted it to `/tmp/law-baseline-review-b60zh93s/Extracted Source With Spaces`. Confirmed `.git` was absent. This was a source export, not a worktree. In that extracted directory:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
source .venv/bin/activate
workshop --version
workshop skills validate
workshop skills sync
workshop doctor
bash scripts/verify.sh
python -m pip check
```

Editable installation succeeded. CLI reported 0.1.0; 11 skills validated and synced, with 7 legacy skills normalized in the generated cache. Doctor passed. **47 tests executed and passed** again. Dependency compatibility check passed. This demonstrates ZIP-without-Git-history installation on Linux with Git/Python already installed and internet available; it does not demonstrate Windows or offline installation.

In the exported baseline:

```sh
/tmp/law-review-tools/bin/ruff check --select E4,E7,E9,F --output-format json src scripts tests
```

Exit 1: seven diagnostics (two F401, five E402). See `lint.json`. No automatic fixes were applied.

Used `jsonschema.Draft202012Validator.check_schema` on all nine schema documents and a local-only `referencing.Registry` for references. Validated the current schema registry against registry.schema.json and current HyperKanban state against hyperkanban-state.schema.json. All nine schemas were well-formed; both artifacts validated. See `schema-audit.json`. This was an additional review check, not a baseline CI capability.

From the actual checkout:

```sh
python reports/codebase-review/reproduce.py
```

Exit 0: **13 diagnostic probes reproduced the observed weaknesses/scope limitations**. Eight baseline defect groups are covered; one probe illustrates the explicitly documented metadata-only scope of registry validation. These are defect-confirmation assertions, not 13 product acceptance passes. Fixtures were temporary; no real secret was read. The script is intended for this reviewed baseline and may stop confirming defects once they are fixed.

Audit of the resolved virtual environment dependencies:

```sh
python -m pip freeze --exclude-editable > /tmp/law-review-requirements.txt
/tmp/law-review-tools/bin/pip-audit --disable-pip --no-deps --cache-dir /tmp/law-review-audit-cache -r /tmp/law-review-requirements.txt --format json --timeout 20 -o reports/codebase-review/dependency-audit.json
```

Exit 0: no known advisories returned for the five listed third-party development packages. The first attempt without `--cache-dir` failed because the home cache directory is read-only; the supported writable cache override resolved that tool setup failure.

Including installer tooling:

```sh
python -m pip freeze --all --exclude-editable > /tmp/law-review-toolchain-requirements.txt
/tmp/law-review-tools/bin/pip-audit --disable-pip --no-deps --cache-dir /tmp/law-review-audit-cache -r /tmp/law-review-toolchain-requirements.txt --format json --timeout 20 -o reports/codebase-review/toolchain-audit.json
```

Exit 1: pip 25.0.1 had 12 returned advisory records, representing six distinct advisory IDs. See the raw audit for aliases, descriptions and fix versions. No exploit or upgrade was performed. Local package excluded as editable; Python/OS/build-isolation environment were not audited. No claim of vulnerability-free software is made.

CLI capability checks in the extracted baseline:

```sh
workshop --help
workshop design-first example
workshop grind resume example
```

Help shows only doctor, skills, hk. Both documented future/design workflow command examples returned argparse exit 2 (invalid choice). No deployment/setup command exists in the baseline.

Git access checks:

```sh
git ls-remote origin HEAD
gh api repos/Aggredicus/Local-Agent-Workshop/pulls --method GET -f state=open -f per_page=30
```

Native Git read succeeded. GitHub API returned 403 Forbidden. Open PRs, current hosted protection settings, and permission to create issues/PRs could not be established. No token was printed or requested. Docker documentation HTTPS request also returned proxy 403; dependency advisory requests to the allowed PyPI service did work. No broad network-health conclusion follows from these different destination results.

Closeout:

```sh
python scripts/repo_cleanup.py --phase after --format json --out reports/codebase-review/cleanup-after.json
git diff --exit-code
git status --short
```

Cleanup had 0 blockers and 1 warning for intentionally untracked review/experimental files. `git diff --exit-code` returned 0: tracked files unchanged. The new review artifacts and paused deployment files remain untracked on `agent/debian-deployment`. No commit, push, PR, merge, publication, or cloud environment draft update occurred during the review.

## Not executed

- Windows-native PowerShell/CMD or Windows CI.
- Other CI Python versions (3.11, 3.13, 3.14).
- Deployment integration, offline package installation, Wi-Fi, firmware, SSH lockout recovery, firewall/IPv6, reboot or physical ThinkCentre2 tests.
- Full dependency/source/archive provenance certification, OS audit, formal proof, penetration test, or exploit validation.
- Lint autofix, application repairs, or governance changes.
