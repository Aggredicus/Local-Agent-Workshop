#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

echo "Running Local Agent Workshop verification"

python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json
python scripts/validate_repo_contracts.py
python -m pytest
