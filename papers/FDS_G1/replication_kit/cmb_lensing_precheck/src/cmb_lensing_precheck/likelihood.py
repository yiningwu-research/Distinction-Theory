from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator


@dataclass
class LikelihoodResult:
    backend: str
    chi2_model: float
    chi2_lcdm: float
    delta_chi2: float
    metadata: dict


class GenericNPZLikelihood:
    def __init__(self, path: str | Path):
        loaded = np.load(path, allow_pickle=False)
        self.data = np.asarray(loaded["data"], dtype=float)
        self.cov = np.asarray(loaded["cov"], dtype=float)
        if self.cov.shape != (self.data.size, self.data.size):
            raise ValueError("NPZ covariance shape does not match data vector.")
        self.cinv = np.linalg.inv(self.cov)
        self.quantity = "clkk"
        if "quantity" in loaded:
            raw = loaded["quantity"]
            self.quantity = str(raw.item() if raw.ndim == 0 else raw[0])
        self.window = np.asarray(loaded["window"], dtype=float) if "window" in loaded else None
        self.window_ell = np.asarray(loaded["window_ell"], dtype=float) if "window_ell" in loaded else None
        self.ell = np.asarray(loaded["ell"], dtype=float) if "ell" in loaded else None
        if self.window is not None:
            if self.window_ell is None:
                raise ValueError("window_ell is required when window is provided.")
            if self.window.shape != (self.data.size, self.window_ell.size):
                raise ValueError("window shape must be (n_band, n_window_ell).")
        elif self.ell is None:
            raise ValueError("NPZ must contain either window/window_ell or ell.")

    def theory_vector(self, ell: np.ndarray, clpp: np.ndarray, clkk: np.ndarray) -> np.ndarray:
        theory = clpp if self.quantity == "clpp" else clkk
        interp = PchipInterpolator(ell, theory, extrapolate=False)
        if self.window is not None:
            vals = interp(self.window_ell)
            if np.any(~np.isfinite(vals)):
                raise ValueError("Theory ell range does not cover NPZ window_ell.")
            return self.window @ vals
        vals = interp(self.ell)
        if np.any(~np.isfinite(vals)):
            raise ValueError("Theory ell range does not cover NPZ ell values.")
        return vals

    def chi2(self, theory: np.ndarray) -> float:
        residual = self.data - theory
        return float(residual @ self.cinv @ residual)


def evaluate_generic_npz(path: str | Path, ell, clpp_model, clkk_model, clpp_lcdm, clkk_lcdm) -> LikelihoodResult:
    like = GenericNPZLikelihood(path)
    tm = like.theory_vector(ell, clpp_model, clkk_model)
    tl = like.theory_vector(ell, clpp_lcdm, clkk_lcdm)
    cm = like.chi2(tm)
    cl = like.chi2(tl)
    return LikelihoodResult("generic_npz", cm, cl, cm - cl, {"path": str(path), "quantity": like.quantity})


def evaluate_act_dr6(cfg: dict, ell, clpp_model, clpp_lcdm) -> LikelihoodResult:
    try:
        import act_dr6_lenslike as alike
    except ImportError as exc:
        raise ImportError("ACT likelihood requested. Install with: pip install -e '.[act]'") from exc
    lcfg = cfg["likelihood"]
    variant = str(lcfg.get("variant", "act_baseline"))
    data_dir = lcfg.get("data_dir")
    data = alike.load_data(
        variant,
        ddir=data_dir,
        lens_only=True,
        like_corrections=False,
        trim_lmax=max(2998, int(np.max(ell))),
    )
    lmax = max(2998, int(np.max(ell)))
    full_ell = np.arange(0, lmax + 1, dtype=int)

    def to_full_clkk(clpp):
        interp = PchipInterpolator(ell, clpp, extrapolate=True)
        pp = np.zeros_like(full_ell, dtype=float)
        pp[2:] = np.maximum(interp(full_ell[2:]), 0.0)
        return alike.pp_to_kk(pp, full_ell)

    zeros = np.zeros_like(full_ell, dtype=float)
    ln_m = alike.generic_lnlike(
        data, full_ell, to_full_clkk(clpp_model), full_ell, zeros, zeros, zeros, zeros,
        trim_lmax=lmax, do_norm_corr=False,
    )
    ln_l = alike.generic_lnlike(
        data, full_ell, to_full_clkk(clpp_lcdm), full_ell, zeros, zeros, zeros, zeros,
        trim_lmax=lmax, do_norm_corr=False,
    )
    cm, cl = -2.0 * float(ln_m), -2.0 * float(ln_l)
    return LikelihoodResult("act_dr6", cm, cl, cm - cl, {"variant": variant, "data_dir": data_dir})
