from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CommonCosmology:
    """
    Shared cosmology builder for G1 ratio engine and CLASS likelihood.

    Uses Planck 2018 fixed physical densities as baseline, then derives
    Omega parameters from a given (Omega_m, h) pair.

    This ensures numerator (G1) and denominator (LCDM) of the lensing
    ratio, plus the CLASS baseline C_L^κκ, all use consistently derived
    parameter values.
    """
    Omega_m: float    # total matter density parameter today
    h: float          # H0 / 100 km/s/Mpc
    ln10As: Optional[float] = None  # ln(10^10 A_s)

    # ── Fixed physical densities (Planck 2018) ────────────────────────
    _omega_b:    float = field(default=0.0224,   repr=False)
    _omega_ncdm: float = field(default=0.000641, repr=False)
    _omega_gamma: float = field(default=2.473e-5, repr=False)
    _n_s:        float = field(default=0.965,    repr=False)
    _N_ur:       float = field(default=2.0328,   repr=False)
    _tau_reio:   float = field(default=0.054,    repr=False)
    _T_cmb:      float = field(default=2.7255,   repr=False)
    _m_ncdm:     float = field(default=0.06,     repr=False)

    # ── Derived ────────────────────────────────────────────────────────
    @property
    def H0(self) -> float: return 100.0 * self.h

    @property
    def omega_cdm(self) -> float:
        return self.Omega_m * self.h**2 - self._omega_b - self._omega_ncdm

    @property
    def omega_m(self) -> float:
        return self._omega_b + self.omega_cdm + self._omega_ncdm

    @property
    def Omega_b(self) -> float:   return self._omega_b    / self.h**2
    @property
    def Omega_cdm(self) -> float: return self.omega_cdm   / self.h**2
    @property
    def Omega_ncdm(self) -> float: return self._omega_ncdm / self.h**2
    @property
    def Omega_r(self) -> float:
        """Early-time radiation density (photons + N_ur ultra-relativistic neutrinos)."""
        omega_ur = self._N_ur * (7.0 / 8.0) * (4.0 / 11.0)**(4.0 / 3.0) * self._omega_gamma
        return (self._omega_gamma + omega_ur) / self.h**2

    @property
    def n_s(self) -> float: return self._n_s
    @property
    def tau_reio(self) -> float: return self._tau_reio

    @property
    def A_s(self) -> Optional[float]:
        if self.ln10As is None: return None
        return 1e-10 * float(np_exp(self.ln10As))

    def __post_init__(self):
        if self.omega_cdm <= 0:
            raise ValueError(
                f"omega_cdm = {self.omega_cdm:.6f} <= 0 "
                f"(Omega_m={self.Omega_m}, h={self.h})"
            )
        # Sanity: reconstructed Omega_m matches input
        omega_total_matter = self._omega_b + self.omega_cdm + self._omega_ncdm
        reconstructed = omega_total_matter / self.h**2
        if abs(reconstructed - self.Omega_m) > 1e-10:
            raise ValueError(
                f"Omega_m inconsistency: input={self.Omega_m}, "
                f"reconstructed from omega_i/h^2={reconstructed}"
            )


# ────────────────────────────────────────────────────────────────────────
# Use numpy.exp to support scalar/array, but import is lightweight
from numpy import exp as np_exp


def build_class_params(cosmo: CommonCosmology) -> dict:
    """Build CLASS parameter dictionary from CommonCosmology."""
    params = {
        "output":       "tCl, lCl, pCl",
        "l_max_scalars": 2999,
        "lensing":      "yes",
        "omega_b":      cosmo._omega_b,
        "omega_cdm":    cosmo.omega_cdm,
        "h":            cosmo.h,
        "n_s":          cosmo._n_s,
        "tau_reio":     cosmo._tau_reio,
        "T_cmb":        cosmo._T_cmb,
        "N_ur":         cosmo._N_ur,
        "N_ncdm":       1,
        "m_ncdm":       cosmo._m_ncdm,
    }
    if cosmo.ln10As is not None:
        params["A_s"] = cosmo.A_s
    return params


def build_ratio_config(base_cfg: dict, cosmo: CommonCosmology,
                       s: float, kappa: float, *,
                       model_name: str,
                       amplitude_mode: str = "primordial",
                       sigma8_target: float | None = None) -> dict:
    """
    Build ratio-engine config from CommonCosmology + G1 parameters.

    Returns a DEEP COPY of base_cfg with all cosmology parameters
    overridden to match the shared cosmology.

    model_name is REQUIRED — never inherits from DEFAULTS.
    For all G1 branches: use "g1de_mkappa" with appropriate kappa.
      - background-only: kappa=0
      - M3/4 locked:     kappa=0.75
      - free kappa:      kappa as sampled
    """
    if model_name != "g1de_mkappa":
        raise ValueError(
            f"Ratio engine requires model_name='g1de_mkappa', got {model_name!r}. "
            f"All G1 branches must use the variable-kappa model."
        )
    from copy import deepcopy
    cfg = deepcopy(base_cfg)

    c = cfg["cosmology"]
    c["Omega_m"]  = cosmo.Omega_m
    c["Omega_b"]  = cosmo.Omega_b
    c["Omega_r"]  = cosmo.Omega_r
    c["H0"]       = cosmo.H0
    c["n_s"]      = cosmo._n_s

    m = cfg["model"]
    m["name"]   = model_name
    m["s"]      = float(s)
    m["kappa"]  = float(kappa)

    a = cfg["amplitude"]
    if amplitude_mode == "primordial":
        a["mode"] = "fixed_primordial"
    else:
        a["mode"] = "fixed_sigma8"
        a["sigma8_target"] = float(sigma8_target) if sigma8_target is not None else 0.811

    return cfg
