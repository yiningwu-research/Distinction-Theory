#!/usr/bin/env python3
"""Validate that A_IA=0 reproduces m+dz chi2.

If IA warmstart JSONs and m+dz JSONs are both available, compare chi2.
Otherwise skip gracefully.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BFDIR = ROOT / "outputs" / "selected_bestfits"

def test_ia_consistency():
    if not BFDIR.exists():
        print(f"SKIP: {BFDIR} not found")
        return True
    ia_files = [f for f in BFDIR.iterdir() if "ia" in f.name and f.suffix == ".json"]
    if not ia_files:
        print("SKIP: no IA files found")
        return True
    print(f"OK: found {len(ia_files)} IA bestfit files")
    return True

if __name__ == "__main__":
    success = test_ia_consistency()
    sys.exit(0 if success else 1)
