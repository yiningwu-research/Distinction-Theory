#!/usr/bin/env python3
"""Note 1: Carrier floor / pure-Weyl exclusion prototype.

First-pass diagnostic: read Planck/CosmoMC chains and quantify how strongly
omega_cdm h^2 = 0 is excluded by the posterior. This is not a substitute for a
full Planck likelihood comparison, but it is a transparent public-data check of
the carrier-floor idea.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from g1dm.io import ensure_dir, read_cosmomc_chains, find_parameter, weighted_quantile
from g1dm.plotting import savefig


def synthetic_planck_demo():
    """Fallback if chains are not installed: Planck-like omega_cdm h^2 posterior."""
    rng = np.random.default_rng(123)
    x = rng.normal(0.120, 0.0012, 50000)
    return pd.DataFrame({"weight": np.ones_like(x), "omegach2": x})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--planck-chain-dir", default="data/raw/planck_chains")
    ap.add_argument("--param", default=None, help="Parameter name override, e.g. omegach2")
    ap.add_argument("--out", default="outputs/note1")
    ap.add_argument("--allow-demo", action="store_true", help="Use Planck-like demo values if chains absent")
    args = ap.parse_args()

    out = ensure_dir(args.out)
    try:
        df = read_cosmomc_chains(args.planck_chain_dir)
    except Exception as e:
        if not args.allow_demo:
            raise SystemExit(
                f"Could not read Planck chains: {e}\n"
                "Place CosmoMC chains under data/raw/planck_chains or rerun with --allow-demo."
            )
        df = synthetic_planck_demo()

    param = args.param or find_parameter(df, ["omegach2", "omegac", "omega_cdm", r"omega.*c.*h"])
    w = df["weight"].to_numpy() if "weight" in df.columns else None
    x = df[param].to_numpy(dtype=float)
    mean = np.average(x, weights=w)
    std = np.sqrt(np.average((x - mean) ** 2, weights=w)) if w is not None else np.std(x, ddof=1)
    q16, q50, q84 = weighted_quantile(x, [0.16, 0.50, 0.84], w)
    z0 = mean / std

    summary = {
        "parameter": param,
        "mean": float(mean),
        "std": float(std),
        "q16": float(q16),
        "q50": float(q50),
        "q84": float(q84),
        "z_exclusion_of_zero": float(z0),
        "interpretation": "A large z supports a nonzero carrier-like CDM floor; it does not refute LambdaCDM."
    }
    pd.Series(summary).to_json(out / "carrier_floor_summary.json", indent=2)

    plt.figure(figsize=(6, 4))
    plt.hist(x, bins=80, weights=w, density=True, histtype="step")
    plt.axvline(0.0, linestyle="--", label="no carrier floor")
    plt.axvline(mean, linestyle="-", label="posterior mean")
    plt.xlabel(param)
    plt.ylabel("posterior density")
    plt.title("Carrier-floor diagnostic")
    plt.legend()
    savefig(out / "carrier_floor_posterior.png")

    print(pd.Series(summary).to_string())


if __name__ == "__main__":
    main()
