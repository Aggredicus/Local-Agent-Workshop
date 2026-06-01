#!/usr/bin/env bash
set -euo pipefail

echo "Running Local Agent Workshop verification"

python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json
python scripts/validate_repo_contracts.py
python -m pytest
