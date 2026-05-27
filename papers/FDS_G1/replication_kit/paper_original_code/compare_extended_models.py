#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json
from pathlib import Path
import numpy as np
import pandas as pd

from run_extended_mcmc import EXT_PARAM_NAMES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables-dir", default="outputs/tables")
    ap.add_argument("--ndata", type=float, default=None, help="If omitted, uses N=SN+BAO+RSD+EG from typical exact run; edit if needed.")
    ap.add_argument("--out", default="outputs/tables/extended_model_comparison.csv")
    args = ap.parse_args()

    rows = []
    for path in glob.glob(str(Path(args.tables_dir) / "*_seed*_summary.json")):
        with open(path) as f:
            s = json.load(f)
        model = s["model"]
        if model not in EXT_PARAM_NAMES:
            continue
        k = len(EXT_PARAM_NAMES[model])
        chi2 = float(s["chi2_total"])
        # Default N is only for rough BIC; better pass exact N from your data vector.
        # Pantheon+ is usually 1701, DESI BAO and curated RSD sizes can vary.
        N = args.ndata or 1725.0
        rows.append({
            "model": model,
            "seed": s["seed"],
            "k": k,
            "chi2": chi2,
            "AIC": chi2 + 2*k,
            "BIC": chi2 + k*np.log(N),
            "acceptance": s.get("acceptance_fraction_mean", np.nan),
            "derived_best": json.dumps(s.get("derived_best", {})),
        })
    if not rows:
        raise FileNotFoundError("No extended *_summary.json files found.")
    df = pd.DataFrame(rows)
    # best seed per model
    best = df.sort_values("chi2").groupby("model", as_index=False).first()
    best["Delta_chi2"] = best["chi2"] - best["chi2"].min()
    best["Delta_AIC"] = best["AIC"] - best["AIC"].min()
    best["Delta_BIC"] = best["BIC"] - best["BIC"].min()
    best = best.sort_values("AIC")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    best.to_csv(args.out, index=False)
    print(best.to_string(index=False))


if __name__ == "__main__":
    main()
