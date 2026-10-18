#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JOB="${1:-/tmp/ss_jobs/golden}"
[ ! -e "$JOB" ] || { echo "Choose a new job path (existing data is preserved)" >&2; exit 1; }
mkdir -p "$(dirname "$JOB")" && cp -r "$ROOT/golden/flowmap_2610.20674" "$JOB"
cd "$ROOT"
python3 -m pipeline.stages.lint "$JOB"
SS_RENDER_MODE=trusted_golden python3 -m pipeline.runner "$JOB"
python3 -c "import json,sys; d=json.load(open('$JOB/out/validation.json')); [print(c['passed'], c['name'], c['detail']) for c in d['checks']]"
ls -la "$JOB/out"
python3 tools/verify_golden.py "$JOB"
