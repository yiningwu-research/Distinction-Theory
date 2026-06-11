from __future__ import annotations

import numpy as np


def chi_h(a: np.ndarray | float, omega_m: float, omega_r: float, s: float) -> np.ndarray:
    """Logistic horizon occupancy using today's non-matter/non-radiation fraction."""
    a = np.asarray(a, dtype=float)
    chi0 = 1.0 - omega_m - omega_r
    if not 0.0 < chi0 < 1.0:
        raise ValueError("Require 0 < 1-Omega_m-Omega_r < 1.")
    b = 1.0 / chi0 - 1.0
    return 1.0 / (1.0 + b * np.power(a, -s))


def xhat_raw(a: np.ndarray | float, omega_m: float, omega_r: float, s: float) -> np.ndarray:
    chi = chi_h(a, omega_m, omega_r, s)
    return 4.0 * chi * (1.0 - chi)


def response_shape(
    a: np.ndarray | float,
    omega_m: float,
    omega_r: float,
    s: float,
    normalization: str,
) -> np.ndarray:
    raw = xhat_raw(a, omega_m, omega_r, s)
    if normalization == "code":
        return raw
    if normalization == "present":
        raw0 = float(xhat_raw(1.0, omega_m, omega_r, s))
        if raw0 <= 0:
            raise ValueError("Present response normalization is non-positive.")
        return raw / raw0
    raise ValueError(f"Unknown normalization {normalization!r}.")


def horizon_factor(
    k_mpc: np.ndarray | float,
    a: np.ndarray | float,
    H_km_s_mpc: np.ndarray | float,
    completion: str,
    gamma_gamma: float,
    c_gamma: float,
) -> np.ndarray:
    k = np.asarray(k_mpc, dtype=float)
    if completion == "none":
        return np.ones_like(k)
    if completion != "single_pole":
        raise ValueError(f"Unknown horizon completion {completion!r}.")
    c_km_s = 299792.458
    aH_over_c = np.asarray(a, dtype=float) * np.asarray(H_km_s_mpc, dtype=float) / c_km_s
    k_h = k / np.maximum(aH_over_c, 1e-30)
    num = (c_gamma * k_h) ** 2
    return num / (gamma_gamma + num)


def sigma_response(
    a: np.ndarray | float,
    k_mpc: np.ndarray | float,
    H_km_s_mpc: np.ndarray | float,
    omega_m: float,
    omega_r: float,
    model_name: str,
    s: float,
    kappa: float,
    normalization: str,
    horizon_completion: str = "none",
    gamma_gamma: float = 1.0,
    c_gamma: float = 1.0,
) -> np.ndarray:
    if model_name in {"lcdm", "background_only"}:
        return np.ones(np.broadcast(np.asarray(a), np.asarray(k_mpc)).shape, dtype=float)
    if model_name == "g1de_m34":
        kappa_eff = 0.75
    elif model_name == "g1de_mkappa":
        kappa_eff = kappa
    else:
        raise ValueError(f"Unsupported model {model_name!r}.")
    shape = response_shape(a, omega_m, omega_r, s, normalization)
    delta = -kappa_eff * (3.0 - s) * shape
    factor = horizon_factor(k_mpc, a, H_km_s_mpc, horizon_completion, gamma_gamma, c_gamma)
    return 1.0 + delta * factor
