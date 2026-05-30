#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Deterministic mock injection audit ==="
cd "$KIT_DIR"

if [ ! -f "outputs/phase2b4_confusion_deterministic.json" ]; then
    echo "ERROR: confusion_deterministic.json not found."
    echo "Run the full pipeline to generate it:"
    echo "  python3 src/phase2b4_mock_injection.py --config-dir configs/ --mock-dir mocks/ --out outputs/"
    exit 1
fi

echo "Pre-computed mock confusion matrix found:"
python3 -c "
import json
with open('outputs/phase2b4_confusion_deterministic.json') as f:
    d = json.load(f)
print('Overall pass:', d.get('overall_pass', 'unknown'))
print('Verdicts:')
for k, v in d.get('verdicts', {}).items():
    print(f'  {k}: {v}')
"

echo ""
echo "Running validation test..."
python3 -m pytest validation/test_mock_injection_confusion.py -v || python3 validation/test_mock_injection_confusion.py

echo "=== Done ==="
