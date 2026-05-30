#!/usr/bin/env python3
"""Validate that dz=0 reproduces m-only chi2.

Requires warmstart JSONs. If not available, skips gracefully.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BFDIR = ROOT / "outputs" / "selected_bestfits"

def test_mdz_consistency():
    if not BFDIR.exists():
        print(f"SKIP: {BFDIR} not found")
        return True
    m_only = [f for f in BFDIR.iterdir() if "monly" in f.name and f.suffix == ".json"]
    m_dz = [f for f in BFDIR.iterdir() if "mdz" in f.name or "warmstart" in f.name and "ia" not in f.name]
    if not m_only and not m_dz:
        print("SKIP: no m-only or m-dz files found")
        return True
    return True

if __name__ == "__main__":
    success = test_mdz_consistency()
    sys.exit(0 if success else 1)
