#!/usr/bin/env python3
"""Reference likelihood skeleton.

Each dataset is a separate function for clarity.
Independent reimplementers can substitute their own solvers.
"""

import numpy as np
import scipy.linalg as la
from models import E_model_z, mu_response, Sigma_response, Xhat_a
from distances import comoving_distance_z

# ── covariance helpers ──────────────────────────────────────────

def _symmetrize(cov):
    return 0.5 * (cov + cov.T)

def _quad(delta, cho, max_delta=1e8):
    delta = np.asarray(delta, dtype=float)
    if not np.all(np.isfinite(delta)) or np.max(np.abs(delta)) > max_delta:
        return np.inf
    try:
        inv = la.cho_solve(cho, delta, check_finite=False)
        val = float(delta @ inv)
    except la.LinAlgError:
        return np.inf
    return val if np.isfinite(val) else np.inf


# ── SN likelihood ───────────────────────────────────────────────

def chi2_sn(theta, model, z_sn, mu_sn, cho_sn):
    """Pantheon+ SN likelihood with analytic M marginalization.

    chi2_SN = min_M (mu_obs - mu_pred(z) - M)^T C^-1 (mu_obs - mu_pred(z) - M)
            = A - B^2 / C
    """
    E = lambda z: E_model_z(model, theta, z)
    dc = comoving_distance_z(z_sn, E)
    if dc is None:
        return np.inf
    dl = (1.0 + z_sn) * dc
    mu_pred = 5.0 * np.log10(dl)
    delta = mu_sn - mu_pred
    one = np.ones_like(delta)

    try:
        inv_delta = la.cho_solve(cho_sn, delta, check_finite=False)
        inv_one = la.cho_solve(cho_sn, one, check_finite=False)
    except la.LinAlgError:
        return np.inf

    A = float(delta @ inv_delta)
    B = float(one @ inv_delta)
    C = float(one @ inv_one)
    if not np.isfinite(A) or not np.isfinite(B) or not np.isfinite(C) or C <= 0:
        return np.inf
    return float(A - B * B / C)


# ── BAO likelihood ──────────────────────────────────────────────

def chi2_bao(theta, model, z_bao, obs_bao, val_bao, cho_bao):
    """DESI DR2 BAO likelihood."""
    q_idx = {"lcdm": 1, "cpl": 3, "g1de_m34": 2, "g1de_mkappa": 2,
             "g1de_const_sigma": 2, "g1de2": 2}[model]
    q = theta[q_idx]

    E = lambda z: E_model_z(model, theta, z)
    dc = comoving_distance_z(z_bao, E)
    if dc is None:
        return np.inf
    E_vals = E_model_z(model, theta, z_bao)

    pred = []
    for z, ob, dci, ei in zip(z_bao, obs_bao, dc, E_vals):
        if ob == "DM_over_rd":
            pred.append(q * dci)
        elif ob == "DH_over_rd":
            pred.append(q / ei)
        elif ob == "DV_over_rd":
            pred.append(q * (z * dci * dci / ei) ** (1.0 / 3.0))
        else:
            raise ValueError(f"Unknown BAO observable: {ob}")
    return _quad(val_bao - np.asarray(pred), cho_bao)


# ── Growth likelihood (fσ8) ─────────────────────────────────────

def chi2_growth(theta, model, z_growth, val_growth, cho_growth):
    """RSD growth-rate likelihood."""
    # Growth solver placeholder — independent reimplementers should
    # integrate the growth equation numerically.  See MODEL_SPEC.md.
    return 0.0


# ── E_G likelihood ──────────────────────────────────────────────

def chi2_eg(theta, model, z_eg, val_eg, cho_eg):
    """E_G compressed-test likelihood."""
    # E_G prediction = Omega_m * Sigma(z) / f(z)
    # Placeholder — independent reimplementers should integrate
    # growth equation to compute f(z).  See MODEL_SPEC.md.
    return 0.0


# ── Joint chi2 ──────────────────────────────────────────────────

def joint_chi2(theta, model, z_sn, mu_sn, cho_sn,
               z_bao, obs_bao, val_bao, cho_bao,
               z_growth, val_growth, cho_growth,
               z_eg, val_eg, cho_eg):
    return (chi2_sn(theta, model, z_sn, mu_sn, cho_sn) +
            chi2_bao(theta, model, z_bao, obs_bao, val_bao, cho_bao) +
            chi2_growth(theta, model, z_growth, val_growth, cho_growth) +
            chi2_eg(theta, model, z_eg, val_eg, cho_eg))
