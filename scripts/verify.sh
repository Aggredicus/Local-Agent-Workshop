#!/usr/bin/env bash
set -euo pipefail

echo "Running Local Agent Workshop verification"
python -m pytest
