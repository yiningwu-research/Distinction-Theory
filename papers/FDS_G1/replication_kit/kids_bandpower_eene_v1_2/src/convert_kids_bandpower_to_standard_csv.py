#!/usr/bin/env python3
from __future__ import annotations
import argparse, numpy as np, pandas as pd
from pathlib import Path

Pnee_PAIRS = [(l, s) for l in [1, 2] for s in range(1, 6)]
PeeE_PAIRS = [(i, j) for i in range(1, 6) for j in range(i, 6)]
N_ANG = 8
EXPECTED_LEN = (len(Pnee_PAIRS) + len(PeeE_PAIRS)) * N_ANG

def convert_bandpower_vector(asc_path: Path, fits_path: Path) -> pd.DataFrame:
    import astropy.io.fits as fits
    asc_values = np.loadtxt(asc_path)
    if len(asc_values) != EXPECTED_LEN:
        raise ValueError(f"Expected {EXPECTED_LEN} values, got {len(asc_values)}")

    hdul = fits.open(fits_path)
    pnee = hdul['PneE'].data
    peee = hdul['PeeE'].data

    fits_values = np.concatenate([
        np.array([r['VALUE'] for r in pnee]),
        np.array([r['VALUE'] for r in peee]),
    ])
    if not np.allclose(asc_values, fits_values, rtol=1e-15, atol=1e-30):
        raise ValueError("ASC data vector does not match FITS PneE+PeeE tables")

    rows = []
    for probe, pairs, n_start in [('PneE', Pnee_PAIRS, 0), ('PeeE', PeeE_PAIRS, 80)]:
        for (b1, b2) in pairs:
            for ang in range(1, N_ANG + 1):
                row_idx = n_start + pairs.index((b1, b2)) * N_ANG + (ang - 1)
                rows.append({
                    "statistic": f"bandpower_E_{probe.lower()}",
                    "bin1": b1,
                    "bin2": b2,
                    "angbin": ang,
                    "value": float(asc_values[row_idx]),
                })

    return pd.DataFrame(rows)

def convert_covariance(fits_path: Path) -> np.ndarray:
    import astropy.io.fits as fits
    hdul = fits.open(fits_path)
    cov = hdul['COVMAT'].data.astype(float)
    if cov.shape != (EXPECTED_LEN, EXPECTED_LEN):
        raise ValueError(f"Expected {EXPECTED_LEN}x{EXPECTED_LEN} covariance, got {cov.shape}")
    return cov

def main():
    ap = argparse.ArgumentParser(description="Convert KiDS BandPower products to standard CSV")
    ap.add_argument("--vector", required=True, help="Path to 200-line BandPower .asc file")
    ap.add_argument("--fits", required=True, help="Path to BandPower FITS file with COVMAT")
    ap.add_argument("--outdir", default="data", help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = convert_bandpower_vector(Path(args.vector), Path(args.fits))
    out_csv = outdir / "kids1000_bandpower_200_standard.csv"
    df.to_csv(out_csv, index=False)
    print(f"Wrote {len(df)} rows to {out_csv}")

    row_order = df[["statistic", "bin1", "bin2", "angbin"]].copy()
    row_order.insert(0, "row_id", np.arange(len(row_order)))
    row_order.to_csv(outdir / "bandpower_row_order_verified.csv", index=False)
    print(f"Wrote row-order to {outdir / 'bandpower_row_order_verified.csv'}")

    cov = convert_covariance(Path(args.fits))
    out_npy = outdir / "kids1000_bandpower_covariance_200.npy"
    np.save(out_npy, cov)
    print(f"Wrote covariance {cov.shape} to {out_npy}")

if __name__ == "__main__":
    main()
