#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json, os
from pathlib import Path
import numpy as np
import pandas as pd

from run_extended_mcmc import EXT_PARAM_NAMES, derived_quantities


def autocorr_1d(x):
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    n = len(x)
    if n < 2 or np.allclose(x, 0):
        return np.ones(1)
    size = 1 << (2*n - 1).bit_length()
    f = np.fft.fft(x, size)
    acf = np.fft.ifft(f*np.conjugate(f))[:n].real
    acf /= acf[0]
    return acf


def tau_int_initial_positive(x, max_lag=5000):
    acf = autocorr_1d(x)
    max_lag = min(max_lag, len(acf)-1)
    tau = 1.0
    for k in range(1, max_lag, 2):
        pair = acf[k] + (acf[k+1] if k+1 < len(acf) else 0)
        if pair <= 0:
            break
        tau += 2*pair
    return max(float(tau), 1.0)


def split_rhat(seed_series):
    parts = []
    for x in seed_series:
        mid = len(x)//2
        parts += [x[:mid], x[mid:]]
    if len(parts) < 2:
        return np.nan
    n = min(len(p) for p in parts)
    if n < 10:
        return np.nan
    arr = np.array([p[:n] for p in parts])
    W = np.mean(np.var(arr, axis=1, ddof=1))
    B = n*np.var(np.mean(arr, axis=1), ddof=1)
    varhat = ((n-1)/n)*W + B/n
    return float(np.sqrt(varhat/W)) if W > 0 else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(EXT_PARAM_NAMES))
    ap.add_argument("--chains-dir", default="outputs/chains")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.chains_dir, f"{args.model}_seed*_chain_flat.npy")))
    if not paths:
        raise FileNotFoundError(f"No flat chains found for model={args.model}")

    flat_by_seed = [np.load(p) for p in paths]
    all_flat = np.vstack(flat_by_seed)
    names = EXT_PARAM_NAMES[args.model]

    q = np.quantile(all_flat, [0.16, 0.5, 0.84], axis=0)
    rows = []
    for j, name in enumerate(names):
        tau = tau_int_initial_positive(all_flat[:, j])
        rows.append({
            "model": args.model,
            "parameter": name,
            "mean": float(np.mean(all_flat[:, j])),
            "std": float(np.std(all_flat[:, j], ddof=1)),
            "q16": float(q[0, j]),
            "q50": float(q[1, j]),
            "q84": float(q[2, j]),
            "Rhat_split": split_rhat([f[:, j] for f in flat_by_seed]),
            "tau_int_proxy": tau,
            "ESS_proxy": float(len(all_flat)/tau),
        })
    diag = pd.DataFrame(rows)

    # Derived quantities for sign tests.
    drows = []
    for th in all_flat:
        drows.append(derived_quantities(args.model, th))
    ddf = pd.DataFrame(drows)

    probs = {"model": args.model, "samples": int(len(all_flat))}
    if "s" in ddf.columns:
        probs["P_s_less_than_3"] = float(np.mean(ddf["s"] < 3.0))
    if "s_H" in ddf.columns:
        probs["P_sH_less_than_3"] = float(np.mean(ddf["s_H"] < 3.0))
    if "s_Sigma" in ddf.columns:
        probs["P_sSigma_less_than_3"] = float(np.mean(ddf["s_Sigma"] < 3.0))
    if "Sigma0" in ddf.columns:
        probs["P_Sigma0_less_than_0"] = float(np.mean(ddf["Sigma0"] < 0.0))
    if "mu0" in ddf.columns:
        probs["P_mu0_less_than_0"] = float(np.mean(ddf["mu0"] < 0.0))
    if "kappa_BW" in ddf.columns:
        probs["kappa_BW_mean"] = float(ddf["kappa_BW"].replace([np.inf, -np.inf], np.nan).mean())
        probs["kappa_BW_q50"] = float(ddf["kappa_BW"].replace([np.inf, -np.inf], np.nan).quantile(0.5))

    outdir = Path(args.outdir)
    (outdir/"tables").mkdir(parents=True, exist_ok=True)
    diag.to_csv(outdir/"tables"/f"{args.model}_extended_diagnostics.csv", index=False)
    ddf.to_csv(outdir/"tables"/f"{args.model}_extended_derived_all.csv", index=False)
    with open(outdir/"tables"/f"{args.model}_extended_probability_stats.json", "w") as f:
        json.dump(probs, f, indent=2)

    print(diag.to_string(index=False))
    print(json.dumps(probs, indent=2))


if __name__ == "__main__":
    main()
