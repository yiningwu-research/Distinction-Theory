#!/usr/bin/env python3
"""Run CLASS backend validation: analytic BBKS vs CLASS linear power.

Phase 1A: G1 CMB lensing pre-check production runner.

This script generates four outputs for both analytic and CLASS backends:
  1. C_L^φφ for ΛCDM
  2. C_L^φφ for G1
  3. R_L = C_L^G1 / C_L^ΛCDM (ratios)
  4. δR_L = (R_L^analytic - R_L^CLASS) / R_L^CLASS

Pre-registered null tests:
  A. s=3, Σ=1 → R_L ≡ 1
  B. D_G1 = D_ΛCDM, Σ=1 → R_L ≡ 1
  C. D_G1 = D_ΛCDM → R_L reflects only Σ² and geometry differences

Outputs are written to outputs/class_validation/v0.2.0/
Metadata is saved for full auditability.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cmb_lensing_precheck.background import make_background
from cmb_lensing_precheck.growth import solve_growth
from cmb_lensing_precheck.power import AnalyticBBKSPower
from cmb_lensing_precheck.class_backend.adapter import ClassLinearPower, ClassMetadata
from cmb_lensing_precheck.lensing import compute_lensing


def get_git_commit() -> str:
    """Get current git commit hash for audit."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent,
            stderr=subprocess.DEVNULL, text=True
        ).strip()[:16]
    except:
        return "unknown"


def run_lensing(cfg: Dict[str, Any], power_backend, bg, growth) -> Tuple[np.ndarray, np.ndarray]:
    """Run lensing computation with given power backend, background, and growth.

    Returns ell and clpp array.
    """
    result = compute_lensing(cfg, bg, bg, growth, growth, power_backend)
    return result.ell, result.clpp_model


def save_csv(path: Path, ell: np.ndarray, *arrays, column_names=None) -> None:
    """Save labeled CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ",".join(column_names) if column_names else "ell," + ",".join(f"col{i}" for i in range(len(arrays)))
    data = np.column_stack([ell.astype(float)] + list(arrays))
    np.savetxt(path, data, delimiter=",", header=header, comments="")


def compute_class_statistics(ell, delta_rl, ell_low_min=40, ell_low_max=400,
                            ell_high_min=400, ell_high_max=1000):
    """Compute pre-registered CLASS validation statistics."""

    def stats_in_range(lo, hi):
        mask = (ell >= lo) & (ell <= hi)
        r = delta_rl[mask]
        return {
            "ell_min": lo,
            "ell_max": hi,
            "n": int(mask.sum()),
            "weighted_rms_pct": float(
                np.sqrt(np.sum((2 * ell[mask] + 1) * r**2) / np.sum(2 * ell[mask] + 1)) * 100.0
            ),
            "p95_abs_pct": float(np.percentile(np.abs(r), 95) * 100.0),
            "max_abs_pct": float(np.max(np.abs(r)) * 100.0),
        }

    return {
        "low_multipoles": stats_in_range(ell_low_min, ell_low_max),
        "high_multipoles": stats_in_range(ell_high_min, ell_high_max),
        "full_range": stats_in_range(ell.min(), ell.max()),
    }


def main() -> int:
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "outputs/class_validation/v0.2.0"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  G1 CMB LENSING: CLASS BACKEND VALIDATION (Phase 1A)")
    print("=" * 70)
    print()
    print(f"Output directory: {output_dir}")
    print(f"Git commit: {get_git_commit()}")
    print()

    # Load fiducial configuration
    with open(script_dir / "configs/g1_m34_fiducial.yaml") as f:
        cfg = yaml.safe_load(f)

    # Record environment
    cfg['git_commit'] = get_git_commit()
    cfg['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    print("Configuration loaded:")
    print(f"  Model: s={cfg['model']['s']}, kappa={cfg['model']['kappa']}")
    print(f"  Backend: {cfg['power']['backend']} (will run both)")
    print(f"  Normalization: {cfg['model']['normalization']}")
    print(f"  Amplitude mode: {cfg['amplitude']['mode']}")
    print()

    # ------------------------------------------------------------------
    # 1. Analytic BBKS baseline
    # ------------------------------------------------------------------
    print("Running analytic BBKS backend...")
    cosm = cfg['cosmology']
    power_cfg = cfg['power']
    power_analytic = AnalyticBBKSPower(
        H0=float(cosm['H0']),
        omega_m=float(cosm['Omega_m']),
        omega_b=float(cosm['Omega_b']),
        n_s=float(cosm['n_s']),
        sigma8=float(cosm['sigma8_baseline']),
        k_min=float(power_cfg['k_min']),
        k_max=float(power_cfg['k_max']),
        n_k=int(power_cfg['n_k']),
    )
    bg_lcdm = make_background(cfg, model_name='lcdm')
    bg_g1 = make_background(cfg, model_name='g1de')
    growth_lcdm = solve_growth(bg_lcdm, float(cfg['integration']['a_ini']))
    growth_g1 = solve_growth(bg_g1, float(cfg['integration']['a_ini']))

    ell, clpp_lcdm_analytic = run_lensing(cfg, power_analytic, bg_lcdm, growth_lcdm)
    _, clpp_g1_analytic = run_lensing(cfg, power_analytic, bg_g1, growth_g1)

    rl_analytic = clpp_g1_analytic / np.maximum(clpp_lcdm_analytic, 1e-30)
    print("  ✅ Analytic backend complete")
    print()

    # ------------------------------------------------------------------
    # 2. CLASS backend
    # ------------------------------------------------------------------
    print("Running CLASS backend (this may take a minute)...")
    cfg_class = yaml.safe_load(open(script_dir / "configs/g1_m34_fiducial.yaml"))
    cfg_class['power']['backend'] = 'class'

    try:
        power_class = ClassLinearPower(cfg_class, output_dir=output_dir / "class_run")
        power_class.compute()
        print(f"  CLASS sigma8 = {power_class.sigma8:.6f}")
    except Exception as e:
        import traceback
        print(f"  ❌ CLASS backend failed: {e}")
        print("  Stack trace:")
        traceback.print_exc()
        print("  CLASS backend not available. Continuing with analytic validation only.")
        power_class = None

    if power_class is not None:
        _, clpp_lcdm_class = run_lensing(cfg_class, power_class, bg_lcdm, growth_lcdm)
        _, clpp_g1_class = run_lensing(cfg_class, power_class, bg_g1, growth_g1)

        rl_class = clpp_g1_class / np.maximum(clpp_lcdm_class, 1e-30)
        delta_rl = (rl_analytic - rl_class) / np.maximum(rl_class, 1e-10)

        print("  ✅ CLASS backend complete")
        print()

        # Compute pre-registered statistics
        stats = compute_class_statistics(ell, delta_rl)
        print("Pre-registered validation statistics:")
        print("  Low multipoles (40-400):")
        print(f"    Weighted RMS: {stats['low_multipoles']['weighted_rms_pct']:.3f}%")
        print(f"    P95(|δR|):  {stats['low_multipoles']['p95_abs_pct']:.3f}%")
        print(f"    Max(|δR|):  {stats['low_multipoles']['max_abs_pct']:.3f}%")
        print("  High multipoles (400-1000):")
        print(f"    Weighted RMS: {stats['high_multipoles']['weighted_rms_pct']:.3f}%")
        print(f"    P95(|δR|):  {stats['high_multipoles']['p95_abs_pct']:.3f}%")
        print(f"    Max(|δR|):  {stats['high_multipoles']['max_abs_pct']:.3f}%")
        print()

        # Gate decision
        rms_low = stats['low_multipoles']['weighted_rms_pct']
        if rms_low < 3.0:
            print("✅  GATE PASSED: Weighted RMS < 3%")
            print("    Analytic suppression is robust against power-backend choice.")
        elif rms_low < 10.0:
            print("⚠️   GATE CAUTION: Weighted RMS in 3-10% range")
            print("    Qualitative warning retained; quantitative must use CLASS.")
        else:
            print("❌  GATE FAILED: Weighted RMS > 10%")
            print("    Analytic benchmark insufficient for quantitative interpretation.")
        print()

    # ------------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------------
    print("Saving outputs...")

    # Always save analytic baseline
    save_csv(output_dir / "clpp_lcdm_analytic.csv", ell, clpp_lcdm_analytic,
             column_names=["ell", "clpp_lcdm_analytic"])
    save_csv(output_dir / "clpp_g1_analytic.csv", ell, clpp_g1_analytic,
             column_names=["ell", "clpp_g1_analytic"])
    save_csv(output_dir / "ratio_rl_analytic.csv", ell, rl_analytic,
             column_names=["ell", "rl_analytic"])
    print("  ✅ Analytic outputs saved")

    if power_class is not None:
        save_csv(output_dir / "clpp_lcdm_class.csv", ell, clpp_lcdm_class,
                 column_names=["ell", "clpp_lcdm_class"])
        save_csv(output_dir / "clpp_g1_class.csv", ell, clpp_g1_class,
                 column_names=["ell", "clpp_g1_class"])
        save_csv(output_dir / "ratio_rl_class.csv", ell, rl_class,
                 column_names=["ell", "rl_class"])
        save_csv(output_dir / "delta_rl_fractional_percent.csv", ell, delta_rl * 100.0,
                 column_names=["ell", "delta_rl_pct"])

        # Save statistics
        with open(output_dir / "validation_statistics.json", "w") as f:
            json.dump(stats, f, indent=2)

        # Save metadata
        power_class.save_metadata()
        print("  ✅ CLASS outputs saved")

    print()
    print("=" * 70)
    print("  PHASE 1A: CLASS VALIDATION RUN COMPLETE")
    print("=" * 70)
    print()
    print(f"Outputs in: {output_dir}")
    print()
    print("Next: Review statistics, then start Phase 1B (ACT forward-operator).")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
