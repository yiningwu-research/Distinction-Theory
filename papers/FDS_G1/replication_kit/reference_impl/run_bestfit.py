#!/usr/bin/env python3
"""Fast best-fit chi2_min reproduction using scipy optimizer.

Verifies that the reference best-fit point reproduces the expected chi2_min.
Use this as a smoke test before running full nested evidence.
"""

import sys
import numpy as np
import scipy.optimize as opt
from models import E_model_z, BESTFIT, PARAM_NAMES, BOUNDS
from distances import comoving_distance_z


def fast_chi2_sn_bao(theta, model, z_sn, mu_sn, z_bao, obs_bao, val_bao,
                      q_idx, bao_pred_fn):
    """Minimal SN+BAO chi2 for optimizer check (no growth integration)."""
    import scipy.linalg as la

    def _quad(delta, cho):
        try:
            inv = la.cho_solve(cho, delta, check_finite=False)
            return float(delta @ inv)
        except la.LinAlgError:
            return np.inf

    q = theta[q_idx]
    E = lambda z: E_model_z(model, theta, z)
    dc_all = comoving_distance_z(np.concatenate([z_sn, z_bao]), E)
    if dc_all is None:
        return np.inf
    dc_sn = dc_all[:len(z_sn)]
    dc_bao = dc_all[len(z_sn):]

    # SN (analytic M marginalization)
    dl = (1.0 + z_sn) * dc_sn
    mu_pred = 5.0 * np.log10(dl)
    delta = mu_sn - mu_pred
    one = np.ones_like(delta)
    # Expect cho_sn to be loaded from data
    return np.inf  # placeholder — implement with data paths


if __name__ == "__main__":
    print("run_bestfit.py: Placeholder — integrate with data loading.")
    print("For full reproduction, use nested sampling or MCMC drivers.")
