#!/usr/bin/env bash
set -euo pipefail
echo 'UNAVAILABLE: release acceptance criteria and platform qualification are not configured.' >&2
echo 'This repository must not infer release readiness from unit tests alone.' >&2
exit 2
