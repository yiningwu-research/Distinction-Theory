#!/usr/bin/env python3
"""
ACT+PR4 combined fiducial check (Phase 1C)
Uses official actplanck_baseline variant.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import classy
import yaml


def get_clkk_from_params(params, ell):
    """Get C_L^κκ from CLASS params with correct conversion."""
    cosmo = classy.Class()
    cosmo.set(params)
    cosmo.compute()
    cls = cosmo.lensed_cl(int(ell[-1]))
    ell_c = np.array(cls['ell'], dtype=float)
    
    clkk = np.zeros_like(ell_c)
    mask = ell_c > 0
    clkk[mask] = (ell_c[mask] * (ell_c[mask] + 1)) ** 2 / 4 * cls['pp'][mask]
    
    return np.interp(ell.astype(float), ell_c, clkk, left=0.0, right=0.0)


def main():
    script_dir = Path(__file__).parent.parent
    outdir = script_dir / "outputs/phase1c_combined_fiducial"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  PHASE 1C: ACT+PR4 COMBINED FIDUCIAL CHECK")
    print("=" * 70)
    print()

    ell = np.arange(0, 3000, dtype=int)
    
    models = {
        'planck2018_lcdm': {
            'desc': 'Planck 2018 ΛCDM (Ω_m=0.315)',
            'params': {
                'output': 'tCl, lCl, pCl, mPk',
                'l_max_scalars': 2999,
                'lensing': 'yes',
                'omega_b': 0.0224,
                'omega_cdm': 0.1192,
                'h': 0.674,
                'A_s': 2.196e-9,
                'tau_reio': 0.056,
                'n_s': 0.965,
            }
        },
        'g1_template_lcdm': {
            'desc': 'G1 template ΛCDM (Ω_m=0.2966)',
            'params': {
                'output': 'tCl, lCl, pCl, mPk',
                'l_max_scalars': 2999,
                'lensing': 'yes',
                'omega_b': 0.049 * 0.674**2,
                'omega_cdm': (0.2966 - 0.049) * 0.674**2,
                'h': 0.674,
                'A_s': 2.1e-9,
                'tau_reio': 0.054,
                'n_s': 0.965,
            }
        },
    }
    
    # Compute spectra
    clkk = {}
    for name, info in models.items():
        print(f"Computing {name} ({info['desc']})...")
        clkk[name] = get_clkk_from_params(info['params'], ell)
    
    print()
    print("=" * 70)
    print("  EVALUATING OFFICIAL ACT+PR4 COMBINED LIKELIHOOD")
    print("=" * 70)
    print()
    
    import act_dr6_lenslike as alike
    
    results = {}
    
    for variant in ['act_baseline', 'actplanck_baseline']:
        print(f"\n=== {variant.upper()} ===")
        data = alike.load_data(variant, lens_only=True, like_corrections=False)
        
        n_bins = len(data['data_binned_clkk'])
        nell = data['binmat_act'].shape[1]
        ell_full = np.arange(nell, dtype=int)
        
        results[variant] = {}
        results[variant]['n_bins'] = n_bins
        
        for name in models:
            clkk_full = np.interp(ell_full.astype(float), ell.astype(float), clkk[name], left=0.0, right=0.0)
            
            if data.get('include_planck', False):
                cl_binned_act = data['binmat_act'] @ clkk_full
                cl_binned_planck = data['binmat_planck'] @ clkk_full
                cl_binned = np.concatenate([cl_binned_act, cl_binned_planck])
            else:
                cl_binned = data['binmat_act'] @ clkk_full
            
            chi2 = float((data['data_binned_clkk'] - cl_binned) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned))
            results[variant][name] = chi2
            print(f"  χ² {name:20s}: {chi2:.2f} (n={n_bins})")
        
        # G1 m=3/4 at fixed σ₈ (ratio 1.0325)
        clkk_full_g1 = np.interp(ell_full.astype(float), ell.astype(float), clkk['g1_template_lcdm'] * 1.0325, left=0.0, right=0.0)
        
        if data.get('include_planck', False):
            cl_binned_act = data['binmat_act'] @ clkk_full_g1
            cl_binned_planck = data['binmat_planck'] @ clkk_full_g1
            cl_binned_g1 = np.concatenate([cl_binned_act, cl_binned_planck])
        else:
            cl_binned_g1 = data['binmat_act'] @ clkk_full_g1
        
        chi2_g1 = float((data['data_binned_clkk'] - cl_binned_g1) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_g1))
        results[variant]['g1_m34_fixed_sigma8'] = chi2_g1
        print(f"  χ² g1_m34_fixed_sigma8    : {chi2_g1:.2f}")
        
        # G1 fixed primordial (ratio 0.685 from earlier diagnostics)
        clkk_full_g1_prim = np.interp(ell_full.astype(float), ell.astype(float), clkk['g1_template_lcdm'] * 0.685, left=0.0, right=0.0)
        
        if data.get('include_planck', False):
            cl_binned_act = data['binmat_act'] @ clkk_full_g1_prim
            cl_binned_planck = data['binmat_planck'] @ clkk_full_g1_prim
            cl_binned_g1_prim = np.concatenate([cl_binned_act, cl_binned_planck])
        else:
            cl_binned_g1_prim = data['binmat_act'] @ clkk_full_g1_prim
        
        chi2_g1_prim = float((data['data_binned_clkk'] - cl_binned_g1_prim) @ data['cinv'] @ (data['data_binned_clkk'] - cl_binned_g1_prim))
        results[variant]['g1_m34_fixed_primordial'] = chi2_g1_prim
        print(f"  χ² g1_m34_fixed_primordial: {chi2_g1_prim:.2f}")
        
        # s=3 exact null
        print(f"  χ² s=3 null (no modification): {results[variant]['g1_template_lcdm']:.2f}")
        
        # Δχ²
        delta = chi2_g1 - results[variant]['g1_template_lcdm']
        print(f"  Δχ² (G1 - ΛCDM fixed σ₈): {delta:+.2f}")
        delta_prim = chi2_g1_prim - results[variant]['g1_template_lcdm']
        print(f"  Δχ² (G1 - ΛCDM fixed prim.): {delta_prim:+.2f}")
    
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print()
    
    for variant in ['act_baseline', 'actplanck_baseline']:
        print(f"\n{variant}:")
        print(f"  Planck 2018 ΛCDM (Ω_m=0.315): χ² = {results[variant]['planck2018_lcdm']:.2f}")
        print(f"  G1 template ΛCDM (Ω_m=0.2966): χ² = {results[variant]['g1_template_lcdm']:.2f}")
        print(f"  G1 m=3/4 fixed σ₈ (+3.3%):   χ² = {results[variant]['g1_m34_fixed_sigma8']:.2f}")
        print(f"  G1 m=3/4 fixed prim. (-31.5%): χ² = {results[variant]['g1_m34_fixed_primordial']:.2f}")
        print(f"  Δχ² (fixed σ₈):   {results[variant]['g1_m34_fixed_sigma8'] - results[variant]['g1_template_lcdm']:+.2f}")
        print(f"  Δχ² (fixed prim.): {results[variant]['g1_m34_fixed_primordial'] - results[variant]['g1_template_lcdm']:+.2f}")
    
    # Save
    with open(outdir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    np.savetxt(outdir / "spectra.csv",
               np.column_stack([ell, clkk['planck2018_lcdm'], clkk['g1_template_lcdm']]),
               delimiter=",", header="ell,clkk_planck2018,clkk_g1_template")
    
    print(f"\nResults saved to {outdir}/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
