#!/usr/bin/env python3
"""Optional Note 5: acceleration-scale drift exploratory test.

Status: exploratory methodology / minimum-detectable-drift (MDE) forecast.
This is NOT a discovery test. The expected G1 signal is too small and too
vulnerable to observational systematics—inclination, beam smearing, gas
turbulence, stellar mass-to-light ratio, selection effects, and limited
high-z rotation-curve resolution—to claim detection now.

The output should be interpreted as answering:
  "How large would a0(z) drift need to be before current public rotation-curve
   data could see it?"

That is useful even if the answer is "not yet detectable."

This script provides a local SPARC-style RAR fit scaffold. It expects a CSV with
columns:
    galaxy, z, gbar, gobs, sigma_gobs
where accelerations are in consistent units.

For SPARC z~0 data, derive gbar/gobs from the mass model tables before using this script.
For high-z samples, only use homogenized rotation-curve products with explicit systematics.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

from g1dm.io import ensure_dir
from g1dm.plotting import savefig


def rar_model(gbar, a0):
    # McGaugh-like interpolating form: gobs = gbar / (1 - exp(-sqrt(gbar/a0)))
    gbar = np.asarray(gbar, dtype=float)
    x = np.sqrt(np.maximum(gbar, 1e-300) / a0)
    denom = 1.0 - np.exp(-x)
    return gbar / np.maximum(denom, 1e-12)


def fit_a0(df):
    gbar = df["gbar"].to_numpy(float)
    gobs = df["gobs"].to_numpy(float)
    sig = df.get("sigma_gobs", pd.Series(np.ones(len(df))*0.1*np.nanmedian(gobs))).to_numpy(float)
    sig = np.where(np.isfinite(sig) & (sig > 0), sig, 0.1*np.nanmedian(gobs))

    def nll(loga0):
        a0 = np.exp(loga0[0])
        r = (gobs - rar_model(gbar, a0)) / sig
        return 0.5 * np.sum(r*r + np.log(2*np.pi*sig*sig))
    res = minimize(nll, x0=[np.log(np.nanmedian(gbar))])
    return float(np.exp(res.x[0])), float(res.fun)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV with galaxy,z,gbar,gobs,sigma_gobs")
    ap.add_argument("--out", default="outputs/note5")
    args = ap.parse_args()
    out = ensure_dir(args.out)
    df = pd.read_csv(args.csv)

    rows = []
    for zbin, sub in df.groupby(pd.cut(df["z"], bins=[-0.01, 0.2, 0.8, 1.3, 2.5])):
        if len(sub) < 10:
            continue
        a0, nll = fit_a0(sub)
        rows.append({"z_bin": str(zbin), "z_mean": sub["z"].mean(), "n_points": len(sub), "a0_hat": a0, "nll": nll})
    res = pd.DataFrame(rows)
    res.to_csv(out / "a0_drift_by_zbin.csv", index=False)

    if not res.empty:
        plt.figure(figsize=(6,4))
        plt.plot(res["z_mean"], res["a0_hat"], marker="o")
        plt.xlabel("mean redshift")
        plt.ylabel("fitted a0 (input units)")
        plt.title("Exploratory acceleration-scale drift")
        savefig(out / "a0_drift.png")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
