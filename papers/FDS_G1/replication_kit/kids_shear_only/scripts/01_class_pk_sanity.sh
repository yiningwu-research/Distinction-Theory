#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== CLASS Pk sanity check ==="
cd "$KIT_DIR"

# Run smoke test
python3 src/run_stage3_smoke_tests.py
echo "Smoke test complete."

# Run mock generator test
python3 src/make_stage3_mock.py
echo "Mock generator test complete."

echo "=== CLASS Pk sanity PASS ==="
