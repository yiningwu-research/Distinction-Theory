#!/usr/bin/env python3
"""
COSEBIs filter functions T_n^+(θ) and T_n^-(θ).

Ported from KiDS Cat_to_Obs_K1000_P1 src/cosebis/measure_cosebis.py
using TLogsRootsAndNorms roots/norms for theta range 0.5'--300'.

Convention:
    E_n = (1/2) ∫ [ξ_+(θ) T_n^+(θ) + ξ_-(θ) T_n^-(θ)] θ dθ
"""
from __future__ import annotations
import numpy as np
from scipy.interpolate import interp1d
from scipy.special.orthogonal import p_roots

ARCMIN = 180.0 * 60.0 / np.pi  # arcminutes per radian


def load_roots_norms(root_path: str, norm_path: str, n_modes: int = 20
                     ) -> tuple[list[np.ndarray], np.ndarray]:
    roots_list: list[np.ndarray] = []
    norms = np.zeros(n_modes)
    with open(root_path) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            idx = int(parts[0])
            if 1 <= idx <= n_modes:
                roots_list.append(np.array([float(v) for v in parts[1:]]))
    with open(norm_path) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            idx = int(parts[0])
            if 1 <= idx <= n_modes:
                norms[idx - 1] = float(parts[1])
    if len(roots_list) < n_modes:
        raise ValueError(f"Expected {n_modes} root entries, got {len(roots_list)}")
    return roots_list, norms


def Tplus(theta_arcmin: np.ndarray, theta_min: float, theta_max: float,
          n: int, norm: float, roots: np.ndarray) -> np.ndarray:
    z = np.log(theta_arcmin / theta_min)
    result = np.ones_like(z)
    for r in range(n + 1):
        result *= (z - roots[r])
    result *= norm
    return result


def Tminus(theta_arcmin: np.ndarray, theta_min: float, theta_max: float,
           n: int, norm: float, roots: np.ndarray, nG: int = 20) -> np.ndarray:
    tp = Tplus(theta_arcmin, theta_min, theta_max, n, norm, roots)
    tp_func = interp1d(np.log(theta_arcmin / theta_min), tp,
                       bounds_error=False, fill_value=0.0)
    z = np.log(theta_arcmin / theta_min)
    tm = tp.copy()
    xG, wG = p_roots(nG + 1)
    integ_limits = np.insert(roots / theta_min, 0, 0.0)
    for iz in range(len(z)):
        good = integ_limits <= z[iz]
        limits_good = integ_limits[good]
        result = 0.0
        for il in range(1, len(limits_good)):
            lo = limits_good[il - 1]
            hi = limits_good[il]
            delta = hi - lo
            y = 0.5 * delta * xG + 0.5 * (hi + lo)
            mask = y >= 0.0
            result += delta * 0.5 * np.sum(wG[mask] * _tminus_integ(y[mask], z[iz], tp_func))
        lo = limits_good[-1]
        hi = z[iz]
        delta = hi - lo
        y = 0.5 * delta * xG + 0.5 * (hi + lo)
        mask = y >= 0.0
        result += delta * 0.5 * np.sum(wG[mask] * _tminus_integ(y[mask], z[iz], tp_func))
        tm[iz] += result
    return tm


def _tminus_integ(y: np.ndarray, z: float, tp_func) -> np.ndarray:
    return 4.0 * tp_func(y) * (np.exp(2.0 * (y - z)) - 3.0 * np.exp(4.0 * (y - z)))


def compute_En(xi_plus: np.ndarray, xi_minus: np.ndarray,
               theta_arcmin: np.ndarray,
               Tplus_matrix: np.ndarray, Tminus_matrix: np.ndarray) -> np.ndarray:
    n_modes = Tplus_matrix.shape[0]
    En = np.zeros(n_modes)
    for n in range(n_modes):
        integ = (xi_plus * Tplus_matrix[n] + xi_minus * Tminus_matrix[n]) * theta_arcmin
        integral = np.trapz(integ, theta_arcmin)
        En[n] = 0.5 * integral / ARCMIN / ARCMIN
    return En
