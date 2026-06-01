#!/usr/bin/env python3
"""
Index a downloaded official KiDS-1000 3×2pt repository tree.

Recommended source:
  https://github.com/KiDS-WL/Cat_to_Obs_K1000_P1

Usage:
  python src/prepare_kids3x2pt_data.py --root /path/to/Cat_to_Obs_K1000_P1/data --out outputs/kids_file_index.csv
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import pandas as pd

INTERESTING_SUFFIXES = {".fits", ".fit", ".fits.gz", ".txt", ".dat", ".ascii", ".csv", ".npy"}
KEYWORDS = ["cov", "covariance", "xipm", "xi", "gamma", "gammat", "gt", "wtheta", "nofz", "fits_iterative_covariance", "Data_Plots", "blindC", "2x2pt", "3x2pt"]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to downloaded KiDS repository/data directory")
    ap.add_argument("--out", required=True, help="CSV file to write")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        rel_low = rel.lower()
        suffix = "".join(p.suffixes[-2:]).lower() if p.name.endswith(".fits.gz") else p.suffix.lower()
        if suffix not in INTERESTING_SUFFIXES and not any(k.lower() in rel_low for k in KEYWORDS):
            continue
        role_guess = [k for k in KEYWORDS if k.lower() in rel_low]
        rows.append({"relative_path": rel, "size_bytes": p.stat().st_size, "suffix": suffix, "role_guess": ";".join(role_guess), "sha256": sha256_file(p)})
    df = pd.DataFrame(rows).sort_values(["role_guess", "relative_path"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} candidate files to {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
