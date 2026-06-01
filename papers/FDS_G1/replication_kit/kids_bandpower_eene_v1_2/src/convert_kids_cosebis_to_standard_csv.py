#!/usr/bin/env python3
"""
Convert official KiDS-1000 COSEBIs data products to standard audit CSV.

COSEBIs are the Complete Orthogonal Sets of E/B-mode Integrals used
for the KiDS-1000 cosmic shear analysis.

Input:
  - 300-line .asc file (one COSEBIs E-mode value per line)
  - 300x300 .ascii covariance matrix

Row ordering (verified from source code):
  15 source-bin pairs (triangular i<=j) x 20 COSEBIs modes (n=1..20):
    (0,0): n=1..20
    (0,1): n=1..20
    ...
    (4,4): n=1..20

Output:
  - kids1000_cosebis_300_standard.csv   (300 rows)
  - kids1000_cosebis_covariance_300.npy (300x300)
  - cosebis_row_order_verified.csv      (300 rows: row_id, bin1, bin2, mode)
"""
from __future__ import annotations
import argparse, numpy as np, pandas as pd
from pathlib import Path

BIN_PAIRS = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,1),(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(3,3),(3,4),(4,4)]
N_MODES = 20
EXPECTED_LEN = len(BIN_PAIRS) * N_MODES  # 300

def convert_cosebis_vector(asc_path: Path) -> pd.DataFrame:
    values = np.loadtxt(asc_path)
    if len(values) != EXPECTED_LEN:
        raise ValueError(f"Expected {EXPECTED_LEN} values, got {len(values)}")

    rows = []
    for (b1, b2) in BIN_PAIRS:
        for n in range(1, N_MODES + 1):
            idx = BIN_PAIRS.index((b1, b2)) * N_MODES + (n - 1)
            rows.append({
                "statistic": "cosebi_E",
                "bin1": b1,
                "bin2": b2,
                "mode": n,
                "value": float(values[idx]),
            })
    return pd.DataFrame(rows)

def convert_covariance(ascii_path: Path) -> np.ndarray:
    cov = np.loadtxt(ascii_path)
    if cov.shape != (EXPECTED_LEN, EXPECTED_LEN):
        raise ValueError(f"Expected {EXPECTED_LEN}x{EXPECTED_LEN} covariance, got {cov.shape}")
    return np.asarray(cov, dtype=float)

def main():
    ap = argparse.ArgumentParser(description="Convert KiDS COSEBIs products to standard CSV")
    ap.add_argument("--vector", required=True, help="Path to 300-line COSEBIs .asc file")
    ap.add_argument("--cov", required=True, help="Path to 300x300 covariance .ascii file")
    ap.add_argument("--outdir", default="data", help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Convert data vector
    df = convert_cosebis_vector(Path(args.vector))
    out_csv = outdir / "kids1000_cosebis_300_standard.csv"
    df.to_csv(out_csv, index=False)
    print(f"Wrote {len(df)} rows to {out_csv}")

    # Row-order metadata
    row_order = df[["statistic", "bin1", "bin2", "mode"]].copy()
    row_order.insert(0, "row_id", np.arange(len(row_order)))
    row_order.to_csv(outdir / "cosebis_row_order_verified.csv", index=False)
    print(f"Wrote row-order to {outdir / 'cosebis_row_order_verified.csv'}")

    # Convert covariance
    cov = convert_covariance(Path(args.cov))
    out_npy = outdir / "kids1000_cosebis_covariance_300.npy"
    np.save(out_npy, cov)
    print(f"Wrote covariance {cov.shape} to {out_npy}")

if __name__ == "__main__":
    main()
