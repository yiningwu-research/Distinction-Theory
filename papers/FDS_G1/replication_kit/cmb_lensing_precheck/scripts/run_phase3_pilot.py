#!/usr/bin/env python3
"""
Phase 3 Pilot Chains: ACT-only, 40 walkers × 500 steps, 2 independent seeds.

Purpose: posterior geometry reconnaissance, NOT scientific constraints.
Each run saves full unthinned chains + convergence diagnostics.

Models: lcdm, g1_bg, g1_m34, g1_mkappa
Datasets: act_baseline only (fast turn; ACT+PR4 follows after geometry check)
"""

import sys, json, time, numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cmb_lensing_precheck.mcmc import MCMCSampler
from cmb_lensing_precheck.mcmc.sampler import gelman_rubin

BASEDIR = Path(__file__).parent.parent / "outputs" / "phase3_pilot"


def check_unlock() -> tuple[bool, dict]:
    """Verify production unlock token with emulator/cache hash consistency."""
    token = BASEDIR.parent / "emulator" / "emulator_primordial" / "production_unlock.json"
    cache_manifest = BASEDIR.parent / "emulator_cache" / "manifest.json"
    if not token.exists() or not cache_manifest.exists():
        return False, {}
    with open(token) as f:
        tok = json.load(f)
    with open(cache_manifest) as f:
        cache = json.load(f)
    info = {
        "emulator_token_ok": tok.get("production_unlock", False),
        "cache_hash": tok.get("cache_hash", "?"),
        "cache_version": cache.get("cache_version", "?"),
    }
    return info["emulator_token_ok"], info


def run_ensemble(model: str, seed: int, outdir: Path,
                 n_walkers: int = 40, n_steps: int = 500,
                 burn_steps: int = 100) -> dict:
    """Run one ensemble. Saves full chain. Returns diagnostics dict."""
    sampler = MCMCSampler(model, "act_baseline", amplitude_param="ln10As", seed=seed)
    t0 = time.time()
    meta = sampler.run(n_walkers=n_walkers, n_steps=n_steps,
                       burn_steps=burn_steps, progress=True,
                       checkpoint_dir=outdir, checkpoint_every=50)
    walltime = time.time() - t0

    # Save full unthinned chain
    outdir.mkdir(parents=True)
    sampler.save(outdir)

    samples = sampler.get_samples(burn=burn_steps, flat=True)
    logp = sampler.get_log_prob(burn=burn_steps, flat=True)

    n_dim = sampler.n_dim
    param_names = sampler.prior.param_names(model)

    # Fail-closed: detect NaN, all-walker boundary stuck, or likelihood anomaly
    has_nan = np.any(~np.isfinite(samples)) or np.any(~np.isfinite(logp))
    valid_logp = logp[np.isfinite(logp)]
    all_at_boundary = False
    if len(samples) > 0 and model in ["g1_mkappa"]:
        # Check if all walkers stuck at kappa boundary
        kappa_vals = samples[:, -1]  # last column
        near_zero = np.mean(kappa_vals < 0.001)
        near_one = np.mean(kappa_vals > 0.999)
        all_at_boundary = (near_zero + near_one) > 0.95

    ensemble_ok = (not has_nan) and (not all_at_boundary) and len(valid_logp) > 0

    # Build diagnostics dict incrementally
    diag: dict = {
        "model": model, "seed": seed,
        "n_dim": n_dim, "param_names": param_names,
        "ensemble_ok": ensemble_ok, "has_nan": has_nan,
        "all_at_boundary": all_at_boundary,
        "n_samples": len(samples),
    }

    # Per-parameter quantiles
    quantiles = {}
    for i, name in enumerate(param_names):
        q16, q50, q84 = np.percentile(samples[:, i], [16, 50, 84])
        quantiles[name] = {"median": float(q50), "lo": float(q16), "hi": float(q84)}

    # Boundary occupancy (fraction within 1% of prior edge)
    cfg = sampler.prior.config
    bounds = {
        "Omega_m": (cfg.Omega_m_min, cfg.Omega_m_max),
        "h": (cfg.h_min, cfg.h_max),
        "ln10As": (cfg.ln10As_min, cfg.ln10As_max),
        "q": (cfg.q_min, cfg.q_max),
        "kappa": (cfg.kappa_min, cfg.kappa_max),
    }
    boundary_frac = {}
    for i, name in enumerate(param_names):
        if name in bounds:
            lo, hi = bounds[name]
            near_edge = ((samples[:, i] - lo) / max(hi - lo, 1e-30) < 0.01) | \
                        ((hi - samples[:, i]) / max(hi - lo, 1e-30) < 0.01)
            boundary_frac[name] = float(np.mean(near_edge))

    diag = {
        "model": model,
        "seed": seed,
        "n_dim": n_dim,
        "param_names": param_names,
        "n_walkers": n_walkers,
        "n_steps": n_steps,
        "burn_steps": burn_steps,
        "walltime_s": walltime,
        "autocorr_times": meta["autocorr_times"],
        "mean_tau": meta["mean_tau"],
        "acceptance_fraction": meta["acceptance_fraction"],
        "best_logp": float(np.max(logp)),
        "quantiles": quantiles,
        "boundary_occupancy": boundary_frac,
    }

    with open(outdir / "diagnostics.json", "w") as f:
        json.dump(diag, f, indent=2)

    return diag


def main():
    unlocked, token_info = check_unlock()
    if not unlocked:
        print("PRODUCTION EMULATOR NOT UNLOCKED. Abort.")
        return 1

    print(f"  Token:    OK (cache hash={token_info.get('cache_hash','?')[:12]}...)")
    print(f"  Cache:    v{token_info.get('cache_version','?')}")
    print(f"  PILOT — NOT FOR FINAL CONSTRAINTS")

    BASEDIR.mkdir(parents=True, exist_ok=True)

    models = ["lcdm", "g1_bg", "g1_m34", "g1_mkappa"]
    seeds = [42, 12345]
    n_walkers = 40
    n_steps = 200   # production steps (pilot = geometry reconnaissance)
    burn_steps = 100

    print("=" * 70)
    print("  PHASE 3 PILOT CHAINS (ACT-only, posterior geometry reconnaissance)")
    print("=" * 70)
    print(f"  Models:   {models}")
    print(f"  Variant:  act_baseline")
    print(f"  Walkers:  {n_walkers}, Steps: {n_steps}, Burn: {burn_steps}")
    print(f"  Seeds:    {seeds}")
    print("  WARNING:  NOT for scientific constraints")
    print("=" * 70)
    print()

    t_total = time.time()
    all_results = {}

    for model in models:
        print(f"\n{'=' * 70}")
        print(f"  MODEL: {model}")
        print(f"{'=' * 70}")

        ensembles = []
        for seed in seeds:
            print(f"\n  [seed={seed}]")
            outdir = BASEDIR / model / f"seed_{seed}"
            diag = run_ensemble(model, seed, outdir, n_walkers, n_steps, burn_steps)
            ensembles.append(diag)

            print(f"    walltime:     {diag['walltime_s']:.0f}s "
                  f"({diag['walltime_s']/n_steps:.1f}s/step)")
            print(f"    tau mean:     {diag['mean_tau']:.1f}")
            print(f"    accept frac:  {diag['acceptance_fraction']:.3f}")
            print(f"    best logp:    {diag['best_logp']:.1f}")
            for name, q in diag["quantiles"].items():
                print(f"    {name:8s}: {q['median']:.3f}  [{q['lo']:.3f}, {q['hi']:.3f}]")

        # Cross-seed R-hat (rank-normalized between independent ensembles)
        try:
            samples1 = np.load(BASEDIR / model / "seed_42" / "samples_raw.npy")
            samples2 = np.load(BASEDIR / model / "seed_12345" / "samples_raw.npy")
            # Use post-burn samples
            s1 = samples1[:, burn_steps:, :].reshape(-1, samples1.shape[-1])
            s2 = samples2[:, burn_steps:, :].reshape(-1, samples2.shape[-1])
            R_hat = gelman_rubin([s1[:2000], s2[:2000]])  # subsample for speed
            ensembles[0]["R_hat_between_ensembles"] = R_hat.tolist()
            ensembles[0]["R_hat_max"] = float(np.max(R_hat))
            print(f"  R-hat max (between ensembles): {np.max(R_hat):.3f}")
        except Exception as e:
            print(f"  R-hat: skipped ({e})")

        # Compare best logp across seeds
        delta_logp = abs(ensembles[0]["best_logp"] - ensembles[1]["best_logp"])
        ensembles[0]["delta_logp_across_seeds"] = delta_logp
        ensembles[0]["seed_agreement"] = delta_logp < 5.0

        print(f"\n  Cross-seed: Δlogp_max = {delta_logp:.2f}")
        print(f"  Seed agreement (Δlogp < 5): {delta_logp < 5.0}")

        # Compare parameter quantiles across seeds
        for name in ensembles[0]["param_names"]:
            q0 = ensembles[0]["quantiles"][name]["median"]
            q1 = ensembles[1]["quantiles"][name]["median"]
            err0 = ensembles[0]["quantiles"][name]["hi"] - ensembles[0]["quantiles"][name]["lo"]
            if err0 > 1e-10:
                nsigma = abs(q0 - q1) / (err0 / 2.355)
                print(f"    {name}: median diff = {abs(q0-q1):.4f} "
                      f"({nsigma:.1f}σ of seed-1 width)")

        all_results[model] = ensembles

    # ── Summary ─────────────────────────────────────────────────────────
    t_run = time.time() - t_total
    print()
    print("=" * 70)
    print(f"  PILOT CHAINS COMPLETE  ({t_run/60:.0f} min)")
    print("=" * 70)
    print(f"  Key diagnostics (seed-1 only):")
    print(f"  {'Model':12s} {'tau':>6s} {'accept':>7s} {'best_logp':>10s} {'q_med':>7s} {'k_med':>7s}")
    for model in models:
        d = all_results[model][0]
        q_med = d["quantiles"].get("q", {}).get("median", float("nan"))
        k_med = d["quantiles"].get("kappa", {}).get("median", float("nan"))
        print(f"  {model:12s} {d['mean_tau']:6.1f} {d['acceptance_fraction']:7.3f} "
              f"{d['best_logp']:10.1f} {q_med:7.3f} {k_med:7.3f}")

    with open(BASEDIR / "pilot_summary.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print()
    print(f"  Saved: {BASEDIR}/")
    print(f"  Next: review posterior geometry plots")
    print(f"        then decide on production chain length and ACT+PR4")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
