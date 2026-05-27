import numpy as np, json, sys, argparse
from pathlib import Path
from scipy.special import logsumexp

outdir = Path("outputs")

ap = argparse.ArgumentParser()
ap.add_argument("model", nargs="?", help="Model name")
ap.add_argument("seeds", nargs="*", type=int, help="Seeds to recover")
ap.add_argument("--prior-label", default="recovered", help="Prior label for output filename")
args = ap.parse_args()

models_seeds = {}
if args.model:
    seeds = args.seeds if args.seeds else [101, 202, 303]
    models_seeds[args.model] = seeds
else:
    models_seeds = {
        "g1dem34": [101, 202, 303],
        "g1demk": [101, 202, 303],
    }

for model, seeds in models_seeds.items():
    for seed in seeds:
        tag = f"{model}_seed{seed}"
        chains = outdir / "chains"
        try:
            logl = np.load(chains / f"{tag}_dynesty_logl.npy")
            logwt = np.load(chains / f"{tag}_dynesty_logwt.npy")
            samples = np.load(chains / f"{tag}_dynesty_samples.npy")
        except FileNotFoundError:
            print(f"{tag}: chains not found")
            continue

        best_idx = int(np.argmax(logl))
        chi2_min = float(-2.0 * logl[best_idx])
        logZ_val = float(logsumexp(logwt))
        ncall_val = len(samples)

        out = {
            "model": model,
            "seed": seed,
            "ndim": int(samples.shape[1]),
            "nlive": 0,
            "dlogz": 0.0,
            "logZ": logZ_val,
            "logZ_err": 0.0,
            "logl_max": float(logl[best_idx]),
            "chi2_min_nested": chi2_min,
            "ncall": ncall_val,
            "eff": None,
            "prior_config": "recovered_from_chains",
            "prior_label": args.prior_label,
            "recovered_from_chains": True,
            "logZ_err_note": "from logsumexp(logwt); dynesty logzerr unavailable",
        }
        out_path = outdir / "tables" / f"{tag}_{args.prior_label}_nested_evidence.json"
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        print(f"{tag}: chi2_min={chi2_min:.2f}, logZ={logZ_val:.2f}, nsamples={ncall_val}")
