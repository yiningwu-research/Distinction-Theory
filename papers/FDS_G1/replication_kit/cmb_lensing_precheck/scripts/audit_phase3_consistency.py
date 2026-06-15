#!/usr/bin/env python3
"""Phase 3 consistency audit.

This script is intentionally cheap: it does not rerun MCMC or nested sampling.
It recomputes posterior summaries from saved chains and compares log-likelihood
values for a deterministic subsample under:
  1. the current registered frozen-v4 loader,
  2. the saved chain log_prob values,
  3. the legacy v2 emulator route.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cmb_lensing_precheck.mcmc.likelihood import LensingLikelihood
from cmb_lensing_precheck.mcmc.structured_emu import StructuredRatioEmulator
from cmb_lensing_precheck.mcmc.baseline_emu import BaselineEmulator


ROOT = Path(__file__).resolve().parents[1]
CHAIN_ROOT = ROOT / "outputs" / "frozen" / "v4_act_only" / "chains"
OUT = ROOT / "outputs" / "phase3_consistency_audit.json"

MODELS = {
    "lcdm": ["Omega_m", "h", "ln10As"],
    "g1_bg": ["Omega_m", "h", "ln10As", "q"],
    "g1_m34": ["Omega_m", "h", "ln10As", "q"],
    "g1_mkappa": ["Omega_m", "h", "ln10As", "q", "kappa"],
}

FIXED = {
    "lcdm": {"q": 0.0, "kappa": 0.0},
    "g1_bg": {"kappa": 0.0},
    "g1_m34": {"kappa": 0.75},
    "g1_mkappa": {},
}


def load_model_samples(model: str, burn: int) -> tuple[np.ndarray, np.ndarray]:
    samples = []
    logp = []
    for seed in (42, 12345):
        base = CHAIN_ROOT / model / f"seed_{seed}"
        chain = np.load(base / "samples_raw.npy")
        raw_logp = np.load(base / "log_prob_raw.npy")
        samples.append(chain[burn:].reshape(-1, chain.shape[-1]))
        logp.append(raw_logp[burn:].reshape(-1))
    return np.vstack(samples), np.concatenate(logp)


def summarize_samples(samples: np.ndarray, names: list[str]) -> dict:
    out = {}
    for i, name in enumerate(names):
        q16, q50, q84 = np.percentile(samples[:, i], [16, 50, 84])
        out[name] = {
            "median": float(q50),
            "q16": float(q16),
            "q84": float(q84),
        }
    if "q" in names and "kappa" in names:
        q = samples[:, names.index("q")]
        k = samples[:, names.index("kappa")]
        alpha = q * k
        k95 = np.percentile(k, [2.5, 97.5])
        out["diagnostics"] = {
            "alpha_median": float(np.median(alpha)),
            "alpha_q16": float(np.percentile(alpha, 16)),
            "alpha_q84": float(np.percentile(alpha, 84)),
            "kappa_q025": float(k95[0]),
            "kappa_q975": float(k95[1]),
            "F_kappa_le_075": float(np.mean(k <= 0.75)),
            "status_075": (
                "central-compatible"
                if out["kappa"]["q16"] <= 0.75 <= out["kappa"]["q84"]
                else "tail-compatible"
                if k95[0] <= 0.75 <= k95[1]
                else "outside-95"
            ),
        }
    return out


def point_dict(model: str, row: np.ndarray) -> dict[str, float]:
    params = dict(zip(MODELS[model], map(float, row)))
    params.update(FIXED[model])
    return params


def compare_loglikes(burn: int, n_points: int) -> dict:
    current = LensingLikelihood("act_baseline", amplitude_param="ln10As")

    legacy = LensingLikelihood("act_baseline", amplitude_param="ln10As")
    legacy._emulator = StructuredRatioEmulator.load(
        ROOT / "outputs" / "emulator" / "emulator_primordial_v2"
    )
    legacy._baseline_emu = BaselineEmulator.load(
        ROOT / "outputs" / "emulator" / "baseline_emulator"
    )

    out = {}
    for model, names in MODELS.items():
        samples, saved_logp = load_model_samples(model, burn)
        idx = np.linspace(0, len(samples) - 1, min(n_points, len(samples)), dtype=int)
        current_vals = []
        saved_vals = []
        legacy_vals = []
        invalid_current = 0
        invalid_legacy = 0

        for i in idx:
            params = point_dict(model, samples[i])
            logl_current = current.log_likelihood(params)
            logl_legacy = legacy.log_likelihood(params)
            current_vals.append(float(logl_current))
            saved_vals.append(float(saved_logp[i]))
            legacy_vals.append(float(logl_legacy))
            invalid_current += int(not np.isfinite(logl_current))
            invalid_legacy += int(not np.isfinite(logl_legacy))

        current_arr = np.asarray(current_vals)
        saved_arr = np.asarray(saved_vals)
        legacy_arr = np.asarray(legacy_vals)
        current_saved = current_arr - saved_arr
        current_legacy = current_arr - legacy_arr

        out[model] = {
            "n_points": int(len(idx)),
            "invalid_current": int(invalid_current),
            "invalid_legacy": int(invalid_legacy),
            "current_minus_saved": finite_stats(current_saved),
            "current_minus_legacy_v2": finite_stats(current_legacy),
        }
    return out


def finite_stats(x: np.ndarray) -> dict:
    finite = x[np.isfinite(x)]
    if len(finite) == 0:
        return {"n_finite": 0}
    return {
        "n_finite": int(len(finite)),
        "mean": float(np.mean(finite)),
        "median": float(np.median(finite)),
        "rms": float(np.sqrt(np.mean(finite**2))),
        "max_abs": float(np.max(np.abs(finite))),
        "p95_abs": float(np.percentile(np.abs(finite), 95)),
    }


def main() -> int:
    burn = 200
    summaries = {}
    for model, names in MODELS.items():
        samples, _ = load_model_samples(model, burn)
        summaries[model] = {
            "burn": burn,
            "n_samples": int(len(samples)),
            "quantiles": summarize_samples(samples, names),
        }

    result = {
        "chain_root": str(CHAIN_ROOT.relative_to(ROOT)),
        "burn": burn,
        "posterior_summaries": summaries,
        "loglike_comparison": compare_loglikes(burn=burn, n_points=24),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
