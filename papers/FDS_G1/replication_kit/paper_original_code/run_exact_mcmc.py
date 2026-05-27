#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.optimize as opt
import emcee

from stage2d_exact_likelihood import (
    PARAM_NAMES, BOUNDS, STARTS, INIT_SCALES,
    load_config, make_likelihood_from_config
)


BAD_CHI2 = 1.0e100


def safe_chi2(model: str, like, x: np.ndarray) -> float:
    if not like.in_prior(model, x):
        return BAD_CHI2
    if not like.physical_ok(model, x):
        return BAD_CHI2
    val = like.chi2(model, x)
    if not np.isfinite(val):
        return BAD_CHI2
    return float(val)


def initialize_walkers(model: str, center: np.ndarray, seed: int, nwalkers: int, like) -> np.ndarray:
    rng = np.random.default_rng(seed)
    scale = INIT_SCALES[model]
    p0 = []
    tries = 0
    while len(p0) < nwalkers and tries < 1_000_000:
        tries += 1
        x = center + scale * rng.normal(size=len(center))
        if like.in_prior(model, x) and like.physical_ok(model, x):
            p0.append(x)
    if len(p0) < nwalkers:
        raise RuntimeError("Failed to initialize walkers inside priors.")
    return np.asarray(p0)


def find_best(model: str, like, x0: np.ndarray) -> tuple[np.ndarray, float]:
    bounds = BOUNDS[model]

    def objective(x):
        val = like.chi2(model, x)
        return float(val) if np.isfinite(val) else np.inf

    res = opt.minimize(objective, x0=x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": 500})
    best = np.asarray(res.x, dtype=float)
    cmin = float(res.fun)
    if not np.isfinite(cmin):
        raise RuntimeError(f"Optimizer failed for {model}; best chi2 is not finite.")
    return best, cmin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=list(PARAM_NAMES))
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--walkers", type=int, default=None)
    ap.add_argument("--burn-fraction", type=float, default=0.5)
    ap.add_argument("--outdir", default="outputs")
    ap.add_argument("--no-optimize", action="store_true", help="Start from STARTS[model] without optimizer warm-start.")
    ap.add_argument("--progress", action="store_true", help="Show tqdm progress bar.")
    args = ap.parse_args()

    config = load_config(args.config)
    like = make_likelihood_from_config(config)

    steps = args.steps or int(config.get("mcmc", {}).get("steps", 20000))
    walkers_default = config.get("mcmc", {}).get("walkers", {}).get(args.model, max(4*len(PARAM_NAMES[args.model]), 48))
    nwalkers = args.walkers or int(walkers_default)

    outdir = Path(args.outdir)
    (outdir / "chains").mkdir(parents=True, exist_ok=True)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)

    x0 = STARTS[args.model].copy()
    if args.no_optimize:
        best = x0
        cmin = safe_chi2(args.model, like, best)
        if not np.isfinite(cmin) or cmin >= BAD_CHI2:
            raise RuntimeError("STARTS[model] is not a finite valid point.")
    else:
        best, cmin = find_best(args.model, like, x0)

    p0 = initialize_walkers(args.model, best, args.seed, nwalkers, like)
    sampler = emcee.EnsembleSampler(nwalkers, len(PARAM_NAMES[args.model]), lambda th: like.logprob(args.model, th))
    sampler.run_mcmc(p0, steps, progress=args.progress)

    burn = int(steps * args.burn_fraction)
    chain_un = sampler.get_chain(discard=burn)
    logp_un = sampler.get_log_prob(discard=burn)
    chain_flat = chain_un.reshape((-1, chain_un.shape[-1]))
    logp_flat = logp_un.reshape(-1)

    tag = f"{args.model}_seed{args.seed}"
    np.save(outdir / "chains" / f"{tag}_chain_unflattened.npy", chain_un)
    np.save(outdir / "chains" / f"{tag}_logp_unflattened.npy", logp_un)
    np.save(outdir / "chains" / f"{tag}_chain_flat.npy", chain_flat)
    np.save(outdir / "chains" / f"{tag}_logp_flat.npy", logp_flat)

    # Best from optimizer plus possible chain improvement
    finite_logp = np.isfinite(logp_flat)
    if np.any(finite_logp):
        idx = np.argmax(logp_flat[finite_logp])
        finite_chain = chain_flat[finite_logp]
        best_chain = finite_chain[idx]
        c_chain = float(-2 * np.max(logp_flat[finite_logp]))
    else:
        best_chain = None
        c_chain = np.inf

    if best_chain is not None and c_chain < cmin:
        best_report = best_chain
        c_report = c_chain
        used_chain_best = True
    else:
        best_report = best
        c_report = cmin
        used_chain_best = False

    q = np.quantile(chain_flat, [0.16, 0.5, 0.84], axis=0)
    rows = []
    for j, name in enumerate(PARAM_NAMES[args.model]):
        rows.append({
            "parameter": name,
            "mean": float(np.mean(chain_flat[:, j])),
            "std": float(np.std(chain_flat[:, j], ddof=1)),
            "q16": float(q[0, j]),
            "q50": float(q[1, j]),
            "q84": float(q[2, j]),
        })
    pd.DataFrame(rows).to_csv(outdir / "tables" / f"{tag}_posterior_summary.csv", index=False)

    comps = like.chi2_components(args.model, best_report)
    summary = {
        "model": args.model,
        "seed": args.seed,
        "parameter_names": PARAM_NAMES[args.model],
        "steps": steps,
        "burn_fraction": args.burn_fraction,
        "nwalkers": nwalkers,
        "postburn_shape": list(chain_un.shape),
        "acceptance_fraction_mean": float(np.mean(sampler.acceptance_fraction)),
        "optimizer_chi2": float(cmin),
        "chain_best_chi2": float(c_chain),
        "used_chain_best": used_chain_best,
        "optimizer_start_best": [float(x) for x in best],
        "best": [float(x) for x in best_report],
        "chi2_min": float(c_report),
        **{k: float(v) for k, v in comps.items()},
    }
    with open(outdir / "tables" / f"{tag}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
