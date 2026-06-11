from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator

C_KM_S = 299792.458


@dataclass(frozen=True)
class Background:
    H0: float
    omega_m: float
    omega_r: float
    s: float
    model_name: str

    @property
    def omega_de(self) -> float:
        return 1.0 - self.omega_m - self.omega_r

    def e2_a(self, a: np.ndarray | float) -> np.ndarray:
        a = np.asarray(a, dtype=float)
        matter = self.omega_m * a ** -3
        radiation = self.omega_r * a ** -4
        if self.model_name == "lcdm":
            dark = self.omega_de * np.ones_like(a)
        else:
            dark = self.omega_de * a ** (self.s - 3.0)
        return matter + radiation + dark

    def e_a(self, a: np.ndarray | float) -> np.ndarray:
        return np.sqrt(self.e2_a(a))

    def e_z(self, z: np.ndarray | float) -> np.ndarray:
        return self.e_a(1.0 / (1.0 + np.asarray(z, dtype=float)))

    def H_z(self, z: np.ndarray | float) -> np.ndarray:
        return self.H0 * self.e_z(z)

    def dlnH_dlna(self, a: np.ndarray | float) -> np.ndarray:
        a = np.asarray(a, dtype=float)
        e2 = self.e2_a(a)
        deriv = -3.0 * self.omega_m * a ** -3 - 4.0 * self.omega_r * a ** -4
        if self.model_name != "lcdm":
            deriv += (self.s - 3.0) * self.omega_de * a ** (self.s - 3.0)
        return 0.5 * deriv / e2

    def omega_m_a(self, a: np.ndarray | float) -> np.ndarray:
        a = np.asarray(a, dtype=float)
        return self.omega_m * a ** -3 / self.e2_a(a)

    def comoving_distance_interpolator(self, z_max: float, n_z: int = 1000) -> PchipInterpolator:
        if z_max <= 0:
            raise ValueError("z_max must be positive.")
        u = np.linspace(0.0, np.log1p(z_max), int(n_z))
        z = np.expm1(u)
        integrand = C_KM_S / self.H_z(z)
        chi = cumulative_trapezoid(integrand, z, initial=0.0)
        return PchipInterpolator(z, chi, extrapolate=False)


def make_background(cfg: dict, model_name: str | None = None) -> Background:
    c = cfg["cosmology"]
    m = cfg["model"]
    name = model_name or m["name"]
    return Background(
        H0=float(c["H0"]),
        omega_m=float(c["Omega_m"]),
        omega_r=float(c["Omega_r"]),
        s=float(m["s"]),
        model_name=name,
    )
