"""
Structured G1 ratio emulator: R_total = R_bg(Ω_m, h, q) × R_Weyl(Ω_m, h, q, κ).

Lightweight loader for production MCMC. No CLASS dependency.
Null conditions enforced by construction: q=0 → R=1, κ=0 → R_Weyl=1.
"""

from __future__ import annotations
import json, numpy as np
from pathlib import Path
from scipy.interpolate import RBFInterpolator


class StructuredRatioEmulator:
    """Loads and predicts with a trained structured ratio emulator."""

    def __init__(self):
        self.ell = None
        self.use_alpha = False  # Default: full 4D, not collapsed α
        # bg emulator
        self.bg_mean = None; self.bg_components = None
        self.bg_min = None; self.bg_max = None
        self.bg_interpolators = None
        # weyl emulator
        self.weyl_mean = None; self.weyl_components = None
        self.weyl_min = None; self.weyl_max = None
        self.weyl_interpolators = None
        # metadata
        self._kernel = "quintic"
        self._neighbors_bg = None
        self._neighbors_weyl = None
        self._weyl_target = "logR"

    def _unit(self, params, pmin, pmax, *, clip: bool = False):
        u = (params - pmin) / np.maximum(pmax - pmin, 1e-30)
        if clip:
            return np.clip(u, 0.0, 1.0)
        if np.any((u < -1e-12) | (u > 1.0 + 1e-12)):
            raise ValueError(
                "StructuredRatioEmulator parameters outside training domain: "
                f"params={np.asarray(params).tolist()}, "
                f"min={np.asarray(pmin).tolist()}, max={np.asarray(pmax).tolist()}"
            )
        return np.clip(u, 0.0, 1.0)

    def _predict_emu(self, unit, interpolators, components, mean):
        coeffs = np.array([float(interp(unit)[0]) for interp in interpolators])
        return coeffs @ components + mean

    @staticmethod
    def _load_first_existing(path: Path, names: list[str]) -> np.ndarray:
        for name in names:
            candidate = path / name
            if candidate.exists():
                return np.load(candidate)
        raise FileNotFoundError(
            f"None of the expected files exist in {path}: {', '.join(names)}"
        )

    def predict_R(self, Omega_m: float, h: float, q: float, kappa: float) -> np.ndarray:
        """Predict R_total(ell) for a parameter point. Returns shape (n_ell,)."""

        # ── R_bg ──────────────────────────────────────────────────────
        if q < 1e-10:
            R_bg = np.ones(len(self.ell))
        else:
            p_bg = np.array([[Omega_m, h, q]])
            u_bg = self._unit(p_bg, self.bg_min, self.bg_max)
            log_R_bg = self._predict_emu(u_bg, self.bg_interpolators,
                                         self.bg_components, self.bg_mean)
            R_bg = np.exp(log_R_bg)

        # ── R_Weyl ────────────────────────────────────────────────────
        if kappa < 1e-10 or q < 1e-10:
            R_weyl = np.ones(len(self.ell))
        else:
            if self.use_alpha:
                alpha = q * kappa
                p_weyl = np.array([[Omega_m, h, q, alpha]])
            else:
                p_weyl = np.array([[Omega_m, h, q, kappa]])
            u_weyl = self._unit(p_weyl, self.weyl_min, self.weyl_max)
            log_R_weyl = self._predict_emu(u_weyl, self.weyl_interpolators,
                                           self.weyl_components, self.weyl_mean)
            if self._weyl_target == "G_L":
                log_R_weyl = log_R_weyl * (q * kappa)
            R_weyl = np.exp(log_R_weyl)

        return R_bg * R_weyl

    @classmethod
    def load(cls, path: str | Path) -> "StructuredRatioEmulator":
        path = Path(path)
        with open(path / "config.json") as f:
            cfg = json.load(f)

        emu = cls()
        emu.use_alpha = cfg.get("use_alpha", False)
        emu._kernel = cfg.get("kernel", "quintic")
        emu._neighbors_bg = cfg.get("neighbors_bg")
        emu._neighbors_weyl = cfg.get("neighbors_weyl")
        emu._weyl_target = cfg.get("weyl_target", "G_L" if (path / "weyl_train_G_L.npy").exists() else "logR")

        ell_path = path / "ell.npy"
        emu.ell = np.load(ell_path) if ell_path.exists() else None
        if emu.ell is None:
            raise FileNotFoundError(f"Missing ell.npy in {path}")

        # Load bg
        emu.bg_mean = np.load(path / "emu_bg_mean.npy")
        emu.bg_components = np.load(path / "emu_bg_components.npy")
        emu.bg_min = np.load(path / "emu_bg_params_min.npy")
        emu.bg_max = np.load(path / "emu_bg_params_max.npy")

        # Load weyl
        emu.weyl_mean = np.load(path / "emu_weyl_mean.npy")
        emu.weyl_components = np.load(path / "emu_weyl_components.npy")
        emu.weyl_min = np.load(path / "emu_weyl_params_min.npy")
        emu.weyl_max = np.load(path / "emu_weyl_params_max.npy")

        # Rebuild interpolators: need training data to reconstruct.
        # The training script saves R_bg_train/R_Weyl_train.
        # We use the same RBF construction.
        # For bg: 3D params, for weyl: 4D params (or 4D with alpha)
        train_bg = cls._load_first_existing(path, ["emu_bg_train_params.npy", "bg_train_params.npy"])
        train_weyl = cls._load_first_existing(path, ["emu_weyl_train_params.npy", "weyl_train_params.npy"])
        logR_bg = cls._load_first_existing(path, ["emu_bg_train_logR.npy", "bg_train_logR.npy"])
        weyl_values = cls._load_first_existing(path, ["emu_weyl_train_logR.npy", "weyl_train_G_L.npy"])

        u_bg = emu._unit(train_bg, emu.bg_min, emu.bg_max, clip=True)
        coeffs_bg = (logR_bg - emu.bg_mean) @ emu.bg_components.T
        rbf_kw_bg = {"kernel": emu._kernel}
        if emu._neighbors_bg is not None:
            rbf_kw_bg["neighbors"] = min(int(emu._neighbors_bg), len(train_bg))
        else:
            rbf_kw_bg["smoothing"] = 1e-10
        emu.bg_interpolators = []
        for i in range(emu.bg_components.shape[0]):
            try:
                emu.bg_interpolators.append(RBFInterpolator(u_bg, coeffs_bg[:, i], **rbf_kw_bg))
            except np.linalg.LinAlgError:
                fallback = {k: v for k, v in rbf_kw_bg.items() if k != "kernel"}
                emu.bg_interpolators.append(RBFInterpolator(u_bg, coeffs_bg[:, i], kernel="cubic", **fallback))

        u_weyl = emu._unit(train_weyl, emu.weyl_min, emu.weyl_max, clip=True)
        coeffs_weyl = (weyl_values - emu.weyl_mean) @ emu.weyl_components.T
        rbf_kw_weyl = {"kernel": emu._kernel}
        if emu._neighbors_weyl is not None:
            rbf_kw_weyl["neighbors"] = min(int(emu._neighbors_weyl), len(train_weyl))
        else:
            rbf_kw_weyl["smoothing"] = 1e-10
        emu.weyl_interpolators = []
        for i in range(emu.weyl_components.shape[0]):
            try:
                emu.weyl_interpolators.append(RBFInterpolator(u_weyl, coeffs_weyl[:, i], **rbf_kw_weyl))
            except np.linalg.LinAlgError:
                fallback = {k: v for k, v in rbf_kw_weyl.items() if k != "kernel"}
                emu.weyl_interpolators.append(RBFInterpolator(u_weyl, coeffs_weyl[:, i], kernel="cubic", **fallback))

        return emu
