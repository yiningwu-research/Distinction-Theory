#!/usr/bin/env python3
"""
Step 1A: Chain-only pilot diagnostics. Zero CLASS calls.

Reads existing samples_raw.npy from outputs/phase3_pilot/ and computes:
  - α = κq distributions (g1_mkappa)
  - F_κ(0.75) — fraction κ ≤ 0.75 (g1_mkappa)
  - κ HPD intervals (68%, 95%)
  - Cross-seed parameter quantile comparisons
  - α stability across seeds
  - Per-parameter ESS, τ, acceptance
  - q-κ correlation structure
  - Boundary occupancy

Saves to outputs/phase3_pilot/pilot_diagnostics.json
"""

import json, sys, numpy as np
from pathlib import Path

BASEDIR = Path(__file__).parent.parent / "outputs" / "phase3_pilot"
OUTFILE = BASEDIR / "pilot_diagnostics.json"


def load_chain(model: str, seed: int) -> np.ndarray:
    """Load full unthinned chain, shape (n_walkers, n_steps, n_params)."""
    path = BASEDIR / model / f"seed_{seed}" / "samples_raw.npy"
    return np.load(path)


def load_logp(model: str, seed: int) -> np.ndarray:
    path = BASEDIR / model / f"seed_{seed}" / "log_prob_raw.npy"
    if path.exists():
        return np.load(path)
    return None


def flat_post_burn(chain: np.ndarray, burn: int = 100) -> np.ndarray:
    """Flatten chain, discarding burn-in. Chain shape: (n_steps, n_walkers, n_dim)."""
    return chain[burn:, :, :].reshape(-1, chain.shape[-1])


def hpd_interval(samples: np.ndarray, prob: float = 0.68) -> tuple:
    """Highest posterior density interval (simple quantile-based)."""
    lower = (1.0 - prob) / 2.0
    upper = 1.0 - lower
    return (np.percentile(samples, 100 * lower),
            np.percentile(samples, 100 * upper))


def ess_from_chain(chain: np.ndarray, burn: int = 100) -> np.ndarray:
    """Effective sample size per parameter (simple autocorrelation method)."""
    flat = flat_post_burn(chain, burn)
    n, d = flat.shape
    ess = np.zeros(d)
    for i in range(d):
        x = flat[:, i]
        # Lag-1 autocorrelation
        acf1 = np.corrcoef(x[:-1], x[1:])[0, 1]
        if abs(acf1) < 1.0:
            ess[i] = n / (1.0 + 2.0 * acf1 / (1.0 - acf1))
        else:
            ess[i] = 1.0
    return ess


def main():
    models_params = {
        "lcdm":    ["Omega_m", "h", "ln10As"],
        "g1_bg":   ["Omega_m", "h", "ln10As", "q"],
        "g1_m34":  ["Omega_m", "h", "ln10As", "q"],
        "g1_mkappa": ["Omega_m", "h", "ln10As", "q", "kappa"],
    }
    seeds = [42, 12345]
    burn = 0  # emcee burn already discarded via sampler.reset()

    results: dict = {"chain_only_metrics": {}, "pending": []}

    # ── Per-model/per-seed basic stats ──────────────────────────────────
    all_samples: dict = {}

    for model, pnames in models_params.items():
        for seed in seeds:
            key = f"{model}_seed{seed}"
            try:
                chain = load_chain(model, seed)
            except FileNotFoundError:
                print(f"  MISSING: {key}")
                results["pending"].append(f"samples missing: {key}")
                continue

            flat = flat_post_burn(chain, burn)
            all_samples[key] = (flat, pnames)

            ess = ess_from_chain(chain, 0)
            tau = flat.shape[0] / np.maximum(ess, 1.0)

            quant = {}
            for i, name in enumerate(pnames):
                q16, q50, q84 = np.percentile(flat[:, i], [16, 50, 84])
                quant[name] = {
                    "median": float(q50),
                    "q16": float(q16),
                    "q84": float(q84),
                    "mean": float(np.mean(flat[:, i])),
                    "ess": float(ess[i]),
                    "tau": float(tau[i]),
                }

            results["chain_only_metrics"][key] = {
                "model": model,
                "seed": seed,
                "n_samples": int(flat.shape[0]),
                "quantiles": quant,
            }

    # ── α = κq for g1_mkappa ──────────────────────────────────────────
    for seed in seeds:
        key = f"g1_mkappa_seed{seed}"
        if key not in all_samples:
            continue
        flat, pnames = all_samples[key]
        qi = pnames.index("q")
        ki = pnames.index("kappa")
        alpha = flat[:, qi] * flat[:, ki]

        a16, a50, a84 = np.percentile(alpha, [16, 50, 84])
        alpha_ref = 0.75 * flat[:, qi]  # locked-branch equivalent α

        results["chain_only_metrics"][f"g1_mkappa_seed{seed}_alpha"] = {
            "description": "α = κq (effective Weyl amplitude)",
            "median": float(a50),
            "q16": float(a16),
            "q84": float(a84),
            "alpha_locked_ref_median": float(np.median(alpha_ref)),
        }

    # ── F_κ(0.75) and κ HPD ──────────────────────────────────────────
    for seed in seeds:
        key = f"g1_mkappa_seed{seed}"
        if key not in all_samples:
            continue
        flat, pnames = all_samples[key]
        ki = pnames.index("kappa")
        k_vals = flat[:, ki]

        f_kappa = float(np.mean(k_vals <= 0.75))
        hpd68 = hpd_interval(k_vals, 0.68)
        hpd95 = hpd_interval(k_vals, 0.95)

        in_68 = float(hpd68[0]) <= 0.75 <= float(hpd68[1])
        in_95 = float(hpd95[0]) <= 0.75 <= float(hpd95[1])

        results["chain_only_metrics"][f"g1_mkappa_seed{seed}_kappa_diag"] = {
            "F_kappa_le_075": f_kappa,
            "kappa_median": float(np.median(k_vals)),
            "HPD_68": [float(hpd68[0]), float(hpd68[1])],
            "HPD_95": [float(hpd95[0]), float(hpd95[1])],
            "kappa_075_in_68_HPD": in_68,
            "kappa_075_in_95_HPD": in_95,
            "status_075": (
                "central-compatible" if in_68
                else "tail-compatible" if in_95
                else "outside-95-HPD"
            ),
        }

    # ── Cross-seed comparisons ─────────────────────────────────────────
    for model in ["lcdm", "g1_bg", "g1_m34"]:
        s1 = f"{model}_seed42"
        s2 = f"{model}_seed12345"
        if s1 not in all_samples or s2 not in all_samples:
            continue
        f1, pn = all_samples[s1]
        f2, _ = all_samples[s2]

        cross = {}
        for i, name in enumerate(pn):
            w1 = 0.5 * (np.percentile(f1[:, i], 84) - np.percentile(f1[:, i], 16))
            w2 = 0.5 * (np.percentile(f2[:, i], 84) - np.percentile(f2[:, i], 16))
            med_diff = np.median(f1[:, i]) - np.median(f2[:, i])
            pool_width = np.sqrt(w1**2 + w2**2)
            t_q = abs(med_diff) / max(pool_width, 1e-30)
            cross[name] = {
                "median_seed42": float(np.median(f1[:, i])),
                "median_seed12345": float(np.median(f2[:, i])),
                "diff": float(med_diff),
                "T_q": float(t_q),
            }
        results["chain_only_metrics"][f"{model}_cross_seed"] = cross

    # ── g1_mkappa cross-seed α comparison ─────────────────────────────
    for m in ["g1_mkappa"]:
        s1 = f"{m}_seed42"
        s2 = f"{m}_seed12345"
        if s1 not in all_samples or s2 not in all_samples:
            continue
        f1, pn = all_samples[s1]
        f2, _ = all_samples[s2]
        qi, ki = pn.index("q"), pn.index("kappa")
        a1 = f1[:, qi] * f1[:, ki]
        a2 = f2[:, qi] * f2[:, ki]
        w = 0.5 * (np.percentile(a1, 84) - np.percentile(a1, 16) +
                    np.percentile(a2, 84) - np.percentile(a2, 16))
        t_alpha = abs(np.median(a1) - np.median(a2)) / max(w, 1e-30)
        results["chain_only_metrics"][f"{m}_alpha_cross_seed"] = {
            "alpha_median_seed42": float(np.median(a1)),
            "alpha_median_seed12345": float(np.median(a2)),
            "diff": float(abs(np.median(a1) - np.median(a2))),
            "T_alpha": float(t_alpha),
        }

    # ── q-κ correlation ───────────────────────────────────────────────
    for seed in seeds:
        key = f"g1_mkappa_seed{seed}"
        if key not in all_samples:
            continue
        flat, pn = all_samples[key]
        qi, ki = pn.index("q"), pn.index("kappa")
        corr = float(np.corrcoef(flat[:, qi], flat[:, ki])[0, 1])
        results["chain_only_metrics"][f"{key}_q_kappa_corr"] = corr

    # ── Boundary occupancy ─────────────────────────────────────────────
    bounds = {
        "Omega_m": (0.15, 0.50),
        "h": (0.55, 0.85),
        "ln10As": (2.5, 3.7),
        "q": (0.0, 1.15),
        "kappa": (0.0, 1.0),
    }
    for model, pnames in models_params.items():
        for seed in seeds:
            key = f"{model}_seed{seed}"
            if key not in all_samples:
                continue
            flat, pn = all_samples[key]
            bocc = {}
            for i, name in enumerate(pn):
                if name in bounds:
                    lo, hi = bounds[name]
                    near_edge = (
                        ((flat[:, i] - lo) / max(hi - lo, 1e-30) < 0.01) |
                        ((hi - flat[:, i]) / max(hi - lo, 1e-30) < 0.01)
                    )
                    bocc[name] = float(np.mean(near_edge))
            results["chain_only_metrics"][f"{key}_boundary"] = bocc

    # ── Save ───────────────────────────────────────────────────────────
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTFILE, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # ── Print summary ──────────────────────────────────────────────────
    print("=" * 70)
    print("  STEP 1A: CHAIN-ONLY PILOT DIAGNOSTICS")
    print("=" * 70)

    # g1_mkappa κ HPD
    for seed in [42, 12345]:
        d = results["chain_only_metrics"].get(f"g1_mkappa_seed{seed}_kappa_diag", {})
        if d:
            print(f"\n  g1_mkappa seed={seed}:")
            print(f"    κ median:     {d['kappa_median']:.3f}")
            print(f"    F(κ≤0.75):    {d['F_kappa_le_075']:.3f}")
            print(f"    68% HPD:      [{d['HPD_68'][0]:.3f}, {d['HPD_68'][1]:.3f}]")
            print(f"    95% HPD:      [{d['HPD_95'][0]:.3f}, {d['HPD_95'][1]:.3f}]")
            print(f"    0.75 status:  {d['status_075']}")

    # α
    for seed in [42, 12345]:
        d = results["chain_only_metrics"].get(f"g1_mkappa_seed{seed}_alpha", {})
        if d:
            print(f"\n  g1_mkappa seed={seed} α=κq: "
                  f"median={d['median']:.4f} [{d['q16']:.4f}, {d['q84']:.4f}]")

    # α cross-seed
    a = results["chain_only_metrics"].get("g1_mkappa_alpha_cross_seed", {})
    if a:
        print(f"\n  α cross-seed: T_α = {a.get('T_alpha', '?'):.2f}")

    # q-κ correlation
    for seed in [42, 12345]:
        c = results["chain_only_metrics"].get(f"g1_mkappa_seed{seed}_q_kappa_corr", None)
        if c is not None:
            print(f"  q-κ correlation seed={seed}: {c:.3f}")

    # Cross-seed T_q for g1_bg
    cs = results["chain_only_metrics"].get("g1_bg_cross_seed", {})
    if cs and "q" in cs:
        print(f"\n  g1_bg q cross-seed: T_q = {cs['q']['T_q']:.2f}")

    print(f"\n  Saved: {OUTFILE}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
