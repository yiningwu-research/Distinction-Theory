#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json, os
from pathlib import Path

import numpy as np
import pandas as pd

from stage2d_exact_likelihood import PARAM_NAMES, load_config, make_likelihood_from_config


def autocorr_1d(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    n = len(x)
    if n < 2 or np.allclose(x, 0):
        return np.ones(1)
    size = 1 << (2*n - 1).bit_length()
    f = np.fft.fft(x, size)
    acf = np.fft.ifft(f * np.conjugate(f))[:n].real
    acf /= acf[0]
    return acf


def tau_int_initial_positive(x: np.ndarray, max_lag: int = 5000) -> float:
    acf = autocorr_1d(x)
    max_lag = min(max_lag, len(acf)-1)
    tau = 1.0
    for k in range(1, max_lag, 2):
        pair = acf[k] + (acf[k+1] if k+1 < len(acf) else 0.0)
        if pair <= 0:
            break
        tau += 2.0 * pair
    return float(max(tau, 1.0))


def split_rhat(seed_series: list[np.ndarray]) -> float:
    parts = []
    for x in seed_series:
        x = np.asarray(x, dtype=float)
        mid = len(x) // 2
        parts.extend([x[:mid], x[mid:]])
    if len(parts) < 2:
        return np.nan
    n = min(len(p) for p in parts)
    if n < 10:
        return np.nan
    arr = np.array([p[:n] for p in parts])
    W = np.mean(np.var(arr, axis=1, ddof=1))
    B = n * np.var(np.mean(arr, axis=1), ddof=1)
    varhat = ((n-1)/n) * W + B/n
    return float(np.sqrt(varhat/W)) if W > 0 else np.nan


def physical_audit(model: str, chain: np.ndarray, like) -> pd.DataFrame:
    if model not in ("g1de1", "g1de2"):
        return pd.DataFrame()
    z = np.linspace(0.0, like.physical_zmax, like.physical_nz)
    a = 1.0 / (1.0 + z)
    rows = []
    for i, th in enumerate(chain):
        pars = like.theta_to_pars(model, th)
        X = like.Xhat_a(a, pars["Omega_m"], pars["s"])
        mu = 1.0 + pars.get("mu0", 0.0) * X
        Sigma = 1.0 + pars.get("Sigma0", 0.0) * X
        rows.append({
            "sample": i,
            "min_mu": float(np.min(mu)),
            "min_Sigma": float(np.min(Sigma)),
            "max_Xhat": float(np.max(X)),
            "physical_ok": bool(np.min(mu) > 0 and np.min(Sigma) > 0),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=list(PARAM_NAMES))
    ap.add_argument("--chains-dir", default="outputs/chains")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.chains_dir, f"{args.model}_seed*_chain_unflattened.npy")))
    if not paths:
        raise FileNotFoundError(f"No chains found for model={args.model} in {args.chains_dir}")

    chains_un = [np.load(p) for p in paths]
    flat_by_seed = [c.reshape((-1, c.shape[-1])) for c in chains_un]
    all_flat = np.vstack(flat_by_seed)

    rows = []
    q = np.quantile(all_flat, [0.16, 0.5, 0.84], axis=0)
    for j, name in enumerate(PARAM_NAMES[args.model]):
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
            "ESS_proxy": float(len(all_flat) / tau),
        })
    diag = pd.DataFrame(rows)

    outdir = Path(args.outdir)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)
    diag.to_csv(outdir / "tables" / f"{args.model}_production_diagnostics.csv", index=False)

    # Probabilities of signs.
    probs = {"model": args.model, "samples": int(len(all_flat))}
    if args.model in ("g1de1", "g1de2"):
        names = PARAM_NAMES[args.model]
        if "s" in names:
            probs["P_s_less_than_3"] = float(np.mean(all_flat[:, names.index("s")] < 3.0))
        if "mu0" in names:
            probs["P_mu0_less_than_0"] = float(np.mean(all_flat[:, names.index("mu0")] < 0.0))
        if "Sigma0" in names:
            probs["P_Sigma0_less_than_0"] = float(np.mean(all_flat[:, names.index("Sigma0")] < 0.0))
            probs["P_mu0_and_Sigma0_less_than_0"] = float(
                np.mean((all_flat[:, names.index("mu0")] < 0.0) & (all_flat[:, names.index("Sigma0")] < 0.0))
            )

    with open(outdir / "tables" / f"{args.model}_production_probability_stats.json", "w") as f:
        json.dump(probs, f, indent=2)

    # Physical audit
    if args.model in ("g1de1", "g1de2"):
        like = make_likelihood_from_config(load_config(args.config))
        phys = physical_audit(args.model, all_flat, like)
        phys.to_csv(outdir / "tables" / f"{args.model}_physical_prior_audit.csv", index=False)
        phys_summary = {
            "all_samples_physical_ok": bool(phys["physical_ok"].all()),
            "min_mu_all_samples": float(phys["min_mu"].min()),
            "min_Sigma_all_samples": float(phys["min_Sigma"].min()),
        }
        with open(outdir / "tables" / f"{args.model}_physical_prior_summary.json", "w") as f:
            json.dump(phys_summary, f, indent=2)

    print(diag.to_string(index=False))
    print(json.dumps(probs, indent=2))


if __name__ == "__main__":
    main()
