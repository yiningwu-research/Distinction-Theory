from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULTS: dict[str, Any] = {
    "run": {"name": "cmb_precheck", "output_dir": "outputs/cmb_precheck", "overwrite": False},
    "cosmology": {
        "H0": 67.4,
        "Omega_m": 0.315,
        "Omega_b": 0.049,
        "Omega_r": 9.2e-5,
        "n_s": 0.965,
        "A_s": 2.1e-9,
        "tau_reio": 0.054,
        "sigma8_baseline": 0.811,
        "z_star": 1089.92,
    },
    "model": {
        "name": "g1de_m34",
        "s": 2.555,
        "kappa": 0.75,
        "normalization": "code",
        "horizon_completion": "none",
        "gamma_Gamma": 1.0,
        "c_Gamma": 1.0,
    },
    "amplitude": {"mode": "fixed_primordial", "sigma8_target": 0.78},
    "power": {"backend": "analytic", "k_min": 1e-5, "k_max": 30.0, "n_k": 1800},
    "integration": {
        "a_ini": 9e-4,
        "z_max": 1089.92,
        "n_z": 900,
        "ell_min": 2,
        "ell_max": 2998,
        "ell_step": 1,
    },
    "likelihood": {"backend": "none", "path": None, "variant": "act_baseline", "data_dir": None},
}


def _deep_update(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_update(out[key], value)
        else:
            out[key] = value
    return out


def validate_config(cfg: dict[str, Any]) -> None:
    c = cfg["cosmology"]
    if not 0.0 < c["Omega_b"] < c["Omega_m"] < 1.0:
        raise ValueError("Require 0 < Omega_b < Omega_m < 1.")
    if c["Omega_m"] + c["Omega_r"] >= 1.0:
        raise ValueError("Omega_m + Omega_r must be < 1 in the flat precheck background.")
    m = cfg["model"]
    if m["name"] not in {"lcdm", "g1de_m34", "g1de_mkappa", "background_only"}:
        raise ValueError(f"Unsupported model.name={m['name']!r}.")
    if m["normalization"] not in {"code", "present"}:
        raise ValueError("model.normalization must be 'code' or 'present'.")
    if m["horizon_completion"] not in {"none", "single_pole"}:
        raise ValueError("model.horizon_completion must be 'none' or 'single_pole'.")
    if cfg["amplitude"]["mode"] not in {"fixed_primordial", "fixed_sigma8"}:
        raise ValueError("amplitude.mode must be fixed_primordial or fixed_sigma8.")
    if cfg["power"]["backend"] not in {"analytic", "class"}:
        raise ValueError("power.backend must be analytic or class.")
    if cfg["likelihood"]["backend"] not in {"none", "generic_npz", "act_dr6"}:
        raise ValueError("likelihood.backend must be none, generic_npz, or act_dr6.")
    integ = cfg["integration"]
    if integ["ell_min"] < 2 or integ["ell_max"] < integ["ell_min"]:
        raise ValueError("Invalid ell range.")
    if integ["a_ini"] <= 0 or integ["a_ini"] >= 1:
        raise ValueError("integration.a_ini must lie in (0,1).")


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}
    cfg = _deep_update(DEFAULTS, user)
    cfg["_config_path"] = str(path.resolve())
    validate_config(cfg)
    return cfg
