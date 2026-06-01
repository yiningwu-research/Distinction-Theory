#!/usr/bin/env python3
"""
Test 3b: Same-ξ± isolated comparison.

Feed KCAP's own ξ₊, ξ₋ through my Tₙ projection and compare
with KCAP's COSEBIs Eₙ for bin pair (1,1).

If Tₙ implementation matches, Eₙ should agree regardless of input Cℓ.
"""
from __future__ import annotations
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosebis_filters import Tplus, Tminus, compute_En, load_roots_norms, ARCMIN

#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
KCAP = Path("/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/stage3_kids1000/raw/extracted/Cat_to_Obs_K1000_P1-master/Predictions/kcap_xi/outputs/test_output_S8_fid_test")

def main():
    # KCAP's θ grid
    theta = np.loadtxt(str(KCAP / "shear_xi_plus/theta.txt"))
    print(f"θ grid: {len(theta)} pts [{theta[0]:.4f}', {theta[-1]:.2f}']")

    # Clip to COSEBIs domain [0.5', 300']
    tmin, tmax = 0.5, 300.0
    mask = (theta >= tmin) & (theta <= tmax)
    theta = theta[mask]
    print(f"Clipped to [{tmin}', {tmax}']: {len(theta)} pts")

    # KCAP's ξ₊, ξ₋ for bin_1_1
    xip_all = np.loadtxt(str(KCAP / "shear_xi_plus/bin_1_1.txt"))
    xim_all = np.loadtxt(str(KCAP / "shear_xi_minus/bin_1_1.txt"))
    xip = xip_all[mask]
    xim = xim_all[mask]
    print(f"ξ₊ shape: {xip.shape}, ξ₋ shape: {xim.shape}")
    print(f"ξ₊ range: [{xip.min():.4e}, {xip.max():.4e}]")
    print(f"ξ₋ range: [{xim.min():.4e}, {xim.max():.4e}]")

    # KCAP's Eₙ for bin_1_1
    kcap_En = np.loadtxt(str(KCAP / "cosebis/bin_1_1.txt"))
    print(f"\nKCAP Eₙ for bin_1_1 (first 5 modes):")
    for n, en in enumerate(kcap_En, 1):
        print(f"  mode {n}: {en:.6e}")

    # Load my Tₙ filters (same roots/norms as KiDS)
    ROOTS = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/external/src/cosebis/TLogsRootsAndNorms")
    roots_list, norms = load_roots_norms(
        str(ROOTS / "Root_0.50-300.00.table"),
        str(ROOTS / "Normalization_0.50-300.00.table"),
        20
    )
    tmin, tmax = 0.5, 300.0

    # Compute my Tₙ on KCAP's θ grid
    Tp = np.zeros((20, len(theta)))
    Tm = np.zeros((20, len(theta)))
    for n in range(20):
        Tp[n] = Tplus(theta, tmin, tmax, n, norms[n], roots_list[n])
        Tm[n] = Tminus(theta, tmin, tmax, n, norms[n], roots_list[n])

    # Compute Eₙ using my projection on KCAP's ξ±
    my_En = compute_En(xip, xim, theta, Tp, Tm)

    print(f"\nMy Eₙ (using KCAP's ξ± and my Tₙ):")
    for n, en in enumerate(my_En[:5], 1):
        print(f"  mode {n}: {en:.6e}")

    print(f"\nComparison (first 5 modes):")
    print(f"{'mode':>5} {'KCAP':>16} {'MINE':>16} {'ratio':>10} {'diff':>12}")
    for n in range(5):
        ratio = my_En[n] / kcap_En[n] if abs(kcap_En[n]) > 1e-30 else np.nan
        diff = my_En[n] - kcap_En[n]
        print(f"{n+1:5d} {kcap_En[n]:16.6e} {my_En[n]:16.6e} {ratio:10.4f} {diff:12.4e}")

    # Also test with forward and reverse mode ordering
    print(f"\nWith reverse mode order:")
    r = my_En[:5][::-1]
    for n in range(5):
        ratio = r[n] / kcap_En[n] if abs(kcap_En[n]) > 1e-30 else np.nan
        diff = r[n] - kcap_En[n]
        print(f"{n+1:5d} {kcap_En[n]:16.6e} {r[n]:16.6e} {ratio:10.4f} {diff:12.4e}")

    # Convergence of Eₙ integration
    sub_n = [100, 300, 1000, 3000, 10000]
    print(f"\nθ-grid convergence (mode 1):")
    for n in sub_n:
        idx = np.logspace(0, np.log10(len(theta)-1), n).astype(int)
        idx = np.unique(np.clip(idx, 0, len(theta)-1))
        th_sub = theta[idx]
        # Recompute Tₙ on sub-sampled grid
        Tp_sub = np.zeros((20, len(th_sub)))
        Tm_sub = np.zeros((20, len(th_sub)))
        for ni in range(20):
            Tp_sub[ni] = Tplus(th_sub, tmin, tmax, ni, norms[ni], roots_list[ni])
            Tm_sub[ni] = Tminus(th_sub, tmin, tmax, ni, norms[ni], roots_list[ni])
        En_sub = compute_En(xip[idx], xim[idx], th_sub, Tp_sub, Tm_sub)
        err = abs(En_sub[0] - my_En[0]) / max(abs(my_En[0]), 1e-30) * 100
        print(f"  nθ={n:5d}: En1={En_sub[0]:.6e}  err={err:.4f}%")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
