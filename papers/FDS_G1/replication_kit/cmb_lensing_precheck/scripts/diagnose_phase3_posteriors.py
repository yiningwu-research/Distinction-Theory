#!/usr/bin/env python3
"""Rank-normalized posterior diagnostics for frozen Phase 3 chains."""

from __future__ import annotations

import json
import argparse
from pathlib import Path

import numpy as np
from scipy.stats import norm, rankdata


ROOT = Path(__file__).resolve().parents[1]
CHAIN_ROOT = ROOT / "outputs" / "frozen" / "v4_act_only" / "chains"
OUT = ROOT / "outputs" / "phase3_posterior_diagnostics.json"

MODELS = {
    "lcdm": ["Omega_m", "h", "ln10As"],
    "g1_bg": ["Omega_m", "h", "ln10As", "q"],
    "g1_m34": ["Omega_m", "h", "ln10As", "q"],
    "g1_mkappa": ["Omega_m", "h", "ln10As", "q", "kappa"],
}

BOUNDS = {
    "Omega_m": (0.15, 0.50),
    "h": (0.55, 0.85),
    "ln10As": (2.50, 3.70),
    "q": (0.00, 1.15),
    "kappa": (0.00, 1.00),
}


def load_seed_chain(chain_root: Path, model: str, seed: int, burn: int) -> np.ndarray:
    path = chain_root / model / f"seed_{seed}" / "samples_raw.npy"
    chain = np.load(path)
    return chain[burn:].reshape(-1, chain.shape[-1])


def rank_normalize(x: np.ndarray) -> np.ndarray:
    flat = x.reshape(-1)
    ranks = rankdata(flat, method="average")
    z = norm.ppf((ranks - 0.5) / len(flat))
    return z.reshape(x.shape)


def split_chains(x: np.ndarray) -> np.ndarray:
    """Split chain axis data from (chains, draws) to (2*chains, draws/2)."""
    n_chains, n_draws = x.shape
    half = n_draws // 2
    trimmed = x[:, : 2 * half]
    return trimmed.reshape(n_chains, 2, half).swapaxes(1, 0).reshape(2 * n_chains, half)


def basic_rhat(x: np.ndarray) -> float:
    chains = split_chains(x)
    m, n = chains.shape
    chain_means = np.mean(chains, axis=1)
    chain_vars = np.var(chains, axis=1, ddof=1)
    W = np.mean(chain_vars)
    B = n * np.var(chain_means, ddof=1)
    var_hat = (n - 1) / n * W + B / n
    return float(np.sqrt(var_hat / max(W, 1e-300)))


def rank_split_rhat_parts(x: np.ndarray) -> tuple[float, float, float]:
    z = rank_normalize(x)
    folded = rank_normalize(np.abs(x - np.median(x)))
    rank = basic_rhat(z)
    folded_rank = basic_rhat(folded)
    return max(rank, folded_rank), rank, folded_rank


def autocorr_1d(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=float) - np.mean(x)
    n = len(y)
    if n < 2:
        return np.ones(1)
    size = 1 << (2 * n - 1).bit_length()
    fft = np.fft.rfft(y, size)
    acov = np.fft.irfft(fft * np.conjugate(fft), size)[:n]
    acov /= np.arange(n, 0, -1)
    if acov[0] <= 0:
        return np.ones(n)
    return acov / acov[0]


def ess_from_chains(x: np.ndarray) -> float:
    chains = np.asarray(x, dtype=float)
    m, n = chains.shape
    if m * n <= 1:
        return float(m * n)
    rho = np.mean([autocorr_1d(chain) for chain in chains], axis=0)
    tau = 1.0
    for t in range(1, len(rho) - 1, 2):
        pair = rho[t] + rho[t + 1]
        if pair < 0:
            break
        tau += 2.0 * pair
    return float(min(m * n, max(1.0, m * n / max(tau, 1e-300))))


def bulk_tail_ess(x: np.ndarray) -> tuple[float, float]:
    z = rank_normalize(x)
    bulk = ess_from_chains(z)
    flat = x.reshape(-1)
    q05, q95 = np.percentile(flat, [5, 95])
    ess_low = ess_from_chains((x <= q05).astype(float))
    ess_high = ess_from_chains((x >= q95).astype(float))
    return bulk, min(ess_low, ess_high)


def parameter_diagnostics(chains: np.ndarray, names: list[str]) -> dict:
    out = {}
    for i, name in enumerate(names):
        x = chains[:, :, i]
        flat = x.reshape(-1)
        bulk, tail = bulk_tail_ess(x)
        lo, hi = BOUNDS[name]
        width = hi - lo
        rhat, rank_rhat, folded_rhat = rank_split_rhat_parts(x)
        out[name] = {
            "rank_split_rhat": rhat,
            "rank_rhat": rank_rhat,
            "folded_rank_rhat": folded_rhat,
            "bulk_ess": bulk,
            "tail_ess": tail,
            "boundary_fraction": float(np.mean((flat <= lo + 0.01 * width) | (flat >= hi - 0.01 * width))),
            "median": float(np.median(flat)),
            "q16": float(np.percentile(flat, 16)),
            "q84": float(np.percentile(flat, 84)),
        }
    return out


def cross_seed_tension(seed_chains: list[np.ndarray], names: list[str]) -> dict:
    out = {}
    for i, name in enumerate(names):
        seed_values = [chain[:, i] for chain in seed_chains]
        med = [np.median(v) for v in seed_values]
        half_widths = [(np.percentile(v, 84) - np.percentile(v, 16)) / 2.0 for v in seed_values]
        pooled = float(np.sqrt(np.mean(np.square(half_widths))))
        out[name] = {
            "seed_medians": [float(x) for x in med],
            "pooled_half_width": pooled,
            "T": float(abs(med[0] - med[1]) / max(pooled, 1e-300)),
        }
    return out


def add_alpha(chains: np.ndarray, seed_chains: list[np.ndarray], names: list[str], diagnostics: dict) -> None:
    if "q" not in names or "kappa" not in names:
        return
    qi, ki = names.index("q"), names.index("kappa")
    alpha_chains = chains[:, :, qi] * chains[:, :, ki]
    bulk, tail = bulk_tail_ess(alpha_chains)
    flat = alpha_chains.reshape(-1)
    rhat, rank_rhat, folded_rhat = rank_split_rhat_parts(alpha_chains)
    diagnostics["alpha"] = {
        "rank_split_rhat": rhat,
        "rank_rhat": rank_rhat,
        "folded_rank_rhat": folded_rhat,
        "bulk_ess": bulk,
        "tail_ess": tail,
        "median": float(np.median(flat)),
        "q16": float(np.percentile(flat, 16)),
        "q84": float(np.percentile(flat, 84)),
    }
    seed_alpha = [chain[:, qi] * chain[:, ki] for chain in seed_chains]
    med = [np.median(v) for v in seed_alpha]
    half_widths = [(np.percentile(v, 84) - np.percentile(v, 16)) / 2.0 for v in seed_alpha]
    pooled = float(np.sqrt(np.mean(np.square(half_widths))))
    diagnostics["alpha"]["seed_medians"] = [float(x) for x in med]
    diagnostics["alpha"]["T"] = float(abs(med[0] - med[1]) / max(pooled, 1e-300))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain-root", default=str(CHAIN_ROOT.relative_to(ROOT)))
    parser.add_argument("--out", default=str(OUT.relative_to(ROOT)))
    parser.add_argument("--burn", type=int, default=200)
    parser.add_argument("--models", nargs="*", default=list(MODELS))
    args = parser.parse_args()

    chain_root = ROOT / args.chain_root
    out_path = ROOT / args.out
    burn = args.burn
    selected_models = {model: MODELS[model] for model in args.models}

    result = {
        "chain_root": str(chain_root.relative_to(ROOT)),
        "burn": burn,
        "method": (
            "Rank-normalized split R-hat with folded check; bulk ESS on rank-normalized "
            "samples; tail ESS as min ESS of 5% lower/upper indicator chains. Each seed is "
            "treated as an independent chain after flattening ensemble walkers."
        ),
        "models": {},
    }

    for model, names in selected_models.items():
        seed_chains = [load_seed_chain(chain_root, model, seed, burn) for seed in (42, 12345)]
        min_draws = min(len(c) for c in seed_chains)
        seed_chains = [c[:min_draws] for c in seed_chains]
        chains = np.stack(seed_chains, axis=0)
        params = parameter_diagnostics(chains, names)
        add_alpha(chains, seed_chains, names, params)
        result["models"][model] = {
            "n_chains": int(chains.shape[0]),
            "draws_per_chain": int(chains.shape[1]),
            "parameters": params,
            "cross_seed_tension": cross_seed_tension(seed_chains, names),
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
