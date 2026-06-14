#!/usr/bin/env python3
"""
DECISIVE CLOSURE TEST: Use ACT's own fiducial spectrum and convention.

This script:
1. Reads ACT's official fiducial lens potential spectrum
2. Converts it to C_L^κκ the EXACT SAME WAY ACT does
3. Passes RAW C_L^κκ to generic_lnlike (NO D_L conversion!)
4. Scans amplitude A to verify recovery of A_lens ~ 1.013 ± 0.023

This is the ONLY WAY to prove the convention is correct.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import act_dr6_lenslike as alike
import inspect

def main():
    print("=" * 70)
    print("  DECISIVE CLOSURE TEST: ACT Fiducial Amplitude Recovery")
    print("=" * 70)
    print()

    # Step 1: Load ACT official data
    data = alike.load_data("act_baseline", lens_only=True, like_corrections=False)

    # Step 2: Load ACT's official fiducial lens potential spectrum
    src_file = inspect.getsourcefile(alike)
    ddir = os.path.join(os.path.dirname(src_file), "data/v1.2")
    print(f"Reading ACT fiducial spectrum from: {ddir}")

    # READ THE EXACT SAME WAY ACT DOES IT
    fd_ls, f_dd = np.loadtxt(f"{ddir}/like_corrs/cosmo2017_10K_acc3_lenspotentialCls.dat", unpack=True, usecols=[0, 5])
    print()
    print(f"  L range: {fd_ls[0]:.0f} to {fd_ls[-1]:.0f}")
    print(f"  f_dd (PP column) at L=100: {f_dd[98]:.3e}")

    # CONVERT THE EXACT SAME WAY ACT DOES (line 302 in source)
    # f_kk = f_dd * 2. * np.pi / 4.
    f_kk_raw = f_dd * 2. * np.pi / 4.

    print()
    print(f"  After ACT conversion:")
    print(f"    C_L^κκ at L=100: {f_kk_raw[98]:.3e}")
    print()

    # THIS IS RAW C_L^κκ - NO FURTHER CONVERSION NEEDED!
    # Trim to L_max = 2999, pad to 0-2999
    trim_lmax = 2999
    trim_mask = fd_ls <= trim_lmax
    ell_theory = fd_ls[trim_mask].astype(float)
    clkk_trimmed = f_kk_raw[trim_mask].copy()
    # Pad to full 0-2999 range (binmat_act expects 3000 elements)
    clkk_theory = np.zeros(trim_lmax + 1)
    start_ell = int(ell_theory[0])
    clkk_theory[start_ell:] = clkk_trimmed[:trim_lmax + 1 - start_ell]
    ell_theory = np.arange(trim_lmax + 1, dtype=float)

    # Step 3: Also compute CLASS native for comparison
    import classy
    h = 0.677  # Planck 2018 best fit
    params = {
        'output': 'tCl, lCl, pCl, mPk',
        'l_max_scalars': 2999,
        'lensing': 'yes',
        'omega_b': 0.0224,
        'omega_cdm': 0.1192,
        'h': h,
        'n_s': 0.965,
        'A_s': 2.196e-9,
        'tau_reio': 0.056,
    }
    print("Computing CLASS native lensing...")
    cosmo = classy.Class()
    cosmo.set(params)
    cosmo.compute()
    cls = cosmo.lensed_cl(2999)
    ell_c = np.array(cls['ell'], dtype=float)
    clkk_class = np.zeros_like(ell_c)
    mask_class = ell_c > 0
    clkk_class[mask_class] = ell_c[mask_class] * (ell_c[mask_class] + 1) * np.pi / 2 * cls['pp'][mask_class]
    print("  Done.")
    print(f"  CLASS native C_L^κκ at L=100: {clkk_class[100]:.3e}")
    print()

    # Step 4: Test raw C_L vs D_L convention
    print("=" * 70)
    print("  TEST 1: Raw C_L^κκ binned directly")
    print("=" * 70)
    cl_binned_raw = data['binmat_act'] @ clkk_theory
    chi2_raw = float((data['data_binned_clkk'] - cl_binned_raw) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_raw))
    print()
    print(f"  Binned C_L^κκ values:")
    for i, bc in enumerate(data['bcents_act']):
        print(f"    Bin {i:2d} (ℓ={bc:4.0f}): theory={cl_binned_raw[i]:.3e}, data={data['data_binned_clkk'][i]:.3e}")
    print()
    print(f"  χ² (raw C_L^κκ): {chi2_raw:.2f}")
    print()

    print("=" * 70)
    print("  TEST 2: D_L = L(L+1)C_L/(2π) binned (WRONG convention!)")
    print("=" * 70)
    dlkk_theory = np.zeros_like(ell_theory)
    mask_dl = ell_theory > 0
    dlkk_theory[mask_dl] = ell_theory[mask_dl] * (ell_theory[mask_dl] + 1) * clkk_theory[mask_dl] / (2 * np.pi)
    dl_binned = data['binmat_act'] @ dlkk_theory
    chi2_dl = float((data['data_binned_clkk'] - dl_binned) @ data['cinv'] @ (data['data_binned_clkk'] - dl_binned))
    print()
    print(f"  Binned D_L values:")
    for i, bc in enumerate(data['bcents_act']):
        print(f"    Bin {i:2d} (ℓ={bc:4.0f}): theory={dl_binned[i]:.3e}, data={data['data_binned_clkk'][i]:.3e}")
    print()
    print(f"  χ² (D_L convention): {chi2_dl:.2f}")
    print()

    print("=" * 70)
    print("  COMPARISON: Which convention matches?")
    print("=" * 70)
    print()
    print(f"  Raw C_L^κκ:    χ² = {chi2_raw:.2f} (LOW is GOOD!)")
    print(f"  D_L (wrong):   χ² = {chi2_dl:.2f}")
    print()

    if chi2_raw < chi2_dl:
        print("  ✓ RAW C_L^κκ gives MUCH BETTER FIT!")
        print("  This confirms: ACT expects RAW C_L^κκ, NOT D_L!")
    else:
        print("  ⚠ D_L gives better fit - something still off")
    print()

    # Step 5: Amplitude scan with RAW C_L
    print("=" * 70)
    print("  AMPLITUDE SCAN WITH RAW C_L^κκ")
    print("=" * 70)
    print()

    A_vals = np.linspace(0.9, 1.15, 51)
    chi2_vals = np.zeros_like(A_vals)

    ell_full = ell_theory.copy()
    cl_tt_dummy = np.zeros_like(ell_full)
    cl_ee_dummy = np.zeros_like(ell_full)
    cl_te_dummy = np.zeros_like(ell_full)
    cl_bb_dummy = np.zeros_like(ell_full)

    print(f"  Scanning A in [{A_vals[0]:.3f}, {A_vals[-1]:.3f}]...")
    print()

    for i, A in enumerate(A_vals):
        lnlike, binned = alike.generic_lnlike(
            data, ell_full, clkk_theory * A,
            ell_full, cl_tt_dummy, cl_ee_dummy, cl_te_dummy, cl_bb_dummy,
            return_theory=True, do_norm_corr=False
        )
        chi2_vals[i] = -2.0 * float(lnlike)

    idx_best = np.argmin(chi2_vals)
    A_best = A_vals[idx_best]
    chi2_best = chi2_vals[idx_best]

    # Parabolic error estimate
    A_near = A_vals[max(0, idx_best - 5):min(len(A_vals), idx_best + 6)]
    chi2_near = chi2_vals[max(0, idx_best - 5):min(len(A_vals), idx_best + 6)]
    p = np.polyfit(A_near, chi2_near, 2)
    A_fit = -p[1] / (2 * p[0])
    sigma_A = np.sqrt(1 / p[0])

    print(f"  Best-fit A: {A_best:.4f} (χ² = {chi2_best:.2f})")
    print(f"  Parabolic fit: A_hat = {A_fit:.4f} ± {sigma_A:.4f}")
    print()
    print(f"  ACT Official Result: A_lens = 1.013 ± 0.023")
    print()

    if abs(A_fit - 1.013) < 0.02:
        print("  ✓ SUCCESS! Recovered A_lens within 0.02 of official result!")
        print(f"  ✓ CONVENTION CONFIRMED: ACT expects RAW C_L^κκ input!")
    else:
        print(f"  ⚠ Mismatch: {abs(A_fit - 1.013):.4f} off target")
        print(f"    This could be: different cosmology, or still a convention issue")
    print()

    print("=" * 70)
    print("  CONCLUSION")
    print("=" * 70)
    print()
    print("  If χ²(raw) << χ²(D_L) AND A_fit ≈ 1.013, then:")
    print("    ✓ ACT likelihood expects RAW C_L^κκ input")
    print("    ✓ Our D_L conversion was wrong!")
    print()
    print("  This explains the 8% amplitude shift.")
    print()

    # Save scan results
    outdir = Path(__file__).parent.parent / "outputs/closure_test"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savetxt(outdir / "amplitude_scan_raw_clkk.csv", np.column_stack([A_vals, chi2_vals]),
               delimiter=",", header="A,chi2")

    return 0


if __name__ == "__main__":
    sys.exit(main())
