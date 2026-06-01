#!/usr/bin/env python3
"""
Exact Stage 2d likelihood for G1fit-real.

Data blocks:
  - Pantheon+ full covariance SN
  - DESI DR2 BAO covariance
  - curated RSD fσ8 subset from Growth Table II + WiggleZ covariance block
  - E_G compressed points

Models:
  lcdm   : Omega_m, q_BAO, sigma8_0
  cpl    : Omega_m, w0, wa, q_BAO, sigma8_0
  g1de1  : Omega_m, s, q_BAO, sigma8_0, mu0
  g1de2  : Omega_m, s, q_BAO, sigma8_0, mu0, Sigma0
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
import json
import math
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import scipy.linalg as la
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d, PchipInterpolator


PARAM_NAMES = {
    "lcdm":  ["Omega_m", "q_BAO", "sigma8_0"],
    "cpl":   ["Omega_m", "w0", "wa", "q_BAO", "sigma8_0"],
    "g1de1": ["Omega_m", "s", "q_BAO", "sigma8_0", "mu0"],
    "g1de2": ["Omega_m", "s", "q_BAO", "sigma8_0", "mu0", "Sigma0"],
}

BOUNDS = {
    "lcdm":  [(0.05, 0.60), (10.0, 80.0), (0.40, 1.20)],
    "cpl":   [(0.05, 0.60), (-3.0, 0.0), (-3.0, 3.0), (10.0, 80.0), (0.40, 1.20)],
    "g1de1": [(0.05, 0.60), (1.0, 5.0), (10.0, 80.0), (0.40, 1.20), (-0.95, 1.0)],
    "g1de2": [(0.05, 0.60), (1.0, 5.0), (10.0, 80.0), (0.40, 1.20), (-0.95, 1.0), (-0.95, 1.0)],
}

STARTS = {
    "lcdm":  np.array([0.309, 29.80, 0.78]),
    "cpl":   np.array([0.321, -0.77, -0.76, 30.46, 0.78]),
    "g1de1": np.array([0.2969, 2.56, 30.42, 0.80, -0.07]),
    "g1de2": np.array([0.2969, 2.56, 30.42, 0.795, -0.07, -0.36]),
}

INIT_SCALES = {
    "lcdm":  np.array([0.010, 0.25, 0.020]),
    "cpl":   np.array([0.010, 0.050, 0.150, 0.25, 0.020]),
    "g1de1": np.array([0.010, 0.100, 0.25, 0.020, 0.120]),
    "g1de2": np.array([0.010, 0.100, 0.25, 0.020, 0.120, 0.120]),
}


def _symmetrize(cov: np.ndarray) -> np.ndarray:
    return 0.5 * (cov + cov.T)


def create_eg_default(path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "z,E_G,sigma,sample\n"
            "0.267,0.43,0.13,GAMA\n"
            "0.305,0.27,0.08,LOWZ+2dFLOZ\n"
            "0.554,0.26,0.07,CMASS+2dFHIZ\n",
            encoding="utf-8",
        )


def build_curated_growth_table(
    growth_table_path: str | Path,
    wigglez_cov_path: str | Path,
    out_csv: str | Path,
    out_cov: str | Path,
) -> Tuple[pd.DataFrame, np.ndarray]:
    """Create the algorithmic curated non-overlapping RSD subset v0.

    Rule:
      - parse Growth_tableII as repeated quadruples: z, fσ8, sigma, Omega_m_fid;
      - insert provided WiggleZ 3x3 covariance block for z=0.44,0.60,0.73;
      - deduplicate epsilon redshift repetitions by keeping the lowest-error representative;
      - keep at most one representative per Δz=0.10 bin;
      - preserve the WiggleZ triplet.
    """
    growth_table_path = Path(growth_table_path)
    wigglez_cov_path = Path(wigglez_cov_path)

    vals = np.loadtxt(growth_table_path).reshape(-1)
    if len(vals) % 4 != 0:
        raise ValueError("Growth_tableII must parse into quadruples: z, fsigma8, sigma, Omega_m_fid.")
    full = pd.DataFrame(vals.reshape((-1, 4)), columns=["z_raw", "fsigma8", "sigma", "Omega_m_fid"])
    full["z"] = np.round(full["z_raw"].astype(float), 3)
    full["index"] = np.arange(len(full))

    cov_full = np.diag(full["sigma"].to_numpy(float) ** 2)

    cwig = np.loadtxt(wigglez_cov_path).reshape(3, 3)
    wiggle_idx = []
    for target in [0.44, 0.60, 0.73]:
        idxs = np.where(np.abs(full["z"].values - target) < 0.002)[0]
        if len(idxs) == 0:
            raise ValueError(f"No WiggleZ row near z={target}")
        wiggle_idx.append(int(idxs[0]))
    for a, i in enumerate(wiggle_idx):
        for b, j in enumerate(wiggle_idx):
            cov_full[i, j] = cwig[a, b]

    dedup = (
        full.sort_values("sigma")
        .groupby("z", as_index=False)
        .first()
        .sort_values("z")
        .reset_index(drop=True)
    )

    selected = set(wiggle_idx)
    for b in np.arange(0.0, 2.05, 0.10):
        sub = dedup[(dedup["z"] >= b) & (dedup["z"] < b + 0.10)]
        if len(sub) == 0:
            continue
        if any(b <= full.loc[i, "z"] < b + 0.10 for i in selected):
            continue
        selected.add(int(sub.sort_values("sigma").iloc[0]["index"]))

    selected_idx = sorted(selected, key=lambda i: full.loc[i, "z"])
    curated = full.loc[selected_idx].copy().reset_index(drop=True)
    cov = cov_full[np.ix_(selected_idx, selected_idx)]

    out_csv = Path(out_csv)
    out_cov = Path(out_cov)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_cov.parent.mkdir(parents=True, exist_ok=True)
    curated.to_csv(out_csv, index=False)
    np.savetxt(out_cov, cov)
    return curated, cov


@dataclass
class ExactStage2DLikelihood:
    stage1_data_dir: Path
    growth_csv: Path
    growth_cov: Path
    eg_csv: Path
    physical_zmax: float = 2.0
    physical_nz: int = 300
    z_grid_size: int = 1600
    growth_nsteps: int = 320

    def __post_init__(self) -> None:
        self.stage1_data_dir = Path(self.stage1_data_dir)
        self.growth_csv = Path(self.growth_csv)
        self.growth_cov = Path(self.growth_cov)
        self.eg_csv = Path(self.eg_csv)

        # SN
        sn_path = self.stage1_data_dir / "pantheon_plus.csv"
        sn_cov_path = self.stage1_data_dir / "pantheon_plus_cov.txt"
        if not sn_path.exists() or not sn_cov_path.exists():
            raise FileNotFoundError(
                f"Missing Pantheon+ data in {self.stage1_data_dir}. "
                "Expected pantheon_plus.csv and pantheon_plus_cov.txt"
            )
        self.sn = pd.read_csv(sn_path)
        self.z_sn = self.sn["z"].to_numpy(float)
        self.mu_sn = self.sn["mu"].to_numpy(float)
        self.Csn = _symmetrize(np.loadtxt(sn_cov_path))
        self.cho_sn = la.cho_factor(self.Csn, lower=True, check_finite=False)

        # BAO
        bao_path = self.stage1_data_dir / "desi_dr2_bao.csv"
        bao_cov_path = self.stage1_data_dir / "desi_dr2_bao_cov.txt"
        if not bao_path.exists() or not bao_cov_path.exists():
            raise FileNotFoundError(
                f"Missing DESI DR2 BAO data in {self.stage1_data_dir}. "
                "Expected desi_dr2_bao.csv and desi_dr2_bao_cov.txt"
            )
        self.bao = pd.read_csv(bao_path)
        self.z_bao = self.bao["z"].to_numpy(float)
        self.obs_bao = self.bao["observable"].astype(str).to_numpy()
        self.val_bao = self.bao["value"].to_numpy(float)
        self.Cbao = _symmetrize(np.loadtxt(bao_cov_path))
        self.cho_bao = la.cho_factor(self.Cbao, lower=True, check_finite=False)

        # Growth
        self.growth = pd.read_csv(self.growth_csv)
        self.z_growth = self.growth["z"].to_numpy(float)
        self.val_growth = self.growth["fsigma8"].to_numpy(float)
        self.Cgrowth = _symmetrize(np.loadtxt(self.growth_cov))
        self.cho_growth = la.cho_factor(self.Cgrowth, lower=True, check_finite=False)

        # E_G
        self.eg = pd.read_csv(self.eg_csv)
        self.z_eg = self.eg["z"].to_numpy(float)
        self.val_eg = self.eg["E_G"].to_numpy(float)
        self.Ceg = np.diag(self.eg["sigma"].to_numpy(float) ** 2)
        self.cho_eg = la.cho_factor(self.Ceg, lower=True, check_finite=False)

        zmax = max(
            float(np.max(self.z_sn)),
            float(np.max(self.z_bao)),
            float(np.max(self.z_growth)),
            float(np.max(self.z_eg)),
        )
        self.z_grid = np.linspace(0.0, zmax * 1.05 + 0.01, self.z_grid_size)

        self.growth_cache_max = 20000
        self._growth_cache: OrderedDict = OrderedDict()

    @staticmethod
    def names(model: str) -> List[str]:
        return PARAM_NAMES[model]

    @staticmethod
    def bounds(model: str) -> List[Tuple[float, float]]:
        return BOUNDS[model]

    def in_prior(self, model: str, theta: np.ndarray) -> bool:
        return all(lo < x < hi for x, (lo, hi) in zip(theta, BOUNDS[model]))

    # ---------- Background expansion ----------
    @staticmethod
    def E_lcdm_z(z: np.ndarray, Om: float) -> np.ndarray:
        a = 1.0 / (1.0 + np.asarray(z))
        return np.sqrt(Om * a**-3 + (1.0 - Om))

    @staticmethod
    def E_cpl_z(z: np.ndarray, Om: float, w0: float, wa: float) -> np.ndarray:
        a = 1.0 / (1.0 + np.asarray(z))
        Ode = 1.0 - Om
        E2 = Om * a**-3 + Ode * a ** (-3.0 * (1.0 + w0 + wa)) * np.exp(3.0 * wa * (a - 1.0))
        if np.any(E2 <= 0) or np.any(~np.isfinite(E2)):
            return np.full_like(np.asarray(z, dtype=float), np.nan)
        return np.sqrt(E2)

    @staticmethod
    def chiH_a(a: np.ndarray, Om: float, s: float) -> np.ndarray:
        a = np.asarray(a, dtype=float)
        chi0 = 1.0 - Om
        if not (0.0 < chi0 < 1.0):
            return np.full_like(a, np.nan)
        B = 1.0 / chi0 - 1.0
        return 1.0 / (1.0 + B * a**(-s))

    @classmethod
    def Xhat_a(cls, a: np.ndarray, Om: float, s: float) -> np.ndarray:
        chi = cls.chiH_a(a, Om, s)
        return 4.0 * chi * (1.0 - chi)

    @classmethod
    def E_g1_z(cls, z: np.ndarray, Om: float, s: float) -> np.ndarray:
        a = 1.0 / (1.0 + np.asarray(z, dtype=float))
        chi = cls.chiH_a(a, Om, s)
        E2 = Om * a**-3 / (1.0 - chi)
        if np.any(~np.isfinite(E2)) or np.any(E2 <= 0):
            return np.full_like(a, np.nan)
        return np.sqrt(E2)

    def E_model_z(self, model: str, theta: np.ndarray, z: np.ndarray) -> np.ndarray:
        if model == "lcdm":
            return self.E_lcdm_z(z, theta[0])
        if model == "cpl":
            return self.E_cpl_z(z, theta[0], theta[1], theta[2])
        if model in ("g1de1", "g1de2"):
            return self.E_g1_z(z, theta[0], theta[1])
        raise ValueError(model)

    @staticmethod
    def q_index(model: str) -> int:
        return {"lcdm": 1, "cpl": 3, "g1de1": 2, "g1de2": 2}[model]

    def comoving_distance(self, model: str, theta: np.ndarray, z: np.ndarray) -> Optional[np.ndarray]:
        E = self.E_model_z(model, theta, self.z_grid)
        if np.any(~np.isfinite(E)) or np.any(E <= 0):
            return None
        dc_grid = cumulative_trapezoid(1.0 / E, self.z_grid, initial=0.0)
        interp = PchipInterpolator(self.z_grid, dc_grid, extrapolate=True)
        return interp(z)

    # ---------- SN/BAO ----------
    def sn_mu0_pred(self, model: str, theta: np.ndarray) -> Optional[np.ndarray]:
        dc = self.comoving_distance(model, theta, self.z_sn)
        if dc is None or np.any(dc <= 0):
            return None
        dl = (1.0 + self.z_sn) * dc
        if np.any(~np.isfinite(dl)) or np.any(dl <= 0):
            return None
        return 5.0 * np.log10(dl)

    @staticmethod
    def quad(delta: np.ndarray, cho) -> float:
        delta = np.asarray(delta, dtype=float)
        if not np.all(np.isfinite(delta)):
            return np.inf
        if np.max(np.abs(delta)) > 1e8:
            return np.inf
        try:
            inv_delta = la.cho_solve(cho, delta, check_finite=False)
            if not np.all(np.isfinite(inv_delta)):
                return np.inf
            with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
                val = float(delta @ inv_delta)
        except (la.LinAlgError, ValueError, RuntimeError):
            return np.inf
        return val if np.isfinite(val) else np.inf

    def _sn_quadratic_terms(self, model: str, theta: np.ndarray):
        pred = self.sn_mu0_pred(model, theta)
        if pred is None:
            return None
        pred = np.asarray(pred, dtype=float)
        if pred.shape != self.mu_sn.shape:
            return None
        if not np.all(np.isfinite(pred)):
            return None
        delta = self.mu_sn - pred
        if not np.all(np.isfinite(delta)):
            return None
        if np.max(np.abs(delta)) > 1e6:
            return None
        one = np.ones_like(delta)
        try:
            inv_delta = la.cho_solve(self.cho_sn, delta, check_finite=False)
            inv_one = la.cho_solve(self.cho_sn, one, check_finite=False)
            if not np.all(np.isfinite(inv_delta)) or not np.all(np.isfinite(inv_one)):
                return None
            with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
                A = float(delta @ inv_delta)
                B = float(one @ inv_delta)
                C = float(one @ inv_one)
        except (la.LinAlgError, ValueError, RuntimeError):
            return None
        if not np.isfinite(A) or not np.isfinite(B) or not np.isfinite(C) or C <= 0:
            return None
        return A, B, C

    def chi2_sn(self, model: str, theta: np.ndarray) -> float:
        terms = self._sn_quadratic_terms(model, theta)
        if terms is None:
            return np.inf
        A, B, C = terms
        chi2 = A - B * B / C
        return float(chi2) if np.isfinite(chi2) else np.inf

    def best_M(self, model: str, theta: np.ndarray) -> float:
        terms = self._sn_quadratic_terms(model, theta)
        if terms is None:
            return np.nan
        _, B, C = terms
        return float(B / C)

    def bao_pred(self, model: str, theta: np.ndarray) -> Optional[np.ndarray]:
        dc = self.comoving_distance(model, theta, self.z_bao)
        if dc is None:
            return None
        E = self.E_model_z(model, theta, self.z_bao)
        if np.any(~np.isfinite(E)) or np.any(E <= 0):
            return None
        q = theta[self.q_index(model)]
        pred = []
        for z, ob, dci, ei in zip(self.z_bao, self.obs_bao, dc, E):
            if ob == "DM_over_rd":
                pred.append(q * dci)
            elif ob == "DH_over_rd":
                pred.append(q / ei)
            elif ob == "DV_over_rd":
                pred.append(q * (z * dci * dci / ei) ** (1.0 / 3.0))
            else:
                raise ValueError(f"Unknown BAO observable: {ob}")
        return np.asarray(pred)

    def chi2_bao(self, model: str, theta: np.ndarray) -> float:
        pred = self.bao_pred(model, theta)
        if pred is None:
            return np.inf
        return self.quad(self.val_bao - pred, self.cho_bao)

    # ---------- Growth ----------
    @staticmethod
    def E2_growth(model: str, a: float, pars: Dict[str, float]) -> float:
        Om = pars["Omega_m"]
        if model == "lcdm":
            return Om * a**-3 + (1.0 - Om)
        if model == "cpl":
            w0, wa = pars["w0"], pars["wa"]
            Ode = 1.0 - Om
            return Om * a**-3 + Ode * a ** (-3.0 * (1.0 + w0 + wa)) * math.exp(3.0 * wa * (a - 1.0))
        if model in ("g1de1", "g1de2"):
            s = pars["s"]
            chi = float(ExactStage2DLikelihood.chiH_a(np.array([a]), Om, s)[0])
            return Om * a**-3 / (1.0 - chi)
        raise ValueError(model)

    @staticmethod
    def dlnE_dln_a(model: str, a: float, pars: Dict[str, float]) -> float:
        Om = pars["Omega_m"]
        if model == "lcdm":
            E2 = Om * a**-3 + (1.0 - Om)
            dE2 = -3.0 * Om * a**-3
            return 0.5 * dE2 / E2
        if model == "cpl":
            w0, wa = pars["w0"], pars["wa"]
            Ode = 1.0 - Om
            de = Ode * a ** (-3.0 * (1.0 + w0 + wa)) * math.exp(3.0 * wa * (a - 1.0))
            E2 = Om * a**-3 + de
            dE2 = -3.0 * Om * a**-3 + de * (-3.0 * (1.0 + w0 + wa) + 3.0 * wa * a)
            return 0.5 * dE2 / E2
        if model in ("g1de1", "g1de2"):
            s = pars["s"]
            chi = float(ExactStage2DLikelihood.chiH_a(np.array([a]), Om, s)[0])
            dchi = s * chi * (1.0 - chi)
            return 0.5 * (-3.0 + dchi / (1.0 - chi))
        raise ValueError(model)

    @staticmethod
    def mu_response(model: str, a: float, pars: Dict[str, float]) -> float:
        if model in ("g1de1", "g1de2"):
            X = float(ExactStage2DLikelihood.Xhat_a(np.array([a]), pars["Omega_m"], pars["s"])[0])
            return 1.0 + pars.get("mu0", 0.0) * X
        return 1.0

    @staticmethod
    def Sigma_response(model: str, a: np.ndarray, pars: Dict[str, float]) -> np.ndarray:
        if model == "g1de2":
            X = ExactStage2DLikelihood.Xhat_a(a, pars["Omega_m"], pars["s"])
            return 1.0 + pars.get("Sigma0", 0.0) * X
        return np.ones_like(np.asarray(a, dtype=float))

    def theta_to_pars(self, model: str, theta: np.ndarray) -> Dict[str, float]:
        if model == "lcdm":
            return {"Omega_m": theta[0], "sigma8_0": theta[2]}
        if model == "cpl":
            return {"Omega_m": theta[0], "w0": theta[1], "wa": theta[2], "sigma8_0": theta[4]}
        if model == "g1de1":
            return {"Omega_m": theta[0], "s": theta[1], "sigma8_0": theta[3], "mu0": theta[4]}
        if model == "g1de2":
            return {"Omega_m": theta[0], "s": theta[1], "sigma8_0": theta[3], "mu0": theta[4], "Sigma0": theta[5]}
        raise ValueError(model)

    def physical_ok(self, model: str, theta: np.ndarray) -> bool:
        if model not in ("g1de1", "g1de2"):
            return True
        pars = self.theta_to_pars(model, theta)
        z = np.linspace(0.0, self.physical_zmax, self.physical_nz)
        a = 1.0 / (1.0 + z)
        X = self.Xhat_a(a, pars["Omega_m"], pars["s"])
        mu = 1.0 + pars.get("mu0", 0.0) * X
        Sigma = 1.0 + pars.get("Sigma0", 0.0) * X
        return bool(np.all(mu > 0.0) and np.all(Sigma > 0.0) and np.all(np.isfinite(mu)) and np.all(np.isfinite(Sigma)))

    def growth_solution(self, model: str, theta: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        pars = self.theta_to_pars(model, theta)
        # Cache rounded physical parameters only.
        key = (model, tuple(round(float(pars[k]), 6) for k in sorted(pars)))
        if key in self._growth_cache:
            self._growth_cache.move_to_end(key)
            return self._growth_cache[key]

        a_ini = 1e-3
        N0, N1 = math.log(a_ini), 0.0
        nsteps = self.growth_nsteps
        h = (N1 - N0) / (nsteps - 1)
        N = np.linspace(N0, N1, nsteps)
        y = np.array([a_ini, a_ini], dtype=float)
        delta = np.empty(nsteps)
        vel = np.empty(nsteps)

        def rhs(Nv: float, yv: np.ndarray) -> np.ndarray:
            a = math.exp(Nv)
            d, v = yv
            E2 = self.E2_growth(model, a, pars)
            dl = self.dlnE_dln_a(model, a, pars)
            mu = self.mu_response(model, a, pars)
            if (not np.isfinite(E2)) or E2 <= 0 or (not np.isfinite(dl)) or (not np.isfinite(mu)) or mu <= 0:
                return np.array([np.nan, np.nan])
            Om_a = pars["Omega_m"] * a**-3 / E2
            return np.array([v, -(2.0 + dl) * v + 1.5 * Om_a * mu * d])

        for i in range(nsteps):
            delta[i] = y[0]
            vel[i] = y[1]
            if i == nsteps - 1:
                break
            Ni = N[i]
            k1 = rhs(Ni, y)
            k2 = rhs(Ni + 0.5 * h, y + 0.5 * h * k1)
            k3 = rhs(Ni + 0.5 * h, y + 0.5 * h * k2)
            k4 = rhs(Ni + h, y + h * k3)
            y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            if np.any(~np.isfinite(y)) or y[0] <= 0:
                return None

        a_grid = np.exp(N)
        D = delta / delta[-1]
        f = vel / delta
        result = (a_grid, D, f)
        self._growth_cache[key] = result
        while len(self._growth_cache) > self.growth_cache_max:
            self._growth_cache.popitem(last=False)
        return result

    def fsigma8_pred(self, model: str, theta: np.ndarray, z: np.ndarray) -> Optional[np.ndarray]:
        sol = self.growth_solution(model, theta)
        if sol is None:
            return None
        pars = self.theta_to_pars(model, theta)
        a, D, f = sol
        ae = 1.0 / (1.0 + np.asarray(z, dtype=float))
        Dv = np.interp(ae, a, D)
        fv = np.interp(ae, a, f)
        return fv * pars["sigma8_0"] * Dv

    def chi2_growth(self, model: str, theta: np.ndarray) -> float:
        pred = self.fsigma8_pred(model, theta, self.z_growth)
        if pred is None or np.any(~np.isfinite(pred)):
            return np.inf
        return self.quad(self.val_growth - pred, self.cho_growth)

    # ---------- E_G ----------
    def eg_pred(self, model: str, theta: np.ndarray) -> Optional[np.ndarray]:
        sol = self.growth_solution(model, theta)
        if sol is None:
            return None
        pars = self.theta_to_pars(model, theta)
        a_grid, D, f = sol
        ae = 1.0 / (1.0 + self.z_eg)
        fz = np.interp(ae, a_grid, f)
        if np.any(~np.isfinite(fz)) or np.any(fz <= 0):
            return None
        Sigma = self.Sigma_response(model, ae, pars)
        if np.any(~np.isfinite(Sigma)):
            return None
        return pars["Omega_m"] * Sigma / fz

    def chi2_eg(self, model: str, theta: np.ndarray) -> float:
        pred = self.eg_pred(model, theta)
        if pred is None or np.any(~np.isfinite(pred)):
            return np.inf
        return self.quad(self.val_eg - pred, self.cho_eg)

    # ---------- Total likelihood ----------
    def chi2(self, model: str, theta: np.ndarray, include_eg: bool = True) -> float:
        theta = np.asarray(theta, dtype=float)
        if not self.in_prior(model, theta):
            return np.inf
        if not self.physical_ok(model, theta):
            return np.inf
        val = self.chi2_sn(model, theta) + self.chi2_bao(model, theta) + self.chi2_growth(model, theta)
        if include_eg:
            val += self.chi2_eg(model, theta)
        return float(val) if np.isfinite(val) else np.inf

    def chi2_components(self, model: str, theta: np.ndarray) -> Dict[str, float]:
        return {
            "chi2_total": self.chi2(model, theta, include_eg=True),
            "chi2_sn": self.chi2_sn(model, theta),
            "chi2_bao": self.chi2_bao(model, theta),
            "chi2_growth": self.chi2_growth(model, theta),
            "chi2_EG": self.chi2_eg(model, theta),
        }

    def loglike(self, model: str, theta: np.ndarray) -> float:
        c = self.chi2(model, theta, include_eg=True)
        return -0.5 * c if np.isfinite(c) else -np.inf

    def logprior(self, model: str, theta: np.ndarray) -> float:
        return 0.0 if self.in_prior(model, theta) and self.physical_ok(model, theta) else -np.inf

    def logprob(self, model: str, theta: np.ndarray) -> float:
        lp = self.logprior(model, theta)
        if not np.isfinite(lp):
            return -np.inf
        ll = self.loglike(model, theta)
        return lp + ll if np.isfinite(ll) else -np.inf


def load_config(path: str | Path) -> dict:
    with open(path) as f:
        return json.load(f)


def make_likelihood_from_config(config: dict) -> ExactStage2DLikelihood:
    create_eg_default(config["eg_data"])
    if not Path(config["curated_growth_out"]).exists() or not Path(config["curated_growth_cov_out"]).exists():
        build_curated_growth_table(
            config["growth_table"],
            config["wigglez_cov"],
            config["curated_growth_out"],
            config["curated_growth_cov_out"],
        )
    phys = config.get("physical_prior", {})
    return ExactStage2DLikelihood(
        stage1_data_dir=Path(config["stage1_data_dir"]),
        growth_csv=Path(config["curated_growth_out"]),
        growth_cov=Path(config["curated_growth_cov_out"]),
        eg_csv=Path(config["eg_data"]),
        physical_zmax=float(phys.get("zmax", 2.0)),
        physical_nz=int(phys.get("nz", 300)),
    )
