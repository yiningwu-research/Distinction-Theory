#!/usr/bin/env bash
#
# Start Phase 1A and 1B parallel execution
#
# Usage: ./start_phase1.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "============================================================"
echo "  FDS-G1 CMB-LENSING: PHASE 1 LAUNCH"
echo "============================================================"
echo ""
echo "Phase 1A: CLASS backend validation"
echo "Phase 1B: ACT forward-operator validation"
echo ""

# Check virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Activated existing virtual environment"
elif [ -d ".venv-integration-test" ]; then
    source .venv-integration-test/bin/activate
    echo "✅ Activated integration test environment"
else
    echo "⚠️  No virtual environment found"
    echo "   Creating fresh environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[test]"
fi

echo ""
echo "Environment info:"
echo "  Python: $(python3 --version)"
echo "  NumPy: $(python3 -c 'import numpy; print(numpy.__version__)' 2>/dev/null)"
echo "  SciPy: $(python3 -c 'import scipy; print(scipy.__version__)' 2>/dev/null)"
echo ""
echo "CLASS installation check:"
python3 -c "import classy; print('✅ classy version:', getattr(classy, '__version__', 'installed'))" 2>/dev/null || \
    echo "⚠️  classy not installed. CLASS backend will be skipped."
echo ""
echo "ACT installation check:"
python3 -c "import act_dr6_lenslike; print('✅ act_dr6_lenslike installed')" 2>/dev/null || \
    echo "⚠️  act_dr6_lenslike not installed. ACT validation will be skipped."

echo ""
echo "============================================================"
echo "  STARTING PHASE 1A: CLASS BACKEND VALIDATION"
echo "============================================================"
echo ""

python3 scripts/run_class_validation.py 2>&1 | tee outputs/class_validation/v0.2.0/phase1a.log || true

echo ""
echo "============================================================"
echo "  STARTING PHASE 1B: ACT FORWARD-OPERATOR VALIDATION"
echo "============================================================"
echo ""

python3 scripts/run_act_validation.py 2>&1 | tee outputs/act_validation/v0.3.0-rc1/phase1b.log || true

echo ""
echo "============================================================"
echo "  PHASE 1 EXECUTION COMPLETE"
echo "============================================================"
echo ""
echo "Outputs:"
echo "  outputs/class_validation/v0.2.0/"
echo "  outputs/act_validation/v0.3.0-rc1/"
echo ""
echo "Next: Review logs and validation reports."
echo "If gates passed, proceed to Phase 2 (four-point ACT/PR4 run)."
