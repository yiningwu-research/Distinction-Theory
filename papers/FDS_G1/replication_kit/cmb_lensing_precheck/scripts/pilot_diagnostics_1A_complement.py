#!/usr/bin/env python3
"""
Complementary diagnostics for Step 1A (zero CLASS calls).

Adds to pilot_diagnostics.json:
  - α_locked = 0.75 * q_m34  (full distribution, not point estimate)
  - α_compatibility: locked-α vs free-α HPD overlap, posterior shift
  - near-null q boundary mass: P(q < 0.02) for all G1 branches
  - P(κ > 0.75) explicit
"""

import json, sys, numpy as np
from pathlib import Path

BASEDIR = Path(__file__).parent.parent / "outputs" / "phase3_pilot"
DIAGFILE = BASEDIR / "pilot_diagnostics.json"


def flat_chain(model: str, seed: int) -> np.ndarray:
    c = np.load(BASEDIR / model / f"seed_{seed}" / "samples_raw.npy")
    return c.reshape(-1, c.shape[-1])  # already post-reset, no burn


def quantiles(x: np.ndarray):
    return float(np.median(x)), float(np.percentile(x, 16)), float(np.percentile(x, 84))


def hpd(x: np.ndarray, prob: float):
    lo = (1.0 - prob) / 2.0
    hi = 1.0 - lo
    return float(np.percentile(x, 100 * lo)), float(np.percentile(x, 100 * hi))


def main():
    with open(DIAGFILE) as f:
        diag = json.load(f)

    # ── α_locked = 0.75 * q_m34 (distribution from both seeds) ─────────
    # Combine both g1_m34 seeds for locked-α distribution
    q_m34_all = []
    for seed in [42, 12345]:
        flat = flat_chain("g1_m34", seed)
        qi = 3  # ["Omega_m","h","ln10As","q"] → q is index 3
        q_m34_all.extend(flat[:, qi].tolist())
    q_m34_all = np.array(q_m34_all)

    alpha_locked = 0.75 * q_m34_all
    al_med, al_q16, al_q84 = quantiles(alpha_locked)
    al_hpd68 = hpd(alpha_locked, 0.68)
    al_hpd95 = hpd(alpha_locked, 0.95)

    diag["alpha_locked"] = {
        "definition": "0.75 * q_m34 (both seeds combined)",
        "n_samples": int(len(alpha_locked)),
        "median": al_med,
        "q16": al_q16,
        "q84": al_q84,
        "hpd68": [al_hpd68[0], al_hpd68[1]],
        "hpd95": [al_hpd95[0], al_hpd95[1]],
    }

    # ── α_free from g1_mkappa (both seeds combined) ────────────────────
    alpha_free = []
    for seed in [42, 12345]:
        flat = flat_chain("g1_mkappa", seed)
        qi, ki = 3, 4  # ["Omega_m","h","ln10As","q","kappa"]
        alpha_free.extend((flat[:, qi] * flat[:, ki]).tolist())
    alpha_free = np.array(alpha_free)

    af_med, af_q16, af_q84 = quantiles(alpha_free)
    af_hpd68 = hpd(alpha_free, 0.68)
    af_hpd95 = hpd(alpha_free, 0.95)

    diag["alpha_free"] = {
        "definition": "κ * q (g1_mkappa, both seeds combined)",
        "n_samples": int(len(alpha_free)),
        "median": af_med,
        "q16": af_q16,
        "q84": af_q84,
        "hpd68": [af_hpd68[0], af_hpd68[1]],
        "hpd95": [af_hpd95[0], af_hpd95[1]],
    }

    # ── α_compatibility: locked median in free HPD ─────────────────────
    locked_med_in_free_hpd68 = bool(af_hpd68[0] <= al_med <= af_hpd68[1])
    locked_med_in_free_hpd95 = bool(af_hpd95[0] <= al_med <= af_hpd95[1])

    # Posterior shift T_alpha: difference in medians / pooled width
    pool_w = 0.5 * ((af_q84 - af_q16) + (al_q84 - al_q16))
    T_alpha = abs(af_med - al_med) / max(pool_w, 1e-30)

    # Overlap: fraction of locked samples within free 95% HPD
    overlap_95 = float(np.mean((alpha_locked >= af_hpd95[0]) &
                                (alpha_locked <= af_hpd95[1])))
    overlap_68 = float(np.mean((alpha_locked >= af_hpd68[0]) &
                                (alpha_locked <= af_hpd68[1])))

    diag["alpha_compatibility"] = {
        "locked_median": al_med,
        "free_median": af_med,
        "locked_median_in_free_hpd68": locked_med_in_free_hpd68,
        "locked_median_in_free_hpd95": locked_med_in_free_hpd95,
        "posterior_shift_T_alpha": round(T_alpha, 4),
        "locked_fraction_in_free_95hpd": round(overlap_95, 4),
        "locked_fraction_in_free_68hpd": round(overlap_68, 4),
        "interpretation": (
            "central-compatible" if locked_med_in_free_hpd68
            else "tail-compatible" if locked_med_in_free_hpd95
            else "outside-95-HPD"
        ),
    }

    # ── κ: explicit P(κ > 0.75) ────────────────────────────────────────
    kappa_all = []
    for seed in [42, 12345]:
        flat = flat_chain("g1_mkappa", seed)
        ki = 4
        kappa_all.extend(flat[:, ki].tolist())
    kappa_all = np.array(kappa_all)

    diag["kappa_diagnostics"] = {
        "median": float(np.median(kappa_all)),
        "P_kappa_le_0p75": float(np.mean(kappa_all <= 0.75)),
        "P_kappa_gt_0p75": float(np.mean(kappa_all > 0.75)),
        "hpd68": list(hpd(kappa_all, 0.68)),
        "hpd95": list(hpd(kappa_all, 0.95)),
        "status_0p75": (
            "central-compatible"
            if hpd(kappa_all, 0.68)[0] <= 0.75 <= hpd(kappa_all, 0.68)[1]
            else "tail-compatible"
            if hpd(kappa_all, 0.95)[0] <= 0.75 <= hpd(kappa_all, 0.95)[1]
            else "outside-95-HPD"
        ),
    }

    # ── Near-null q boundary mass: P(q < 0.02) ─────────────────────────
    Q_NEAR = 0.02
    near_null = {}
    for model, qi in [("g1_bg", 3), ("g1_m34", 3), ("g1_mkappa", 3)]:
        q_all = []
        for seed in [42, 12345]:
            flat = flat_chain(model, seed)
            q_all.extend(flat[:, qi].tolist())
        q_all = np.array(q_all)
        near_null[model] = {
            "threshold": Q_NEAR,
            "P_q_below_threshold": float(np.mean(q_all < Q_NEAR)),
            "n_samples": int(len(q_all)),
            "description": "near-null boundary mass (NOT point-null exclusion)",
        }
    diag["near_null_q"] = near_null

    # ── Save ───────────────────────────────────────────────────────────
    with open(DIAGFILE, "w") as f:
        json.dump(diag, f, indent=2, default=str)

    # ── Print ──────────────────────────────────────────────────────────
    print("=" * 70)
    print("  COMPLEMENTARY DIAGNOSTICS")
    print("=" * 70)
    print(f"\n  α_locked (0.75*q_m34):")
    print(f"    median = {al_med:.4f} [{al_q16:.4f}, {al_q84:.4f}]")
    print(f"    68% HPD: [{al_hpd68[0]:.4f}, {al_hpd68[1]:.4f}]")
    print(f"    95% HPD: [{al_hpd95[0]:.4f}, {al_hpd95[1]:.4f}]")
    print(f"\n  α_free (κq, g1_mkappa):")
    print(f"    median = {af_med:.4f} [{af_q16:.4f}, {af_q84:.4f}]")
    print(f"    68% HPD: [{af_hpd68[0]:.4f}, {af_hpd68[1]:.4f}]")

    print(f"\n  α compatibility:")
    print(f"    locked median ({al_med:.4f}) in free 68% HPD: {locked_med_in_free_hpd68}")
    print(f"    locked median ({al_med:.4f}) in free 95% HPD: {locked_med_in_free_hpd95}")
    print(f"    T_α = {T_alpha:.3f}")
    print(f"    locked overlap with free 68%: {overlap_68:.3f}")
    print(f"    locked overlap with free 95%: {overlap_95:.3f}")
    print(f"    Status: {diag['alpha_compatibility']['interpretation']}")

    print(f"\n  κ diagnostics (both seeds combined):")
    kd = diag["kappa_diagnostics"]
    print(f"    median = {kd['median']:.3f}")
    print(f"    P(κ ≤ 0.75) = {kd['P_kappa_le_0p75']:.3f}")
    print(f"    P(κ > 0.75) = {kd['P_kappa_gt_0p75']:.3f}")
    print(f"    68% HPD: [{kd['hpd68'][0]:.3f}, {kd['hpd68'][1]:.3f}]")
    print(f"    Status 0.75: {kd['status_0p75']}")

    print(f"\n  Near-null q boundary (q < {Q_NEAR}):")
    for model, v in near_null.items():
        print(f"    {model:12s}: P(q<{Q_NEAR}) = {v['P_q_below_threshold']:.4f}")

    print(f"\n  Saved: {DIAGFILE}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
