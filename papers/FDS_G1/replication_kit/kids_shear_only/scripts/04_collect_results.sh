#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Collect KiDS results ==="
cd "$KIT_DIR"

python3 src/collect_kids_results.py --output-dir outputs
python3 src/plot_kids_diagnostics.py --confusion outputs/phase2b4_confusion_deterministic.json --outdir figures

echo ""
echo "Outputs:"
ls -lh outputs/phase2b_summary_table.csv outputs/phase2b4_confusion_deterministic.csv
ls -lh figures/
echo "=== Done ==="
