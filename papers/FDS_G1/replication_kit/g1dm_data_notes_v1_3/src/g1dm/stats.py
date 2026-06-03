"""Statistical helpers for G1DM compressed diagnostics."""
from __future__ import annotations

import itertools
import numpy as np
from scipy.stats import norm, chi2


def summarize_samples(
    df,
    weight_col: str = "weight",
) -> tuple[np.ndarray, np.ndarray]:
    """Return weighted mean vector and covariance matrix from chain samples.

    Parameters
    ----------
    df : pd.DataFrame
        Samples as columns (excluding any weight column).
    weight_col : str, optional
        Name of the weight column. If absent, uniform weights are used.

    Returns
    -------
    mean : ndarray of shape (n_params,)
    cov : ndarray of shape (n_params, n_params)

    Raises
    ------
    ValueError
        If the covariance matrix has a non-positive minimum eigenvalue.
    """
    param_cols = [c for c in df.columns if c != weight_col]
    data = df[param_cols].to_numpy(dtype=float)
    if weight_col in df.columns:
        w = df[weight_col].to_numpy(dtype=float)
    else:
        w = np.ones(len(data), dtype=float)
    w = np.where(np.isfinite(w) & (w >= 0), w, 0.0)
    wsum = w.sum()
    if wsum <= 0:
        raise ValueError("Total weight is zero or negative.")
    mean = (data * w[:, None]).sum(axis=0) / wsum
    resid = data - mean
    cov = (resid * w[:, None]).T @ resid / wsum
    eigvals = np.linalg.eigvalsh(cov)
    if np.any(eigvals <= 0):
        raise ValueError(
            f"Sample covariance is not positive definite. "
            f"Minimum eigenvalue: {eigvals.min():.4g}. "
            f"Consider increasing sample size or checking for degenerate parameters."
        )
    return mean, cov


def gaussian_loglike(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    x = np.atleast_1d(np.asarray(x, dtype=float))
    mean = np.atleast_1d(np.asarray(mean, dtype=float))
    cov = np.atleast_2d(np.asarray(cov, dtype=float))
    r = x - mean
    sign, logdet = np.linalg.slogdet(cov)
    if sign <= 0:
        raise ValueError("Covariance must be positive definite")
    inv = np.linalg.inv(cov)
    return float(-0.5 * (r @ inv @ r + logdet + len(x) * np.log(2 * np.pi)))


def chi2_value(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    x = np.atleast_1d(np.asarray(x, dtype=float))
    mean = np.atleast_1d(np.asarray(mean, dtype=float))
    cov = np.atleast_2d(np.asarray(cov, dtype=float))
    r = x - mean
    return float(r @ np.linalg.inv(cov) @ r)


def bic(loglike_max: float, n_params: int, n_data: int) -> float:
    return n_params * np.log(max(n_data, 1)) - 2.0 * loglike_max


def aic(loglike_max: float, n_params: int) -> float:
    return 2 * n_params - 2.0 * loglike_max


def gaussian_linear_fit(y: np.ndarray, cov: np.ndarray, design: np.ndarray, fixed: dict[int, float] | None = None):
    """Fit y = design @ theta with Gaussian covariance.

    Parameters
    ----------
    y : array, shape (n,)
    cov : array, shape (n,n)
    design : array, shape (n,k)
    fixed : optional dict mapping parameter index to fixed value

    Returns
    -------
    theta_hat, cov_theta, loglike_max, chi2_min
    """
    y = np.asarray(y, dtype=float)
    cov = np.asarray(cov, dtype=float)
    X = np.asarray(design, dtype=float)
    if fixed:
        y_eff = y.copy()
        keep_cols = []
        for j in range(X.shape[1]):
            if j in fixed:
                y_eff = y_eff - X[:, j] * fixed[j]
            else:
                keep_cols.append(j)
        X_eff = X[:, keep_cols]
    else:
        y_eff = y
        keep_cols = list(range(X.shape[1]))
        X_eff = X
    inv = np.linalg.inv(cov)
    if X_eff.size == 0:
        theta_full = np.zeros(X.shape[1])
        if fixed:
            for j, val in fixed.items():
                theta_full[j] = val
        chi2_min = float(y_eff @ inv @ y_eff)
        loglike = gaussian_loglike(y_eff, np.zeros_like(y_eff), cov)
        return theta_full, np.zeros((X.shape[1], X.shape[1])), loglike, chi2_min
    fisher = X_eff.T @ inv @ X_eff
    cov_theta_eff = np.linalg.inv(fisher)
    theta_eff = cov_theta_eff @ (X_eff.T @ inv @ y_eff)
    theta_full = np.zeros(X.shape[1])
    cov_theta = np.zeros((X.shape[1], X.shape[1]))
    for a, j in enumerate(keep_cols):
        theta_full[j] = theta_eff[a]
        for b, k in enumerate(keep_cols):
            cov_theta[j, k] = cov_theta_eff[a, b]
    if fixed:
        for j, val in fixed.items():
            theta_full[j] = val
    resid = y - X @ theta_full
    chi2_min = float(resid @ inv @ resid)
    sign, logdet = np.linalg.slogdet(cov)
    loglike = float(-0.5 * (chi2_min + logdet + len(y) * np.log(2 * np.pi)))
    return theta_full, cov_theta, loglike, chi2_min


def model_mask_grid(n_components: int):
    """All non-empty component masks for SRO audits."""
    for mask in itertools.product([0, 1], repeat=n_components):
        if any(mask):
            yield mask


def zscore_from_gaussian(value: float, mean: float, sigma: float) -> float:
    return (value - mean) / sigma


def two_sided_p_from_z(z: float) -> float:
    return 2 * norm.sf(abs(z))


def p_from_delta_chi2(delta_chi2: float, dof: int = 1) -> float:
    return chi2.sf(delta_chi2, dof)
