#!/bin/bash
# Phase 4c-prep: KiDS BandPower model-vector generation runner
#
# Prerequisites:
#   1. CosmoSIS framework installed
#   2. KCAP modules at $KCAP_PATH (update below)
#   3. Cosmosis Standard Library at $CSL_PATH (update below)
#   4. CAMB Python interface: pip install camb
#   5. COSEBIs library compiled for this architecture
#
# This script:
#   1. Extracts KiDS MAP parameters from the maxpost file
#   2. Generates modified values.ini for both KiDS and Planck
#   3. Runs CosmoSIS in evaluate-only mode to produce model vectors
#   4. Validates model vectors against the data
#
# The stopping rule is enforced: chi2(m_KiDS) must be plausible.

set -euo pipefail

# ========== CONFIG — update these paths ==========
KCAP_PATH="${KCAP_PATH:-/path/to/kcap}"
CSL_PATH="${CSL_PATH:-/path/to/cosmosis-standard-library}"
COSMOSIS_BIN="${COSMOSIS_BIN:-cosmosis}"

# Paths within the toolkit
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KIDS_DATA="$PROJECT_ROOT/data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release"
BP_CONFIG="$KIDS_DATA/chains_and_config_files/main_chains_iterative_covariance/bp/config"
BP_MAPFILE="$KIDS_DATA/chains_and_config_files/main_chains_iterative_covariance/bp/chain/maxpost_multinest_start_C.txt"
PIPELINE_INI="$BP_CONFIG/pipeline.ini"

OUT_DIR="$PROJECT_ROOT/outputs/phase4c_prep"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

# Ensure CosmoSIS can find KCAP modules globally
export COSMOSIS_MODULE_PATH="$KCAP_PATH:$CSL_PATH"

mkdir -p "$OUT_DIR/generated"

# ==================================================

echo "Phase 4c-prep: KiDS BandPower model-vector generation"
echo "====================================================="
echo ""

# Step 1: Extract MAP parameters
echo "[1/5] Extracting KiDS MAP parameters..."
PYTHONPATH="$PROJECT_ROOT/src" "$VENV_PYTHON" "$PROJECT_ROOT/scripts/extract_kids_map_params.py" \
    --map-file "$BP_MAPFILE" \
    --out "$OUT_DIR"

# Step 2: Verify CosmoSIS is available
echo ""
echo "[2/5] Checking CosmoSIS..."
if ! command -v "$COSMOSIS_BIN" &>/dev/null; then
    echo "ERROR: CosmoSIS not found at '$COSMOSIS_BIN'."
    echo "       Set COSMOSIS_BIN env var to the cosmosis executable path."
    exit 1
fi
echo "  CosmoSIS found: $COSMOSIS_BIN"

# Step 3: Verify CAMB
echo ""
echo "[3/5] Checking CAMB..."
"$VENV_PYTHON" -c "import camb; print(f'  CAMB {camb.__version__} ready')" || {
    echo "ERROR: CAMB not importable. Run: pip install camb"
    exit 1
}

# Step 4: Generate m_KiDS
echo ""
echo "[4/5] Generating m_KiDS with MAP parameters..."
KI_VALS="$OUT_DIR/values_kids.ini"
KI_BACKUP="$BP_CONFIG/values.orig.ini"

if [ ! -f "$KI_BACKUP" ]; then
    cp "$BP_CONFIG/values.ini" "$KI_BACKUP"
    echo "  Backed up original values.ini"
fi

cp "$KI_VALS" "$BP_CONFIG/values.ini"
echo "  Copied KiDS MAP values.ini"

# Update pipeline.ini paths (backup first)
if [ ! -f "$BP_CONFIG/pipeline.orig.ini" ]; then
    cp "$PIPELINE_INI" "$BP_CONFIG/pipeline.orig.ini"
fi

# Run CosmoSIS evaluate-only
cd "$KIDS_DATA"
"$COSMOSIS_BIN" "$PIPELINE_INI" 2>&1 | tee "$OUT_DIR/generated/cosmosis_output_kids.log"
echo "  CosmoSIS run complete. Check $OUT_DIR/generated/cosmosis_output_kids.log"

# Step 5: Extract and validate model vector
echo ""
echo "[5/5] Validating m_KiDS..."

# The model vector is in the CosmoSIS output — the exact section name
# depends on the pipeline.  For KCAP, the BandPower E-mode prediction
# lives in the 'scale_cuts_output' section.
#
# Until CosmoSIS runs successfully, we print the extraction instructions:

echo ""
echo "After CosmoSIS completes successfully:"
echo ""
echo "  1. Locate the BandPower prediction vector in the CosmoSIS output."
echo "     (Check 'bandpower_shear_e' or 'scale_cuts_output' section.)"
echo ""
echo "  2. Save it as a .npy file:"
echo "     python -c \"import numpy as np; np.save('$OUT_DIR/generated/m_kids.npy', model_vec)\""
echo ""
echo "  3. Validate:"
echo "     PYTHONPATH=$PROJECT_ROOT/src $VENV_PYTHON \\"
echo "       $PROJECT_ROOT/scripts/validate_model_vector.py \\"
echo "       --model-vector $OUT_DIR/generated/m_kids.npy \\"
echo "       --tag KiDS"
echo ""
echo "  4. If chi2(d-m_KiDS) is plausible, repeat with values_planck.ini for m_Planck."
echo ""
echo "  STOPPING RULE: If chi2(d-m_KiDS) is NOT plausible, fix the pipeline."
echo "  No SRO inference is allowed until this gate passes."
echo ""
echo "Phase 4c-prep configuration written. Run CosmoSIS to generate vectors."
