#!/usr/bin/env python3
"""
Convert official KiDS-1000 xi± data products to standard audit CSV.

Produces two outputs:
  - kids1000_xipm_270_standard.csv  (compact vector: 15 bin pairs × 9 theta × 2 probes)
  - kids1000_xipm_fine_standard.csv (per-bin-pair fine-binned at native resolution)

Standard CSV schema: probe,bin1,bin2,theta_arcmin,value
probe ∈ {xip, xim}
"""
from __future__ import annotations
import argparse, re, numpy as np, pandas as pd
from pathlib import Path

# KiDS-1000 9-bin edges for real-space xi± (Asgari et al. 2021)
XI9_EDGES = np.array([0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 300.0])

# Non-diagonal triangle ordering for 5 tomographic bins
BIN_PAIRS = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,1),(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(3,3),(3,4),(4,4)]

XI_FINE_RE = re.compile(r"XI_.*_nBins_5_Bin(\d+)_Bin(\d+)\.ascii$", re.IGNORECASE)

def parse_xi_fine(path: Path, bin1: int, bin2: int) -> pd.DataFrame:
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            parts = line.strip().split()
            if len(parts) < 6:
                continue
            theta = float(parts[1])
            xip   = float(parts[3])
            xim   = float(parts[4])
            rows.append({"bin1": bin1, "bin2": bin2,
                         "theta_arcmin": theta,
                         "probe": "xip", "value": xip})
            rows.append({"bin1": bin1, "bin2": bin2,
                         "theta_arcmin": theta,
                         "probe": "xim", "value": xim})
    return pd.DataFrame(rows)

def convert_270_vector(asc_path: Path, theta_edges: np.ndarray) -> pd.DataFrame:
    values = np.loadtxt(asc_path)
    if len(values) != 270:
        raise ValueError(f"Expected 270 values, got {len(values)}")
    thetas = np.sqrt(theta_edges[:-1] * theta_edges[1:])  # geometric means
    rows = []
    for probe, probe_label in [(0, "xip"), (135, "xim")]:
        for (b1, b2) in BIN_PAIRS:
            for ti in range(9):
                idx = probe + len(BIN_PAIRS) * 0 * 9 + BIN_PAIRS.index((b1, b2)) * 9 + ti
                idx = probe + BIN_PAIRS.index((b1, b2)) * 9 + ti
                rows.append({"probe": probe_label, "bin1": b1, "bin2": b2,
                             "theta_arcmin": thetas[ti], "value": values[idx]})
    return pd.DataFrame(rows)

def convert_fine_binned(fine_dir: Path) -> pd.DataFrame:
    frames = []
    for f in sorted(fine_dir.iterdir()):
        m = XI_FINE_RE.search(f.name)
        if m:
            b1, b2 = int(m.group(1)) - 1, int(m.group(2)) - 1
            frames.append(parse_xi_fine(f, b1, b2))
    if not frames:
        raise FileNotFoundError(f"No XI_*_Bin*_Bin*.ascii files found in {fine_dir}")
    return pd.concat(frames, ignore_index=True)

def main():
    ap = argparse.ArgumentParser(description="Convert KiDS xi± products to standard CSV")
    ap.add_argument("--kids-data", help="Path to KiDS data/kids directory for auto-discovery")
    ap.add_argument("--compact-xipm", help="Explicit path to the 270-element xipm .asc file")
    ap.add_argument("--fine-dir", help="Directory containing XI_*_Bin*.ascii files")
    ap.add_argument("--outdir", default="data", help="Output directory")
    ap.add_argument("--theta-edges", nargs=9, type=float,
                    default=None, help="9+1 theta bin edges for compact vector")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Locate the compact (270) xipm file
    compact_path = None
    if args.compact_xipm:
        compact_path = Path(args.compact_xipm)
    elif args.kids_data:
        root = Path(args.kids_data)
        candidates = sorted(root.glob("xipm_*_nbins_9_*.asc"))
        if candidates:
            compact_path = candidates[0]
            print(f"Auto-discovered compact xipm: {compact_path}")
        else:
            print("No compact xipm file found via auto-discovery")
    if compact_path and compact_path.exists():
        theta_edges = XI9_EDGES if args.theta_edges is None else np.array(args.theta_edges)
        df_270 = convert_270_vector(compact_path, theta_edges)
        out_270 = outdir / "kids1000_xipm_270_standard.csv"
        df_270.to_csv(out_270, index=False)
        print(f"Wrote {len(df_270)} rows to {out_270}")

        # Row-order metadata
        row_order = df_270[["probe", "bin1", "bin2", "theta_arcmin"]].copy()
        row_order.insert(0, "row_id", np.arange(len(row_order)))
        row_order.to_csv(outdir / "row_order_xipm_270.csv", index=False)
        print(f"Wrote row-order to {outdir / 'row_order_xipm_270.csv'}")
    else:
        print("Skipping compact vector conversion (no source file)")

    # Convert fine-binned per-pair files
    fine_dir = None
    if args.fine_dir:
        fine_dir = Path(args.fine_dir)
    elif args.kids_data:
        fine_dir = Path(args.kids_data) / "xipm"
    if fine_dir and fine_dir.exists():
        df_fine = convert_fine_binned(fine_dir)
        out_fine = outdir / "kids1000_xipm_fine_standard.csv"
        df_fine.to_csv(out_fine, index=False)
        print(f"Wrote {len(df_fine)} rows to {out_fine}")
        row_order_f = df_fine[["probe", "bin1", "bin2", "theta_arcmin"]].copy()
        row_order_f.insert(0, "row_id", np.arange(len(row_order_f)))
        row_order_f.to_csv(outdir / "row_order_xipm_fine.csv", index=False)
        print(f"Wrote fine row-order to {outdir / 'row_order_xipm_fine.csv'}")
    else:
        print("Skipping fine-binned conversion (no source directory)")

if __name__ == "__main__":
    main()
