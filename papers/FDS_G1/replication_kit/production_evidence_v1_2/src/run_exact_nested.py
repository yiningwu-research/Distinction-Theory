#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, subprocess, sys
from pathlib import Path

import numpy as np

import dynesty

from stage2d_exact_likelihood import PARAM_NAMES, BOUNDS, load_config, make_likelihood_from_config


def prior_transform(u: np.ndarray, bounds):
    return np.array([lo + ui*(hi-lo) for ui, (lo, hi) in zip(u, bounds)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--prior-config", default=None,
                    help="JSON config with 'priors' dict to override per-parameter bounds")
    ap.add_argument("--model", required=True, choices=list(PARAM_NAMES))
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--nlive", type=int, default=None)
    ap.add_argument("--dlogz", type=float, default=None)
    ap.add_argument("--run-type", default="production", choices=["smoke", "production"])
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed) if args.seed is not None else None
    if args.seed is not None:
        np.random.seed(args.seed)

    config = load_config(args.config)
    like = make_likelihood_from_config(config)

    nlive = args.nlive or int(config.get("nested", {}).get("nlive", {}).get(args.model, 1000))
    dlogz = args.dlogz if args.dlogz is not None else float(config.get("nested", {}).get("dlogz", 0.1))

    # Prior bounds: apply prior-config overrides if provided
    base_bounds = BOUNDS[args.model]
    param_names = PARAM_NAMES[args.model]
    if args.prior_config:
        prior_cfg = load_config(args.prior_config)
        cfg_priors = prior_cfg.get("priors", {})
        overridden = []
        for name in param_names:
            if name in cfg_priors:
                overridden.append(tuple(cfg_priors[name]))
            else:
                idx = param_names.index(name)
                overridden.append(base_bounds[idx])
        bounds = overridden
    else:
        bounds = base_bounds
    ndim = len(bounds)

    sampler = dynesty.NestedSampler(
        lambda th: like.loglike(args.model, th) if like.logprior(args.model, th) == 0 else -np.inf,
        lambda u: prior_transform(u, bounds),
        ndim,
        nlive=nlive,
        bound="multi",
        sample="rwalk",
        rstate=rng,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=True)
    res = sampler.results

    outdir = Path(args.outdir)
    prior_label = (
        Path(args.prior_config).stem.replace("nested_priors_", "")
        if args.prior_config else "default"
    )
    seed_str = f"seed_{args.seed}" if args.seed is not None else "seed_none"
    tag_base = f"{args.model}_{seed_str}_{prior_label}"

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
        "parameter_names": param_names,
        "ndim": ndim,
        "nlive": nlive,
        "dlogz_target": dlogz,
        "logZ": float(res.logz[-1]),
        "logZ_err": float(res.logzerr[-1]),
        "logl_max": float(res.logl[best_idx]),
        "chi2_min_nested": chi2_min,
        "ncall": ncall_val,
        "eff": eff,
        "prior_config": args.prior_config or args.config,
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
