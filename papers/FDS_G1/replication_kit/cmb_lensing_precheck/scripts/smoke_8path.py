#!/usr/bin/env python3
"""
Quick 8-path smoke test: verify all 4 models × 2 variants run without crash.

Parameters: 8 walkers × 10 burn + 10 production steps each.
NOT for science — infrastructure validation only.
"""

import sys, json, numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cmb_lensing_precheck.mcmc import MCMCSampler

def _emu_unlocked() -> bool:
    token = Path(__file__).parent.parent / "outputs/emulator/emulator_primordial/production_unlock.json"
    if not token.exists():
        return False
    with open(token) as f:
        return json.load(f).get("production_unlock", False)

BASEDIR = Path(__file__).parent.parent / "outputs" / "phase3_smoke"

def smoke_one(model: str, variant: str, seed: int = 42) -> dict:
    sampler = MCMCSampler(model, variant, amplitude_param="ln10As", seed=seed)
    meta = sampler.run(n_walkers=12, n_steps=10, burn_steps=5, progress=False)
    samples = sampler.get_samples(burn=5, flat=True)
    logp = sampler.get_log_prob(burn=5, flat=True)

    return {
        "model": model, "variant": variant,
        "n_samples": len(samples),
        "n_dim": sampler.n_dim,
        "param_names": sampler.prior.param_names(model),
        "best_log_prob_encountered": float(np.max(logp)) if len(logp) else -np.inf,
        "finite_logprob": bool(np.any(np.isfinite(logp))),
        "medians": np.median(samples, axis=0).tolist() if len(samples) else [],
        "emulator_loaded": sampler.like._emulator is not None,
    }

def main():
    if not _emu_unlocked():
        print("PRODUCTION EMULATOR NOT UNLOCKED. Aborting.")
        return 1

    BASEDIR.mkdir(parents=True, exist_ok=True)

    variants = ["act_baseline", "actplanck_baseline"]
    models = ["lcdm", "g1_bg", "g1_m34", "g1_mkappa"]

    print("=" * 70)
    print("  8-PATH SMOKE TEST")
    print(f"  Models: {models}")
    print(f"  Variants: {variants}")
    print(f"  8 walkers × 10 burn + 10 prod steps each")
    print("=" * 70)

    results = {}
    all_ok = True

    for variant in variants:
        for model in models:
            path = f"{variant}/{model}"
            print(f"\n  [{path}] ", end="", flush=True)
            try:
                r = smoke_one(model, variant)
                results[path] = r
                if r["finite_logprob"]:
                    emu_flag = "EMU" if r.get("emulator_loaded") else "DIRECT"
                    print(f"✓ [{emu_flag}] dim={r['n_dim']} logp={r['best_log_prob_encountered']:.1f} "
                          f"med=[{', '.join(f'{m:.2f}' for m in r['medians'])}]")
                else:
                    print(f"✗ no finite log-prob")
                    all_ok = False
            except Exception as e:
                print(f"✗ {e}")
                results[path] = {"error": str(e)}
                all_ok = False

    with open(BASEDIR / "smoke_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    if all_ok:
        print("  ALL 8 PATHS PASSED ✓")
        print("  Ready for pilot chains")
        rc = 0
    else:
        print("  SOME PATHS FAILED ✗")
        failed = [k for k, v in results.items() if not v.get("finite_logprob", False)]
        print(f"  Failed: {failed}")
        rc = 1
    print("=" * 70)
    return rc

if __name__ == "__main__":
    sys.exit(main())
