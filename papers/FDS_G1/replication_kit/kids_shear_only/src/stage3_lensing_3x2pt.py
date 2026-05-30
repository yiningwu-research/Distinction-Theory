#!/usr/bin/env python3
"""
FDS-G1 Stage-3 expanded lensing / 3x2pt likelihood prototype.

NOTE (v1.1-rc1): Despite the name, in this release the module is used for
KiDS-1000 shear-only xi_pm diagnostics.  Full 3x2pt (galaxy-galaxy lensing +
angular clustering + cosmic shear) is not yet included.  See the
kids_shear_only/README.md for context.

Purpose
-------
This module extends the Stage-2d G1 replication style to an expanded
weak-lensing / 3x2pt block.  It is intentionally self-contained and uses a
Limber + BBKS linear-P(k) backend so it can be run before a full CLASS/CAMB/CCL
production implementation is available.

It supports three real-space 3x2pt observables:
    xip      : cosmic shear xi_+(theta)
    xim      : cosmic shear xi_-(theta)
    gammat   : galaxy-galaxy lensing tangential shear gamma_t(theta)
    wtheta   : angular galaxy clustering w(theta)

Input format
------------
1. data_vector_csv with columns:
       kind,bin1,bin2,theta_arcmin,value
   where kind in {xip, xim, gammat, wtheta}.

2. covariance_txt: square covariance matrix matching row order of data_vector_csv.

3. n(z) files for source/lens bins, each with columns:
       z,nz

4. YAML config; see stage3_lensing_config_example.yaml.

Model intent
------------
The key G1/M3/4 lensing-channel lock is implemented as

    Sigma(a) - 1 = - kappa * (3 - s) * R_bH(a),   kappa = 3/4 for M3/4.

For a paper-grade run, supply an R_bH(a) table from the G1 replication kit via
config["rbh_table"].  If no table is supplied, the code falls back to the
Stage-2d Xhat-like shape X(a)=4 chi_H(a)(1-chi_H(a)); this is useful for smoke
tests but should not be presented as the production M3/4 shape.

Dependencies
------------
Required: numpy, pandas, scipy, pyyaml
Optional: dynesty, matplotlib

Example
-------
    python stage3_lensing_3x2pt.py --config stage3_lensing_config_example.yaml \
        --model m34 --theta-json '{"Omega_m":0.30,"h":0.68,"Omega_b":0.049,"sigma8":0.80,"n_s":0.965,"s":2.55}'

    python stage3_lensing_3x2pt.py --config stage3_lensing_config_example.yaml \
        --model m34 --nested --nlive 500
"""
from __future__ import annotations

import argparse
import json
import math
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.linalg as la
from scipy.integrate import solve_ivp, cumulative_trapezoid, simpson
from scipy.interpolate import PchipInterpolator, interp1d
from scipy.optimize import differential_evolution, minimize
from scipy.special import j0, jv

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Please install pyyaml: pip install pyyaml") from exc

C_LIGHT = 299792.458  # km/s

# -----------------------------------------------------------------------------
# Model priors.  Bias and shear-calibration nuisance parameters are appended
# dynamically from config.
# -----------------------------------------------------------------------------
BASE_PARAM_NAMES: Dict[str, List[str]] = {
    "lcdm": ["Omega_m", "h", "Omega_b", "sigma8", "n_s"],
    "const_sigma": ["Omega_m", "h", "Omega_b", "sigma8", "n_s", "Sigma0"],
    "m34": ["Omega_m", "h", "Omega_b", "sigma8", "n_s", "s"],
    "mkappa": ["Omega_m", "h", "Omega_b", "sigma8", "n_s", "s", "kappa"],
    "binned_sigma": ["Omega_m", "h", "Omega_b", "sigma8", "n_s"],
}

BASE_BOUNDS: Dict[str, List[Tuple[float, float]]] = {
    "lcdm": [(0.15, 0.45), (0.62, 0.76), (0.045, 0.055), (0.50, 1.00), (0.92, 1.00)],
    "const_sigma": [(0.15, 0.45), (0.62, 0.76), (0.045, 0.055), (0.50, 1.00), (0.92, 1.00), (-0.95, 1.0)],
    "m34": [(0.15, 0.45), (0.62, 0.76), (0.045, 0.055), (0.50, 1.00), (0.92, 1.00), (1.0, 5.0)],
    "mkappa": [(0.15, 0.45), (0.62, 0.76), (0.045, 0.055), (0.50, 1.00), (0.92, 1.00), (1.0, 5.0), (0.0, 1.5)],
    "binned_sigma": [(0.15, 0.45), (0.62, 0.76), (0.045, 0.055), (0.50, 1.00), (0.92, 1.00)],
}

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _symmetrize(cov: np.ndarray) -> np.ndarray:
    return 0.5 * (cov + cov.T)


def _normalize_nz(z: np.ndarray, nz: np.ndarray) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    nz = np.asarray(nz, dtype=float)
    nz = np.clip(nz, 0.0, np.inf)
    area = simpson(nz, x=z)
    if area <= 0 or not np.isfinite(area):
        raise ValueError("n(z) has non-positive integral")
    return nz / area


def _read_nz(path: str | Path, z_eval: np.ndarray) -> Tuple[np.ndarray, Callable]:
    df = pd.read_csv(path)
    if "z" not in df.columns or "nz" not in df.columns:
        raise ValueError(f"n(z) file {path} must have columns z,nz")
    z = df["z"].to_numpy(float)
    nz = _normalize_nz(z, df["nz"].to_numpy(float))
    interp = PchipInterpolator(z, nz, extrapolate=False)
    out = interp(z_eval)
    out = np.where(np.isfinite(out), out, 0.0)
    out = np.clip(out, 0.0, np.inf)
    out = _normalize_nz(z_eval, out)
    return out, interp


def chiH_a(a: np.ndarray, Om: float, s: float) -> np.ndarray:
    """Stage-2d style horizon occupancy variable chi_H(a)."""
    a = np.asarray(a, dtype=float)
    chi0 = 1.0 - Om
    if not (0.0 < chi0 < 1.0):
        return np.full_like(a, np.nan)
    B = 1.0 / chi0 - 1.0
    return 1.0 / (1.0 + B * a ** (-s))


def xhat_a(a: np.ndarray, Om: float, s: float) -> np.ndarray:
    chi = chiH_a(a, Om, s)
    return 4.0 * chi * (1.0 - chi)


def E_lcdm_z(z: np.ndarray, Om: float) -> np.ndarray:
    a = 1.0 / (1.0 + np.asarray(z, dtype=float))
    return np.sqrt(Om * a ** -3 + (1.0 - Om))


def E_g1_z(z: np.ndarray, Om: float, s: float) -> np.ndarray:
    """Stage-2d G1 background proxy: E^2 = Om a^-3 /(1-chi_H)."""
    a = 1.0 / (1.0 + np.asarray(z, dtype=float))
    chi = chiH_a(a, Om, s)
    E2 = Om * a ** -3 / (1.0 - chi)
    return np.sqrt(E2)


@dataclass
class RedshiftBin:
    name: str
    z: np.ndarray
    nz: np.ndarray
    kind: str  # "source" or "lens"
    bias_param: Optional[str] = None
    fixed_bias: float = 1.0
    shear_m_param: Optional[str] = None
    fixed_m: float = 0.0
    nz_interp: Optional[Callable] = None
    dz_param: Optional[str] = None
    fixed_dz: float = 0.0


class LinearMatterPower:
    """Small self-contained linear P(k,z) engine.

    This is a prototype backend.  For production runs replace with CLASS/CAMB/CCL
    while preserving the same Stage3Lensing3x2ptLikelihood interface.
    """

    def __init__(self, Om: float, Ob: float, h: float, ns: float, sigma8: float, model: str, s: Optional[float], z_grid: np.ndarray):
        self.Om = float(Om)
        self.Ob = float(Ob)
        self.h = float(h)
        self.ns = float(ns)
        self.sigma8 = float(sigma8)
        self.model = model
        self.s = s
        self.z_grid = np.asarray(z_grid, dtype=float)
        self.a_grid = 1.0 / (1.0 + self.z_grid)
        self._D_interp = self._build_growth_interp()
        self._A = self._sigma8_normalization()

    def E_z(self, z: np.ndarray) -> np.ndarray:
        if self.model in ("m34", "mkappa") and self.s is not None:
            return E_g1_z(z, self.Om, self.s)
        return E_lcdm_z(z, self.Om)

    def _dlnE_dlna(self, a: float) -> float:
        eps = 1e-4
        a1 = max(1e-4, a * np.exp(-eps))
        a2 = min(1.0, a * np.exp(eps))
        z1, z2 = 1.0 / a1 - 1.0, 1.0 / a2 - 1.0
        E1, E2 = float(self.E_z(np.array([z1]))[0]), float(self.E_z(np.array([z2]))[0])
        return (math.log(E2) - math.log(E1)) / (math.log(a2) - math.log(a1))

    def _Omega_m_a(self, a: float) -> float:
        z = 1.0 / a - 1.0
        E = float(self.E_z(np.array([z]))[0])
        return self.Om * a ** -3 / (E * E)

    def _build_growth_interp(self) -> Callable[[np.ndarray], np.ndarray]:
        # Solve in x=ln a from early matter-dominated initial conditions.
        x0 = math.log(1e-3)
        x1 = 0.0

        def rhs(x: float, y: np.ndarray) -> np.ndarray:
            a = math.exp(x)
            D, dD = y
            coeff = 2.0 + self._dlnE_dlna(a)
            source = 1.5 * self._Omega_m_a(a)  # mu=1 for M3/4 lensing tests
            return np.array([dD, source * D - coeff * dD])

        y0 = np.array([math.exp(x0), math.exp(x0)])
        sol = solve_ivp(rhs, (x0, x1), y0, rtol=1e-5, atol=1e-8, dense_output=True, max_step=0.05)
        xs = np.linspace(x0, x1, 600)
        D = sol.sol(xs)[0]
        D /= D[-1]
        return PchipInterpolator(np.exp(xs), D, extrapolate=True)

    def transfer_bbks(self, k_hmpc: np.ndarray) -> np.ndarray:
        # BBKS no-wiggle transfer. k input in h/Mpc.
        Gamma = self.Om * self.h
        q = np.asarray(k_hmpc, dtype=float) / max(Gamma, 1e-12)
        q = np.maximum(q, 1e-12)
        L0 = np.log(1.0 + 2.34 * q) / (2.34 * q)
        C0 = (1.0 + 3.89 * q + (16.1 * q) ** 2 + (5.46 * q) ** 3 + (6.71 * q) ** 4) ** (-0.25)
        return L0 * C0

    def _sigma8_normalization(self) -> float:
        R = 8.0  # Mpc/h
        k = np.logspace(-4, 2, 1200)  # h/Mpc
        T = self.transfer_bbks(k)
        P0 = k ** self.ns * T * T
        x = k * R
        W = 3.0 * (np.sin(x) - x * np.cos(x)) / np.maximum(x ** 3, 1e-30)
        integ = k ** 2 * P0 * W ** 2
        sig2_unit = simpson(integ, x=k) / (2.0 * np.pi ** 2)
        if sig2_unit <= 0 or not np.isfinite(sig2_unit):
            raise ValueError("sigma8 normalization failed")
        return self.sigma8 ** 2 / sig2_unit

    def P(self, k_1mpc: np.ndarray, z: np.ndarray) -> np.ndarray:
        # Convert k [1/Mpc] to h/Mpc for transfer shape and output Mpc^3.
        k_hmpc = np.asarray(k_1mpc, dtype=float) / self.h
        z = np.asarray(z, dtype=float)
        a = 1.0 / (1.0 + z)
        D = np.asarray(self._D_interp(a), dtype=float)
        T = self.transfer_bbks(k_hmpc)
        P_h = self._A * k_hmpc ** self.ns * T * T * D ** 2  # (Mpc/h)^3 up to normalization
        return P_h / self.h ** 3  # Mpc^3


class ClassMatterPower:
    """CLASS P(k,z) backend via classy.

    Replaces the self-contained BBKS + growth ODE with CLASS linear matter
    power. The cosmology parameters match the existing LinearMatterPower
    interface so the Limber and lensing layers are unchanged.

    Input k is in [1/Mpc]; CLASS internally uses [h/Mpc].  Output P(k,z) is
    in [Mpc^3].  sigma8 is enforced by a single overall normalization factor
    applied to the full P(k,z) table after CLASS computation.
    """

    def __init__(self, Om: float, Ob: float, h: float, ns: float, sigma8: float, model: str, s: Optional[float], z_grid: np.ndarray, kmin: float = 1e-4, kmax: float = 100.0, nk: int = 128, class_nz: int = 64):
        self.Om = float(Om)
        self.Ob = float(Ob)
        self.h = float(h)
        self.ns = float(ns)
        self.sigma8 = float(sigma8)
        self.model = model
        self.s = s
        self.z_grid = np.asarray(z_grid, dtype=float)
        # Build coarse internal CLASS grid to speed up table construction.
        self._class_z = np.linspace(0.0, float(np.max(z_grid)) + 0.5, class_nz)

        from classy import Class
        omega_b = self.Ob * self.h * self.h
        omega_cdm = max(self.Om * self.h * self.h - omega_b, 1e-10)
        A_s_fid = 2.1e-9

        k_hmpc_grid = np.logspace(np.log10(kmin / self.h), np.log10(kmax / self.h), nk)
        class_params = {
            "output": "mPk",
            "P_k_max_h/Mpc": 300.0,
            "z_max_pk": float(np.max(z_grid)) + 1.0,
            "h": self.h,
            "omega_b": omega_b,
            "omega_cdm": omega_cdm,
            "n_s": self.ns,
            "A_s": A_s_fid,
            "T_cmb": 2.7255,
            "N_ur": 3.046,
            "N_ncdm": 0,
        }

        cosmo = Class()
        cosmo.set(class_params)
        cosmo.compute()

        sigma8_raw = float(cosmo.sigma8())
        if not np.isfinite(sigma8_raw) or sigma8_raw <= 0:
            cosmo.struct_cleanup()
            cosmo.empty()
            raise RuntimeError(f"CLASS returned non-finite sigma8: {sigma8_raw}")
        self._A_norm = (self.sigma8 / sigma8_raw) ** 2

        # Pre-compute P(k,z) on safe k grid, using coarse CLASS z grid.
        self._k_hmpc_grid = k_hmpc_grid
        self._pk_table = np.empty((nk, len(self._class_z)), dtype=float)
        for iz, zv in enumerate(self._class_z):
            for ik, kv in enumerate(k_hmpc_grid):
                self._pk_table[ik, iz] = float(cosmo.pk(kv, zv))
        self._pk_table *= self._A_norm

        cosmo.struct_cleanup()
        cosmo.empty()

        from scipy.interpolate import RegularGridInterpolator
        self._interp = RegularGridInterpolator(
            (np.log(k_hmpc_grid), self._class_z),
            np.log(np.maximum(self._pk_table, 1e-300)),
            bounds_error=False,
            fill_value=None,
        )

    def P(self, k_1mpc: np.ndarray, z: np.ndarray) -> np.ndarray:
        # k [1/Mpc] → k [h/Mpc]  for CLASS convention.
        # P CLASS [(Mpc/h)^3] → P [Mpc^3] dividing by h^3.
        k_hmpc = np.asarray(k_1mpc, dtype=float) / self.h
        z = np.asarray(z, dtype=float)
        pts = np.column_stack((np.log(np.maximum(k_hmpc, 1e-12)), z))
        logP = self._interp(pts)
        P_hmpc3 = np.exp(logP)
        return P_hmpc3 / self.h ** 3

    def E_z(self, z: np.ndarray) -> np.ndarray:
        # Keep the self-contained G1/LCDM background; CLASS is only for P(k).
        if self.model in ("m34", "mkappa") and self.s is not None:
            return E_g1_z(z, self.Om, self.s)
        return E_lcdm_z(z, self.Om)


class Stage3Lensing3x2ptLikelihood:
    def __init__(self, config_path: str | Path, theory_backend: str = "bbks", class_nk: int = 128, class_nz: int = 64):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.data_dir = self.config_path.parent
        self.theory_backend = theory_backend
        self.class_nk = class_nk
        self.class_nz = class_nz
        # scale cuts: only active when enabled in config AND kind_filter specifies which kinds
        sc = self.cfg.get("scale_cuts", {})
        self._scale_cuts_enabled = bool(sc.get("enabled", False))
        self._scale_cuts: Dict[str, float] = {str(k): float(v) for k, v in sc.items() if k not in ("enabled", "kind_filter")}
        self._scale_kinds = [str(k).strip().lower() for k in sc.get("kind_filter", [])] if self._scale_cuts_enabled else []
        self.z_grid = np.linspace(float(self.cfg.get("z_min", 1e-4)), float(self.cfg.get("z_max", 3.0)), int(self.cfg.get("nz_grid", 500)))
        self.ell_grid = np.logspace(np.log10(float(self.cfg.get("ell_min", 2.0))), np.log10(float(self.cfg.get("ell_max", 5000.0))), int(self.cfg.get("nell", 500)))
        self.theta_grid_arcmin = np.asarray(self.cfg.get("theta_grid_arcmin", []), dtype=float)
        if self.theta_grid_arcmin.size == 0:
            self.theta_grid_arcmin = np.geomspace(2.5, 250.0, 60)
        self._load_bins()
        self._load_data_vector()
        self._load_rbh_table()
        self._pk_cache: Dict[Tuple, Any] = {}

    # ------------------------- loading -------------------------
    def _resolve(self, p: str | Path) -> Path:
        p = Path(p)
        return p if p.is_absolute() else (self.config_path.parent / p)

    def _load_bins(self) -> None:
        self.sources: Dict[str, RedshiftBin] = {}
        self.lenses: Dict[str, RedshiftBin] = {}
        for entry in self.cfg.get("sources", []):
            name = str(entry["name"])
            nz, interp = _read_nz(self._resolve(entry["nz_file"]), self.z_grid)
            self.sources[name] = RedshiftBin(name=name, z=self.z_grid, nz=nz, kind="source", shear_m_param=f"m_{name}", fixed_m=float(entry.get("m", 0.0)), nz_interp=interp, dz_param=f"dz_{name}", fixed_dz=0.0)
        for entry in self.cfg.get("lenses", []):
            name = str(entry["name"])
            nz, interp = _read_nz(self._resolve(entry["nz_file"]), self.z_grid)
            self.lenses[name] = RedshiftBin(name=name, z=self.z_grid, nz=nz, kind="lens", bias_param=f"b_{name}", fixed_bias=float(entry.get("bias", 1.5)))

    def _load_data_vector(self) -> None:
        data_path = self._resolve(self.cfg["data_vector_csv"])
        cov_path = self._resolve(self.cfg["covariance_txt"])
        self.data = pd.read_csv(data_path)
        required = {"kind", "bin1", "bin2", "theta_arcmin", "value"}
        missing = required - set(self.data.columns)
        if missing:
            raise ValueError(f"data_vector_csv missing columns: {missing}")
        self._data_full = self.data.copy()  # preserve pre-cut version
        self._apply_scale_cuts()
        self.cov_full = _symmetrize(np.loadtxt(cov_path))
        self.cov = self._apply_scale_cuts_to_cov(self.cov_full) if self._scale_cuts_enabled else self.cov_full
        if self.cov.shape != (len(self.data), len(self.data)):
            raise ValueError(f"covariance shape {self.cov.shape} does not match data length {len(self.data)}")
        self.cho_cov = la.cho_factor(self.cov, lower=True, check_finite=False)

    def _apply_scale_cuts(self) -> None:
        if not self._scale_cuts_enabled:
            return
        df = self._data_full
        mask = np.ones(len(df), dtype=bool)
        if self._scale_kinds:
            mask &= df["kind"].str.lower().isin(self._scale_kinds)
        for key, val in self._scale_cuts.items():
            if key.endswith("_theta_min"):
                kind = key.replace("_theta_min", "").strip().lower()
                m = df["kind"].str.lower() == kind
                mask[m] = mask[m] & (df.loc[m, "theta_arcmin"] >= val)
            elif key.endswith("_theta_max"):
                kind = key.replace("_theta_max", "").strip().lower()
                m = df["kind"].str.lower() == kind
                mask[m] = mask[m] & (df.loc[m, "theta_arcmin"] <= val)
        self.data = self._data_full[mask].reset_index(drop=True)
        if len(self.data) == 0:
            raise ValueError("Scale cuts removed all data rows")

    def _apply_scale_cuts_to_cov(self, cov: np.ndarray) -> np.ndarray:
        indices = self._data_full.index[self.data.index]  # original row indices
        return cov[np.ix_(indices, indices)]

    def _load_rbh_table(self) -> None:
        self.rbh_interp: Optional[Callable[[np.ndarray], np.ndarray]] = None
        table = self.cfg.get("rbh_table")
        if table:
            df = pd.read_csv(self._resolve(table))
            if not {"a", "R_bH"}.issubset(df.columns):
                raise ValueError("rbh_table must have columns a,R_bH")
            self.rbh_interp = PchipInterpolator(df["a"].to_numpy(float), df["R_bH"].to_numpy(float), extrapolate=True)

    # ------------------------- parameters -------------------------
    def param_names(self, model: str) -> List[str]:
        names = list(BASE_PARAM_NAMES[model])
        if model == "binned_sigma":
            edges = self.cfg.get("sigma_bin_edges", [0.0, 0.5, 10.0])
            names.extend([f"Sigma_bin{i}" for i in range(len(edges) - 1)])
        if bool(self.cfg.get("vary_lens_bias", True)):
            names.extend([f"b_{name}" for name in self.lenses])
        if bool(self.cfg.get("vary_shear_m", False)):
            names.extend([f"m_{name}" for name in self.sources])
        if bool(self.cfg.get("vary_dz", False)):
            names.extend([f"dz_{name}" for name in self.sources])
        if bool(self.cfg.get("vary_ia", False)):
            names.append("A_IA")
        return names

    def bounds(self, model: str) -> List[Tuple[float, float]]:
        bounds = list(BASE_BOUNDS[model])
        if model == "binned_sigma":
            bin_bounds = self.cfg.get("sigma_bin_bounds", [-0.95, 1.0])
            edges = self.cfg.get("sigma_bin_edges", [0.0, 0.5, 10.0])
            bounds.extend([tuple(bin_bounds) for _ in range(len(edges) - 1)])
        if bool(self.cfg.get("vary_lens_bias", True)):
            bounds.extend([tuple(self.cfg.get("lens_bias_bounds", [0.3, 4.0])) for _ in self.lenses])
        if bool(self.cfg.get("vary_shear_m", False)):
            bounds.extend([tuple(self.cfg.get("shear_m_bounds", [-0.1, 0.1])) for _ in self.sources])
        if bool(self.cfg.get("vary_dz", False)):
            bounds.extend([tuple(self.cfg.get("dz_bounds", [-0.05, 0.05])) for _ in self.sources])
        if bool(self.cfg.get("vary_ia", False)):
            bounds.append(tuple(self.cfg.get("A_IA_bounds", [-5.0, 5.0])))
        return [(float(a), float(b)) for a, b in bounds]

    def theta_to_dict(self, model: str, theta: Iterable[float]) -> Dict[str, float]:
        names = self.param_names(model)
        theta = list(theta)
        if len(theta) != len(names):
            raise ValueError(f"theta length {len(theta)} does not match {len(names)} params: {names}")
        return dict(zip(names, map(float, theta)))

    def in_prior(self, model: str, theta: Iterable[float]) -> bool:
        return all(lo <= x <= hi for x, (lo, hi) in zip(theta, self.bounds(model)))

    # ------------------------- theory -------------------------
    def E_z(self, model: str, pars: Dict[str, float], z: np.ndarray) -> np.ndarray:
        if model in ("m34", "mkappa"):
            return E_g1_z(z, pars["Omega_m"], pars["s"])
        return E_lcdm_z(z, pars["Omega_m"])

    def chi_comoving(self, model: str, pars: Dict[str, float], z: np.ndarray) -> np.ndarray:
        z_eval = np.asarray(z, dtype=float)
        z_grid = np.linspace(0.0, max(float(np.max(z_eval)) * 1.02, 1e-3), 1200)
        E = self.E_z(model, pars, z_grid)
        if np.any(~np.isfinite(E)) or np.any(E <= 0):
            return np.full_like(z_eval, np.nan)
        chi_grid = cumulative_trapezoid(C_LIGHT / (100.0 * pars["h"] * E), z_grid, initial=0.0)
        return PchipInterpolator(z_grid, chi_grid, extrapolate=True)(z_eval)

    def rbh_shape(self, pars: Dict[str, float], a: np.ndarray) -> np.ndarray:
        if self.rbh_interp is not None:
            return np.asarray(self.rbh_interp(a), dtype=float)
        warnings.warn("No rbh_table supplied; using Xhat fallback for smoke tests, not production M3/4.", RuntimeWarning, stacklevel=2)
        return xhat_a(a, pars["Omega_m"], pars["s"])

    def Sigma_lensing(self, model: str, pars: Dict[str, float], z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        a = 1.0 / (1.0 + z)
        if model == "lcdm":
            return np.ones_like(z)
        if model == "const_sigma":
            return np.ones_like(z) + pars["Sigma0"]
        if model == "binned_sigma":
            edges = self.cfg.get("sigma_bin_edges", [0.0, 0.5, 10.0])
            result = np.ones_like(z)
            for i in range(len(edges) - 1):
                key = f"Sigma_bin{i}"
                val = pars.get(key, 0.0)
                if i == len(edges) - 2:
                    mask = z >= edges[i]
                else:
                    mask = (z >= edges[i]) & (z < edges[i + 1])
                result[mask] += val
            return result
        if model == "m34":
            return 1.0 - 0.75 * (3.0 - pars["s"]) * self.rbh_shape(pars, a)
        if model == "mkappa":
            return 1.0 - pars["kappa"] * (3.0 - pars["s"]) * self.rbh_shape(pars, a)
        raise ValueError(model)

    def lens_bias(self, name: str, pars: Dict[str, float]) -> float:
        key = f"b_{name}"
        return pars.get(key, self.lenses[name].fixed_bias)

    def shear_m(self, name: str, pars: Dict[str, float]) -> float:
        key = f"m_{name}"
        return pars.get(key, self.sources[name].fixed_m)

    def get_nz(self, source_name: str, pars: Dict[str, float]) -> np.ndarray:
        src = self.sources[source_name]
        dz_key = src.dz_param
        dz = pars.get(dz_key, src.fixed_dz) if dz_key else src.fixed_dz
        if abs(dz) < 1e-12 or src.nz_interp is None:
            return src.nz
        z_shifted = src.z - dz
        nz = np.asarray(src.nz_interp(z_shifted), dtype=float)
        nz = np.where(np.isfinite(nz), nz, 0.0)
        nz = np.clip(nz, 0.0, np.inf)
        norm = simpson(nz, x=src.z)
        if norm > 0 and np.isfinite(norm):
            nz = nz / norm
        else:
            nz = src.nz
        return nz

    def _growth_factor(self, model: str, pars: Dict[str, float], z_eval: np.ndarray) -> np.ndarray:
        a = 1.0 / (1.0 + np.asarray(z_eval, dtype=float))

        def _dlnE_dlna(av: float) -> float:
            eps = 1e-4
            a1 = max(1e-4, av * np.exp(-eps))
            a2 = min(1.0, av * np.exp(eps))
            z1, z2 = 1.0 / a1 - 1.0, 1.0 / a2 - 1.0
            E1 = float(self.E_z(model, pars, np.array([z1]))[0])
            E2 = float(self.E_z(model, pars, np.array([z2]))[0])
            return (math.log(E2) - math.log(E1)) / (math.log(a2) - math.log(a1))

        def _Omega_m_a(av: float) -> float:
            z_av = 1.0 / av - 1.0
            E_av = float(self.E_z(model, pars, np.array([z_av]))[0])
            return pars["Omega_m"] * av ** -3 / (E_av * E_av)

        x0 = math.log(1e-3)
        x1 = 0.0

        def rhs(x: float, y: np.ndarray) -> np.ndarray:
            av = math.exp(x)
            D, dD = y
            coeff = 2.0 + _dlnE_dlna(av)
            source = 1.5 * _Omega_m_a(av)
            return np.array([dD, source * D - coeff * dD])

        y0 = np.array([math.exp(x0), math.exp(x0)])
        sol = solve_ivp(rhs, (x0, x1), y0, rtol=1e-5, atol=1e-8, dense_output=True, max_step=0.05)
        xs = np.linspace(x0, x1, 600)
        D_all = np.asarray(sol.sol(xs)[0], dtype=float)
        D_all /= D_all[-1]
        D_interp = PchipInterpolator(np.exp(xs), D_all, extrapolate=True)
        return np.asarray(D_interp(a), dtype=float)

    def _ia_factor(self, model: str, pars: Dict[str, float], z: np.ndarray) -> np.ndarray:
        A = pars.get("A_IA", 0.0)
        if not self.cfg.get("vary_ia", False) and abs(A) < 1e-12:
            return np.zeros_like(z, dtype=float)
        C1rho = float(self.cfg.get("C1rho_crit", 0.0134))
        Om = pars["Omega_m"]
        D = self._growth_factor(model, pars, z)
        D = np.maximum(D, 1e-8)
        return -A * C1rho * Om / D

    def _kappa_kernel(self, model: str, pars: Dict[str, float], src: RedshiftBin, chi: np.ndarray, E: np.ndarray, nz_override: Optional[np.ndarray] = None) -> np.ndarray:
        z = self.z_grid
        a = 1.0 / (1.0 + z)
        nz_src = src.nz if nz_override is None else nz_override
        # I(z)=int_z^inf dz_s n(z_s) (chi_s-chi)/chi_s
        chi_safe = np.maximum(chi, 1e-12)
        integrand_matrix = np.maximum(chi[None, :] - chi[:, None], 0.0) / np.maximum(chi[None, :], 1e-12)
        # For each z_i, integrate over z_s.  Matrix dimensions: i rows, source columns.
        I = simpson(integrand_matrix * nz_src[None, :], x=z, axis=1)
        H0_over_c = (100.0 * pars["h"]) / C_LIGHT
        W = 1.5 * pars["Omega_m"] * H0_over_c ** 2 * chi_safe / a * I
        return W

    def _density_kernel(self, lens: RedshiftBin, pars: Dict[str, float]) -> np.ndarray:
        return lens.nz * self.lens_bias(lens.name, pars)

    def _compute_cl_pair(self, model: str, pars: Dict[str, float], kind: str, bin1: str, bin2: str, ell: np.ndarray) -> np.ndarray:
        z = self.z_grid
        E = self.E_z(model, pars, z)
        if np.any(~np.isfinite(E)) or np.any(E <= 0):
            return np.full_like(ell, np.nan, dtype=float)
        chi = self.chi_comoving(model, pars, z)
        if np.any(~np.isfinite(chi)):
            return np.full_like(ell, np.nan, dtype=float)
        chi = np.maximum(chi, 1e-6)
        pk: Any
        if self.theory_backend == "class":
            key = (model, pars["Omega_m"], pars["Omega_b"], pars["h"], pars["n_s"], pars["sigma8"], pars.get("s"))
            pk = self._pk_cache.get(key)
            if pk is None:
                pk = ClassMatterPower(
                    Om=pars["Omega_m"], Ob=pars["Omega_b"], h=pars["h"], ns=pars["n_s"], sigma8=pars["sigma8"],
                    model=model, s=pars.get("s"), z_grid=z,
                    nk=self.class_nk, class_nz=self.class_nz,
                )
                if len(self._pk_cache) > 32:
                    self._pk_cache.pop(next(iter(self._pk_cache)))
                self._pk_cache[key] = pk
        else:
            pk = LinearMatterPower(
                Om=pars["Omega_m"], Ob=pars["Omega_b"], h=pars["h"], ns=pars["n_s"], sigma8=pars["sigma8"],
                model=model, s=pars.get("s"), z_grid=z,
            )
        Sigma = self.Sigma_lensing(model, pars, z)
        if np.any(Sigma <= 0) or np.any(~np.isfinite(Sigma)):
            return np.full_like(ell, np.nan, dtype=float)

        if kind in ("xip", "xim"):
            nz1 = self.get_nz(bin1, pars)
            nz2 = self.get_nz(bin2, pars)
            W1k = self._kappa_kernel(model, pars, self.sources[bin1], chi, E, nz_override=nz1)
            W2k = self._kappa_kernel(model, pars, self.sources[bin2], chi, E, nz_override=nz2)
            if self.cfg.get("vary_ia", False):
                F = self._ia_factor(model, pars, z)
                Hz_over_c = (100.0 * pars["h"] * self.E_z(model, pars, z)) / C_LIGHT
                W1 = W1k * Sigma + F * nz1 * Hz_over_c
                W2 = W2k * Sigma + F * nz2 * Hz_over_c
            else:
                W1 = W1k * Sigma
                W2 = W2k * Sigma
        elif kind == "gammat":
            W1 = self._density_kernel(self.lenses[bin1], pars)
            nz2 = self.get_nz(bin2, pars)
            W2 = self._kappa_kernel(model, pars, self.sources[bin2], chi, E, nz_override=nz2) * Sigma
        elif kind == "wtheta":
            W1 = self._density_kernel(self.lenses[bin1], pars)
            W2 = self._density_kernel(self.lenses[bin2], pars)
        else:
            raise ValueError(f"unknown kind {kind}")

        pref = C_LIGHT / (100.0 * pars["h"] * E) / (chi * chi)
        cls = []
        for L in ell:
            k = (L + 0.5) / chi
            P = pk.P(k, z)
            vals = pref * W1 * W2 * P
            vals = np.where(np.isfinite(vals), vals, 0.0)
            cls.append(simpson(vals, x=z))
        return np.asarray(cls)

    def _realspace_from_cl(self, ell: np.ndarray, cl: np.ndarray, kind: str, theta_rad: np.ndarray) -> np.ndarray:
        out = []
        for th in theta_rad:
            x = ell * th
            if kind in ("xip", "wtheta"):
                J = j0(x)
            elif kind == "xim":
                J = jv(4, x)
            elif kind == "gammat":
                J = jv(2, x)
            else:
                raise ValueError(kind)
            out.append(simpson(ell * cl * J / (2.0 * np.pi), x=ell))
        return np.asarray(out)

    def predict_vector(self, model: str, theta: Iterable[float]) -> np.ndarray:
        pars = self.theta_to_dict(model, theta)
        ell = self.ell_grid
        theta_rad_all = self.data["theta_arcmin"].to_numpy(float) / 60.0 * np.pi / 180.0
        pred = np.empty(len(self.data), dtype=float)
        # Cache C_ell per unique observable/bin pair.
        cl_cache: Dict[Tuple[str, str, str], Tuple[np.ndarray, np.ndarray]] = {}
        for key, sub_idx in self.data.groupby(["kind", "bin1", "bin2"]).groups.items():
            kind, bin1, bin2 = key
            kind = str(kind)
            bin1 = str(bin1)
            bin2 = str(bin2)
            cl = self._compute_cl_pair(model, pars, kind, bin1, bin2, ell)
            if np.any(~np.isfinite(cl)):
                pred[list(sub_idx)] = np.nan
                continue
            th = theta_rad_all[list(sub_idx)]
            vals = self._realspace_from_cl(ell, cl, kind, th)
            # multiplicative shear calibration for observables with source shear
            if kind in ("xip", "xim"):
                vals *= (1.0 + self.shear_m(bin1, pars)) * (1.0 + self.shear_m(bin2, pars))
            elif kind == "gammat":
                vals *= (1.0 + self.shear_m(bin2, pars))
            pred[list(sub_idx)] = vals
        return pred

    def chi2(self, model: str, theta: Iterable[float]) -> float:
        theta = list(theta)
        if model not in BASE_PARAM_NAMES:
            raise ValueError(f"unknown model {model}; choose {list(BASE_PARAM_NAMES)}")
        if not self.in_prior(model, theta):
            return np.inf
        pred = self.predict_vector(model, theta)
        if np.any(~np.isfinite(pred)):
            return np.inf
        delta = self.data["value"].to_numpy(float) - pred
        try:
            return float(delta @ la.cho_solve(self.cho_cov, delta, check_finite=False))
        except la.LinAlgError:
            return np.inf

    def loglike(self, model: str, theta: Iterable[float]) -> float:
        c2 = self.chi2(model, theta)
        if not np.isfinite(c2):
            return -np.inf
        return -0.5 * c2

    def prior_transform(self, model: str, u: Iterable[float]) -> np.ndarray:
        u = np.asarray(list(u), dtype=float)
        bnds = self.bounds(model)
        lo = np.asarray([b[0] for b in bnds])
        hi = np.asarray([b[1] for b in bnds])
        return lo + u * (hi - lo)

    def run_nested(self, model: str, nlive: int = 500, dlogz: float = 0.1, seed: int = 1234, out_json: Optional[str | Path] = None) -> Dict[str, object]:
        try:
            import dynesty
        except ImportError as exc:  # pragma: no cover
            raise SystemExit("Nested run requires dynesty: pip install dynesty") from exc
        ndim = len(self.param_names(model))
        rng = np.random.default_rng(seed)

        def loglike(theta: np.ndarray) -> float:
            return self.loglike(model, theta)

        def ptform(u: np.ndarray) -> np.ndarray:
            return self.prior_transform(model, u)

        sampler = dynesty.NestedSampler(loglike, ptform, ndim=ndim, nlive=nlive, rstate=rng, bound="multi", sample="rwalk")
        sampler.run_nested(dlogz=dlogz, print_progress=True)
        res = sampler.results
        out = {
            "model": model,
            "param_names": self.param_names(model),
            "logz": float(res.logz[-1]),
            "logzerr": float(res.logzerr[-1]),
            "nlive": int(nlive),
            "dlogz_target": float(dlogz),
            "seed": int(seed),
        }
        if out_json is not None:
            Path(out_json).parent.mkdir(parents=True, exist_ok=True)
            Path(out_json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def _theta_from_json(theta_json: str, names: List[str]) -> List[float]:
    obj = json.loads(theta_json)
    if isinstance(obj, list):
        return [float(x) for x in obj]
    if isinstance(obj, dict):
        missing = [n for n in names if n not in obj]
        if missing:
            raise ValueError(f"theta-json missing parameters: {missing}; expected {names}")
        return [float(obj[n]) for n in names]
    raise ValueError("theta-json must be a list or dict")


def _parse_profile_s(raw: str) -> Tuple[float, float, float]:
    parts = raw.strip().replace(",", " ").split()
    if len(parts) != 3:
        raise SystemExit("--profile-s requires START STOP STEP (e.g. 1.5 3.2 0.1)")
    return float(parts[0]), float(parts[1]), float(parts[2])


def _opt_optimize(
    like: Stage3Lensing3x2ptLikelihood,
    model: str,
    optimizer: str,
    popsize: int,
    maxiter: int,
    seed: int,
    fix_params: Dict[str, float],
    no_polish: bool = False,
) -> Dict[str, Any]:
    import time as _time
    t0 = _time.time()
    counter: Dict[str, int] = {"n": 0}
    names = like.param_names(model)
    bounds = like.bounds(model)
    name_to_idx = {n: i for i, n in enumerate(names)}

    # Remove fixed params from bounds/names; insert their values at eval time.
    fixed_entries = [(name_to_idx[name], val) for name, val in fix_params.items() if name in name_to_idx]
    fixed_entries.sort(key=lambda x: x[0])
    opt_names = list(names)
    opt_bounds = list(bounds)
    # Remove from highest index first to preserve lower indices.
    for idx, _ in reversed(fixed_entries):
        opt_names.pop(idx)
        opt_bounds.pop(idx)

    def neg_loglike(theta_opt: np.ndarray) -> float:
        counter["n"] += 1
        theta_full = list(theta_opt)
        # Re-insert fixed params at saved positions.
        for idx, val in fixed_entries:
            theta_full.insert(idx, val)
        ll = like.loglike(model, theta_full)
        if not np.isfinite(ll):
            return 1e100
        return -float(ll)

    result: Any
    polish_needed = True
    if optimizer == "de":
        result = differential_evolution(
            neg_loglike,
            opt_bounds,
            popsize=popsize,
            maxiter=maxiter,
            seed=seed,
            polish=False,
            disp=False,
        )
        best_x_opt = result.x
        nfev_de = int(result.nfev)
        if no_polish:
            polish_needed = False
    elif optimizer == "lbfgs":
        best_x_opt = np.array([0.5 * (lo + hi) for lo, hi in opt_bounds])
        polish_needed = False
        nfev_de = 0
    else:
        raise ValueError(f"Unknown optimizer: {optimizer}")

    if polish_needed and optimizer != "lbfgs":
        res_polish = minimize(
            neg_loglike, best_x_opt, bounds=opt_bounds, method="L-BFGS-B",
            options={"maxiter": 100, "ftol": 1e-8},
        )
        if res_polish.success or res_polish.fun < neg_loglike(best_x_opt).item():
            best_x_opt = res_polish.x
        nfev_polish = int(getattr(res_polish, "nfev", 0))
    else:
        nfev_polish = 0

    # Reconstruct full theta
    best_theta = best_x_opt.tolist()
    for idx, val in fixed_entries:
        best_theta.insert(idx, val)
    theta_dict = like.theta_to_dict(model, best_theta)
    chi2_min = like.chi2(model, best_theta)
    loglike_best = like.loglike(model, best_theta)
    v_bounds = like.bounds(model)
    at_bounds = {
        name: abs(float(x) - lo) < 1e-6 or abs(float(x) - hi) < 1e-6
        for name, x, (lo, hi) in zip(names, best_theta, v_bounds)
    }

    # Derived parameters
    derived: Dict[str, Any] = {}
    Om = theta_dict.get("Omega_m", 0.3)
    s8 = theta_dict.get("sigma8", 0.8)
    derived["S8"] = float(s8 * math.sqrt(Om / 0.3))
    if model == "m34":
        derived["A_eff"] = float(0.75 * (3.0 - theta_dict.get("s", 2.55)))
    elif model == "mkappa":
        derived["A_eff"] = float(theta_dict.get("kappa", 0.75) * (3.0 - theta_dict.get("s", 2.55)))
    elif model == "const_sigma":
        derived["Sigma_z0_minus_1"] = float(theta_dict.get("Sigma0", 0.0))

    return {
        "model": model,
        "optimizer": optimizer,
        "popsize": popsize,
        "maxiter": maxiter,
        "seed": seed,
        "fixed_params": fix_params,
        "n_total_evals": counter["n"],
        "n_evals_de": nfev_de,
        "n_evals_polish": nfev_polish,
        "params": theta_dict,
        "chi2_min": chi2_min,
        "loglike": loglike_best,
        "at_bounds": at_bounds,
        "derived": derived,
        "runtime_seconds": float(_time.time() - t0),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="FDS-G1 Stage-3 expanded lensing / 3x2pt likelihood")
    ap.add_argument("--config", required=True)
    ap.add_argument("--theory-backend", choices=["bbks", "class"], default="bbks", help="Matter power backend: bbks (default) or class.")
    ap.add_argument("--model", choices=list(BASE_PARAM_NAMES), required=True)
    ap.add_argument("--theta-json", help="Parameter dict/list. If omitted with --nested, run evidence; otherwise print param names.")
    ap.add_argument("--nested", action="store_true")
    ap.add_argument("--nlive", type=int, default=500)
    ap.add_argument("--dlogz", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--out-json")
    ap.add_argument("--time-eval", type=int, default=0, help="Run N single-point evals and report timing.")
    ap.add_argument("--optimize", action="store_true")
    ap.add_argument("--optimizer", choices=["de", "lbfgs"], default="de")
    ap.add_argument("--popsize", type=int, default=15, help="DE popsize (real pop = popsize * dim)")
    ap.add_argument("--maxiter", type=int, default=40, help="DE max generations")
    ap.add_argument("--no-polish", action="store_true", help="Skip L-BFGS-B polish after DE.")
    ap.add_argument("--class-nk", type=int, default=128, help="CLASS backend k grid size (default 128).")
    ap.add_argument("--class-nz", type=int, default=64, help="CLASS backend z grid size (default 64).")
    ap.add_argument("--profile-s", default=None, help="Profile scan: 'START STOP STEP' (e.g. '1.5 3.2 0.1')")
    ap.add_argument("--s-fixed", type=float, default=None, help="Fix s parameter to this value for conditional optimization. (Deprecated; use --fix-param.)")
    ap.add_argument("--fix-param", default=None, help="Fix parameters: 'h=0.68,Omega_b=0.049,n_s=0.965'")
    args = ap.parse_args()

    # Parse --fix-param
    fix_params: Dict[str, float] = {}
    if args.fix_param:
        for token in args.fix_param.replace(",", " ").split():
            if "=" not in token:
                raise SystemExit(f"--fix-param: expected key=value, got '{token}'. Example: h=0.68,n_s=0.965")
            key, val = token.split("=", 1)
            fix_params[key.strip()] = float(val.strip())
    # Backward compatibility: --s-fixed
    if args.s_fixed is not None and "s" not in fix_params:
        fix_params["s"] = float(args.s_fixed)

    like = Stage3Lensing3x2ptLikelihood(args.config, theory_backend=args.theory_backend, class_nk=args.class_nk, class_nz=args.class_nz)
    names = like.param_names(args.model)

    # ------------------------- timing benchmark -------------------------
    if args.time_eval:
        theta = [0.5 * (lo + hi) for lo, hi in like.bounds(args.model)]
        if args.theta_json:
            theta = _theta_from_json(args.theta_json, names)
        t_start = time.time()
        for _ in range(args.time_eval):
            like.chi2(args.model, theta)
        elapsed = time.time() - t_start
        out = {
            "model": args.model,
            "n_eval": args.time_eval,
            "seconds_total": round(elapsed, 4),
            "seconds_per_eval": round(elapsed / args.time_eval, 6),
            "evals_per_minute": round(args.time_eval / elapsed * 60, 1),
        }
        print(json.dumps(out, indent=2))
        return

    # ------------------------- profile scan in s -------------------------
    if args.profile_s is not None:
        s_start, s_stop, s_step = _parse_profile_s(args.profile_s)
        s_vals = []
        sv = s_start
        while sv <= s_stop + 1e-9:
            s_vals.append(round(sv, 10))
            sv += s_step
        results = []
        for s_i, s_val in enumerate(s_vals):
            result = _opt_optimize(
                like, args.model, args.optimizer,
                popsize=8, maxiter=15, seed=args.seed,
                fix_params={**fix_params, "s": s_val},
                no_polish=False,
            )
            result["s_index"] = s_i
            results.append(result)
            chi2_str = f"{result['chi2_min']:.3f}" if np.isfinite(result['chi2_min']) else "inf"
            print(f"[profile {s_i}/{len(s_vals)}] s={s_val:.4g} chi2_min={chi2_str}", flush=True)
        out = {
            "model": args.model,
            "s_grid": s_vals,
            "profile_results": results,
        }
        print(json.dumps(out, indent=2))
        if args.out_json:
            Path(args.out_json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        return

    # ------------------------- optimizer mode -------------------------
    if args.optimize:
        result = _opt_optimize(
            like, args.model, args.optimizer,
            popsize=args.popsize, maxiter=args.maxiter, seed=args.seed,
            fix_params=fix_params,
            no_polish=args.no_polish,
        )
        print(json.dumps(result, indent=2))
        if args.out_json:
            Path(args.out_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    # ------------------------- original modes -------------------------
    if args.nested:
        out = like.run_nested(args.model, nlive=args.nlive, dlogz=args.dlogz, seed=args.seed, out_json=args.out_json)
        print(json.dumps(out, indent=2))
        return
    if not args.theta_json:
        print(json.dumps({"model": args.model, "param_names": names, "bounds": like.bounds(args.model)}, indent=2))
        return
    theta = _theta_from_json(args.theta_json, names)
    print(json.dumps({
        "model": args.model,
        "param_names": names,
        "theta": theta,
        "chi2": like.chi2(args.model, theta),
        "loglike": like.loglike(args.model, theta),
    }, indent=2))


if __name__ == "__main__":
    main()
