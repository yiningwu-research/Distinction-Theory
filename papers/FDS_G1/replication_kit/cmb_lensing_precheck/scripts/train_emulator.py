#!/usr/bin/env python3
"""
Train G1 lensing ratio emulator.

DEPRECATED: Prefer train_emulator_from_cache.py which:
  - Reuses pre-generated truth cache (no redundant physics computation)
  - Supports nested learning curves and kernel CV
  - Has proper spectrum + likelihood dual gates

This script is retained for backward compatibility and single-shot training.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import numpy as np
from cmb_lensing_precheck.mcmc import learning_curve, RatioEmulator, EmulatorConfig


def main():
    script_dir = Path(__file__).parent.parent
    cachedir = script_dir / "outputs" / "emulator_cache"

    if cachedir.exists():
        print("=" * 70)
        print("  Cache found - using cache-based training (recommended)")
        print("=" * 70)
        print()
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_dir / "scripts/train_emulator_from_cache.py")],
            cwd=script_dir,
        )
        return result.returncode

    outdir = script_dir / "outputs" / "emulator"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  G1 Lensing Ratio Emulator Training (LEGACY)")
    print("  (No cache found - generating training data on the fly)")
    print("=" * 70)
    print()

    amplitude_mode = "primordial"

    print("Step 1: Learning curve")
    print("-" * 70)
    lc = learning_curve(amplitude_mode=amplitude_mode,
                        n_train_list=[100, 200])

    with open(outdir / "learning_curve.json", "w") as f:
        json.dump({str(k): v for k, v in lc.items()}, f, indent=2)

    print("\nLearning curve results:")
    for n, metrics in lc.items():
        print(f"  n_train={n}: RMS={metrics['rms_pct']:.3f}%, "
              f"P95={metrics['p95_pct']:.3f}%")

    best_n = None
    for n in sorted(lc.keys()):
        if lc[n]["passed_all"]:
            best_n = n
            break

    if best_n is None:
        print("\nWARNING: No n_train passed spectrum gate.")
        best_n = 200
    else:
        print(f"\nBest n_train={best_n}")

    print()
    print("Step 2: Train final emulator")
    print("-" * 70)

    config = EmulatorConfig(n_train=best_n, n_test=100)
    emulator = RatioEmulator(amplitude_mode=amplitude_mode, config=config)
    val_metrics = emulator.train(validate_likelihood=False)

    print(f"Final validation:")
    print(f"  RMS: {val_metrics['rms_pct']:.4f}%")
    print(f"  P95: {val_metrics['p95_pct']:.4f}%")

    with open(outdir / "validation_metrics.json", "w") as f:
        json.dump(val_metrics, f, indent=2)

    print()
    print("=" * 70)
    passed = val_metrics.get("passed_all", False)
    if passed:
        print("  EMULATOR VALIDATION PASSED ✓")
        emulator_path = outdir / f"emulator_{amplitude_mode}"
        emulator.save(emulator_path)
        print(f"  Saved to: {emulator_path}")
        rc = 0
    else:
        print("  EMULATOR VALIDATION FAILED ✗")
        print("  Consider: python scripts/generate_truth_cache.py")
        print("           python scripts/train_emulator_from_cache.py")
        print("  NO production emulator written.")
        rc = 1
    print("=" * 70)

    return rc


if __name__ == "__main__":
    sys.exit(main())
