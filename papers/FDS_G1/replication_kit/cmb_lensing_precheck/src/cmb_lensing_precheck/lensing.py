from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.integrate import simpson

from .background import Background, C_KM_S
from .growth import GrowthSolution
from .models import sigma_response
from .power import PowerSpectrum


@dataclass
class LensingResult:
    ell: np.ndarray
    clpp_lcdm: np.ndarray
    clpp_model: np.ndarray
    clkk_lcdm: np.ndarray
    clkk_model: np.ndarray
    ratio: np.ndarray
    z_grid: np.ndarray
    kernel_weight_lcdm: np.ndarray
    sigma_pivot: np.ndarray
    growth_ratio: np.ndarray


def _redshift_grid(z_max: float, n_z: int) -> np.ndarray:
    # Log(1+z) spacing resolves both the low-z kernel and the high-z source endpoint.
    z = np.expm1(np.linspace(0.0, np.log1p(z_max), int(n_z)))
    z[0] = 1e-7
    z[-1] = z_max * (1.0 - 1e-8)
    return z


def compute_lensing(
    cfg: dict,
    background_model: Background,
    background_lcdm: Background,
    growth_model: GrowthSolution,
    growth_lcdm: GrowthSolution,
    power: PowerSpectrum,
) -> LensingResult:
    c = cfg["cosmology"]
    m = cfg["model"]
    amp = cfg["amplitude"]
    integ = cfg["integration"]

    ell = np.arange(int(integ["ell_min"]), int(integ["ell_max"]) + 1, int(integ["ell_step"]), dtype=int)
    z = _redshift_grid(float(integ["z_max"]), int(integ["n_z"]))
    a = 1.0 / (1.0 + z)

    chi_model_fun = background_model.comoving_distance_interpolator(float(c["z_star"]), max(1500, int(integ["n_z"]) * 2))
    chi_lcdm_fun = background_lcdm.comoving_distance_interpolator(float(c["z_star"]), max(1500, int(integ["n_z"]) * 2))
    chi_model = np.asarray(chi_model_fun(z))
    chi_lcdm = np.asarray(chi_lcdm_fun(z))
    chi_star_model = float(chi_model_fun(float(c["z_star"])))
    chi_star_lcdm = float(chi_lcdm_fun(float(c["z_star"])))

    H_model = background_model.H_z(z)
    H_lcdm = background_lcdm.H_z(z)
    dchi_dz_model = C_KM_S / H_model
    dchi_dz_lcdm = C_KM_S / H_lcdm

    prefactor = 1.5 * float(c["Omega_m"]) * (float(c["H0"]) / C_KM_S) ** 2
    w_model = prefactor * (1.0 + z) * chi_model * (chi_star_model - chi_model) / chi_star_model
    w_lcdm = prefactor * (1.0 + z) * chi_lcdm * (chi_star_lcdm - chi_lcdm) / chi_star_lcdm

    if amp["mode"] == "fixed_primordial":
        growth_model_factor = growth_model.delta(a) / growth_lcdm.delta_today
        growth_lcdm_factor = growth_lcdm.delta(a) / growth_lcdm.delta_today
    elif amp["mode"] == "fixed_sigma8":
        sigma_ratio = float(amp["sigma8_target"]) / float(power.sigma8)
        growth_model_factor = sigma_ratio * growth_model.D(a)
        growth_lcdm_factor = growth_lcdm.D(a)
    else:
        raise ValueError(f"Unknown amplitude mode {amp['mode']!r}.")

    clkk_model = np.zeros_like(ell, dtype=float)
    clkk_lcdm = np.zeros_like(ell, dtype=float)

    # Store one diagnostic Sigma curve at a representative L.
    pivot_L = 200
    k_pivot = (pivot_L + 0.5) / np.maximum(chi_model, 1e-8)
    sigma_pivot = sigma_response(
        a=a,
        k_mpc=k_pivot,
        H_km_s_mpc=H_model,
        omega_m=float(c["Omega_m"]),
        omega_r=float(c["Omega_r"]),
        model_name=m["name"],
        s=float(m["s"]),
        kappa=float(m["kappa"]),
        normalization=m["normalization"],
        horizon_completion=m["horizon_completion"],
        gamma_gamma=float(m["gamma_Gamma"]),
        c_gamma=float(m["c_Gamma"]),
    )

    kernel_diag = dchi_dz_lcdm * (w_lcdm / np.maximum(chi_lcdm, 1e-20)) ** 2

    for i, L in enumerate(ell):
        k_model = (L + 0.5) / np.maximum(chi_model, 1e-8)
        k_lcdm = (L + 0.5) / np.maximum(chi_lcdm, 1e-8)
        p_model = power.p0(k_model) * growth_model_factor**2
        p_lcdm = power.p0(k_lcdm) * growth_lcdm_factor**2
        sigma = sigma_response(
            a=a,
            k_mpc=k_model,
            H_km_s_mpc=H_model,
            omega_m=float(c["Omega_m"]),
            omega_r=float(c["Omega_r"]),
            model_name=m["name"],
            s=float(m["s"]),
            kappa=float(m["kappa"]),
            normalization=m["normalization"],
            horizon_completion=m["horizon_completion"],
            gamma_gamma=float(m["gamma_Gamma"]),
            c_gamma=float(m["c_Gamma"]),
        )
        integrand_model = dchi_dz_model * (w_model / np.maximum(chi_model, 1e-20)) ** 2 * p_model * sigma**2
        integrand_lcdm = dchi_dz_lcdm * (w_lcdm / np.maximum(chi_lcdm, 1e-20)) ** 2 * p_lcdm
        clkk_model[i] = simpson(integrand_model, x=z)
        clkk_lcdm[i] = simpson(integrand_lcdm, x=z)

    denom = (ell * (ell + 1.0)) ** 2
    clpp_model = 4.0 * clkk_model / denom
    clpp_lcdm = 4.0 * clkk_lcdm / denom
    ratio = np.divide(clpp_model, clpp_lcdm, out=np.full_like(clpp_model, np.nan), where=clpp_lcdm > 0)
    growth_ratio = growth_model.delta(a) / growth_lcdm.delta(a)

    return LensingResult(
        ell=ell,
        clpp_lcdm=clpp_lcdm,
        clpp_model=clpp_model,
        clkk_lcdm=clkk_lcdm,
        clkk_model=clkk_model,
        ratio=ratio,
        z_grid=z,
        kernel_weight_lcdm=kernel_diag,
        sigma_pivot=sigma_pivot,
        growth_ratio=growth_ratio,
    )
