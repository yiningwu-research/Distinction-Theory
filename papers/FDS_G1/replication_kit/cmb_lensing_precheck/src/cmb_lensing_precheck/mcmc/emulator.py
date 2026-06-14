from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import RBFInterpolator

from .ratio_engine import G1LensingRatio


def _latin_hypercube(n_samples: int, n_dim: int) -> np.ndarray:
    """Generate Latin hypercube samples in [0, 1]^n_dim."""
    samples = np.zeros((n_samples, n_dim))
    for i in range(n_dim):
        samples[:, i] = np.random.permutation(n_samples) / n_samples + np.random.rand(n_samples) / n_samples
    return samples


@dataclass
class EmulatorConfig:
    n_train: int = 400
    n_test: int = 150
    n_pca_components_min: int = 3
    n_pca_components_max: int = 15
    rbf_kernel: str = "thin_plate_spline"
    rms_tol_pct: float = 0.2
    p95_tol_pct: float = 0.5
    delta_chi2_tol: float = 0.1

    # Parameter ranges (match PriorConfig)
    Omega_m_min: float = 0.15
    Omega_m_max: float = 0.50
    h_min: float = 0.55
    h_max: float = 0.85
    q_min: float = 0.0
    q_max: float = 1.15
    kappa_min: float = 0.0
    kappa_max: float = 1.0


class RatioEmulator:
    """
    PCA-based emulator for G1 lensing ratio R_L(Omega_m, h, q, kappa).

    Trained on log(R_L) for better interpolation behavior.
    Uses RBF interpolation for PCA coefficients.
    """

    def __init__(self, amplitude_mode: str = "primordial",
                 config: EmulatorConfig | None = None):
        self.amplitude_mode = amplitude_mode
        self.config = config or EmulatorConfig()
        self.ratio_engine = G1LensingRatio(amplitude_mode=amplitude_mode)

        self.pca_mean = None
        self.pca_components = None
        self.interpolators = None
        self.ell = None

        self.training_params = None
        self.training_logR = None
        self.test_params = None
        self.test_logR = None

    def _params_to_unit(self, params: np.ndarray) -> np.ndarray:
        """Convert physical params to unit cube [0,1]^4."""
        cfg = self.config
        unit = np.zeros_like(params, dtype=float)

        unit[:, 0] = (params[:, 0] - cfg.Omega_m_min) / (cfg.Omega_m_max - cfg.Omega_m_min)
        unit[:, 1] = (params[:, 1] - cfg.h_min) / (cfg.h_max - cfg.h_min)
        unit[:, 2] = (params[:, 2] - cfg.q_min) / (cfg.q_max - cfg.q_min)
        unit[:, 3] = (params[:, 3] - cfg.kappa_min) / (cfg.kappa_max - cfg.kappa_min)

        return np.clip(unit, 0.0, 1.0)

    def _sample_params(self, n: int) -> np.ndarray:
        """Sample parameters from prior using Latin hypercube."""
        cfg = self.config
        unit = _latin_hypercube(n, 4)

        params = np.zeros_like(unit)
        params[:, 0] = unit[:, 0] * (cfg.Omega_m_max - cfg.Omega_m_min) + cfg.Omega_m_min
        params[:, 1] = unit[:, 1] * (cfg.h_max - cfg.h_min) + cfg.h_min
        params[:, 2] = unit[:, 2] * (cfg.q_max - cfg.q_min) + cfg.q_min
        params[:, 3] = unit[:, 3] * (cfg.kappa_max - cfg.kappa_min) + cfg.kappa_min

        return params

    def generate_training_data(self) -> None:
        """Generate training and test sets using the exact ratio engine."""
        print(f"Generating {self.config.n_train} training samples...")
        train_params = self._sample_params(self.config.n_train)
        train_logR = []

        for i, (Omega_m, h, q, kappa) in enumerate(train_params):
            if i % 50 == 0:
                print(f"  Computing {i}/{self.config.n_train}...")
            s = 3.0 - q
            result = self.ratio_engine.compute(Omega_m, h, s, kappa)
            train_logR.append(np.log(result.R_total))

        self.training_params = train_params
        self.training_logR = np.array(train_logR)
        self.ell = result.ell

        print(f"Generating {self.config.n_test} test samples...")
        test_params = self._sample_params(self.config.n_test)
        test_logR = []

        for Omega_m, h, q, kappa in test_params:
            s = 3.0 - q
            result = self.ratio_engine.compute(Omega_m, h, s, kappa)
            test_logR.append(np.log(result.R_total))

        self.test_params = test_params
        self.test_logR = np.array(test_logR)

        print("Done generating data.")

    def train(self, validate_likelihood: bool = True) -> dict:
        """
        Train PCA + RBF emulator with ADAPTIVE component selection.

        Selects the minimum number of PCA components that satisfies:
            1. RMS < 0.2%
            2. P95 < 0.5%

        Returns full validation metrics including likelihood-level error.
        """
        if self.training_logR is None:
            self.generate_training_data()

        logR = self.training_logR
        self.pca_mean = np.mean(logR, axis=0)
        logR_centered = logR - self.pca_mean

        U, S, Vt = np.linalg.svd(logR_centered, full_matrices=False)
        train_unit = self._params_to_unit(self.training_params)

        best_n = None
        best_metrics = None
        best_interp = None
        best_components = None

        for n in range(self.config.n_pca_components_min,
                       self.config.n_pca_components_max + 1):
            components = Vt[:n]
            coeffs = logR_centered @ components.T

            interpolators = []
            for i in range(n):
                interp = RBFInterpolator(train_unit, coeffs[:, i],
                                         kernel=self.config.rbf_kernel)
                interpolators.append(interp)

            self.pca_components = components
            self.interpolators = interpolators

            metrics = self.validate(likelihood=False)

            if (metrics["rms_pct"] < self.config.rms_tol_pct and
                metrics["p95_pct"] < self.config.p95_tol_pct):
                best_n = n
                best_metrics = metrics
                best_interp = interpolators
                best_components = components
                print(f"  n_pca={n}: PASSED (RMS={metrics['rms_pct']:.3f}%, "
                      f"P95={metrics['p95_pct']:.3f}%)")
                break
            else:
                print(f"  n_pca={n}: FAILED (RMS={metrics['rms_pct']:.3f}%, "
                      f"P95={metrics['p95_pct']:.3f}%)")

        if best_n is None:
            best_n = self.config.n_pca_components_max
            self.pca_components = Vt[:best_n]
            coeffs = logR_centered @ self.pca_components.T
            self.interpolators = []
            for i in range(best_n):
                interp = RBFInterpolator(train_unit, coeffs[:, i],
                                         kernel=self.config.rbf_kernel)
                self.interpolators.append(interp)
            best_metrics = self.validate(likelihood=False)

        self.n_pca_used = best_n

        final_metrics = self.validate(likelihood=validate_likelihood)
        return final_metrics

    def __call__(self, params: np.ndarray) -> np.ndarray:
        """Emulate log(R_L) for given parameters. Shape (n_samples, n_ell)."""
        if params.ndim == 1:
            params = params.reshape(1, -1)

        unit = self._params_to_unit(params)
        n_comp = self.pca_components.shape[0]

        coeffs_pred = np.zeros((len(unit), n_comp))
        for i, interp in enumerate(self.interpolators):
            coeffs_pred[:, i] = interp(unit)

        logR_pred = coeffs_pred @ self.pca_components + self.pca_mean
        return logR_pred

    def predict_R(self, Omega_m: float, h: float, q: float, kappa: float) -> np.ndarray:
        """Predict R_L for a single parameter point."""
        params = np.array([[Omega_m, h, q, kappa]])
        logR_pred = self(params)
        return np.exp(logR_pred[0])

    def validate(self, likelihood: bool = True) -> dict:
        """
        Run held-out validation. Returns error metrics.

        Parameters
        ----------
        likelihood : bool
            If True, also compute likelihood-level Δχ² error
        """
        if self.test_logR is None:
            raise RuntimeError("No test data - call generate_training_data first")

        logR_pred = self(self.test_params)
        logR_true = self.test_logR

        frac_error = (np.exp(logR_pred) - np.exp(logR_true)) / np.maximum(np.exp(logR_true), 1e-30)

        rms_by_L = np.sqrt(np.mean(frac_error ** 2, axis=0))
        rms_global = np.sqrt(np.mean(frac_error ** 2)) * 100
        p95_global = np.percentile(np.abs(frac_error), 95) * 100

        metrics = {
            "n_pca_components": getattr(self, "n_pca_used", self.pca_components.shape[0]),
            "rms_pct": float(rms_global),
            "p95_pct": float(p95_global),
            "max_abs_pct": float(np.max(np.abs(frac_error)) * 100),
            "rms_by_L_pct": rms_by_L.tolist(),
            "passed_rms": bool(rms_global < self.config.rms_tol_pct),
            "passed_p95": bool(p95_global < self.config.p95_tol_pct),
        }

        # ACT-relevant multipole range diagnostics (L ~ 50-750)
        if self.ell is not None:
            act_mask = (self.ell >= 50) & (self.ell <= 750)
            if np.any(act_mask):
                act_err = frac_error[:, act_mask]
                metrics["rms_act_range_pct"] = float(np.sqrt(np.mean(act_err**2)) * 100)
                metrics["p95_act_range_pct"] = float(np.percentile(np.abs(act_err), 95) * 100)

        if likelihood:
            delta_chi2 = self._validate_likelihood_level()
            metrics.update(delta_chi2)
            metrics["passed_delta_chi2"] = bool(
                metrics["delta_chi2_rms"] < self.config.delta_chi2_tol)
            metrics["passed_all"] = bool(
                metrics["passed_rms"] and metrics["passed_p95"] and metrics["passed_delta_chi2"])
        else:
            metrics["passed_all"] = bool(metrics["passed_rms"] and metrics["passed_p95"])

        return metrics

    def _validate_likelihood_level(self) -> dict:
        """
        Likelihood-level validation: compute Δχ² for random points.
        This is the critical gate - spectrum-level error doesn't guarantee
        covariance-weighted likelihood error is small.

        Uses fixed ln10As=3.0 to focus validation on R_L ratios only.
        """
        import act_dr6_lenslike as alike

        test_params = self.test_params
        delta_chi2 = []

        act_data = alike.load_data("act_baseline")
        ell_full = np.arange(act_data["binmat_act"].shape[1], dtype=int)
        data_vec = act_data["data_binned_clkk"]
        binmat = act_data["binmat_act"]
        cinv = act_data["cinv"]

        from .likelihood import LensingLikelihood

        like = LensingLikelihood("act_baseline", amplitude_param="ln10As")

        for Omega_m, h, q, kappa in test_params:
            s = 3.0 - q

            clkk_lcdm = like._compute_clkk_lcdm(Omega_m, h, ln10As=3.0)
            if clkk_lcdm is None:
                continue

            result = self.ratio_engine.compute(Omega_m, h, s, kappa)

            # Continuous interpolation to full ell grid (NOT step-filling)
            # R_L outside ratio engine range extrapolates to 1.0 (superhorizon / far tail)
            R_true = np.interp(
                ell_full.astype(float), result.ell.astype(float), result.R_total,
                left=1.0, right=1.0,
            )
            clkk_g1_true = clkk_lcdm * R_true

            R_emu_raw = self.predict_R(Omega_m, h, q, kappa)
            R_emu = np.interp(
                ell_full.astype(float), result.ell.astype(float), R_emu_raw,
                left=1.0, right=1.0,
            )
            clkk_g1_emu = clkk_lcdm * R_emu

            chi2_true = float((data_vec - binmat @ clkk_g1_true)
                             @ cinv @ (data_vec - binmat @ clkk_g1_true))
            chi2_emu = float((data_vec - binmat @ clkk_g1_emu)
                            @ cinv @ (data_vec - binmat @ clkk_g1_emu))

            delta_chi2.append(abs(chi2_true - chi2_emu))

        if not delta_chi2:
            return {"delta_chi2_rms": 0.0, "delta_chi2_p95": 0.0, "delta_chi2_max": 0.0}

        delta_chi2 = np.array(delta_chi2)
        return {
            "delta_chi2_rms": float(np.sqrt(np.mean(delta_chi2**2))),
            "delta_chi2_p95": float(np.percentile(delta_chi2, 95)),
            "delta_chi2_max": float(np.max(delta_chi2)),
        }

    def save(self, path: str | Path) -> None:
        """Save emulator to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        np.save(path / "pca_mean.npy", self.pca_mean)
        np.save(path / "pca_components.npy", self.pca_components)
        np.save(path / "training_params.npy", self.training_params)
        np.save(path / "training_logR.npy", self.training_logR)
        np.save(path / "test_params.npy", self.test_params)
        np.save(path / "test_logR.npy", self.test_logR)
        if self.ell is not None:
            np.save(path / "ell.npy", self.ell)

        with open(path / "config.json", "w") as f:
            json.dump({
                "amplitude_mode": self.amplitude_mode,
                "n_pca_used": self.n_pca_used,
                "rbf_kernel": self.config.rbf_kernel,
                "epsilon": getattr(self, "_epsilon", None),
                "smoothing": getattr(self, "_smoothing", 0.0),
            }, f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "RatioEmulator":
        """Load emulator from disk with full round-trip integrity."""
        path = Path(path)

        with open(path / "config.json") as f:
            cfg_data = json.load(f)

        kernel   = cfg_data.get("rbf_kernel", "thin_plate_spline")
        n_pca    = cfg_data.get("n_pca_used", cfg_data.get("n_pca_components", 4))
        epsilon  = cfg_data.get("epsilon", None)
        smoothing = cfg_data.get("smoothing", 0.0)

        config = EmulatorConfig(rbf_kernel=kernel)

        emulator = cls(amplitude_mode=cfg_data["amplitude_mode"], config=config)
        emulator._epsilon  = epsilon
        emulator._smoothing = smoothing
        emulator.pca_mean = np.load(path / "pca_mean.npy")
        emulator.pca_components = np.load(path / "pca_components.npy")
        emulator.n_pca_used = int(n_pca)
        emulator.training_params = np.load(path / "training_params.npy")
        emulator.training_logR   = np.load(path / "training_logR.npy")
        emulator.test_params     = np.load(path / "test_params.npy")
        emulator.test_logR       = np.load(path / "test_logR.npy")

        ell_path = path / "ell.npy"
        emulator.ell = np.load(ell_path) if ell_path.exists() else None

        train_unit = emulator._params_to_unit(emulator.training_params)
        coeffs = (emulator.training_logR - emulator.pca_mean) @ emulator.pca_components.T

        rbf_kw = {"kernel": kernel, "smoothing": smoothing}
        if kernel not in {"linear", "thin_plate_spline", "cubic", "quintic"}:
            if epsilon is not None:
                rbf_kw["epsilon"] = epsilon

        emulator.interpolators = []
        for i in range(emulator.n_pca_used):
            emulator.interpolators.append(
                RBFInterpolator(train_unit, coeffs[:, i], **rbf_kw)
            )
        return emulator


def learning_curve(amplitude_mode: str = "primordial",
                   n_train_list: "list[int] | None" = None) -> dict:
    """Test emulator accuracy vs training set size."""
    if n_train_list is None:
        n_train_list = [100, 200, 400, 800]

    results = {}
    for n_train in n_train_list:
        print(f"\nTesting n_train = {n_train}")
        config = EmulatorConfig(n_train=n_train, n_test=100)
        emulator = RatioEmulator(amplitude_mode=amplitude_mode, config=config)
        metrics = emulator.train()
        results[n_train] = metrics
        print(f"  RMS: {metrics['rms_pct']:.3f}%, P95: {metrics['p95_pct']:.3f}%")

    return results
