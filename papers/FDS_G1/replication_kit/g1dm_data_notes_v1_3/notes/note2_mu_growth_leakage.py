#!/usr/bin/env python3
"""Note 2: DESI DR1 full-shape/RSD mu=1 growth-leakage consistency.

Compressed prototype: use Gaussian constraints on modified-gravity deviation mu0.
Convention: GR corresponds to mu0 = 0.
"""
from __future__ import annotations

import argparse
import pandas as pd

from g1dm.io import read_yaml, ensure_dir
from g1dm.stats import zscore_from_gaussian, two_sided_p_from_z
from g1dm.plotting import plot_gaussian_1d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--constraints", default="data/compressed_constraints/desi_mg_2024_mu_sigma.yml")
    ap.add_argument("--out", default="outputs/note2")
    args = ap.parse_args()
    out = ensure_dir(args.out)

    cfg = read_yaml(args.constraints)
    params = cfg["parameters"]
    mean = dict(zip(params, cfg["mean"]))
    sig = dict(zip(params, cfg["sigma"]))

    mu_mean = mean["mu0"]
    mu_sig = sig["mu0"]
    z_gr = zscore_from_gaussian(0.0, mu_mean, mu_sig)
    p_gr = two_sided_p_from_z(z_gr)

    rows = [
        {"test": "GR growth response", "null_value_mu0": 0.0, "mean_mu0": mu_mean, "sigma_mu0": mu_sig,
         "z_null": z_gr, "p_two_sided": p_gr,
         "interpretation": "If |z| is small, mu_grav=1 is compatible with public compressed growth constraints."}
    ]
    df = pd.DataFrame(rows)
    df.to_csv(out / "mu_growth_leakage_summary.csv", index=False)
    plot_gaussian_1d(mu_mean, mu_sig, out / "mu0_gr_consistency.png", xlabel="mu0 deviation from GR", markers=[(0.0, "GR")], title="Growth-leakage consistency")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
