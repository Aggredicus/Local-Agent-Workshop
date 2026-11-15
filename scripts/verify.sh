#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

if [[ $# -gt 1 || ( $# -eq 1 && $1 != --quiet ) ]]; then
  echo "Usage: bash scripts/verify.sh [--quiet]" >&2
  exit 2
fi
contract_args=()
test_args=()
if [[ ${1:-} == --quiet ]]; then
  contract_args=(--quiet)
  test_args=(-q)
fi

echo "Running Local Agent Workshop verification"

python scripts/validate_hyperkanban.py orchestration/hyperkanban/state.json
python scripts/validate_repo_contracts.py "${contract_args[@]}"
python -m pytest "${test_args[@]}"
