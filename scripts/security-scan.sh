#!/usr/bin/env bash
set -euo pipefail
# A heuristic skill scan is not a complete repository/security qualification.
echo 'UNAVAILABLE: a complete repository security gate is not configured.' >&2
echo 'Run the documented static/advisory checks and independent review; do not treat this command as security acceptance.' >&2
exit 2
