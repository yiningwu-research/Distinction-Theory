#!/usr/bin/env python3
"""Nested evidence sampling for standard (cpl, g1de1, g1de2, lcdm)
and extended (g1dem34, g1demk, g1deconstsig, g1dew, g1desplit) models."""
from __future__ import annotations

import argparse, json, os, subprocess, sys
from pathlib import Path

import numpy as np

import dynesty

from stage2d_exact_likelihood import PARAM_NAMES, BOUNDS, load_config, make_likelihood_from_config
from run_extended_mcmc import EXT_PARAM_NAMES, EXT_BOUNDS, EXT_STARTS, ExtendedModelLikelihood, in_ext_prior

ALL_MODELS = sorted(set(list(PARAM_NAMES) + list(EXT_PARAM_NAMES)))
ALL_BOUNDS = {**BOUNDS, **EXT_BOUNDS}

# Reference best-fit points from MCMC pilots for validation
REF_STARTS = {
    "lcdm":    [0.3073, 29.747, 0.7467],
    "cpl":     [0.3023, -0.799, -0.449, 30.370, 0.7737],
    "g1de1":   [0.2929, 2.548, 30.375, 0.6986, 0.425],
    "g1de2":   [0.2964, 2.560, 30.419, 0.7727, 0.045, -0.330],
    "g1dem34": [0.2966, 2.555, 30.431, 0.7765],
    "g1demk":  [0.2979, 2.592, 30.376, 0.7744, 0.840],
    "g1deconstsig": [0.2966, 2.561, 30.418, 0.7770, -0.336],
    "g1dew":   [0.2964, 2.560, 30.419, 0.7727, -0.330],
    "g1dem1":  [0.2983, 2.610, 30.342, 0.7701],
    "g1desplit": [0.2964, 2.560, 2.560, 30.419, 0.7727, -0.330],
    "g1decplsig": [0.2964, 2.560, 30.419, 0.7727, -0.330, 0.0],
}


def prior_transform(u: np.ndarray, bounds: list) -> np.ndarray:
    return np.array([lo + ui * (hi - lo) for ui, (lo, hi) in zip(u, bounds)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=ALL_MODELS)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--nlive", type=int, default=None)
    ap.add_argument("--dlogz", type=float, default=None)
    ap.add_argument("--check-loglike-only", action="store_true")
    ap.add_argument("--run-type", default="production", choices=["smoke", "production"],
                    help="Tag output as smoke or production; collector filters production by default")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed) if args.seed is not None else None
    if args.seed is not None:
        np.random.seed(args.seed)

    config = load_config(args.config)
    # Likelihood always uses the main config; --config only provides prior overrides
    like = make_likelihood_from_config(load_config("configs/stage2d_exact_config.json"))
    is_extended = args.model in EXT_PARAM_NAMES

    # --- prior bounds override from config ---
    base_bounds = {**BOUNDS, **EXT_BOUNDS}
    cfg_priors = config.get("priors", {})
    if cfg_priors:
        names = EXT_PARAM_NAMES[args.model] if is_extended else PARAM_NAMES[args.model]
        overridden = []
        for name in names:
            if name in cfg_priors:
                overridden.append(tuple(cfg_priors[name]))
            else:
                # Fall back to default
                idx = names.index(name)
                overridden.append(base_bounds[args.model][idx])
        bounds = overridden
    else:
        bounds = base_bounds[args.model]
    ndim = len(bounds)

    if is_extended:
        ext_like = ExtendedModelLikelihood(like)
        nlive = args.nlive or int(config.get("nested", {}).get("nlive", {}).get(args.model, 800))
        dlogz = args.dlogz if args.dlogz is not None else float(config.get("nested", {}).get("dlogz", 0.1))

        # Analytic physical checks — avoids 300-point z-grid audit
        def fast_physical_ok(model, theta):
            th = np.asarray(theta, dtype=float)
            if model == "g1dem34":
                Om, s, q, sig = th
                if s < 3.0:
                    return 1.0 - 0.75*(3.0 - s) > 0.0  # Sigma_min > 0, mu=1 always
                return True
            if model == "g1dem1":
                Om, s, q, sig = th
                if s < 3.0:
                    return 1.0 - (3.0 - s) > 0.0
                return True
            if model == "g1demk":
                Om, s, q, sig, kappa = th
                return kappa*(3.0 - s) < 1.0 if s < 3.0 else True
            if model == "g1deconstsig":
                Sigma0 = th[4]
                return 1.0 + Sigma0 > 0.0
            if model == "g1dew":
                Sigma0 = th[4]
                return 1.0 + Sigma0 > 0.0
            # Fallback for split/CPL-Weil models
            return ext_like.physical_ok(model, theta)

        def loglike_fn(theta):
            if not in_ext_prior(args.model, theta):
                return -np.inf
            if not fast_physical_ok(args.model, theta):
                return -np.inf
            return ext_like.logprob(args.model, theta)

        def pt_fn(u):
            return prior_transform(u, bounds)
    else:
        bounds = BOUNDS[args.model]
        ndim = len(bounds)
        nlive = args.nlive or int(config.get("nested", {}).get("nlive", {}).get(args.model, 1000))
        dlogz = args.dlogz if args.dlogz is not None else float(config.get("nested", {}).get("dlogz", 0.1))

        def loglike_fn(theta):
            if like.logprior(args.model, theta) != 0:
                return -np.inf
            return like.loglike(args.model, theta)

        def pt_fn(u):
            return prior_transform(u, bounds)

    # --- check-loglike-only mode ---
    if args.check_loglike_only:
        x0 = np.array(REF_STARTS.get(args.model, np.zeros(ndim)), dtype=float)
        lp = loglike_fn(x0)
        c = -2.0 * lp if np.isfinite(lp) else np.inf
        print(f"model={args.model}  ndim={ndim}  valid={np.isfinite(lp)}  logL={lp:.2f}  chi2={c:.2f}")
        return

    # --- full nested sampling ---
    sampler = dynesty.NestedSampler(
        loglike_fn, pt_fn, ndim,
        nlive=nlive, bound="multi", sample="rwalk",
        rstate=rng,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=True)
    res = sampler.results

    outdir = Path(args.outdir)
    prior_label = (
        Path(args.config).stem.replace("nested_priors_", "")
        if args.config else "default"
    )
    seed_str = f"seed_{args.seed}" if args.seed is not None else "seed_none"
    tag_base = f"{args.model}_{seed_str}_{prior_label}"

    # Hierarchical output paths
    chain_dir = outdir / "chains" / prior_label / args.model / seed_str
    table_dir = outdir / "tables" / prior_label
    chain_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    np.save(chain_dir / "dynesty_samples.npy", res.samples)
    np.save(chain_dir / "dynesty_logwt.npy", res.logwt)
    np.save(chain_dir / "dynesty_logl.npy", res.logl)

    best_idx = int(np.argmax(res.logl))
    chi2_min = float(-2.0 * res.logl[best_idx])
    ncall_val = int(np.sum(res.ncall))
    eff = float(ncall_val / len(res.samples)) if len(res.samples) else 0.0

    # Git commit for provenance
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent,
        ).stdout.strip()
    except Exception:
        git_commit = "unknown"

    out = {
        "model": args.model,
        "seed": args.seed,
        "ndim": ndim,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "logZ": float(res.logz[-1]),
        "logZ_err": float(res.logzerr[-1]),
        "logl_max": float(res.logl[best_idx]),
        "chi2_min_nested": chi2_min,
        "ncall": ncall_val,
        "eff": eff,
        "prior_config": args.config,
        "prior_label": prior_label,
        "run_type": args.run_type,
        "dynesty_version": dynesty.__version__,
        "python_version": sys.version,
        "git_commit": git_commit,
    }
    json_path = table_dir / f"{tag_base}_nested_evidence.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
