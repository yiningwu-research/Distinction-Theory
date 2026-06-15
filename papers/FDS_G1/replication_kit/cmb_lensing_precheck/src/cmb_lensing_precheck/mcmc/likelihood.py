from __future__ import annotations

from typing import Optional
import numpy as np

try:
    import classy
    HAVE_CLASS = True
except ImportError:
    HAVE_CLASS = False

try:
    import act_dr6_lenslike as alike
    HAVE_ACT = True
except ImportError:
    HAVE_ACT = False

from .ratio_engine import G1LensingRatio
from .cosmology import CommonCosmology, build_class_params
from .emulator import RatioEmulator


class LensingLikelihood:
    """
    ACT lensing likelihood with G1 ratio correction.

    Computes lensing-only χ² using official bandpower data and covariance
    from act_dr6_lenslike.load_data(). Uses manual binning (verified
    equivalent to official generic_lnlike for lensing-only in Phase 1B).

    Architecture:
        1. Compute ΛCDM C_L^κκ via CLASS (single call per point)
        2. Apply σ8 scaling if needed
        3. Multiply by G1 ratio R_L(Omega_m, h, s, kappa)
        4. Evaluate χ² against binned data

    Uses CommonCosmology to ensure cosmology parameters are consistent
    between CLASS and the G1 ratio engine.
    """

    def __init__(self, variant: str = "act_baseline", amplitude_param: str = "ln10As"):
        if not HAVE_CLASS:
            raise ImportError("classy is required for MCMC")
        if not HAVE_ACT:
            raise ImportError("act_dr6_lenslike is required")

        self.variant = variant
        self.amplitude_param = amplitude_param

        # Load production emulators
        self._emulator = self._load_emulator()
        self._baseline_emu = self._load_baseline_emulator()

        # Direct engine kept only for diagnostics (not used in MCMC)
        self._direct_engine = G1LensingRatio(
            amplitude_mode="primordial" if amplitude_param == "ln10As" else "present_sigma8"
        )
        self._direct_engine._base_cfg["integration"]["n_z"] = 450

        self.act_data = alike.load_data(variant)
        self.ell_full = np.arange(self.act_data["binmat_act"].shape[1], dtype=int)

    def _project_root(self):
        from pathlib import Path
        return Path(__file__).parent.parent.parent.parent

    def _load_emulator(self):
        """Load the registered production G1 ratio emulator."""
        base = self._project_root()
        from .structured_emu import StructuredRatioEmulator

        candidate_paths = [
            base / "outputs" / "frozen" / "v4_act_only" / "ratio_emulator",
            base / "artifacts" / "ratio_v4_candidate_001",
            base / "outputs" / "emulator" / "emulator_primordial_v2",
        ]

        for candidate in candidate_paths:
            if (candidate / "config.json").exists():
                return StructuredRatioEmulator.load(candidate)

        # Fallback to deprecated v1, retained only for old analytic smoke outputs.
        v1_path = base / "outputs" / "emulator" / "emulator_primordial"
        if (v1_path / "production_unlock.json").exists():
            return RatioEmulator.load(v1_path)

        return None

    def _load_baseline_emulator(self):
        """Load production 2D ΛCDM baseline emulator."""
        from .baseline_emu import BaselineEmulator

        base = self._project_root()
        candidate_paths = [
            base / "outputs" / "frozen" / "v4_act_only" / "baseline_emulator",
            base / "outputs" / "emulator" / "baseline_emulator",
        ]
        for emu_path in candidate_paths:
            if (emu_path / "production_unlock.json").exists():
                return BaselineEmulator.load(emu_path)
        return None

    def _get_class_params(self, Omega_m: float, h: float,
                          ln10As: Optional[float] = None) -> Optional[dict]:
        """
        Build CLASS parameter dict from CommonCosmology.

        ln10As = ln(10^10 A_s), so A_s = 10^-10 * exp(ln10As)
        """
        try:
            cosmo = CommonCosmology(Omega_m=Omega_m, h=h, ln10As=ln10As)
        except ValueError:
            return None
        return build_class_params(cosmo)

    def _compute_clkk_lcdm(self, Omega_m: float, h: float,
                           ln10As: Optional[float] = None,
                           sigma8_target: Optional[float] = None) -> Optional[np.ndarray]:
        """Compute ΛCDM C_L^κκ using baseline emulator (or CLASS fallback)."""
        # Production path: use 2D baseline emulator
        if self._baseline_emu is not None:
            try:
                cl = self._baseline_emu.predict(Omega_m, h, ln10As=ln10As)
                return cl
            except Exception:
                pass  # fall through to CLASS

        # CLASS fallback (diagnostic / no emulator available)
        if ln10As is not None:
            params = self._get_class_params(Omega_m, h, ln10As)
        else:
            params = self._get_class_params(Omega_m, h, ln10As=2.1)

        if params is None:
            return None

        cosmo = classy.Class()
        try:
            cosmo.set(params)
            cosmo.compute()
            if sigma8_target is not None:
                sigma8_fid = cosmo.sigma(8.0 / h, 0.0)
                sigma8_scale = (sigma8_target / sigma8_fid) ** 2
            else:
                sigma8_scale = 1.0
            cls = cosmo.lensed_cl(2999)
            ell = np.array(cls["ell"], dtype=float)
            clkk = np.zeros_like(ell)
            mask = ell > 0
            clkk[mask] = ((ell[mask] * (ell[mask] + 1))**2 / 4
                          * cls["pp"][mask] * sigma8_scale)
        finally:
            cosmo.struct_cleanup()
            cosmo.empty()
        return np.interp(self.ell_full.astype(float), ell, clkk, left=0.0, right=0.0)

    def compute_clkk(self, params: dict[str, float]) -> Optional[np.ndarray]:
        """
        Compute C_L^κκ for given parameters.

        Uses PRODUCTION EMULATOR for G1 ratio (not direct engine).
        The direct engine is retained for diagnostic spot checks only.

        Parameters
        ----------
        params : dict
            Must contain: Omega_m, h, ln10As or sigma8
            May contain: q, kappa

        Returns
        -------
        clkk : np.ndarray or None
            None if invalid parameters
        """
        Omega_m = params["Omega_m"]
        h = params["h"]
        q = params.get("q", 0.0)
        kappa = params.get("kappa", 0.0)

        if self.amplitude_param == "ln10As":
            clkk_lcdm = self._compute_clkk_lcdm(Omega_m, h, ln10As=params["ln10As"])
        else:
            clkk_lcdm = self._compute_clkk_lcdm(Omega_m, h, sigma8_target=params["sigma8"])

        if clkk_lcdm is None:
            return None

        if q != 0.0 or kappa != 0.0:
            if self._emulator is not None:
                # Production path: use validated emulator (microseconds)
                try:
                    R_emu = self._emulator.predict_R(Omega_m, h, q, kappa)
                    R_interp = np.interp(self.ell_full.astype(float),
                                         self._emulator.ell.astype(float),
                                         R_emu, left=1.0, right=1.0)
                except ValueError:
                    return None
            else:
                # Test/validation fallback: direct engine (seconds)
                ratio = self._direct_engine.compute(Omega_m, h, 3.0 - q, kappa)
                R_interp = np.interp(self.ell_full.astype(float),
                                     ratio.ell.astype(float),
                                     ratio.R_total, left=1.0, right=1.0)
            clkk = clkk_lcdm * R_interp
        else:
            clkk = clkk_lcdm

        return clkk

    def log_likelihood(self, params: dict[str, float]) -> float:
        """
        Evaluate ACT lensing-only log likelihood.

        Uses official data vector, binning matrices, and inverse covariance
        from act_dr6_lenslike.load_data(). Manual chi^2 calculation confirmed
        equivalent to official generic_lnlike for lensing-only (Phase 1B).
        """
        clkk = self.compute_clkk(params)
        if clkk is None:
            return -np.inf

        if self.act_data.get("include_planck", False):
            cl_binned_act = self.act_data["binmat_act"] @ clkk
            cl_binned_planck = self.act_data["binmat_planck"] @ clkk
            cl_binned = np.concatenate([cl_binned_act, cl_binned_planck])
        else:
            cl_binned = self.act_data["binmat_act"] @ clkk

        diff = self.act_data["data_binned_clkk"] - cl_binned
        chi2 = diff @ self.act_data["cinv"] @ diff

        return -0.5 * chi2
