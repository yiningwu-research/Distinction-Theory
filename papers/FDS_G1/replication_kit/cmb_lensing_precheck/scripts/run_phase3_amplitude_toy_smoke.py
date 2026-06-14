#!/usr/bin/env python3
"""
PHYSICS_PLACEHOLDER: DO NOT USE FOR SCIENCE INFERENCE.

Amplitude-toy smoke test: {Ω_m, σ₈, h, κ} with s=3 fixed.
This uses a placeholder ratio R=1+0.044κ, NOT the real G1 lensing response.

Three toy model families:
- bg_only: κ = 0
- m34: κ = 0.75
- free_kappa: κ sampled

This code is for MCMC infrastructure testing ONLY.
It does NOT implement the G1 model physics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import emcee
import numpy as np
import classy
import yaml


class LensingLikelihood:
    def __init__(self, variant='act_baseline', lens_only=True, like_corrections=False, model='free_kappa'):
        import act_dr6_lenslike as alike
        self.data = alike.load_data(variant, lens_only=lens_only, like_corrections=like_corrections)
        self.include_planck = self.data.get('include_planck', False)
        self.ell_full = np.arange(self.data['binmat_act'].shape[1], dtype=int)
        self.model = model
        
        # Fixed Planck 2018 reference values
        self.fixed = {
            'omega_b': 0.0224,
            'n_s': 0.965,
            'tau_reio': 0.056,
        }
    
    def _ratio(self, kappa):
        """G1/ΛCDM C_L^κκ ratio: κ=0 → 1, κ=0.75 → 1.0325 (3.3%)."""
        return 1.0 + 0.044 * min(max(kappa, 0.0), 1.0)
    
    def get_clkk(self, theta):
        if self.model == 'bg_only':
            Omega_m, sigma8, h = theta
            kappa = 0.0
        elif self.model == 'm34':
            Omega_m, sigma8, h = theta
            kappa = 0.75
        else:
            Omega_m, sigma8, h, kappa = theta
        
        omega_b = self.fixed['omega_b']
        omega_nu = 0.0006
        omega_cdm = Omega_m * h**2 - omega_b - omega_nu
        
        if omega_cdm <= 0:
            return None
        
        # Compute σ₈-scaled A_s
        params_pk = {
            'output': 'mPk',
            'P_k_max_1/Mpc': 3.0,
            'omega_b': omega_b,
            'omega_cdm': omega_cdm,
            'h': h,
            'n_s': self.fixed['n_s'],
            'A_s': 2.1e-9,
            'tau_reio': self.fixed['tau_reio'],
        }
        
        cosmo = classy.Class()
        cosmo.set(params_pk)
        cosmo.compute()
        
        sigma8_lcdm = cosmo.sigma(8.0 / h, 0.0)
        A_s = 2.1e-9 * (sigma8 / sigma8_lcdm)**2
        
        # Lensing
        params_len = {
            'output': 'tCl, lCl, pCl',
            'l_max_scalars': 2999,
            'lensing': 'yes',
            'omega_b': omega_b,
            'omega_cdm': omega_cdm,
            'h': h,
            'n_s': self.fixed['n_s'],
            'A_s': A_s,
            'tau_reio': self.fixed['tau_reio'],
        }
        
        cosmo_len = classy.Class()
        cosmo_len.set(params_len)
        cosmo_len.compute()
        
        cls = cosmo_len.lensed_cl(2999)
        ell_c = np.array(cls['ell'], dtype=float)
        
        clkk = np.zeros_like(ell_c)
        mask = ell_c > 0
        clkk[mask] = (ell_c[mask] * (ell_c[mask] + 1)) ** 2 / 4 * cls['pp'][mask]
        
        if kappa > 0:
            clkk *= self._ratio(kappa)
        
        return np.interp(self.ell_full.astype(float), ell_c, clkk, left=0.0, right=0.0)
    
    def log_prior(self, theta):
        if self.model in ['bg_only', 'm34']:
            Omega_m, sigma8, h = theta
        else:
            Omega_m, sigma8, h, kappa = theta
        
        if not (0.1 < Omega_m < 0.6): return -np.inf
        if not (0.5 < sigma8 < 1.3): return -np.inf
        if not (0.55 < h < 0.9): return -np.inf
        
        if self.model not in ['bg_only', 'm34']:
            if not (0.0 <= kappa < 1.5): return -np.inf
        
        lp = 0.0
        lp += -np.log(Omega_m)
        lp += -np.log(sigma8)
        
        return lp
    
    def log_likelihood(self, theta):
        clkk = self.get_clkk(theta)
        if clkk is None:
            return -np.inf
        
        if self.include_planck:
            cl_binned_act = self.data['binmat_act'] @ clkk
            cl_binned_planck = self.data['binmat_planck'] @ clkk
            cl_binned = np.concatenate([cl_binned_act, cl_binned_planck])
        else:
            cl_binned = self.data['binmat_act'] @ clkk
        
        chi2 = float((self.data['data_binned_clkk'] - cl_binned) @ self.data['cinv'] @ (self.data['data_binned_clkk'] - cl_binned))
        return -0.5 * chi2
    
    def log_prob(self, theta):
        lp = self.log_prior(theta)
        if not np.isfinite(lp):
            return -np.inf
        return lp + self.log_likelihood(theta)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', default='act_baseline')
    parser.add_argument('--model', default='free_kappa')
    parser.add_argument('--n-walkers', type=int, default=40)
    parser.add_argument('--n-steps', type=int, default=5000)
    args = parser.parse_args()
    
    variant = args.variant
    model = args.model
    n_walkers = args.n_walkers
    n_steps = args.n_steps
    
    script_dir = Path(__file__).parent.parent
    
    if model in ['bg_only', 'm34']:
        ndim = 3
        param_names = ['Omega_m', 'sigma8', 'h']
        if model == 'bg_only':
            center = np.array([0.315, 0.811, 0.674])
        else:
            center = np.array([0.315, 0.811, 0.674])
    else:
        ndim = 4
        param_names = ['Omega_m', 'sigma8', 'h', 'kappa']
        center = np.array([0.315, 0.811, 0.674, 0.1])
    
    print("=" * 70)
    print(f"  L0 MCMC: {variant.upper()}, model={model}")
    print(f"  Parameters: {{{', '.join(param_names)}}}")
    print(f"  Walkers: {n_walkers}, Steps: {n_steps}")
    print("=" * 70)
    print()
    
    like = LensingLikelihood(variant=variant, lens_only=True, like_corrections=False, model=model)
    
    pos = center + 1e-2 * np.random.randn(n_walkers, ndim)
    sampler = emcee.EnsembleSampler(n_walkers, ndim, like.log_prob)
    
    print("Running burn-in (500 steps)...")
    pos, _, _ = sampler.run_mcmc(pos, 500, progress=True)
    sampler.reset()
    
    print(f"\nRunning production ({n_steps} steps)...")
    sampler.run_mcmc(pos, n_steps, progress=True)
    
    print()
    print("=" * 70)
    print("  CONVERGENCE")
    print("=" * 70)
    
    tau = sampler.get_autocorr_time(tol=0)
    print(f"Autocorrelation times: {tau}")
    print(f"Mean τ = {tau.mean():.1f}")
    print(f"Steps / τ = {n_steps / tau.mean():.1f}")
    print(f"Mean acceptance fraction: {np.mean(sampler.acceptance_fraction):.3f}")
    
    outdir = script_dir / f"outputs/phase3_mcmc_l0_{variant}_{model}"
    outdir.mkdir(parents=True, exist_ok=True)
    
    flat_samples = sampler.get_chain(discard=0, flat=True)
    log_probs = sampler.get_log_prob(discard=0, flat=True)
    
    np.save(outdir / "samples.npy", flat_samples)
    np.save(outdir / "log_probs.npy", log_probs)
    
    with open(outdir / "summary.json", "w") as f:
        json.dump({
            'n_walkers': n_walkers,
            'n_steps': n_steps,
            'autocorr_times': tau.tolist(),
            'acceptance_fraction': float(np.mean(sampler.acceptance_fraction)),
            'parameters': param_names,
            'variant': variant,
            'model': model,
        }, f, indent=2)
    
    print()
    print("=" * 70)
    print("  POSTERIOR SUMMARY (median ± std)")
    print("=" * 70)
    
    burn = int(2 * tau.max())
    samples_thin = sampler.get_chain(discard=burn, flat=True, thin=int(tau.mean()))
    
    display_names = {'Omega_m': 'Ω_m', 'sigma8': 'σ₈', 'h': 'h', 'kappa': 'κ'}
    for i, name in enumerate(param_names):
        med = np.median(samples_thin[:, i])
        std = np.std(samples_thin[:, i])
        print(f"  {display_names[name]:5s}: {med:.4f} ± {std:.4f}")
    
    print()
    print(f"Results saved to {outdir}/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
