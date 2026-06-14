#!/usr/bin/env python3
"""
Phase 3 Production: ACT-only, convergence-driven stopping.

Uses the full emulator pipeline (baseline + ratio).
Runs 4 models × 2 independent ensembles.
Extends chains in 500-step chunks until convergence criteria met.
"""

import sys, json, time, numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cmb_lensing_precheck.mcmc import MCMCSampler

BASEDIR = Path(__file__).parent.parent / "outputs" / "phase3_production"


def check_convergence(samplers) -> dict:
    """Check convergence across independent ensembles."""
    from scipy.stats import rankdata
    chains = []
    for s in samplers:
        c = s.get_samples(burn=0, flat=True)
        if len(c) > 10000:
            c = c[np.linspace(0, len(c)-1, 10000, dtype=int)]
        chains.append(c)

    n_c, n_s, n_d = len(chains), chains[0].shape[0], chains[0].shape[1]
    R = np.zeros(n_d)
    for i in range(n_d):
        combined = np.concatenate([c[:, i] for c in chains])
        ranks = rankdata(combined)
        off = 0
        chain_ranks = []
        for c in chains:
            chain_ranks.append(ranks[off:off+len(c)])
            off += len(c)
        means = [np.mean(r) for r in chain_ranks]
        grand = np.mean(means)
        B = sum(len(c) * (m - grand)**2 for c, m in zip(chains, means)) / (n_c - 1)
        W = np.mean([np.var(r, ddof=1) for r in chain_ranks])
        var_hat = (n_s - 1) / n_s * W + B / n_s
        R[i] = np.sqrt(var_hat / max(W, 1e-30))

    combined = np.vstack(chains)
    n, d = combined.shape
    ess = np.zeros(d)
    for i in range(d):
        x = combined[:, i]
        acf1 = np.corrcoef(x[:-1], x[1:])[0, 1]
        if abs(acf1) < 1.0:
            ess[i] = n / (1.0 + 2.0 * acf1 / (1.0 - acf1))
        else:
            ess[i] = 1.0
    bulk_ess = float(np.min(ess))
    tail_ess = float(np.percentile(ess, 5))

    max_R = float(np.max(R))
    mcse_ok = True
    model = samplers[0].model
    if model == "g1_mkappa":
        k_all = combined[:, -1]
        F = np.mean(k_all <= 0.75)
        mcse = np.sqrt(F * (1 - F) / n)
        mcse_ok = mcse < 0.02

    conv = {
        "R_hat_max": max_R, "bulk_ESS": bulk_ess, "tail_ESS": tail_ess,
        "n_samples": int(n),
        "converged": max_R < 1.01 and bulk_ess > 1000 and tail_ess > 1000 and mcse_ok,
        "passed_R": max_R < 1.01,
        "passed_ESS": bulk_ess > 1000 and tail_ess > 1000,
    }
    if model == "g1_mkappa":
        conv["mcse_Fkappa"] = float(mcse)
        conv["passed_mcse"] = mcse_ok
    return conv


def main():
    BASEDIR.mkdir(parents=True, exist_ok=True)

    models = ["lcdm", "g1_bg", "g1_m34", "g1_mkappa"]
    seeds = [42, 12345]
    n_walkers = 40
    burn = 200
    chunk = 500
    max_total = 5000

    print("=" * 70)
    print("  PHASE 3 PRODUCTION — ACT-ONLY")
    print(f"  {models}")
    print(f"  {n_walkers} walkers, burn={burn}, chunk={chunk}, max={max_total}")
    print("=" * 70)

    all_results = {}

    for model in models:
        print(f"\n{'='*70}")
        print(f"  MODEL: {model}")
        print(f"{'='*70}")

        samplers = []
        for seed in seeds:
            s = MCMCSampler(model, "act_baseline", amplitude_param="ln10As", seed=seed)
            samplers.append(s)

        # Initial burn + first chunk
        t0 = time.time()
        for i, s in enumerate(samplers):
            print(f"  seed={seeds[i]}: burn({burn}) + first chunk({chunk})... ", end="", flush=True)
            s.run(n_walkers=n_walkers, n_steps=chunk, burn_steps=burn, progress=False)
            print(f"done")
        total_prod = chunk
        print(f"  First round: {time.time()-t0:.0f}s")

        conv = check_convergence(samplers)
        while total_prod < max_total and not conv["converged"]:
            total_prod += chunk
            print(f"  Extending to {total_prod} steps "
                  f"(R̂={conv['R_hat_max']:.3f} ESS={conv['bulk_ESS']:.0f})...")
            t0 = time.time()
            for s in samplers:
                pos = s.sampler.get_chain(flat=False)[-1, :, :]
                s.sampler.run_mcmc(pos, chunk, progress=False)
            print(f"    {time.time()-t0:.0f}s")
            conv = check_convergence(samplers)

        print(f"\n  Converged: {conv['converged']} "
              f"(R̂={conv['R_hat_max']:.3f} ESS_bulk={conv['bulk_ESS']:.0f} "
              f"ESS_tail={conv['tail_ESS']:.0f})")

        # Save
        for i, s in enumerate(samplers):
            outdir = BASEDIR / model / f"seed_{seeds[i]}"
            s.save(outdir)
            with open(outdir / "convergence.json", "w") as f:
                json.dump(conv, f, indent=2)

        # Diagnostics
        samples = np.vstack([s.get_samples(burn=burn, flat=True) for s in samplers])
        pnames = samplers[0].prior.param_names(model)

        qs = {}
        for i, name in enumerate(pnames):
            q16, q50, q84 = np.percentile(samples[:, i], [16, 50, 84])
            qs[name] = {"median": float(q50), "q16": float(q16), "q84": float(q84)}

        kd = None
        if model == "g1_mkappa":
            ki, qi = pnames.index("kappa"), pnames.index("q")
            kv, qv = samples[:, ki], samples[:, qi]
            av = kv * qv
            k_hpd68 = np.percentile(kv, [16, 84])
            k_hpd95 = np.percentile(kv, [2.5, 97.5])
            kd = {
                "kappa_median": float(np.median(kv)),
                "F_kappa_le_075": float(np.mean(kv <= 0.75)),
                "kappa_hpd68": [float(k_hpd68[0]), float(k_hpd68[1])],
                "kappa_hpd95": [float(k_hpd95[0]), float(k_hpd95[1])],
                "status_075": ("central-compatible" if k_hpd68[0] <= 0.75 <= k_hpd68[1]
                              else "tail-compatible" if k_hpd95[0] <= 0.75 <= k_hpd95[1]
                              else "outside-95-HPD"),
                "alpha_median": float(np.median(av)),
                "alpha_hpd68": [float(np.percentile(av, 16)), float(np.percentile(av, 84))],
                "P_q_below_002": float(np.mean(qv < 0.02)),
            }

        result = {"model": model, "n_prod": int(total_prod), "converged": conv["converged"],
                  "R_hat_max": conv["R_hat_max"], "bulk_ESS": conv["bulk_ESS"],
                  "tail_ESS": conv["tail_ESS"], "quantiles": qs, "kappa_diagnostics": kd}
        all_results[model] = result

        print(f"\n  Summary ({model}):")
        for name in pnames:
            print(f"    {name:8s} {qs[name]['median']:.4f} [{qs[name]['q16']:.4f}, {qs[name]['q84']:.4f}]")
        if kd:
            print(f"    {'κ':8s} median={kd['kappa_median']:.3f} F(≤0.75)={kd['F_kappa_le_075']:.3f} {kd['status_075']}")
            print(f"    {'α':8s} median={kd['alpha_median']:.4f} [{kd['alpha_hpd68'][0]:.4f}, {kd['alpha_hpd68'][1]:.4f}]")
            print(f"    {'P(q<.02)':8s} {kd['P_q_below_002']:.4f}")

    with open(BASEDIR / "production_summary.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*70}")
    print(f"  PRODUCTION COMPLETE")
    print(f"  Summary: {BASEDIR}/production_summary.json")
    print(f"{'='*70}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
