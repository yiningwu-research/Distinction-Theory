#!/usr/bin/env python3
"""Extend selected Phase 3 MCMC chains into a non-frozen audit directory."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import emcee
except ImportError as exc:  # pragma: no cover
    raise SystemExit("emcee is required to extend chains") from exc

from cmb_lensing_precheck.mcmc import MCMCSampler


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "outputs" / "frozen" / "v4_act_only" / "chains"
DEFAULT_OUT = ROOT / "outputs" / "phase3_extension_v4_rhat_audit" / "chains"


def extend_one(model: str, seed: int, in_root: Path, out_root: Path, n_steps: int) -> dict:
    in_dir = in_root / model / f"seed_{seed}"
    old_samples = np.load(in_dir / "samples_raw.npy")
    old_logp = np.load(in_dir / "log_prob_raw.npy")
    with open(in_dir / "metadata.json") as f:
        old_meta = json.load(f)

    sampler_owner = MCMCSampler(
        model,
        old_meta.get("variant", "act_baseline"),
        amplitude_param=old_meta.get("amplitude_param", "ln10As"),
        seed=seed,
    )
    n_walkers = old_samples.shape[1]
    n_dim = old_samples.shape[2]
    sampler_owner.sampler = emcee.EnsembleSampler(
        n_walkers,
        n_dim,
        sampler_owner._log_prob_fn,
    )

    t0 = time.time()
    sampler_owner.sampler.run_mcmc(old_samples[-1], n_steps, progress=False)
    elapsed = time.time() - t0

    new_samples = sampler_owner.sampler.get_chain(flat=False)
    new_logp = sampler_owner.sampler.get_log_prob(flat=False)
    combined_samples = np.concatenate([old_samples, new_samples], axis=0)
    combined_logp = np.concatenate([old_logp, new_logp], axis=0)

    out_dir = out_root / model / f"seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "samples_raw.npy", combined_samples)
    np.save(out_dir / "log_prob_raw.npy", combined_logp)

    meta = dict(old_meta)
    meta.update(
        {
            "source_chain": str(in_dir.relative_to(ROOT)),
            "old_n_steps": int(old_samples.shape[0]),
            "extension_n_steps": int(n_steps),
            "combined_n_steps": int(combined_samples.shape[0]),
            "extension_walltime_s": float(elapsed),
            "audit_note": "Non-frozen chain extension for rank-normalized R-hat audit.",
        }
    )
    with open(out_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    return {
        "model": model,
        "seed": seed,
        "old_shape": list(old_samples.shape),
        "new_shape": list(new_samples.shape),
        "combined_shape": list(combined_samples.shape),
        "walltime_s": float(elapsed),
        "mean_acceptance_fraction": float(np.mean(sampler_owner.sampler.acceptance_fraction)),
    }


def copy_unextended_model(model: str, in_root: Path, out_root: Path) -> None:
    for seed in (42, 12345):
        in_dir = in_root / model / f"seed_{seed}"
        out_dir = out_root / model / f"seed_{seed}"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in ("samples_raw.npy", "log_prob_raw.npy", "metadata.json"):
            data = (in_dir / name).read_bytes()
            (out_dir / name).write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=str(DEFAULT_IN.relative_to(ROOT)))
    parser.add_argument("--output-root", default=str(DEFAULT_OUT.relative_to(ROOT)))
    parser.add_argument("--models", nargs="+", default=["g1_bg", "g1_mkappa"])
    parser.add_argument("--copy-models", nargs="*", default=["lcdm", "g1_m34"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 12345])
    parser.add_argument("--steps", type=int, default=500)
    args = parser.parse_args()

    in_root = ROOT / args.input_root
    out_root = ROOT / args.output_root
    out_root.mkdir(parents=True, exist_ok=True)

    for model in args.copy_models:
        copy_unextended_model(model, in_root, out_root)

    results = []
    for model in args.models:
        for seed in args.seeds:
            print(f"Extending {model} seed={seed} by {args.steps} steps...", flush=True)
            results.append(extend_one(model, seed, in_root, out_root, args.steps))

    summary = {
        "input_root": str(in_root.relative_to(ROOT)),
        "output_root": str(out_root.relative_to(ROOT)),
        "extension_steps": int(args.steps),
        "extended_models": args.models,
        "copied_models": args.copy_models,
        "results": results,
    }
    summary_path = out_root.parent / "extension_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Wrote {summary_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
