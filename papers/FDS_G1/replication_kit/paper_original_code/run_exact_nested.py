#!/usr/bin/env python3
from __future__ import annotations

import argparse, json
from pathlib import Path

import numpy as np

from stage2d_exact_likelihood import PARAM_NAMES, BOUNDS, load_config, make_likelihood_from_config


def prior_transform(u: np.ndarray, bounds):
    return np.array([lo + ui*(hi-lo) for ui, (lo, hi) in zip(u, bounds)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/stage2d_exact_config.json")
    ap.add_argument("--model", required=True, choices=list(PARAM_NAMES))
    ap.add_argument("--nlive", type=int, default=None)
    ap.add_argument("--dlogz", type=float, default=None)
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    try:
        import dynesty
    except ImportError as e:
        raise ImportError("Install dynesty first: pip install dynesty") from e

    config = load_config(args.config)
    like = make_likelihood_from_config(config)

    nlive = args.nlive or int(config.get("nested", {}).get("nlive", {}).get(args.model, 1000))
    dlogz = args.dlogz if args.dlogz is not None else float(config.get("nested", {}).get("dlogz", 0.1))
    bounds = BOUNDS[args.model]
    ndim = len(bounds)

    sampler = dynesty.NestedSampler(
        lambda th: like.loglike(args.model, th) if like.logprior(args.model, th) == 0 else -np.inf,
        lambda u: prior_transform(u, bounds),
        ndim,
        nlive=nlive,
        bound="multi",
        sample="rwalk",
    )
    sampler.run_nested(dlogz=dlogz, print_progress=True)
    res = sampler.results

    outdir = Path(args.outdir)
    (outdir / "chains").mkdir(parents=True, exist_ok=True)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)

    np.save(outdir / "chains" / f"{args.model}_dynesty_samples.npy", res.samples)
    np.save(outdir / "chains" / f"{args.model}_dynesty_logwt.npy", res.logwt)
    np.save(outdir / "chains" / f"{args.model}_dynesty_logl.npy", res.logl)

    out = {
        "model": args.model,
        "parameter_names": PARAM_NAMES[args.model],
        "nlive": nlive,
        "dlogz": dlogz,
        "logZ": float(res.logz[-1]),
        "logZ_err": float(res.logzerr[-1]),
    }
    with open(outdir / "tables" / f"{args.model}_nested_evidence.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
