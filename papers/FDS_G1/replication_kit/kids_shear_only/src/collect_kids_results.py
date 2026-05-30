#!/usr/bin/env python3
"""Aggregate KiDS shear-only results into unified summary table."""
import argparse, json, os, sys
from pathlib import Path

def load_bestfit(path):
    with open(path) as f:
        d = json.load(f)
    return d.get("chi2_min", None), d.get("params", {}), d.get("n_params", None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="outputs")
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    bfdir = outdir / "selected_bestfits"

    rows = []
    for bf in sorted(bfdir.glob("*.json")):
        name = bf.stem
        chi2, params, npar = load_bestfit(bf)
        row = {"name": name, "chi2_min": chi2, "n_params": npar}
        if params:
            row.update({f"param_{k}": v for k, v in params.items()})
        rows.append(row)

    import csv
    outpath = outdir / "phase2b_summary_table.csv"
    with open(outpath, "w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {outpath}")

if __name__ == "__main__":
    main()
