#!/usr/bin/env python3
"""Collect nested evidence across multiple runs and produce comparison table."""
from __future__ import annotations

import argparse, glob, json, os
from pathlib import Path

import numpy as np
import pandas as pd


def infer_prior_label(prior_config):
    """Extract prior label from config path or default to 'unknown'."""
    if prior_config is None or prior_config == "recovered_from_chains":
        return "recovered"
    return os.path.splitext(os.path.basename(prior_config))[0].replace("nested_priors_", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables-dir", default="outputs/tables")
    ap.add_argument("--out-dir", default="outputs/tables")
    ap.add_argument("--prior-label", default=None,
                    help="Filter to specific prior label (e.g. medium, wide)")
    args = ap.parse_args()

    rows = []
    for path in sorted(glob.glob(str(Path(args.tables_dir) / "*_nested_evidence.json"))):
        with open(path) as f:
            s = json.load(f)
        if "prior_label" not in s:
            s["prior_label"] = infer_prior_label(s.get("prior_config"))
            print(f"WARNING: legacy file {os.path.basename(path)} lacks prior_label; inferred as '{s['prior_label']}' from prior_config")
        rows.append(s)

    if not rows:
        print("No nested evidence files found.")
        return

    df = pd.DataFrame(rows)
    df = df[df["logZ"].notna() & np.isfinite(df["logZ"])]

    if args.prior_label:
        df = df[df["prior_label"] == args.prior_label]
        if len(df) == 0:
            print(f"No evidence files with prior_label='{args.prior_label}'.")
            return

    for label, gdf in df.groupby("prior_label"):
        grouped = gdf.groupby("model").agg(
            ndim=("ndim", "first"),
            n_runs=("logZ", "count"),
            logZ_mean=("logZ", "mean"),
            logZ_run_std=("logZ", lambda x: float(np.std(x, ddof=1)) if len(x) > 1 else 0.0),
            logZ_dynesty_err_mean=("logZ_err", "mean"),
            chi2_best=("chi2_min_nested", "min"),
            logl_best=("logl_max", "max"),
            ncall_total=("ncall", "sum"),
        ).reset_index()

        grouped["logZ_total_err"] = np.sqrt(
            grouped["logZ_run_std"].fillna(0) ** 2 + grouped["logZ_dynesty_err_mean"].fillna(0) ** 2
        )
        grouped = grouped.sort_values("logZ_mean", ascending=False)
        grouped["Delta_logZ"] = grouped["logZ_mean"].max() - grouped["logZ_mean"]
        grouped["Bayes_factor"] = np.exp(grouped["Delta_logZ"].max() - grouped["Delta_logZ"])

        cols = ["model", "ndim", "n_runs", "logZ_mean", "logZ_total_err",
                "chi2_best", "Delta_logZ", "Bayes_factor"]
        print(f"\n--- prior: {label} ---")
        print(grouped[cols].to_string(index=False))
        out = Path(args.out_dir) / f"nested_evidence_comparison_{label}.csv"
        grouped.to_csv(out, index=False)
        print(f"Saved to {out}")


if __name__ == "__main__":
    main()
