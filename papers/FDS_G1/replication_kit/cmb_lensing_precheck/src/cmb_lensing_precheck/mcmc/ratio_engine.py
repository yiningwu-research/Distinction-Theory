from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import numpy as np

from ..background import Background, make_background
from ..growth import GrowthSolution, solve_growth
from ..power import PowerSpectrum, make_power
from ..lensing import compute_lensing, LensingResult
from ..config import DEFAULTS
from .cosmology import CommonCosmology, build_ratio_config


@dataclass
class RatioResult:
    ell: np.ndarray
    R_total: np.ndarray
    R_bg: np.ndarray
    R_Weyl: np.ndarray
    config: dict


class G1LensingRatio:
    """
    G1 lensing ratio engine: computes full multipole-dependent R_L(Omega_m, h, s, kappa).

    Splits into:
        R_total = R_bg * R_Weyl

    where:
        R_bg: background/growth only (kappa = 0)
        R_Weyl: Weyl response factor only

    Two amplitude modes:
        'primordial': common early-time amplitude normalization (A_s fixed)
        'present_sigma8': common present-day sigma8 normalization

    Uses CommonCosmology to ensure consistent Omega_b, Omega_r, n_s between
    the ratio engine and the CLASS baseline.
    """

    def __init__(self, amplitude_mode: str = "primordial"):
        if amplitude_mode not in {"primordial", "present_sigma8"}:
            raise ValueError(f"Unknown amplitude_mode: {amplitude_mode}")
        self.amplitude_mode = amplitude_mode
        self._base_cfg = self._build_base_config()

    def _build_base_config(self) -> dict:
        cfg = deepcopy(DEFAULTS)
        cfg["power"]["backend"] = "analytic"
        cfg["integration"]["n_z"] = 450
        cfg["integration"]["ell_min"] = 2
        cfg["integration"]["ell_max"] = 2998
        cfg["integration"]["ell_step"] = 1
        cfg["model"]["normalization"] = "code"
        cfg["model"]["horizon_completion"] = "none"
        return cfg

    def _build_config(self, cosmo: CommonCosmology, s: float, kappa: float) -> dict:
        return build_ratio_config(
            self._base_cfg, cosmo, s, kappa,
            model_name="g1de_mkappa",
            amplitude_mode=self.amplitude_mode,
            sigma8_target=(
                self._base_cfg["cosmology"]["sigma8_baseline"]
                if self.amplitude_mode == "present_sigma8" else None
            ),
        )

    def _compute_single(self, cfg: dict) -> LensingResult:
        bg_g1 = make_background(cfg, "g1de_mkappa")
        bg_lcdm = make_background(cfg, "lcdm")

        a_ini = cfg["integration"]["a_ini"]
        growth_g1 = solve_growth(bg_g1, a_ini, n_a=700)
        growth_lcdm = solve_growth(bg_lcdm, a_ini, n_a=700)

        power = make_power(cfg)
        return compute_lensing(cfg, bg_g1, bg_lcdm, growth_g1, growth_lcdm, power)

    def compute(self, Omega_m: float, h: float, s: float, kappa: float) -> RatioResult:
        """
        Compute full lensing ratio for given parameters.

        Parameters
        ----------
        Omega_m : float
            Total matter density parameter today
        h : float
            Dimensionless Hubble constant (H0 / 100 km/s/Mpc)
        s : float
            G1 background exponent
        kappa : float
            G1 Weyl response coupling

        Returns
        -------
        RatioResult
            Contains R_total, R_bg, R_Weyl as functions of ell
        """
        cosmo = CommonCosmology(Omega_m=Omega_m, h=h)

        cfg = self._build_config(cosmo, s, kappa)
        result_total = self._compute_single(cfg)

        cfg_bg = self._build_config(cosmo, s, 0.0)
        result_bg = self._compute_single(cfg_bg)

        R_total = result_total.ratio
        R_bg = result_bg.ratio
        R_Weyl = R_total / np.maximum(R_bg, 1e-30)

        return RatioResult(
            ell=result_total.ell,
            R_total=R_total,
            R_bg=R_bg,
            R_Weyl=R_Weyl,
            config=cfg,
        )

    def null_test_s_equals_3(self, Omega_m: float = 0.315, h: float = 0.674,
                             kappa: float = 0.75) -> float:
        """Test: s=3 should give R_L = 1 for any kappa."""
        result = self.compute(Omega_m, h, 3.0, kappa)
        return float(np.max(np.abs(result.R_total - 1.0)))

    def null_test_kappa_equals_0(self, Omega_m: float = 0.315, h: float = 0.674,
                                 s: float = 2.555) -> float:
        """Test: kappa=0 should give R_Weyl = 1."""
        result = self.compute(Omega_m, h, s, 0.0)
        return float(np.max(np.abs(result.R_Weyl - 1.0)))

    def fiducial_test_present_sigma8(self) -> tuple[float, float]:
        """
        Test fixed-sigma8 fiducial point for analytic backend.
        The ~+3.3% enhancement value 1.0325 is CLASS-backend corrected.
        Analytic backend gives a different absolute value but correct shape.

        Returns (mean_ratio, max_deviation_from_expected_analytic)
        """
        if self.amplitude_mode != "present_sigma8":
            raise ValueError("This test requires amplitude_mode='present_sigma8'")

        result = self.compute(0.2966, 0.674, 2.555, 0.75)
        mask = (result.ell >= 40) & (result.ell <= 1000)
        mean_ratio = float(np.mean(result.R_total[mask]))
        expected_analytic = 0.8241
        return mean_ratio, abs(mean_ratio - expected_analytic)

    def fiducial_test_primordial(self) -> tuple[float, float]:
        """
        Test primordial fiducial point should give ~-20% to -30% suppression at low ell.
        Returns (mean_ratio_L40_400, expected_approximate_value)
        """
        if self.amplitude_mode != "primordial":
            raise ValueError("This test requires amplitude_mode='primordial'")

        result = self.compute(0.2966, 0.674, 2.555, 0.75)
        mask = (result.ell >= 40) & (result.ell <= 400)
        mean_ratio = float(np.mean(result.R_total[mask]))
        expected_approx = 0.7136
        return mean_ratio, abs(mean_ratio - expected_approx)
