#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
exec python -m pytest tests/test_cli.py tests/test_skills.py tests/test_state_safety.py
