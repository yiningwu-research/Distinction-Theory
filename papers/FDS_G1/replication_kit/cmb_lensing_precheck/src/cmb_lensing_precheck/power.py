from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator


class PowerSpectrum(Protocol):
    sigma8: float

    def p0(self, k_mpc: np.ndarray | float) -> np.ndarray:
        """Linear matter P(k,z=0) in Mpc^3, k in 1/Mpc."""


def _tophat(x: np.ndarray) -> np.ndarray:
    out = np.ones_like(x)
    mask = np.abs(x) > 1e-5
    xm = x[mask]
    out[mask] = 3.0 * (np.sin(xm) - xm * np.cos(xm)) / xm**3
    return out


@dataclass
class AnalyticBBKSPower:
    H0: float
    omega_m: float
    omega_b: float
    n_s: float
    sigma8: float
    k_min: float
    k_max: float
    n_k: int

    def __post_init__(self) -> None:
        self.h = self.H0 / 100.0
        k = np.geomspace(self.k_min, self.k_max, int(self.n_k))
        gamma = self.omega_m * self.h * np.exp(
            -self.omega_b * (1.0 + np.sqrt(2.0 * self.h) / self.omega_m)
        )
        q = k / max(gamma * self.h, 1e-12)
        tq = np.ones_like(q)
        mask = q > 0
        qm = q[mask]
        tq[mask] = (
            np.log1p(2.34 * qm) / (2.34 * qm)
            * (1.0 + 3.89 * qm + (16.1 * qm) ** 2 + (5.46 * qm) ** 3 + (6.71 * qm) ** 4) ** -0.25
        )
        p_unnorm = k**self.n_s * tq**2
        radius = 8.0 / self.h
        window = _tophat(k * radius)
        sigma2 = simpson(k**3 * p_unnorm * window**2, x=np.log(k)) / (2.0 * np.pi**2)
        if sigma2 <= 0 or not np.isfinite(sigma2):
            raise RuntimeError("Failed to normalize analytic matter power.")
        amplitude = self.sigma8**2 / sigma2
        self._interp = PchipInterpolator(np.log(k), np.log(amplitude * p_unnorm), extrapolate=True)

    def p0(self, k_mpc: np.ndarray | float) -> np.ndarray:
        k = np.asarray(k_mpc, dtype=float)
        k_safe = np.maximum(k, 1e-12)
        return np.exp(self._interp(np.log(k_safe)))


class ClassLinearPower:
    def __init__(self, cfg: dict):
        try:
            from classy import Class
        except ImportError as exc:
            raise ImportError("CLASS backend requested. Install with: pip install -e '.[class]'") from exc
        c = cfg["cosmology"]
        p = cfg["power"]
        h = float(c["H0"]) / 100.0
        omega_cdm = float(c["Omega_m"]) - float(c["Omega_b"])
        if omega_cdm <= 0:
            raise ValueError("Omega_m must exceed Omega_b for CLASS backend.")
        params = {
            "output": "mPk",
            "h": h,
            "Omega_b": float(c["Omega_b"]),
            "Omega_cdm": omega_cdm,
            "A_s": float(c["A_s"]),
            "n_s": float(c["n_s"]),
            "tau_reio": float(c["tau_reio"]),
            "P_k_max_h/Mpc": float(p["k_max"]) / h * 1.05,
            "z_max_pk": 0.0,
        }
        self._cosmo = Class()
        self._cosmo.set(params)
        self._cosmo.compute()
        self.sigma8 = float(self._cosmo.sigma8())

    def p0(self, k_mpc: np.ndarray | float) -> np.ndarray:
        k = np.asarray(k_mpc, dtype=float)
        flat = np.array([self._cosmo.pk_lin(float(ki), 0.0) for ki in k.ravel()])
        return flat.reshape(k.shape)

    def close(self) -> None:
        self._cosmo.struct_cleanup()
        self._cosmo.empty()


def make_power(cfg: dict) -> PowerSpectrum:
    p = cfg["power"]
    c = cfg["cosmology"]
    if p["backend"] == "analytic":
        return AnalyticBBKSPower(
            H0=float(c["H0"]),
            omega_m=float(c["Omega_m"]),
            omega_b=float(c["Omega_b"]),
            n_s=float(c["n_s"]),
            sigma8=float(c["sigma8_baseline"]),
            k_min=float(p["k_min"]),
            k_max=float(p["k_max"]),
            n_k=int(p["n_k"]),
        )
    if p["backend"] == "class":
        return ClassLinearPower(cfg)
    raise ValueError(f"Unknown power backend {p['backend']!r}.")
