#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Reproduce Phase 2B summary ==="
cd "$KIT_DIR"

echo ""
echo "Step 1: Warm-start profiler (m-only)"
echo "  python3 src/warmstart_profile.py m34 --config configs/stage3_kids1000_xipm_270_config_cuts_mdz.yaml"
echo "  (Requires CLASS + KiDS data vector. See data/README_DATA.md)"
echo ""

echo "Step 2: Aggregating existing outputs"
python3 src/collect_kids_results.py --output-dir outputs
echo ""

echo "See outputs/phase2b_summary_table.csv for results"
echo "See outputs/phase2b{1,2,3}_summary.md for detailed per-phase narratives"
echo "=== Done ==="
