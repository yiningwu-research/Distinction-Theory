#!/usr/bin/env python3
"""
Phase 2: Fiducial ACT Lens Likelihood (CORRECT CONVENTIONS)

CLASS pp = raw C_L^φφ (NOT D_L format)
C_L^κκ = [L(L+1)]²/4 * pp  (correct conversion)
ACT expects raw C_L^κκ (NOT D_L = L(L+1)C_L/(2π))
Limber calibration: 4.874 (calibrated against CLASS native)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import classy
import yaml


def get_class_native_clkk(cfg: dict, ell: np.ndarray) -> np.ndarray:
    """Get CLASS native C_L^κκ with correct conversion."""
    h = cfg['cosmology']['H0'] / 100.0
    params = {
        'output': 'tCl, lCl, pCl, mPk',
        'l_max_scalars': int(ell[-1]),
        'lensing': 'yes',
        'omega_b': cfg['cosmology']['Omega_b'] * h**2,
        'omega_cdm': (cfg['cosmology']['Omega_m'] - cfg['cosmology']['Omega_b']) * h**2,
        'h': h,
        'n_s': float(cfg['cosmology'].get('n_s', 0.965)),
        'A_s': float(cfg['cosmology'].get('A_s', 2.1e-9)),
        'tau_reio': float(cfg['cosmology'].get('tau_reio', 0.054)),
    }
    cosmo = classy.Class()
    cosmo.set(params)
    cosmo.compute()
    cls = cosmo.lensed_cl(int(ell[-1]))
    ell_c = np.array(cls['ell'], dtype=float)
    
    # CORRECT: C_L^κκ = [L(L+1)]²/4 * pp  (pp is raw C_L^φφ)
    clkk = np.zeros_like(ell_c)
    mask = ell_c > 0
    clkk[mask] = (ell_c[mask] * (ell_c[mask] + 1)) ** 2 / 4 * cls['pp'][mask]
    
    return np.interp(ell.astype(float), ell_c, clkk, left=0.0, right=0.0)


def compute_limber_ratio(cfg: dict) -> tuple:
    """Compute G1/ΛCDM C_L^κκ ratio via Limber (robust)."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from cmb_lensing_precheck.background import make_background
    from cmb_lensing_precheck.growth import solve_growth
    from cmb_lensing_precheck.class_backend.adapter import ClassLinearPower

    int_cfg = cfg['integration']
    z_max = float(int_cfg['z_max'])
    n_z = int(int_cfg['n_z'])
    z = np.expm1(np.linspace(np.log(1+1e-7), np.log(1+z_max), n_z))
    z[0] = 1e-7
    z[-1] = z_max * (1 - 1e-8)

    C_KM_S = 299792.458
    H0 = cfg['cosmology']['H0']
    Omega_m = cfg['cosmology']['Omega_m']
    h = H0 / 100.0
    power = ClassLinearPower(cfg)
    power.compute()

    ell_min = int(int_cfg['ell_min'])
    ell_max = int(int_cfg['ell_max'])
    ell = np.arange(ell_min, ell_max + 1, dtype=int)

    for model_name in ['lcdm', 'g1']:
        bg = make_background(cfg, model_name=model_name)
        growth = solve_growth(bg, float(int_cfg['a_ini']))
        chi_fun = bg.comoving_distance_interpolator(z_max, n_z * 2)
        chi = chi_fun(z)
        chi_star = float(chi[-1])
        H_z = bg.H_z(z)
        dchi_dz = C_KM_S / H_z
        a_arr = 1.0 / (1.0 + z)
        D = growth.delta(a_arr) / growth.delta_today
        H0_1Mpc = H0 / C_KM_S
        W = 1.5 * Omega_m * H0_1Mpc**2 * (1 + z) * chi * (chi_star - chi) / chi_star

        clkk = np.zeros_like(ell, dtype=float)
        for i, L in enumerate(ell):
            k = L / chi
            k_h = k / h
            pk_mpc3 = power.p0(k_h) * h**3
            integrand = dchi_dz * W**2 / chi**2 * D**2 * pk_mpc3
            clkk[i] = np.trapz(integrand, x=z)

        if model_name == 'lcdm':
            clkk_lcdm = clkk.copy()
        else:
            clkk_g1 = clkk.copy()

    return ell, clkk_g1 / clkk_lcdm


def main():
    script_dir = Path(__file__).parent.parent
    outdir = script_dir / "outputs/phase2_fiducial_corrected"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  PHASE 2: FIDUCIAL LENSING LIKELIHOOD (CORRECTED CONVENTIONS)")
    print("=" * 70)
    print()

    with open(script_dir / "configs/g1_m34_fiducial.yaml") as f:
        cfg = yaml.safe_load(f)

    print("Configuration:", cfg['model']['name'], "Omega_m =", cfg['cosmology']['Omega_m'])
    print()

    # Step 1: Get CLASS native ΛCDM spectrum
    print("Computing CLASS native ΛCDM C_L^κκ (gold standard)...")
    ell = np.arange(2, 2999, dtype=int)
    clkk_lcdm = get_class_native_clkk(cfg, ell)
    print("  Done.  L=100: C_L^κκ =", f"{clkk_lcdm[98]:.3e}")
    print()

    # Step 2: Get G1/ΛCDM ratio from Limber
    print("Computing G1/ΛCDM ratio via Limber...")
    ell_ratio, ratio = compute_limber_ratio(cfg)
    print("  Done.")
    mask_40_1000 = (ell_ratio >= 40) & (ell_ratio <= 1000)
    mean_ratio = float(np.mean(ratio[mask_40_1000]))
    print(f"  Mean ratio (40-1000): {mean_ratio:.4f} (+{100*(mean_ratio-1):.2f}%)")
    print()

    # Step 3: Scale ΛCDM by ratio to get G1
    clkk_g1 = clkk_lcdm * ratio
    print(f"G1 C_L^κκ at L=100:  {clkk_g1[98]:.3e}")
    print(f"LCDM C_L^κκ at L=100: {clkk_lcdm[98]:.3e}")
    print()

    # Step 4: ACT DR6 likelihood
    print("Evaluating ACT DR6 lensing likelihood with RAW C_L^κκ...")
    import act_dr6_lenslike as alike
    
    data = alike.load_data("act_baseline", lens_only=True, like_corrections=False)
    nell = data['binmat_act'].shape[1]
    ell_full = np.arange(nell, dtype=int)
    
    # Interpolate to full range
    clkk_lcdm_full = np.interp(ell_full.astype(float), ell.astype(float), clkk_lcdm, left=0.0, right=0.0)
    clkk_g1_full = np.interp(ell_full.astype(float), ell.astype(float), clkk_g1, left=0.0, right=0.0)
    
    # NO D_L conversion! Just bin raw C_L^κκ directly
    cl_binned_lcdm = data['binmat_act'] @ clkk_lcdm_full
    cl_binned_g1 = data['binmat_act'] @ clkk_g1_full
    
    # Compute χ²
    chi2_lcdm = float((data['data_binned_clkk'] - cl_binned_lcdm) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_lcdm))
    chi2_g1 = float((data['data_binned_clkk'] - cl_binned_g1) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_g1))
    
    print()
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print()
    print(f"  χ² (ΛCDM, CLASS native): {chi2_lcdm:.2f}")
    print(f"  χ² (G1 m=34):            {chi2_g1:.2f}")
    print(f"  Δχ² (G1 - ΛCDM):        {chi2_g1 - chi2_lcdm:+.2f}")
    print()
    print(f"  G1/ΛCDM ratio (40-1000): {mean_ratio:.4f} (+{100*(mean_ratio-1):.1f}%)")
    print()

    # Amplitude scan
    print("Amplitude scan verification:")
    A_vals = np.linspace(0.90, 1.12, 45)
    chi2_A = np.zeros_like(A_vals)
    for i, A in enumerate(A_vals):
        cl_binned_A = data['binmat_act'] @ (clkk_lcdm_full * A)
        chi2_A[i] = float((data['data_binned_clkk'] - cl_binned_A) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_A))
    
    idx = np.argmin(chi2_A)
    A_near = A_vals[max(0,idx-5):min(len(A_vals),idx+6)]
    chi2_near = chi2_A[max(0,idx-5):min(len(A_vals),idx+6)]
    p = np.polyfit(A_near, chi2_near, 2)
    A_hat = -p[1] / (2*p[0])
    sigma_A = np.sqrt(1/p[0])
    
    print(f"  A_hat = {A_hat:.4f} ± {sigma_A:.4f}")
    print(f"  ACT official: A_lens = 1.013 ± 0.023")
    print(f"  Difference: {abs(A_hat - 1.013):.4f} = {abs(A_hat-1.013)/sigma_A:.1f}σ")
    print()

    # Save
    np.savetxt(outdir / "spectra.csv",
               np.column_stack([ell, clkk_lcdm, clkk_g1, ratio]),
               delimiter=",", header="ell,clkk_lcdm,clkk_g1,ratio")
    with open(outdir / "results.json", "w") as f:
        json.dump({
            "chi2_lcdm": chi2_lcdm,
            "chi2_g1": chi2_g1,
            "delta_chi2": chi2_g1 - chi2_lcdm,
            "mean_ratio_40_1000": mean_ratio,
            "amplitude_scan_A_hat": A_hat,
            "amplitude_scan_sigma_A": sigma_A,
            "note": "Raw C_L^κκ convention. CLASS pp = raw C_L^φφ."
        }, f, indent=2)
    
    print(f"Results saved to {outdir}/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
