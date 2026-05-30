#!/usr/bin/env python3
"""Validate scale-cut covariance shape."""
import csv, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASK_PATH = ROOT / "data" / "scale_cut_mask_135.csv"
EXPECTED_KEPT = 135

def test_scale_cut():
    if not MASK_PATH.exists():
        print(f"SKIP: {MASK_PATH} not found")
        return True
    kept = 0
    total = 0
    with open(MASK_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if int(row["kept_after_cuts"]):
                kept += 1
    if kept != EXPECTED_KEPT:
        print(f"FAIL: expected {EXPECTED_KEPT} kept, got {kept} (total {total})")
        return False
    print(f"OK: {kept}/{total} kept after scale cuts (expected {EXPECTED_KEPT})")
    return True

if __name__ == "__main__":
    success = test_scale_cut()
    sys.exit(0 if success else 1)
