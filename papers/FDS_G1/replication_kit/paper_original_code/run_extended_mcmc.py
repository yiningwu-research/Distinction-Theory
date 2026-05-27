#!/usr/bin/env python3
"""
Extended exact-likelihood tests for the G1 background--Weyl program.

Drop this file into your existing G_production_code/src/ directory.
It imports the existing exact likelihood implementation:

    stage2d_exact_likelihood.py

New models:

  g1dew:
      parameters = Omega_m, s, q_BAO, sigma8_0, Sigma0
      mu0 = 0

  g1demk:
      parameters = Omega_m, s, q_BAO, sigma8_0, kappa
      mu0 = 0
      Sigma0 = -kappa*(3-s)

  g1dem34:
      parameters = Omega_m, s, q_BAO, sigma8_0
      mu0 = 0
      Sigma0 = -(3/4)*(3-s)

  g1dem1:
      parameters = Omega_m, s, q_BAO, sigma8_0
      mu0 = 0
      Sigma0 = -(3-s)

  g1desplit:
      parameters = Omega_m, s_H, s_Sigma, q_BAO, sigma8_0, Sigma0
      mu0 = 0
      H/growth use s_H, Weyl response uses s_Sigma.

  g1deconstsig:
      parameters = Omega_m, s, q_BAO, sigma8_0, Sigma0
      mu0 = 0
      Sigma(a)=1+Sigma0.

  g1decplsig:
      parameters = Omega_m, s, q_BAO, sigma8_0, Sigma0, Sigmaa
      mu0 = 0
      Sigma(a)=1+Sigma0+Sigmaa*(1-a).

All models use:
  Pantheon+ full covariance + DESI DR2 BAO + exact growth + E_G.
"""

from __future__ import annotations

import argparse, json, os
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import scipy.optimize as opt
import emcee

from stage2d_exact_likelihood import load_config, make_likelihood_from_config


EXT_PARAM_NAMES = {
    "g1dew":        ["Omega_m", "s", "q_BAO", "sigma8_0", "Sigma0"],
    "g1demk":       ["Omega_m", "s", "q_BAO", "sigma8_0", "kappa"],
    "g1dem34":      ["Omega_m", "s", "q_BAO", "sigma8_0"],
    "g1dem1":       ["Omega_m", "s", "q_BAO", "sigma8_0"],
    "g1desplit":    ["Omega_m", "s_H", "s_Sigma", "q_BAO", "sigma8_0", "Sigma0"],
    "g1deconstsig": ["Omega_m", "s", "q_BAO", "sigma8_0", "Sigma0"],
    "g1decplsig":   ["Omega_m", "s", "q_BAO", "sigma8_0", "Sigma0", "Sigmaa"],
}

EXT_BOUNDS = {
    "g1dew":        [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20), (-0.95,1.0)],
    "g1demk":       [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20), (0.0,2.5)],
    "g1dem34":      [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20)],
    "g1dem1":       [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20)],
    "g1desplit":    [(0.05,0.60), (1.0,5.0), (1.0,5.0), (10.0,80.0), (0.40,1.20), (-0.95,1.0)],
    "g1deconstsig": [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20), (-0.95,1.0)],
    "g1decplsig":   [(0.05,0.60), (1.0,5.0), (10.0,80.0), (0.40,1.20), (-0.95,1.0), (-2.0,2.0)],
}

# Starts are centered around the exact pilot result:
# Omega_m=0.2964, s=2.5598, q_BAO=30.419, sigma8=0.7727, Sigma0=-0.3303.
EXT_STARTS = {
    "g1dew":        np.array([0.2964, 2.5598, 30.419, 0.7727, -0.3303]),
    "g1demk":       np.array([0.2964, 2.5598, 30.419, 0.7727, 0.75]),
    "g1dem34":      np.array([0.2964, 2.5598, 30.419, 0.7727]),
    "g1dem1":       np.array([0.2964, 2.5598, 30.419, 0.7727]),
    "g1desplit":    np.array([0.2964, 2.5598, 2.5598, 30.419, 0.7727, -0.3303]),
    "g1deconstsig": np.array([0.2964, 2.5598, 30.419, 0.7727, -0.3303]),
    "g1decplsig":   np.array([0.2964, 2.5598, 30.419, 0.7727, -0.3303, 0.0]),
}

EXT_SCALES = {
    "g1dew":        np.array([0.010, 0.12, 0.26, 0.060, 0.14]),
    "g1demk":       np.array([0.010, 0.12, 0.26, 0.060, 0.20]),
    "g1dem34":      np.array([0.010, 0.12, 0.26, 0.060]),
    "g1dem1":       np.array([0.010, 0.12, 0.26, 0.060]),
    "g1desplit":    np.array([0.010, 0.12, 0.18, 0.26, 0.060, 0.14]),
    "g1deconstsig": np.array([0.010, 0.12, 0.26, 0.060, 0.14]),
    "g1decplsig":   np.array([0.010, 0.12, 0.26, 0.060, 0.14, 0.30]),
}


def in_ext_prior(model: str, theta: np.ndarray) -> bool:
    return all(lo < x < hi for x, (lo, hi) in zip(theta, EXT_BOUNDS[model]))


def map_to_g1de2(model: str, theta: np.ndarray) -> np.ndarray:
    """Map shared-shape models to the existing g1de2 parameter vector.

    g1de2 vector = [Omega_m, s, q_BAO, sigma8_0, mu0, Sigma0].
    """
    th = np.asarray(theta, dtype=float)
    if model == "g1dew":
        Om, s, q, sig, Sigma0 = th
        return np.array([Om, s, q, sig, 0.0, Sigma0])
    if model == "g1demk":
        Om, s, q, sig, kappa = th
        return np.array([Om, s, q, sig, 0.0, -kappa*(3.0-s)])
    if model == "g1dem34":
        Om, s, q, sig = th
        return np.array([Om, s, q, sig, 0.0, -0.75*(3.0-s)])
    if model == "g1dem1":
        Om, s, q, sig = th
        return np.array([Om, s, q, sig, 0.0, -(3.0-s)])
    if model in ("g1desplit", "g1deconstsig", "g1decplsig"):
        raise ValueError(f"{model} requires custom E_G handling.")
    raise ValueError(model)


def derived_quantities(model: str, theta: np.ndarray) -> Dict[str, float]:
    """Return derived mu0, Sigma0, and kappa_BW if defined."""
    th = np.asarray(theta, dtype=float)
    out = {}
    if model in ("g1dew", "g1demk", "g1dem34", "g1dem1"):
        base = map_to_g1de2(model, th)
        out["Omega_m"] = float(base[0])
        out["s"] = float(base[1])
        out["q_BAO"] = float(base[2])
        out["sigma8_0"] = float(base[3])
        out["mu0"] = float(base[4])
        out["Sigma0"] = float(base[5])
    elif model == "g1desplit":
        Om, sH, sS, q, sig, Sigma0 = th
        out.update({"Omega_m":float(Om), "s_H":float(sH), "s_Sigma":float(sS), "q_BAO":float(q),
                    "sigma8_0":float(sig), "mu0":0.0, "Sigma0":float(Sigma0)})
    elif model == "g1deconstsig":
        Om, s, q, sig, Sigma0 = th
        out.update({"Omega_m":float(Om), "s":float(s), "q_BAO":float(q), "sigma8_0":float(sig),
                    "mu0":0.0, "Sigma0":float(Sigma0)})
    elif model == "g1decplsig":
        Om, s, q, sig, Sigma0, Sigmaa = th
        out.update({"Omega_m":float(Om), "s":float(s), "q_BAO":float(q), "sigma8_0":float(sig),
                    "mu0":0.0, "Sigma0":float(Sigma0), "Sigmaa":float(Sigmaa)})
    s_val = out.get("s", out.get("s_H", np.nan))
    if np.isfinite(s_val) and abs(3.0 - s_val) > 1e-8:
        out["kappa_BW"] = float(-out.get("Sigma0", np.nan)/(3.0-s_val))
    else:
        out["kappa_BW"] = np.nan
    return out


class ExtendedModelLikelihood:
    def __init__(self, like):
        self.like = like

    def base_theta_for_background(self, model: str, theta: np.ndarray) -> np.ndarray:
        """Return a g1de2 theta used for background and growth blocks."""
        th = np.asarray(theta, dtype=float)
        if model in ("g1dew", "g1demk", "g1dem34", "g1dem1"):
            return map_to_g1de2(model, th)
        if model == "g1desplit":
            Om, sH, sS, q, sig, Sigma0 = th
            return np.array([Om, sH, q, sig, 0.0, 0.0])
        if model == "g1deconstsig":
            Om, s, q, sig, Sigma0 = th
            return np.array([Om, s, q, sig, 0.0, 0.0])
        if model == "g1decplsig":
            Om, s, q, sig, Sigma0, Sigmaa = th
            return np.array([Om, s, q, sig, 0.0, 0.0])
        raise ValueError(model)

    def physical_ok(self, model: str, theta: np.ndarray) -> bool:
        if not in_ext_prior(model, theta):
            return False
        th = np.asarray(theta, dtype=float)
        z = np.linspace(0.0, self.like.physical_zmax, self.like.physical_nz)
        a = 1.0/(1.0+z)

        if model in ("g1dew", "g1demk", "g1dem34", "g1dem1"):
            base = map_to_g1de2(model, th)
            return bool(self.like.in_prior("g1de2", base) and self.like.physical_ok("g1de2", base))

        if model == "g1desplit":
            Om, sH, sS, q, sig, Sigma0 = th
            X = self.like.Xhat_a(a, Om, sS)
            Sigma = 1.0 + Sigma0*X
            return bool(np.all(np.isfinite(Sigma)) and np.all(Sigma > 0))

        if model == "g1deconstsig":
            Sigma0 = th[4]
            return bool(1.0 + Sigma0 > 0)

        if model == "g1decplsig":
            Om, s, q, sig, Sigma0, Sigmaa = th
            Sigma = 1.0 + Sigma0 + Sigmaa*(1.0-a)
            return bool(np.all(np.isfinite(Sigma)) and np.all(Sigma > 0))

        raise ValueError(model)

    def eg_pred_custom(self, model: str, theta: np.ndarray):
        """Custom E_G for split-shape and control Weyl models."""
        base = self.base_theta_for_background(model, theta)
        sol = self.like.growth_solution("g1de2", base)
        if sol is None:
            return None
        a_grid, D, f = sol
        ae = 1.0/(1.0+self.like.z_eg)
        fz = np.interp(ae, a_grid, f)
        if np.any(~np.isfinite(fz)) or np.any(fz <= 0):
            return None

        th = np.asarray(theta, dtype=float)
        if model == "g1desplit":
            Om, sH, sS, q, sig, Sigma0 = th
            Sigma = 1.0 + Sigma0*self.like.Xhat_a(ae, Om, sS)
            return Om*Sigma/fz

        if model == "g1deconstsig":
            Om, s, q, sig, Sigma0 = th
            Sigma = np.ones_like(ae)*(1.0+Sigma0)
            return Om*Sigma/fz

        if model == "g1decplsig":
            Om, s, q, sig, Sigma0, Sigmaa = th
            Sigma = 1.0 + Sigma0 + Sigmaa*(1.0-ae)
            return Om*Sigma/fz

        raise ValueError(model)

    def chi2_eg_custom(self, model: str, theta: np.ndarray) -> float:
        pred = self.eg_pred_custom(model, theta)
        if pred is None or np.any(~np.isfinite(pred)):
            return np.inf
        return self.like.quad(self.like.val_eg - pred, self.like.cho_eg)

    def chi2_components(self, model: str, theta: np.ndarray) -> Dict[str, float]:
        if not self.physical_ok(model, theta):
            return {"chi2_total": np.inf, "chi2_sn": np.inf, "chi2_bao": np.inf, "chi2_growth": np.inf, "chi2_EG": np.inf}

        if model in ("g1dew", "g1demk", "g1dem34", "g1dem1"):
            base = map_to_g1de2(model, theta)
            comps = self.like.chi2_components("g1de2", base)
            return comps

        base = self.base_theta_for_background(model, theta)
        c_sn = self.like.chi2_sn("g1de2", base)
        c_bao = self.like.chi2_bao("g1de2", base)
        c_growth = self.like.chi2_growth("g1de2", base)
        c_eg = self.chi2_eg_custom(model, theta)
        total = c_sn + c_bao + c_growth + c_eg
        return {
            "chi2_total": float(total) if np.isfinite(total) else np.inf,
            "chi2_sn": float(c_sn),
            "chi2_bao": float(c_bao),
            "chi2_growth": float(c_growth),
            "chi2_EG": float(c_eg),
        }

    def chi2(self, model: str, theta: np.ndarray) -> float:
        return self.chi2_components(model, theta)["chi2_total"]

    def logprob(self, model: str, theta: np.ndarray) -> float:
        c = self.chi2(model, theta)
        return -0.5*c if np.isfinite(c) else -np.inf


def find_best(model: str, ext_like: ExtendedModelLikelihood, x0: np.ndarray) -> Tuple[np.ndarray, float]:
    res = opt.minimize(lambda x: ext_like.chi2(model, x), x0=x0, method="L-BFGS-B",
                       bounds=EXT_BOUNDS[model], options={"maxiter": 500})
    best = np.asarray(res.x, dtype=float)
    cmin = float(res.fun)

    # Powell polish can improve for locked-ratio models.
    try:
        res2 = opt.minimize(lambda x: ext_like.chi2(model, x), x0=best, method="Powell",
                            bounds=EXT_BOUNDS[model], options={"maxiter": 800, "xtol": 1e-4, "ftol": 1e-4})
        if float(res2.fun) < cmin:
            best = np.asarray(res2.x, dtype=float)
            cmin = float(res2.fun)
    except Exception:
        pass
    return best, cmin


def initialize_walkers(model: str, center: np.ndarray, seed: int, nwalkers: int, ext_like: ExtendedModelLikelihood) -> np.ndarray:
    rng = np.random.default_rng(seed)
    scale = EXT_SCALES[model]
    p0 = []
    tries = 0
    while len(p0) < nwalkers and tries < 1_000_000:
        tries += 1
        x = center + scale*rng.normal(size=len(center))
        if in_ext_prior(model, x) and ext_like.physical_ok(model, x):
            p0.append(x)
    if len(p0) < nwalkers:
        raise RuntimeError(f"Failed to initialize walkers for {model}.")
    return np.asarray(p0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=list(EXT_PARAM_NAMES))
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--walkers", type=int, default=None)
    ap.add_argument("--burn-fraction", type=float, default=0.5)
    ap.add_argument("--outdir", default="outputs")
    ap.add_argument("--no-optimize", action="store_true")
    ap.add_argument("--progress", action="store_true")
    args = ap.parse_args()

    config = load_config(args.config)
    like = make_likelihood_from_config(config)
    ext_like = ExtendedModelLikelihood(like)

    ndim = len(EXT_PARAM_NAMES[args.model])
    nwalkers = args.walkers or max(2*ndim+2, 16)
    outdir = Path(args.outdir)
    (outdir/"chains").mkdir(parents=True, exist_ok=True)
    (outdir/"tables").mkdir(parents=True, exist_ok=True)

    x0 = EXT_STARTS[args.model].copy()
    if args.no_optimize:
        best = x0
        cmin = ext_like.chi2(args.model, best)
    else:
        best, cmin = find_best(args.model, ext_like, x0)

    p0 = initialize_walkers(args.model, best, args.seed, nwalkers, ext_like)
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lambda th: ext_like.logprob(args.model, th))
    sampler.run_mcmc(p0, args.steps, progress=args.progress)

    burn = int(args.steps*args.burn_fraction)
    chain_un = sampler.get_chain(discard=burn)
    logp_un = sampler.get_log_prob(discard=burn)
    chain_flat = chain_un.reshape((-1, chain_un.shape[-1]))
    logp_flat = logp_un.reshape(-1)

    tag = f"{args.model}_seed{args.seed}"
    np.save(outdir/"chains"/f"{tag}_chain_unflattened.npy", chain_un)
    np.save(outdir/"chains"/f"{tag}_logp_unflattened.npy", logp_un)
    np.save(outdir/"chains"/f"{tag}_chain_flat.npy", chain_flat)
    np.save(outdir/"chains"/f"{tag}_logp_flat.npy", logp_flat)

    chain_best = chain_flat[np.argmax(logp_flat)]
    chain_best_chi2 = float(-2*np.max(logp_flat))
    if chain_best_chi2 < cmin:
        best_report = chain_best
        c_report = chain_best_chi2
        used_chain_best = True
    else:
        best_report = best
        c_report = cmin
        used_chain_best = False

    q = np.quantile(chain_flat, [0.16, 0.5, 0.84], axis=0)
    rows = []
    for j, name in enumerate(EXT_PARAM_NAMES[args.model]):
        rows.append({
            "parameter": name,
            "mean": float(np.mean(chain_flat[:, j])),
            "std": float(np.std(chain_flat[:, j], ddof=1)),
            "q16": float(q[0, j]),
            "q50": float(q[1, j]),
            "q84": float(q[2, j]),
        })
    pd.DataFrame(rows).to_csv(outdir/"tables"/f"{tag}_posterior_summary.csv", index=False)

    # Derived posterior summary.
    drows = [derived_quantities(args.model, th) for th in chain_flat]
    pd.DataFrame(drows).to_csv(outdir/"tables"/f"{tag}_derived_samples.csv", index=False)

    comps = ext_like.chi2_components(args.model, best_report)
    summary = {
        "model": args.model,
        "seed": args.seed,
        "parameter_names": EXT_PARAM_NAMES[args.model],
        "steps": args.steps,
        "burn_fraction": args.burn_fraction,
        "nwalkers": nwalkers,
        "postburn_shape": list(chain_un.shape),
        "acceptance_fraction_mean": float(np.mean(sampler.acceptance_fraction)),
        "optimizer_or_start_best": [float(x) for x in best],
        "optimizer_or_start_chi2": float(cmin),
        "chain_best_chi2": float(chain_best_chi2),
        "used_chain_best": bool(used_chain_best),
        "best": [float(x) for x in best_report],
        "derived_best": derived_quantities(args.model, best_report),
        **{k: float(v) for k, v in comps.items()},
    }
    with open(outdir/"tables"/f"{tag}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
