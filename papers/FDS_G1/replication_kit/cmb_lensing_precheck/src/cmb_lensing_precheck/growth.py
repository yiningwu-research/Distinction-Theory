from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

from .background import Background


@dataclass
class GrowthSolution:
    a_grid: np.ndarray
    delta_grid: np.ndarray
    ddelta_dN_grid: np.ndarray

    def __post_init__(self) -> None:
        self._delta = PchipInterpolator(self.a_grid, self.delta_grid, extrapolate=False)
        self._vel = PchipInterpolator(self.a_grid, self.ddelta_dN_grid, extrapolate=False)

    @property
    def delta_today(self) -> float:
        return float(self.delta_grid[-1])

    def delta(self, a: np.ndarray | float) -> np.ndarray:
        return np.asarray(self._delta(a), dtype=float)

    def D(self, a: np.ndarray | float) -> np.ndarray:
        return self.delta(a) / self.delta_today

    def f(self, a: np.ndarray | float) -> np.ndarray:
        d = self.delta(a)
        return np.asarray(self._vel(a), dtype=float) / d


def solve_growth(background: Background, a_ini: float, n_a: int = 1400) -> GrowthSolution:
    """Solve scale-independent linear growth with mu=1 from a common early amplitude."""
    n_ini = float(np.log(a_ini))
    n_eval = np.linspace(n_ini, 0.0, int(n_a))

    def rhs(n: float, y: np.ndarray) -> tuple[float, float]:
        a = np.exp(n)
        delta, vel = y
        friction = 2.0 + float(background.dlnH_dlna(a))
        source = 1.5 * float(background.omega_m_a(a))
        return vel, -friction * vel + source * delta

    y0 = np.array([a_ini, a_ini], dtype=float)
    sol = solve_ivp(rhs, (n_ini, 0.0), y0, t_eval=n_eval, rtol=2e-9, atol=1e-11)
    if not sol.success:
        raise RuntimeError(f"Growth integration failed: {sol.message}")
    return GrowthSolution(np.exp(sol.t), sol.y[0], sol.y[1])
