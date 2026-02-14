#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

EVERY_INTERVAL="${1:-12h}"

python3 skills/memory-mesh-core/scripts/ensure_openclaw_cron.py \
  --workspace "$ROOT_DIR" \
  --job-name "memory_mesh_sync" \
  --every "$EVERY_INTERVAL" \
  --run-now
