#!/usr/bin/env python3
"""
Step 3.2: Generate 2D ΛCDM baseline truth cache.

Sobol-scrambled sampling in (Ω_m, h).
Fixed A_s reference: ln10As = 3.044 (Planck 2018 best-fit).
CLASS computes C_L^κκ once per (Ω_m, h) pair.
Saves log(C_L^κκ) for numerical stability in PCA training.

Outputs: outputs/baseline_emulator_cache/
"""

import sys, json, hashlib, time, numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cmb_lensing_precheck.mcmc.likelihood import LensingLikelihood
from cmb_lensing_precheck.mcmc.priors import PriorConfig

N_TRAIN = 200
N_TEST = 80
N_SPECIAL = 16
RANDOM_SEED = 42
LN10AS_REF = 3.044
OUTDIR = Path(__file__).parent.parent / "outputs" / "baseline_emulator_cache"

# ── Special points ─────────────────────────────────────────────────────
SPECIAL_POINTS = [
    # Fiducial + pilot centers
    (0.315, 0.674),   # Planck 2018 fiducial
    (0.337, 0.664),   # LCDM pilot center (avg both seeds)
    (0.301, 0.687),   # g1_m34 pilot center
    (0.313, 0.668),   # g1_bg pilot center (avg)
    # Prior corners
    (0.15, 0.55),
    (0.50, 0.85),
    (0.15, 0.85),
    (0.50, 0.55),
    # Low-Ω_m compensation region
    (0.20, 0.674),
    (0.25, 0.674),
    # High/low h extremes
    (0.315, 0.60),
    (0.315, 0.80),
    # g1_mkappa pilot center
    (0.307, 0.668),
    # Additional coverage
    (0.40, 0.60),
    (0.20, 0.75),
    (0.45, 0.70),
]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    prior = PriorConfig()
    print("=" * 70)
    print("  2D ΛCDM BASELINE TRUTH CACHE")
    print("=" * 70)
    print(f"  N_train:   {N_TRAIN}")
    print(f"  N_test:    {N_TEST}")
    print(f"  N_special: {len(SPECIAL_POINTS)}")
    print(f"  ln10As:    {LN10AS_REF}")
    print(f"  Ω_m:       [{prior.Omega_m_min}, {prior.Omega_m_max}]")
    print(f"  h:         [{prior.h_min}, {prior.h_max}]")
    print(f"  Output:    {OUTDIR}")
    print("=" * 70)
    print()

    # ── Sobol sampling ──────────────────────────────────────────────────
    from scipy.stats import qmc
    total_random = N_TRAIN + N_TEST
    sampler = qmc.Sobol(d=2, scramble=True, seed=RANDOM_SEED)
    sobol = sampler.random(total_random)

    Om = sobol[:, 0] * (prior.Omega_m_max - prior.Omega_m_min) + prior.Omega_m_min
    hh = sobol[:, 1] * (prior.h_max - prior.h_min) + prior.h_min

    train_params = np.column_stack([Om[:N_TRAIN], hh[:N_TRAIN]])
    test_params = np.column_stack([Om[N_TRAIN:N_TRAIN+N_TEST], hh[N_TRAIN:N_TRAIN+N_TEST]])
    special_params = np.array(SPECIAL_POINTS)

    all_params = np.vstack([train_params, test_params, special_params])
    n_total = len(all_params)

    # ── Compute CLASS spectra ──────────────────────────────────────────
    print(f"Computing CLASS C_L^κκ for {n_total} points...")
    like = LensingLikelihood("act_baseline", amplitude_param="ln10As")
    ell = None
    logCL = []

    t0 = time.time()
    for i, (Omega_m, h) in enumerate(all_params):
        if i % max(1, n_total // 10) == 0:
            print(f"  [{i}/{n_total}] ({time.time()-t0:.0f}s) Om={Omega_m:.3f} h={h:.3f}")

        cl = like._compute_clkk_lcdm(Omega_m, h, ln10As=LN10AS_REF)
        if cl is None:
            print(f"  ERROR: CLASS failed for Om={Omega_m}, h={h}")
            sys.exit(1)

        if ell is None:
            ell = np.arange(len(cl))

        logCL.append(np.log(np.maximum(cl, 1e-40)))

    t_gen = time.time() - t0
    logCL_arr = np.array(logCL)

    logCL_train   = logCL_arr[:N_TRAIN]
    logCL_test    = logCL_arr[N_TRAIN:N_TRAIN+N_TEST]
    logCL_special = logCL_arr[N_TRAIN+N_TEST:]

    # ── Save ───────────────────────────────────────────────────────────
    print("\nSaving...")
    np.save(OUTDIR / "ell.npy", ell)
    np.save(OUTDIR / "params_train.npy", train_params)
    np.save(OUTDIR / "params_test.npy", test_params)
    np.save(OUTDIR / "params_special.npy", special_params)
    np.save(OUTDIR / "logCL_train.npy", logCL_train)
    np.save(OUTDIR / "logCL_test.npy", logCL_test)
    np.save(OUTDIR / "logCL_special.npy", logCL_special)

    # SHA256
    checksums = {}
    for fname in sorted(OUTDIR.glob("*.npy")):
        with open(fname, "rb") as f:
            checksums[fname.name] = hashlib.sha256(f.read()).hexdigest()
    with open(OUTDIR / "SHA256SUMS", "w") as f:
        for fn, sha in sorted(checksums.items()):
            f.write(f"{sha}  {fn}\n")

    # Manifest
    manifest = {
        "description": "2D ΛCDM baseline C_L^κκ emulator truth cache",
        "cache_version": "1.0",
        "ln10As_ref": LN10AS_REF,
        "A_s_ref": float(1e-10 * np.exp(LN10AS_REF)),
        "A_s_scaling": "linear — verified to machine precision",
        "parameter_bounds": {
            "Omega_m": [prior.Omega_m_min, prior.Omega_m_max],
            "h": [prior.h_min, prior.h_max],
        },
        "n_train": N_TRAIN, "n_test": N_TEST,
        "n_special": len(SPECIAL_POINTS),
        "n_ell": len(ell), "ell_min": 0, "ell_max": len(ell)-1,
        "sampling": "scrambled_sobol", "random_seed": RANDOM_SEED,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generation_time_s": round(t_gen, 1),
        "checksums": checksums,
        "arrays": [{"name": f.name, "shape": list(np.load(f).shape),
                     "dtype": str(np.load(f).dtype)}
                    for f in sorted(OUTDIR.glob("*.npy"))],
    }
    with open(OUTDIR / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*70}")
    print(f"  CACHE GENERATED ({t_gen:.0f}s)")
    print(f"  Path:    {OUTDIR}")
    print(f"  Points:  {n_total} ({N_TRAIN} train + {N_TEST} test + {len(SPECIAL_POINTS)} special)")
    print(f"  Next:    build and validate baseline emulator")
    print(f"{'='*70}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
