"""
Lightweight 2D ΛCDM baseline emulator loader.

Loads a pre-trained BaselineEmulator from disk and provides predict().
No CLASS dependency — uses only numpy + scipy RBF.
"""

from __future__ import annotations
import json
import numpy as np
from pathlib import Path
from typing import Optional


class BaselineEmulator:
    """Load and predict with a pre-trained 2D (Ω_m, h) ΛCDM emulator."""

    def __init__(self):
        self.pca_mean = None
        self.pca_components = None
        self.params_train = None
        self.logCL_train = None
        self.n_pca = 0
        self.interpolators = []
        self._kernel = "quintic"
        self._epsilon = None
        self._smoothing = 0.0
        self._Om_min, self._Om_max = 0.15, 0.50
        self._h_min, self._h_max = 0.55, 0.85
        self._ln10As_ref = 3.044
        self._A_s_ref = 1e-10 * np.exp(self._ln10As_ref)

    def _to_unit(self, params):
        u = np.zeros_like(params)
        u[:, 0] = (params[:, 0] - self._Om_min) / (self._Om_max - self._Om_min)
        u[:, 1] = (params[:, 1] - self._h_min) / (self._h_max - self._h_min)
        return np.clip(u, 0.0, 1.0)

    def predict(self, Omega_m: float, h: float, ln10As: Optional[float] = None):
        """Predict C_L^κκ. If ln10As given, apply A_s linear scaling."""
        p = np.array([[Omega_m, h]])
        u = self._to_unit(p)
        coeffs = np.array([float(interp(u)[0]) for interp in self.interpolators])
        logCL_train = coeffs @ self.pca_components + self.pca_mean
        cl = np.zeros(3000)
        cl[2:] = np.exp(logCL_train)
        if ln10As is not None:
            A_s = 1e-10 * np.exp(ln10As)
            cl = cl * (A_s / self._A_s_ref)
        return cl

    @classmethod
    def load(cls, path: str | Path) -> "BaselineEmulator":
        path = Path(path)
        with open(path / "config.json") as f:
            cfg = json.load(f)

        from scipy.interpolate import RBFInterpolator

        emu = cls()
        emu.pca_mean = np.load(path / "pca_mean.npy")
        emu.pca_components = np.load(path / "pca_components.npy")
        emu.n_pca = cfg["n_pca"]
        emu.params_train = np.load(path / "params_train.npy")
        emu.logCL_train = np.load(path / "logCL_train.npy")
        emu._kernel = cfg.get("kernel", "quintic")
        emu._epsilon = cfg.get("epsilon", None)
        emu._smoothing = cfg.get("smoothing", 0.0)
        emu._ln10As_ref = cfg.get("ln10As_ref", 3.044)
        emu._A_s_ref = 1e-10 * np.exp(emu._ln10As_ref)

        unit = emu._to_unit(emu.params_train)
        centered = emu.logCL_train - emu.pca_mean
        coeffs = centered @ emu.pca_components.T
        rbf_kw = {"kernel": emu._kernel, "smoothing": emu._smoothing}
        if emu._kernel not in {"linear", "thin_plate_spline", "cubic", "quintic"}:
            rbf_kw["epsilon"] = emu._epsilon

        emu.interpolators = [
            RBFInterpolator(unit, coeffs[:, i], **rbf_kw) for i in range(emu.n_pca)
        ]
        return emu
