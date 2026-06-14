from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class PriorConfig:
    """Flat prior configuration for G1 L0 MCMC."""
    Omega_m_min: float = 0.15
    Omega_m_max: float = 0.50
    h_min: float = 0.55
    h_max: float = 0.85
    ln10As_min: float = 2.5
    ln10As_max: float = 3.7
    sigma8_min: float = 0.6
    sigma8_max: float = 1.1
    q_min: float = 0.0
    q_max: float = 1.15
    kappa_min: float = 0.0
    kappa_max: float = 1.0

    @property
    def s_min(self) -> float:
        return 3.0 - self.q_max

    @property
    def s_max(self) -> float:
        return 3.0 - self.q_min


def in_range(x: float, lo: float, hi: float) -> bool:
    return bool(lo <= x <= hi)


class FlatPrior:
    """
    Flat prior in sampling coordinates.

    Common parameters:
        - Omega_m: total matter density
        - h: dimensionless Hubble constant
        - Either ln10As = ln(10^10 A_s) (primordial amplitude)
        - Or sigma8 (present-day rms amplitude)

    G1 parameters:
        - q: 3 - s (ΛCDM null at q=0)
        - kappa: Weyl response coupling
    """

    def __init__(self, amplitude_param: str = "ln10As", config: PriorConfig | None = None):
        if amplitude_param not in {"ln10As", "sigma8"}:
            raise ValueError(f"amplitude_param must be 'ln10As' or 'sigma8', got {amplitude_param}")

        self.amplitude_param = amplitude_param
        self.config = config or PriorConfig()

    def log_prior(self, params: dict[str, float]) -> float:
        """Evaluate log prior, returns -inf if out of bounds."""
        cfg = self.config

        if not in_range(params["Omega_m"], cfg.Omega_m_min, cfg.Omega_m_max):
            return -np.inf
        if not in_range(params["h"], cfg.h_min, cfg.h_max):
            return -np.inf

        if self.amplitude_param == "ln10As":
            if not in_range(params["ln10As"], cfg.ln10As_min, cfg.ln10As_max):
                return -np.inf
        else:
            if not in_range(params["sigma8"], cfg.sigma8_min, cfg.sigma8_max):
                return -np.inf

        if "q" in params:
            if not in_range(params["q"], cfg.q_min, cfg.q_max):
                return -np.inf

        if "kappa" in params:
            if not in_range(params["kappa"], cfg.kappa_min, cfg.kappa_max):
                return -np.inf

        return 0.0

    def param_names(self, model: str) -> list[str]:
        """Get parameter names for a given model."""
        common = ["Omega_m", "h", self.amplitude_param]

        if model == "lcdm":
            return common
        elif model == "g1_bg":
            return common + ["q"]
        elif model == "g1_m34":
            return common + ["q"]
        elif model == "g1_mkappa":
            return common + ["q", "kappa"]
        else:
            raise ValueError(f"Unknown model: {model}")

    def n_dim(self, model: str) -> int:
        return len(self.param_names(model))

    def array_to_dict(self, model: str, x: np.ndarray) -> dict[str, float]:
        """Convert parameter array to dict."""
        names = self.param_names(model)
        return dict(zip(names, x))

    def sample_prior(self, model: str, n: int = 1) -> np.ndarray:
        """Draw n samples uniformly from the prior."""
        names = self.param_names(model)
        cfg = self.config
        samples = []

        for _ in range(n):
            row = []
            for name in names:
                if name == "Omega_m":
                    row.append(np.random.uniform(cfg.Omega_m_min, cfg.Omega_m_max))
                elif name == "h":
                    row.append(np.random.uniform(cfg.h_min, cfg.h_max))
                elif name == "ln10As":
                    row.append(np.random.uniform(cfg.ln10As_min, cfg.ln10As_max))
                elif name == "sigma8":
                    row.append(np.random.uniform(cfg.sigma8_min, cfg.sigma8_max))
                elif name == "q":
                    row.append(np.random.uniform(cfg.q_min, cfg.q_max))
                elif name == "kappa":
                    row.append(np.random.uniform(cfg.kappa_min, cfg.kappa_max))
            samples.append(row)

        return np.array(samples)


def make_h_gaussian_prior(mean: float = 0.674, std: float = 0.008):
    """
    Create an external Gaussian prior on h for robustness runs.

    Usage: log_prior_total = prior.log_prior(params) + log_h_prior(params['h'])
    """
    def log_h_prior(h: float) -> float:
        return -0.5 * ((h - mean) / std) ** 2
    return log_h_prior
