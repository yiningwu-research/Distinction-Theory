from __future__ import annotations

import json
from pathlib import Path
import numpy as np

try:
    import emcee
    HAVE_EMCEE = True
except ImportError:
    HAVE_EMCEE = False

from .priors import FlatPrior
from .likelihood import LensingLikelihood


def gelman_rubin(chains: list[np.ndarray]) -> np.ndarray:
    """Compute Gelman-Rubin R-hat statistic for convergence."""
    n_chains = len(chains)
    n_steps, n_dim = chains[0].shape

    chain_means = [np.mean(c, axis=0) for c in chains]
    overall_mean = np.mean(chain_means, axis=0)

    B = n_steps / (n_chains - 1) * np.sum(
        [(cm - overall_mean) ** 2 for cm in chain_means], axis=0
    )

    W = np.mean(
        [np.sum((c - cm) ** 2, axis=0) / (n_steps - 1)
         for c, cm in zip(chains, chain_means)],
        axis=0,
    )

    var_hat = (n_steps - 1) / n_steps * W + B / n_steps
    R_hat = np.sqrt(var_hat / np.maximum(W, 1e-30))

    return R_hat


def effective_sample_size(chain: np.ndarray) -> np.ndarray:
    """Compute effective sample size using autocorrelation."""
    n_steps, n_dim = chain.shape
    ess = np.zeros(n_dim)

    for i in range(n_dim):
        x = chain[:, i]
        acf = emcee.autocorr.function_1d(x)

        tau = 1.0 + 2.0 * np.sum(acf[1:])
        ess[i] = n_steps / tau

    return ess


class MCMCSampler:
    """
    G1 L0 MCMC sampler using emcee.

    Supports 4 models:
        - lcdm:    {Omega_m, h, amplitude_param}
        - g1_bg:   {Omega_m, h, amplitude_param, q}        (kappa=0)
        - g1_m34:  {Omega_m, h, amplitude_param, q}        (kappa=0.75)
        - g1_mkappa: {Omega_m, h, amplitude_param, q, kappa} (both free)

    Always saves full unthinned chains.
    """

    def __init__(self, model: str, variant: str = "act_baseline",
                 amplitude_param: str = "ln10As", seed: int | None = None):
        if not HAVE_EMCEE:
            raise ImportError("emcee is required for MCMC")

        self.model = model
        self.variant = variant
        self.amplitude_param = amplitude_param
        self.seed = seed if seed is not None else np.random.randint(0, 2**31)

        np.random.seed(self.seed)

        self.prior = FlatPrior(amplitude_param=amplitude_param)
        self.like = LensingLikelihood(variant=variant, amplitude_param=amplitude_param)
        self.n_dim = self.prior.n_dim(model)

        self.sampler = None
        self._samples = None
        self._log_prob = None

    def _log_prob_fn(self, x: np.ndarray) -> float:
        params = self.prior.array_to_dict(self.model, x)

        if self.model == "g1_m34":
            params["kappa"] = 0.75
        elif self.model == "g1_bg":
            params["kappa"] = 0.0
        elif self.model == "lcdm":
            params["q"] = 0.0
            params["kappa"] = 0.0

        lp = self.prior.log_prior(params)
        if not np.isfinite(lp):
            return -np.inf

        return lp + self.like.log_likelihood(params)

    def run(self, n_walkers: int = 40, n_steps: int = 5000,
            burn_steps: int = 500, progress: bool = True,
            checkpoint_dir: Optional[Path] = None,
            checkpoint_every: int = 0) -> dict:
        """
        Run MCMC sampler.

        Parameters
        ----------
        checkpoint_dir : Path, optional
            If set, saves intermediate chain snapshots every checkpoint_every steps.
        checkpoint_every : int
            Save checkpoint this many production steps.
        """
        from pathlib import Path
        pos0 = self.prior.sample_prior(self.model, n_walkers)
        pos = pos0 + 1e-3 * np.random.randn(n_walkers, self.n_dim)

        self.sampler = emcee.EnsembleSampler(n_walkers, self.n_dim, self._log_prob_fn)

        if burn_steps > 0:
            pos, _, _ = self.sampler.run_mcmc(pos, burn_steps, progress=progress)
            self.sampler.reset()

        # Run production in chunks if checkpointing
        if checkpoint_dir is not None and checkpoint_every > 0:
            checkpoint_dir = Path(checkpoint_dir)
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            n_done = 0
            while n_done < n_steps:
                chunk = min(checkpoint_every, n_steps - n_done)
                pos, _, _ = self.sampler.run_mcmc(pos, chunk, progress=progress)
                n_done += chunk
                self._samples = self.sampler.get_chain(flat=False)
                self._log_prob = self.sampler.get_log_prob(flat=False)
                self.save(checkpoint_dir)
                if progress:
                    print(f"  checkpoint: {n_done}/{n_steps} steps saved")
        else:
            self.sampler.run_mcmc(pos, n_steps, progress=progress)

        self._samples = self.sampler.get_chain(flat=False)
        self._log_prob = self.sampler.get_log_prob(flat=False)

        tau = self.sampler.get_autocorr_time(tol=0)

        return {
            "n_walkers": n_walkers,
            "n_steps": n_steps,
            "burn_steps": burn_steps,
            "autocorr_times": tau.tolist(),
            "mean_tau": float(np.mean(tau)),
            "acceptance_fraction": float(np.mean(self.sampler.acceptance_fraction)),
            "seed": self.seed,
            "model": self.model,
            "variant": self.variant,
            "amplitude_param": self.amplitude_param,
            "param_names": self.prior.param_names(self.model),
        }

    def save(self, outdir: str | Path) -> None:
        """Save full unthinned chain and metadata."""
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        np.save(outdir / "samples_raw.npy", self._samples)
        np.save(outdir / "log_prob_raw.npy", self._log_prob)

        metadata = {
            "model": self.model,
            "variant": self.variant,
            "amplitude_param": self.amplitude_param,
            "param_names": self.prior.param_names(self.model),
            "seed": self.seed,
        }

        with open(outdir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def get_samples(self, burn: int | None = None, thin: int = 1, flat: bool = True):
        """Get samples with optional burn-in and thinning (for analysis only)."""
        if self._samples is None:
            raise RuntimeError("No samples available - run first")

        if burn is None:
            tau = self.sampler.get_autocorr_time(tol=0)
            burn = int(2 * np.max(tau))

        return self.sampler.get_chain(discard=burn, thin=thin, flat=flat)

    def get_log_prob(self, burn: int | None = None, thin: int = 1, flat: bool = True):
        """Get log prob with optional burn-in and thinning (for analysis only)."""
        if self._log_prob is None:
            raise RuntimeError("No samples available - run first")

        if burn is None:
            tau = self.sampler.get_autocorr_time(tol=0)
            burn = int(2 * np.max(tau))

        return self.sampler.get_log_prob(discard=burn, thin=thin, flat=flat)


def run_two_ensembles(model: str, variant: str, amplitude_param: str = "ln10As",
                      n_walkers: int = 40, n_steps: int = 5000,
                      burn_steps: int = 500) -> tuple:
    """
    Run TWO INDEPENDENT ENSEMBLES for convergence checking.

    IMPORTANT: Gelman-Rubin R-hat is computed BETWEEN ENSEMBLES,
    NOT between walkers within an ensemble. Walkers within an ensemble
    are coupled via the stretch move and not independent.

    Returns (sampler1, sampler2, convergence_diagnostics)
    """
    sampler1 = MCMCSampler(model, variant, amplitude_param, seed=None)
    sampler2 = MCMCSampler(model, variant, amplitude_param, seed=None)

    print(f"Running ensemble 1 for {model}/{variant}...")
    meta1 = sampler1.run(n_walkers, n_steps, burn_steps, progress=True)

    print(f"Running ensemble 2 for {model}/{variant}...")
    meta2 = sampler2.run(n_walkers, n_steps, burn_steps, progress=True)

    # Flatten within each ensemble (keeping ensembles separate)
    # Shape: (n_steps * n_walkers, n_params) for each ensemble
    samples1 = sampler1.get_samples(burn=burn_steps, flat=True)
    samples2 = sampler2.get_samples(burn=burn_steps, flat=True)

    # Downsample to 1000 samples each for R-hat (sufficient for convergence)
    idx1 = np.linspace(0, len(samples1) - 1, 1000, dtype=int)
    idx2 = np.linspace(0, len(samples2) - 1, 1000, dtype=int)

    # Rank-normalized Gelman-Rubin between the two independent ensembles
    from scipy.stats import rankdata
    n_dim = samples1.shape[1]
    R_hat = np.zeros(n_dim)

    for i in range(n_dim):
        combined = np.concatenate([samples1[idx1, i], samples2[idx2, i]])
        ranks = rankdata(combined)

        z1 = ranks[:1000]
        z2 = ranks[1000:]

        B = 1000 * (np.mean(z1) - np.mean(combined))**2 + \
            1000 * (np.mean(z2) - np.mean(combined))**2
        W = 0.5 * (np.var(z1, ddof=1) + np.var(z2, ddof=1))

        var_hat = (1000 - 1) / 1000 * W + B / 1000
        R_hat[i] = np.sqrt(var_hat / W)

    convergence = {
        "R_hat_between_ensembles": R_hat.tolist(),
        "R_hat_max": float(np.max(R_hat)),
        "passed_R_hat_lt_101": bool(np.max(R_hat) < 1.01),
        "note": "R-hat computed between independent ensembles, not walkers",
    }

    return sampler1, sampler2, convergence
