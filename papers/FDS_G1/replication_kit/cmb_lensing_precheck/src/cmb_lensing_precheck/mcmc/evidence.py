"""
Nested evidence module for G1 L0 MCMC.

Uses UltraNest (primary) for nested sampling with:
  - Persistent storage and resume
  - Reactive sampling
  - RJD diagnostics

Supports dynesty as independent cross-check.

Architecture:
  log_likelihood(params_cube) → uses full emulator pipeline
  prior_transform(cube) → maps [0,1]^d to registered flat priors
"""

from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any


# ── Registered prior bounds ────────────────────────────────────────────

PRIOR_BOUNDS = {
    "Omega_m": (0.15, 0.50),
    "h":       (0.55, 0.85),
    "ln10As":  (2.50, 3.70),
    "q":       (0.00, 1.15),
    "kappa":   (0.00, 1.00),
}

MODEL_PARAMS = {
    "lcdm":     ["Omega_m", "h", "ln10As"],
    "g1_bg":    ["Omega_m", "h", "ln10As", "q"],
    "g1_m34":   ["Omega_m", "h", "ln10As", "q"],
    "g1_mkappa":["Omega_m", "h", "ln10As", "q", "kappa"],
}

MODEL_FIXED = {
    "lcdm":     {"q": 0.0, "kappa": 0.0},
    "g1_bg":    {"kappa": 0.0},
    "g1_m34":   {"kappa": 0.75},
    "g1_mkappa":{},
}


def prior_transform(cube: np.ndarray, model: str) -> np.ndarray:
    """
    Transform unit cube [0,1]^d to registered flat priors.
    For UltraNest and dynesty.
    """
    params = np.zeros_like(cube)
    names = MODEL_PARAMS[model]
    for i, name in enumerate(names):
        lo, hi = PRIOR_BOUNDS[name]
        params[:, i] = lo + cube[:, i] * (hi - lo)
    return params


class EvidenceLikelihood:
    """
    Log-likelihood wrapper using the full emulator pipeline.

    Loads baseline emulator and v4 G1 ratio emulator.
    Uses registered priors and amplitude mode.

    Parameters
    ----------
    model : str
        One of "lcdm", "g1_bg", "g1_m34", "g1_mkappa"
    variant : str
        "act_baseline" or "actplanck_baseline"
    amplitude_param : str
        "ln10As" (default, primordial normalization)
    """

    def __init__(self, model: str, variant: str = "act_baseline",
                 amplitude_param: str = "ln10As"):
        self.model = model
        self.variant = variant
        self.amplitude_param = amplitude_param
        self.param_names = MODEL_PARAMS[model]
        self.fixed = MODEL_FIXED[model]
        self.n_dim = len(self.param_names)

        # Load likelihood with emulators
        from cmb_lensing_precheck.mcmc.likelihood import LensingLikelihood
        self._like = LensingLikelihood(variant, amplitude_param=amplitude_param)

        # Inject v4 emulator (train from frozen cache)
        self._inject_v4_emulator()

    def _inject_v4_emulator(self):
        """Train v4 structured emulator from frozen cache and inject."""
        from scripts.train_v4 import V4Emulator
        import numpy as np
        from pathlib import Path

        # Find project root relative to this file
        project_root = Path(__file__).parent.parent.parent.parent

        frozen = project_root / "outputs" / "frozen" / "v4_act_only"

        cache = {
            "params_train": np.load(frozen / "truth_cache/params_train.npy"),
            "ell": np.load(frozen / "truth_cache/ell.npy"),
            "R_bg_train": np.load(frozen / "truth_cache/R_bg_train.npy"),
            "R_Weyl_train": np.load(frozen / "truth_cache/R_Weyl_train.npy"),
        }
        emu = V4Emulator()
        emu.train(cache, n_pca_bg=5, n_pca_weyl=6,
                 neighbors_bg=80, neighbors_weyl=100,
                 kernel="thin_plate_spline")
        self._like._emulator = emu

    def log_likelihood(self, params: np.ndarray) -> float:
        """
        Evaluate log-likelihood for a parameter vector.

        Parameters
        ----------
        params : np.ndarray
            Parameter values in registered order

        Returns
        -------
        float
            Log-likelihood value (-inf if parameters invalid)
        """
        params_dict = dict(zip(self.param_names, params))
        params_dict.update(self.fixed)
        return self._like.log_likelihood(params_dict)


# ── Recovery test likelihoods ──────────────────────────────────────────

def constant_likelihood(params: np.ndarray) -> float:
    """LogL = 0 everywhere → evidence = 0, posterior = prior."""
    return 0.0


def gaussian_evidence(model: str) -> tuple:
    """
    Analytic Gaussian likelihood for evidence recovery test.
    Returns (log_likelihood_fn, analytic_logZ, n_dim).
    Gaussian centered within registered prior bounds.
    """
    n_dim = len(MODEL_PARAMS[model])
    rng = np.random.RandomState(42)
    # Center Gaussian at prior center (not origin)
    mean = np.zeros(n_dim)
    for i, name in enumerate(MODEL_PARAMS[model]):
        lo, hi = PRIOR_BOUNDS[name]
        mean[i] = (lo + hi) / 2.0  # prior center
    # Random covariance, scaled to fit well within prior
    A = rng.randn(n_dim, n_dim)
    raw_cov = A @ A.T + np.eye(n_dim)
    # Scale so typical width is ~1/4 of prior width
    scales = np.zeros(n_dim)
    for i, name in enumerate(MODEL_PARAMS[model]):
        lo, hi = PRIOR_BOUNDS[name]
        scales[i] = (hi - lo) / 4.0
    cov = np.diag(scales) @ raw_cov @ np.diag(scales)
    # Normalize to reasonable condition number
    inv_cov = np.linalg.inv(cov)
    # Prior volume
    prior_vol = 1.0
    for name in MODEL_PARAMS[model]:
        lo, hi = PRIOR_BOUNDS[name]
        prior_vol *= (hi - lo)

    def log_likelihood(params: np.ndarray) -> float:
        x = params - mean
        return -0.5 * x @ inv_cov @ x

    # Analytic evidence: -ln(V) + 0.5*n*ln(2π) + 0.5*ln(|cov|)
    from numpy.linalg import det
    analytic_logZ = -np.log(prior_vol) + 0.5 * n_dim * np.log(2 * np.pi) + 0.5 * np.log(det(cov))

    return log_likelihood, analytic_logZ, n_dim


# ── UltraNest wrapper ──────────────────────────────────────────────────

def run_ultranest(loglike: callable, prior_cube: callable, n_dim: int,
                  outdir: str | Path, **kwargs) -> dict:
    """
    Run UltraNest ReactiveNestedSampler.

    Parameters
    ----------
    loglike : callable
        Log-likelihood function taking PHYSICAL parameters (np.ndarray)
    prior_cube : callable
        Prior transform: unit cube → physical params (for UltraNest transform=)
    n_dim : int
        Number of parameters
    outdir : Path
        Output directory
    kwargs : dict
        Passed to ReactiveNestedSampler.run()

    Returns
    -------
    dict with keys: logZ, logZerr, samples, result
    """
    import ultranest
    from ultranest import ReactiveNestedSampler

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sampler = ReactiveNestedSampler(
        param_names=[f"p{i}" for i in range(n_dim)],
        loglike=loglike,
        transform=prior_cube,
        resume=True,
        log_dir=str(outdir),
    )

    run_kwargs = dict(min_num_live_points=400, min_ess=400)
    run_kwargs.update(kwargs)
    result = sampler.run(**run_kwargs)

    return {
        "logZ": float(result["logz"]),
        "logZerr": float(result["logzerr"]),
        "samples": result.get("samples", None),
        "posterior": result.get("weighted_samples", {}).get("points", None),
        "result": result,
    }
