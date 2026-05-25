#!/usr/bin/env python3
"""Reference distance calculations."""

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator


def comoving_distance_z(z, E_func, z_grid_size=1600):
    """Comoving distance D_c(z) = integral_0^z dz'/E(z').

    Parameters
    ----------
    z : array-like
        Redshifts at which to evaluate D_c.
    E_func : callable
        Function E(z) returning H(z)/H0.
    z_grid_size : int
        Number of points in integration grid (default 1600).

    Returns
    -------
    D_c(z) in units of c/H0.
    """
    z = np.asarray(z, dtype=float)
    z_max = max(2.0, float(np.max(z)) * 1.05 + 0.01)
    z_grid = np.linspace(0.0, z_max, z_grid_size)
    E = np.asarray(E_func(z_grid), dtype=float)
    if np.any(~np.isfinite(E)) or np.any(E <= 0):
        return None
    dc_grid = cumulative_trapezoid(1.0 / E, z_grid, initial=0.0)
    interp = PchipInterpolator(z_grid, dc_grid, extrapolate=True)
    return interp(z)
