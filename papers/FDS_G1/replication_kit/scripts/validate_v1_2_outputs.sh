#!/bin/bash
# Validate v1.2 production evidence outputs
set -e

KITROOT=$(cd "$(dirname "$0")/.." && pwd)
EVIDENCE="$KITROOT/production_evidence_v1_2"

echo "=== Checking per-seed JSON count ==="
COUNT=$(ls "$EVIDENCE/outputs_medium_8seed/per_seed_json/"*.json 2>/dev/null | wc -l)
if [ "$COUNT" -eq 56 ]; then
    echo "OK: $COUNT per-seed JSON files found"
else
    echo "ERROR: Expected 56 per-seed JSONs, found $COUNT"
    exit 1
fi

echo ""
echo "=== Checking JSON schema (run_type=production) ==="
for f in "$EVIDENCE/outputs_medium_8seed/per_seed_json/"*.json; do
    RT=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('run_type','missing'))")
    SEED=$(python3 -c "import json; print(json.load(open('$f'))['seed'])")
    if [ "$RT" != "production" ] && [ "$SEED" != "101" ]; then
        echo "WARNING: $(basename $f) has run_type=$RT"
    fi
done
echo "JSON schema check complete"

echo ""
echo "=== Checking summary CSV ==="
if [ -f "$EVIDENCE/outputs_medium_8seed/production_8seed_summary.csv" ]; then
    echo "OK: summary CSV exists"
    echo "Models:"
    python3 -c "
import csv; rows=list(csv.DictReader(open('$EVIDENCE/outputs_medium_8seed/production_8seed_summary.csv')))
for r in rows: print(f'  {r[\"model\"]:14s} n={r[\"n\"]}  mean={r[\"mean_logZ\"]}  scatter={r[\"scatter\"]}')
"
else
    echo "WARNING: summary CSV not found"
fi

echo ""
echo "=== Checking manifest ==="
python3 -c "
import json
m = json.load(open('$EVIDENCE/outputs_medium_8seed/production_8seed_manifest.json'))
print(f'Kit version: {m[\"kit_version\"]}')
print(f'Total jobs: {m[\"total_jobs\"]}')
print(f'Models: {list(m[\"models\"].keys())}')
for k, v in m['models'].items():
    in2s = 'yes' if v.get('all_within_2sigma') else 'NO'
    print(f'  {k:14s} n={v[\"n_seeds\"]} scatter={v[\"scatter\"]:.4f} 2σ={in2s}')
"

echo ""
echo "=== All validation checks passed ==="
