#!/usr/bin/env python3
"""
Phase 3 Smoke Test: Short MCMC runs for all 4 models × 2 variants.

Purpose: Verify infrastructure works before committing to production.

REQUIRES: production_unlock=true in the emulator.
Runs: 20 walkers × 100 steps (after 50 step burn)
This is NOT for science - just for validation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import numpy as np
from cmb_lensing_precheck.mcmc import MCMCSampler


def check_emulator_unlocked() -> bool:
    """Verify the production emulator has valid production_unlock token."""
    emu_path = Path(__file__).parent.parent / "outputs" / "emulator" / "emulator_primordial"
    token = emu_path / "production_unlock.json"
    if not token.exists():
        return False
    with open(token) as f:
        data = json.load(f)
    return data.get("production_unlock", False)


def main():
    # ── Gate: emulator must be production-unlocked ──────────────────────
    if not check_emulator_unlocked():
        print("=" * 70)
        print("  SMOKE TEST REJECTED ✗")
        print("  Production emulator NOT unlocked.")
        print("  Run train_emulator_from_cache.py and pass all gates first.")
        print("=" * 70)
        return 1

    basedir = Path(__file__).parent.parent / "outputs" / "phase3_smoke"
    basedir.mkdir(parents=True, exist_ok=True)

    variants = ["act_baseline", "actplanck_baseline"]
    models = ["lcdm", "g1_bg", "g1_m34", "g1_mkappa"]

    n_walkers = 8
    n_steps = 20
    burn_steps = 10

    print("=" * 70)
    print("  PHASE 3 SMOKE TEST")
    print("=" * 70)
    print(f"  Models: {models}")
    print(f"  Variants: {variants}")
    print(f"  Walkers: {n_walkers}, Steps: {n_steps}, Burn: {burn_steps}")
    print("  WARNING: NOT for science - for infrastructure validation only")
    print("=" * 70)
    print()

    all_passed = True
    results = {}

    for variant in variants:
        results[variant] = {}

        for model in models:
            print(f"\nRunning: {variant} / {model}")
            print("-" * 70)

            try:
                sampler = MCMCSampler(model, variant, amplitude_param="ln10As", seed=42)
                meta = sampler.run(n_walkers, n_steps, burn_steps, progress=True)

                samples = sampler.get_samples(burn=burn_steps, flat=True)
                log_probs = sampler.get_log_prob(burn=burn_steps, flat=True)

                medians = np.median(samples, axis=0)
                param_names = sampler.prior.param_names(model)

                print(f"\n  Posterior medians:")
                for name, val in zip(param_names, medians):
                    print(f"    {name:10s} = {val:.4f}")

                print(f"  Best log like = {np.max(log_probs):.2f}")
                print(f"  ✓ {variant}/{model} passed")

                results[variant][model] = {
                    "status": "success",
                    "n_samples": len(samples),
                    "best_log_like": float(np.max(log_probs)),
                    "medians": medians.tolist(),
                }

            except Exception as e:
                print(f"\n  ✗ {variant}/{model} FAILED: {e}")
                import traceback
                traceback.print_exc()
                all_passed = False
                results[variant][model] = {
                    "status": "failed",
                    "error": str(e),
                }

    print("\n" + "=" * 70)
    print("  SMOKE TEST SUMMARY")
    print("=" * 70)

    for variant in variants:
        for model in models:
            status = results[variant][model]["status"]
            symbol = "✓" if status == "success" else "✗"
            print(f"  {symbol} {variant:18s} / {model:10s}: {status}")

    print()
    if all_passed:
        print("  ALL SMOKE TESTS PASSED ✓")
        print()
        print("  Ready for:")
        print("    - Production emulator training")
        print("    - Full MCMC runs with 2+ independent ensembles")
        print("    - Production validation gates")
        rc = 0
    else:
        print("  SOME SMOKE TESTS FAILED ✗")
        print("  Do NOT run production until fixed.")
        rc = 1
    print("=" * 70)

    return rc


if __name__ == "__main__":
    sys.exit(main())