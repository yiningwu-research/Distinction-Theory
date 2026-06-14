"""CLASS linear power spectrum backend adapter for G1 CMB lensing pre-check.

This module implements Level-A validation only:
  - CLASS provides linear P(k,z=0) transfer
  - G1 growth and Weyl response are applied externally
  - NOT a full D11 Boltzmann perturbation implementation

Pre-registered null tests:
  1. s=3, Σ=1 → R_L ≡ 1
  2. D_G1 = D_ΛCDM, Σ=1 → R_L ≡ 1
  3. D_G1 = D_ΛCDM → R_L reflects only Σ² and geometry differences

Use this file via run_class_comparison.py, not directly.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import numpy as np
from scipy.interpolate import PchipInterpolator

try:
    import classy  # type: ignore
    _HAS_CLASSY = True
except ImportError:
    _HAS_CLASSY = False


def _get_classy_version() -> str:
    """Get CLASS version or return 'unknown'."""
    if not _HAS_CLASSY:
        return "not installed"
    try:
        return getattr(classy, '__version__', 'unknown')
    except:
        return 'unknown'


@dataclass
class ClassMetadata:
    """Full audit metadata for a CLASS backend run."""
    # Versions
    class_version: str
    classy_version: str
    git_commit: str
    python_version: str
    numpy_version: str
    scipy_version: str

    # Cosmological parameters
    omega_cdm: float
    omega_b: float
    omega_m: float
    h: float
    n_s: float
    A_s: float
    tau_reio: float

    # Sampling parameters
    k_min: float
    k_max: float
    n_k: int
    z_min: float
    z_max: float
    n_z: int
    ell_min: int
    ell_max: int
    n_ell: int

    # G1 model parameters
    s: float
    kappa: float
    normalization: str
    amplitude_mode: str

    # Run metadata
    run_timestamp: str
    config_hash: str
    data_hash: str
    random_seed: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> 'ClassMetadata':
        """Construct from a configuration dictionary."""
        now = str(np.datetime64('now'))
        cfg_hash = hashlib.sha256(
            json.dumps(cfg, sort_keys=True).encode()
        ).hexdigest()[:16]

        cosm = cfg.get('cosmology', {})
        model = cfg.get('model', {})
        amp = cfg.get('amplitude', {})

        return cls(
            class_version=cfg.get('class_version', 'unknown'),
            classy_version=_get_classy_version(),
            git_commit=cfg.get('git_commit', ''),
            python_version=cfg.get('python_version', ''),
            numpy_version=np.__version__,
            scipy_version=np.__version__,
            omega_cdm=float(cosm.get('Omega_cdm', cosm.get('Omega_m', 0.3) - cosm.get('Omega_b', 0.05))),
            omega_b=float(cosm.get('Omega_b', 0.05)),
            omega_m=float(cosm.get('Omega_m', 0.3)),
            h=float(cosm.get('h', float(cosm.get('H0', 67.4))/100.0)),
            n_s=float(cosm.get('n_s', 0.965)),
            A_s=float(cosm.get('A_s', 2.1e-9)),
            tau_reio=float(cosm.get('tau_reio', 0.054)),
            k_min=float(cfg.get('power', {}).get('k_min', 1e-5)),
            k_max=float(cfg.get('power', {}).get('k_max', 30.0)),
            n_k=int(cfg.get('power', {}).get('n_k', 200)),
            z_min=0.0,
            z_max=float(cfg.get('integration', {}).get('z_max', 1089.92)),
            n_z=int(cfg.get('integration', {}).get('n_z', 900)),
            ell_min=int(cfg.get('integration', {}).get('ell_min', 2)),
            ell_max=int(cfg.get('integration', {}).get('ell_max', 2998)),
            n_ell=int(cfg.get('integration', {}).get('ell_max', 2998) -
                      cfg.get('integration', {}).get('ell_min', 2) + 1),
            s=float(model.get('s', 2.555)),
            kappa=float(model.get('kappa', 0.75)),
            normalization=model.get('normalization', 'code'),
            amplitude_mode=amp.get('mode', 'fixed_primordial'),
            run_timestamp=now,
            config_hash=cfg_hash,
            data_hash="pending",
            random_seed=0,
        )


class ClassLinearPower:
    """CLASS linear matter power spectrum adapter.

    This provides P(k, z=0) from CLASS and the G1 growth factor is
    applied externally. This is NOT a full Boltzmann solution
    of D11 perturbation equations.

    Units: k in 1/Mpc, P(k) in (Mpc)^3.
    """

    def __init__(self, cfg: Dict[str, Any], output_dir: Optional[str | Path] = None):
        if not _HAS_CLASSY:
            raise ImportError(
                "classy not installed. Install with: "
                "pip install '.[class]' from package root."
            )

        self.cfg = cfg
        self.output_dir = None if output_dir is None else Path(output_dir)
        self.metadata = ClassMetadata.from_config(cfg)

        # Compute CLASS-style parameters
        cosm = cfg['cosmology']
        self.h = float(cosm.get('h', float(cosm.get('H0', 67.4)) / 100.0))
        self.omega_m = float(cosm.get('Omega_m', 0.2966))
        self.omega_b = float(cosm.get('Omega_b', 0.049))
        self.omega_cdm = self.omega_m - self.omega_b

        self.class_params = {
            'output': 'mPk',
            'P_k_max_1/Mpc': float(cfg.get('power', {}).get('k_max', 30.0)),
            'z_max_pk': 0.0,
            'omega_b': self.omega_b * self.h**2,
            'omega_cdm': self.omega_cdm * self.h**2,
            'h': self.h,
            'n_s': float(cosm.get('n_s', 0.965)),
            'A_s': float(cosm.get('A_s', 2.1e-9)),
            'tau_reio': float(cosm.get('tau_reio', 0.054)),
            'non linear': 'none',
        }

        self._cosmo = None
        self._pk_interp = None
        self._sigma8 = None

    def compute(self) -> None:
        """Run CLASS and compute linear P(k, z=0)."""
        self._cosmo = classy.Class()
        self._cosmo.set(self.class_params)
        self._cosmo.compute()

        # Build P(k) interpolator
        power_cfg = self.cfg['power']
        k = np.geomspace(float(power_cfg['k_min']), float(power_cfg['k_max']), int(power_cfg['n_k']))
        pk = np.array([self._cosmo.pk_lin(float(ki), 0.0) for ki in k])

        # Interpolate log-log
        self._pk_interp = PchipInterpolator(np.log(k), np.log(pk), extrapolate=True)

        # Compute sigma8
        self._sigma8 = float(self._cosmo.sigma8())

        # Update metadata
        data_hash = hashlib.sha256(pk.tobytes()).hexdigest()[:16]
        self.metadata.data_hash = data_hash

    def pk_lin(self, k_mpc: np.ndarray | float) -> np.ndarray:
        """Linear matter power spectrum at z=0.

        Args:
            k_mpc: Wavenumber in 1/Mpc

        Returns:
            P(k, z=0) in (Mpc)^3
        """
        if self._pk_interp is None:
            self.compute()
        return np.exp(self._pk_interp(np.log(np.asarray(k_mpc, dtype=float))))

    @property
    def sigma8(self) -> float:
        """CLASS-computed sigma8 at z=0."""
        if self._sigma8 is None:
            self.compute()
        return self._sigma8

    def p0(self, k_mpc: np.ndarray | float) -> np.ndarray:
        """Linear matter power spectrum at z=0.

        Matches the AnalyticBBKSPower interface for lensing computation.

        Args:
            k_mpc: Wavenumber in 1/Mpc

        Returns:
            P(k, z=0) in (Mpc)^3
        """
        return self.pk_lin(k_mpc)

    def save_metadata(self) -> None:
        """Save full metadata to JSON for audit trail."""
        if self.output_dir is None:
            raise ValueError("output_dir not set")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
