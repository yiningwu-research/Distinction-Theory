"""FDS-G1 CMB-lensing pre-production stress test."""

__version__ = "0.1.0"

from .config import load_config
from .pipeline import run_precheck

__all__ = ["load_config", "run_precheck"]
