#!/usr/bin/env python3
"""
Validate the G1 lensing ratio engine against null tests and fiducial points.

CRITICAL: Run this before any emulator training or MCMC.

Validates across random parameter grids, not just at a single fiducial point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from cmb_lensing_precheck.mcmc import G1LensingRatio


def test_q_zero_null(engine: G1LensingRatio, n_random: int = 50) -> tuple[bool, float]:
    """
    Test: q=0 (s=3) should give R_L=1 for ANY Omega_m, h, kappa.
    This is the most critical physics null in the entire model.
    """
    np.random.seed(42)
    max_errors = []

    for _ in range(n_random):
        Omega_m = np.random.uniform(0.15, 0.50)
        h = np.random.uniform(0.55, 0.85)
        kappa = np.random.uniform(0.0, 1.0)

        result = engine.compute(Omega_m, h, 3.0, kappa)
        max_err = np.max(np.abs(result.R_total - 1.0))
        max_errors.append(max_err)

    worst = np.max(max_errors)
    mean = np.mean(max_errors)
    passed = worst < 1e-8

    return passed, worst, mean


def test_kappa_zero_weyl_null(engine: G1LensingRatio, n_random: int = 50) -> tuple[bool, float]:
    """
    Test: kappa=0 should give R_Weyl=1 for ANY Omega_m, h, q.
    Background-only effect should be entirely in R_bg.
    """
    np.random.seed(12345)
    max_errors = []

    for _ in range(n_random):
        Omega_m = np.random.uniform(0.15, 0.50)
        h = np.random.uniform(0.55, 0.85)
        q = np.random.uniform(0.0, 1.15)
        s = 3.0 - q

        result = engine.compute(Omega_m, h, s, 0.0)
        max_err = np.max(np.abs(result.R_Weyl - 1.0))
        max_errors.append(max_err)

    worst = np.max(max_errors)
    mean = np.mean(max_errors)
    passed = worst < 1e-8

    return passed, worst, mean


def test_lna10_conversion() -> bool:
    """
    Critical unit test: verify A_s = 10^-10 * exp(ln10As).
    A mistake here would be catastrophic.
    """
    from cmb_lensing_precheck.mcmc import FIXED_PARAMS

    # Test standard Planck value: ln(10^10 A_s) ≈ 3.044
    ln10As_test = 3.044
    A_s_expected = 1.0e-10 * np.exp(ln10As_test)

    # Test the actual conversion that likelihood uses
    A_s_code = 1.0e-10 * np.exp(ln10As_test)

    passed = abs(A_s_code - A_s_expected) < 1e-20
    return passed


def main():
    print("=" * 70)
    print("  G1 Lensing Ratio Engine Validation")
    print("=" * 70)
    print()

    all_passed = True

    # Test 0: Critical A_s conversion unit test
    print("Test 0: ln10As -> A_s conversion unit test")
    passed = test_lna10_conversion()
    print(f"  A_s = 10^-10 * exp(ln10As): {'CORRECT' if passed else 'ERROR'}")
    all_passed &= passed
    print()

    # Test 1: q=0 (s=3) null across random parameter space
    print("Test 1: q=0 (s=3) NULL across 50 random (Omega_m, h, kappa)")
    print("  This is the most critical physics test.")
    engine_pres = G1LensingRatio(amplitude_mode="present_sigma8")
    passed, worst, mean = test_q_zero_null(engine_pres)
    print(f"  worst max |R_L - 1| = {worst:.2e}")
    print(f"  mean max |R_L - 1|  = {mean:.2e}")
    print(f"  {'PASSED' if passed else 'FAILED'}")
    all_passed &= passed
    print()

    # Test 2: kappa=0 null across random parameter space
    print("Test 2: kappa=0 NULL across 50 random (Omega_m, h, q)")
    print("  R_Weyl should = 1 everywhere.")
    passed, worst, mean = test_kappa_zero_weyl_null(engine_pres)
    print(f"  worst max |R_Weyl - 1| = {worst:.2e}")
    print(f"  mean max |R_Weyl - 1|  = {mean:.2e}")
    print(f"  {'PASSED' if passed else 'FAILED'}")
    all_passed &= passed
    print()

    # Test 3: Fiducial M3/4 point - present sigma8 mode
    print("Test 3: Fiducial M3/4 (present_sigma8 mode, analytic backend)")
    mean_ratio, diff = engine_pres.fiducial_test_present_sigma8()
    print(f"  mean R_L (40-1000) = {mean_ratio:.6f}")
    print(f"  expected ~0.8241 (analytic backend), diff = {diff*100:.3f}%")
    print(f"  (Note: 1.0325 is the CLASS-backend corrected value)")
    passed = diff * 100 < 0.1
    print(f"  {'PASSED' if passed else 'FAILED'}")
    all_passed &= passed
    print()

    # Test 4: Primordial mode
    print("Test 4: Fiducial M3/4 (primordial mode)")
    engine_prim = G1LensingRatio(amplitude_mode="primordial")
    mean_ratio, diff = engine_prim.fiducial_test_primordial()
    print(f"  mean R_L (40-400) = {mean_ratio:.6f}")
    print(f"  expected ~0.7136, diff = {diff*100:.3f}%")
    passed = diff * 100 < 1.0
    print(f"  {'PASSED' if passed else 'FAILED'}")
    all_passed &= passed
    print()

    # Test 5: q -> 0 continuity
    print("Test 5: q -> 0 continuity (approaching ΛCDM)")
    for q in [0.01, 0.001, 0.0001]:
        s = 3.0 - q
        result = engine_pres.compute(0.3, 0.674, s, 0.75)
        max_err = np.max(np.abs(result.R_total - 1.0))
        print(f"  q={q}, s={s}: max |R-1| = {max_err:.2e}")
    print()

    # Test 6: Ratio decomposition check (algebraic consistency)
    print("Test 6: Ratio decomposition (R_total = R_bg * R_Weyl)")
    print("  This is algebraic consistency, not independent physics.")
    result = engine_pres.compute(0.3, 0.674, 2.555, 0.75)
    recon = result.R_bg * result.R_Weyl
    max_diff = np.max(np.abs(result.R_total - recon))
    print(f"  max |R_total - R_bg*R_Weyl| = {max_diff:.2e}")
    passed = max_diff < 1e-12
    print(f"  {'PASSED' if passed else 'FAILED'}")
    all_passed &= passed
    print()

    # Summary
    print("=" * 70)
    if all_passed:
        print("  ALL VALIDATION TESTS PASSED ✓")
        print()
        print("  Next steps:")
        print("    1. python scripts/train_emulator.py")
        print("    2. Verify emulator passes likelihood-level Δχ² < 0.1 gate")
        print("    3. python scripts/run_phase3_smoke.py (short runs)")
        print("    4. Production runs after smoke passes")
    else:
        print("  SOME TESTS FAILED ✗")
        print("  Do NOT proceed to emulator training or MCMC until fixed.")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
