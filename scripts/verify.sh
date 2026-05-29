#!/usr/bin/env bash
set -euo pipefail

echo "Running Local Agent Workshop verification"

python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json
python -m pytest
