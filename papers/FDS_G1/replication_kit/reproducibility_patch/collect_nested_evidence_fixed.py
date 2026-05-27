#!/usr/bin/env python3
"""Patched nested evidence collector for third-party reproduction.

Fixes vs. paper_original_code/collect_nested_evidence.py:
- B1: BF_best_over_model and BF_model_over_best columns (explicit direction).
- R1: Exclude recovered-from-chains evidence unless --include-recovered is passed.
"""

import json
import argparse
import os
import glob
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--prior-label", default="medium")
    parser.add_argument("--include-recovered", action="store_true",
                        help="R1 fix: include emergency-recovered evidence files")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # Collect nested evidence JSON files
    pattern = os.path.join(args.tables_dir, "*_nested_evidence.json")
    evidence_files = sorted(glob.glob(pattern))

    records = []
    for fpath in evidence_files:
        with open(fpath) as f:
            data = json.load(f)

        # R1 fix: exclude recovered files unless explicitly included
        if not args.include_recovered:
            prior = data.get("prior_config", "")
            if prior == "recovered_from_chains" or data.get("recovered_from_chains", False):
                continue

        # Extract model name from filename
        fname = os.path.basename(fpath)
        model = fname.split("_seed")[0] if "_seed" in fname else fname.replace("_nested_evidence.json", "")

        # Handle different JSON structures
        logz = data.get("logz", data.get("logZ", data.get("logZ_mean", None)))
        logzerr = data.get("logzerr", data.get("logZ_err", None))
        seed = data.get("seed", None)

        if logz is not None:
            records.append({
                "model": model,
                "seed": seed,
                "logZ": float(logz),
                "logZ_err": float(logzerr) if logzerr is not None else None,
            })

    if not records:
        print("No evidence files found.")
        return

    # Aggregate by model (mean over seeds)
    df = pd.DataFrame(records)
    grouped = df.groupby("model")["logZ"].agg(["mean", "std", "count"]).reset_index()
    grouped.columns = ["model", "logZ_mean", "logZ_std", "n_seeds"]
    grouped["logZ_err"] = grouped["logZ_std"] / np.sqrt(grouped["n_seeds"])

    # B1 fix: explicit Bayes factor columns
    grouped["Delta_logZ"] = grouped["logZ_mean"].max() - grouped["logZ_mean"]
    grouped["BF_best_over_model"] = np.exp(grouped["Delta_logZ"])
    grouped["BF_model_over_best"] = np.exp(-grouped["Delta_logZ"])

    cols = ["model", "n_seeds", "logZ_mean", "logZ_err",
            "Delta_logZ", "BF_best_over_model", "BF_model_over_best"]
    result = grouped[cols].sort_values("Delta_logZ")

    # Save
    outpath = os.path.join(args.out_dir, f"nested_evidence_comparison_{args.prior_label}.csv")
    result.to_csv(outpath, index=False)
    print(f"Saved: {outpath}")


if __name__ == "__main__":
    main()
