#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== KiDS-1000 data preparation ==="
echo ""

# Option 1: Use the included download script
if [ -f "$KIT_DIR/src/kids1000_download_prepare.py" ]; then
    echo "Running kids1000_download_prepare.py ..."
    python3 "$KIT_DIR/src/kids1000_download_prepare.py"
    echo "Done. Check $KIT_DIR/stage3_kids1000/ for downloaded products."
else
    echo "SKIP: kids1000_download_prepare.py not found"
fi

echo ""
echo "=== Manual download instructions ==="
echo "See $KIT_DIR/data/DOWNLOAD_INSTRUCTIONS.md"
echo ""
echo "After obtaining data, verify hashes:"
echo "  cd $KIT_DIR/data && sha256sum -c expected_sha256.txt"
