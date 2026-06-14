#!/usr/bin/env python3
"""
Generate one-time truth cache for G1 ratio emulator.

Design: 800 training + 200 test + 50 special (Sobol nested sequence).
Initial prefix: 400 train + 80 test + 50 special (fast turn for first pass).
Subsequent prefixes can extend without resampling.

Outputs go to outputs/emulator_cache/ (gitignored).
Only manifest, SHA256, and mini benchmark (~20 pts) enter git.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import hashlib
import json
import time
import numpy as np

from cmb_lensing_precheck.mcmc import G1LensingRatio
from cmb_lensing_precheck.mcmc.emulator import _latin_hypercube
from cmb_lensing_precheck.mcmc.priors import PriorConfig

# ────────────────────────────────────────────────────────────────────────
# Configuration

N_TRAIN_FULL      = 800
N_TEST_FULL       = 200
N_SPECIAL         = 50   # design max (actual count from registry below)
N_TRAIN_INITIAL   = 400   # first pass prefix
N_TEST_INITIAL    = 80    # first pass prefix

# ── Explicit special-point registry ────────────────────────────────────
# These are NOT random. They cover null conditions, fiducial points,
# prior corners, and small-q asymptotics.
SPECIAL_POINTS = [
    # Exact nulls (q=0, s=3: must give R_L=1 regardless of kappa)
    [0.315, 0.674, 0.0, 0.0],    # ΛCDM null
    [0.315, 0.674, 0.0, 0.75],   # q=0, κ=0.75: R ≡ 1
    [0.300, 0.600, 0.0, 1.0],    # q=0, κ=1: R ≡ 1
    # Kappa=0 (Weyl null: R_Weyl ≡ 1)
    [0.315, 0.674, 0.5, 0.0],
    [0.300, 0.600, 0.8, 0.0],
    # Fiducial M3/4 (s=2.555, κ=0.75)
    [0.2966, 0.674, 0.445, 0.75],
    # Prior corners
    [0.15, 0.55, 0.0, 0.0],      # low Ω_m, low h, ΛCDM null
    [0.50, 0.85, 1.15, 1.0],     # high Ω_m, high h, high q, high κ
    [0.15, 0.85, 1.15, 0.0],     # low Ω_m, high h, high q, no Weyl
    [0.50, 0.55, 0.0, 1.0],      # high Ω_m, low h, ΛCDM null
    # Small-q asymptotics (approaching ΛCDM, lensing ratio continuous)
    [0.315, 0.674, 0.01, 0.75],
    [0.315, 0.674, 0.001, 0.75],
    [0.250, 0.650, 0.005, 0.50],
    # Compensation ridge (low Ω_m, moderate q, κ ~ 0.75)
    [0.20, 0.674, 0.4, 0.75],
    [0.25, 0.674, 0.3, 0.75],
]

AMPLITUDE_MODE    = "primordial"
RANDOM_SEED       = 42
ELL_STEP          = 1
N_Z               = 450
ELL_MIN           = 2
ELL_MAX           = 2998


def main():
    outdir = Path(__file__).parent.parent / "outputs" / "emulator_cache"
    outdir.mkdir(parents=True, exist_ok=True)

    prior = PriorConfig()

    engine_config = {
        "n_z": N_Z,
        "ell_step": ELL_STEP,
        "ell_min": ELL_MIN,
        "ell_max": ELL_MAX,
    }

    total_initial = N_TRAIN_INITIAL + N_TEST_INITIAL + N_SPECIAL

    print("=" * 70)
    print("  TRUTH CACHE GENERATION")
    print("=" * 70)
    print(f"  Design:         {N_TRAIN_FULL} train + {N_TEST_FULL} test + {N_SPECIAL} special")
    print(f"  Initial prefix: {N_TRAIN_INITIAL} train + {N_TEST_INITIAL} test + {N_SPECIAL} special")
    print(f"  Engine:         production (n_z={N_Z}, ΔL={ELL_STEP})")
    print(f"  Ell grid:       {ELL_MIN}..{ELL_MAX} ({ELL_MAX - ELL_MIN + 1} values)")
    print(f"  Amplitude mode: {AMPLITUDE_MODE}")
    print(f"  Seed:           {RANDOM_SEED}")
    print(f"  Output:         {outdir}")
    print("=" * 70)
    print()

    t0 = time.time()

    # ── Engine ──────────────────────────────────────────────────────────
    print("Initializing production-resolution engine...")
    engine = G1LensingRatio(amplitude_mode=AMPLITUDE_MODE)
    engine._base_cfg["integration"]["n_z"] = N_Z
    engine._base_cfg["integration"]["ell_step"] = ELL_STEP
    engine._base_cfg["integration"]["ell_min"] = ELL_MIN
    engine._base_cfg["integration"]["ell_max"] = ELL_MAX

    # ── Generate nested prefix design (train + test only) ────────────
    # Train/test from shuffled LHS with T_n ⊂ T_{n+1}.
    # Special points are separate, explicit register (not random).
    total_rand = N_TRAIN_FULL + N_TEST_FULL
    print(f"Generating {total_rand} nested prefix design samples (train + test only)...")
    np.random.seed(RANDOM_SEED)
    random_params = generate_nested_params(prior, total_rand)

    # Explicit special-point register
    special_params = list(SPECIAL_POINTS)
    n_special_computed = len(special_params)
    print(f"Special-point register: {n_special_computed} explicit points "
          f"(nulls, fiducial, corners, small-q)")

    n_total_initial = N_TRAIN_INITIAL + N_TEST_INITIAL + n_special_computed
    # all_params = train_prefix + test_prefix + special
    all_params = (list(random_params[:N_TRAIN_INITIAL + N_TEST_INITIAL])
                  + special_params)

    # ── Compute ratios ──────────────────────────────────────────────────
    ell = None
    R_total = []
    R_bg    = []
    R_Weyl  = []

    print(f"Computing truth ratios ({n_total_initial} points - initial prefix)...")
    for i in range(n_total_initial):
        Omega_m, h, q, kappa = all_params[i]
        if i % max(1, n_total_initial // 10) == 0:
            print(f"  [{i}/{n_total_initial}] ({time.time()-t0:.0f}s) "
                  f"Ω_m={Omega_m:.3f}, h={h:.3f}, q={q:.3f}, κ={kappa:.3f}")

        s = 3.0 - q
        result = engine.compute(Omega_m, h, s, kappa)

        if ell is None:
            ell = result.ell.copy()

        R_total.append(result.R_total.copy())
        R_bg.append(result.R_bg.copy())
        R_Weyl.append(result.R_Weyl.copy())

    t_gen = time.time() - t0
    n_computed = len(R_total)
    print(f"\nGeneration complete: {t_gen:.0f}s ({t_gen/n_computed:.1f}s/pt)")
    print()

    R_total_arr = np.array(R_total)
    R_bg_arr    = np.array(R_bg)
    R_Weyl_arr  = np.array(R_Weyl)
    params_arr  = np.array(all_params[:n_computed])

    # ── Partition ───────────────────────────────────────────────────────
    params_train   = params_arr[:N_TRAIN_INITIAL]
    params_test    = params_arr[N_TRAIN_INITIAL:N_TRAIN_INITIAL + N_TEST_INITIAL]
    params_special = params_arr[N_TRAIN_INITIAL + N_TEST_INITIAL:]

    assert len(params_train)   == N_TRAIN_INITIAL
    assert len(params_test)    == N_TEST_INITIAL
    assert len(params_special) == n_special_computed

    # Verify no overlap
    train_set = {tuple(p) for p in params_train}
    test_set  = {tuple(p) for p in params_test}
    spec_set  = {tuple(p) for p in params_special}
    assert len(train_set & test_set) == 0, "train/test overlap!"
    assert len(train_set & spec_set) == 0, "train/special overlap!"

    # ── Save arrays ─────────────────────────────────────────────────────
    print("Saving cache files...")
    np.save(outdir / "ell.npy", ell)
    np.save(outdir / "params_train.npy",   params_train)
    np.save(outdir / "params_test.npy",    params_test)
    np.save(outdir / "params_special.npy", params_special)

    r_idx = slice(N_TRAIN_INITIAL)
    t_idx = slice(N_TRAIN_INITIAL, N_TRAIN_INITIAL + N_TEST_INITIAL)
    s_idx = slice(N_TRAIN_INITIAL + N_TEST_INITIAL, n_computed)

    np.save(outdir / "R_total_train.npy",    R_total_arr[r_idx])
    np.save(outdir / "R_bg_train.npy",       R_bg_arr[r_idx])
    np.save(outdir / "R_Weyl_train.npy",     R_Weyl_arr[r_idx])

    np.save(outdir / "R_total_test.npy",     R_total_arr[t_idx])
    np.save(outdir / "R_bg_test.npy",        R_bg_arr[t_idx])
    np.save(outdir / "R_Weyl_test.npy",      R_Weyl_arr[t_idx])

    np.save(outdir / "R_total_special.npy",  R_total_arr[s_idx])
    np.save(outdir / "R_bg_special.npy",     R_bg_arr[s_idx])
    np.save(outdir / "R_Weyl_special.npy",   R_Weyl_arr[s_idx])

    # Fallback params for remaining 400 train + 120 test (zero-fill)
    remaining_train_test = N_TRAIN_FULL - N_TRAIN_INITIAL + N_TEST_FULL - N_TEST_INITIAL
    if remaining_train_test > 0:
        # Future params are from the un-computed random_params beyond train+test initial
        future_start = N_TRAIN_INITIAL + N_TEST_INITIAL
        future = random_params[future_start:future_start + remaining_train_test]
        np.save(outdir / "params_future.npy", future)
        print(f"  Saved {len(future)} future params for incremental extension")

    # ── Checksums ───────────────────────────────────────────────────────
    print("Computing SHA256 checksums...")
    checksums = {}
    for fname in sorted(outdir.glob("*.npy")):
        with open(fname, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        checksums[fname.name] = sha

    with open(outdir / "SHA256SUMS", "w") as f:
        for fname, sha in sorted(checksums.items()):
            f.write(f"{sha}  {fname}\n")

    # ── Manifest ────────────────────────────────────────────────────────
    manifest = {
        "description": "G1 ratio emulator truth cache",
        "cache_version": "1.0",
        "amplitude_mode": AMPLITUDE_MODE,
        "truth_resolution_class": "production",
        "engine_config": {
            "n_z": N_Z,
            "ell_step": ELL_STEP,
            "ell_min": ELL_MIN,
            "ell_max": ELL_MAX,
        },
        "neutrino_convention": "0.06 eV massive (N_ncdm=1, m_ncdm=0.06, N_ur=2.0328)",
        "normalization_convention": "code",
        "parameter_bounds": {
            "Omega_m": [prior.Omega_m_min, prior.Omega_m_max],
            "h":       [prior.h_min, prior.h_max],
            "q":       [prior.q_min, prior.q_max],
            "kappa":   [prior.kappa_min, prior.kappa_max],
        },
        "n_train_design":  N_TRAIN_FULL,
        "n_test_design":   N_TEST_FULL,
        "n_special":       n_special_computed,
        "n_train_current": N_TRAIN_INITIAL,
        "n_test_current":  N_TEST_INITIAL,
        "n_total_computed": n_computed,
        "n_ell":           len(ell),
        "ell_min":         int(ell[0]),
        "ell_max":         int(ell[-1]),
        "ell_step":        int(ELL_STEP),
        "sampling_method": "nested_prefix_design",
        "random_seed":     RANDOM_SEED,
        "generated_at":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generation_time_seconds": t_gen,
        "arrays": [],
        "checksums": checksums,
        "train_test_disjoint": True,
    }

    # Record array metadata
    for fname in sorted(outdir.glob("*.npy")):
        arr = np.load(fname)
        manifest["arrays"].append({
            "name": fname.name,
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
        })

    with open(outdir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # ── Mini benchmark subset (≤ 20 pts, for git) ──────────────────────
    mini_dir = outdir / "mini_benchmark"
    mini_dir.mkdir(exist_ok=True)
    mini_n = min(20, N_TRAIN_INITIAL)
    np.save(mini_dir / "params_mini.npy",    params_arr[:mini_n])
    np.save(mini_dir / "ell_mini.npy",       ell)
    np.save(mini_dir / "R_total_mini.npy",   R_total_arr[:mini_n])
    np.save(mini_dir / "R_bg_mini.npy",      R_bg_arr[:mini_n])
    np.save(mini_dir / "R_Weyl_mini.npy",    R_Weyl_arr[:mini_n])

    with open(mini_dir / "manifest.json", "w") as f:
        json.dump({"n_points": mini_n, "parent_cache": str(outdir.resolve())}, f, indent=2)

    # ── Summary ─────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"  CACHE GENERATED ({t_gen:.0f}s)")
    print(f"  Path:            {outdir}")
    print(f"  Points computed: {n_computed}")
    print(f"  Train:           {N_TRAIN_INITIAL} (design {N_TRAIN_FULL})")
    print(f"  Test:            {N_TEST_INITIAL}  (design {N_TEST_FULL})")
    print(f"  Special:         {n_special_computed} (explicit register)")
    print(f"  Ell:             {ell[0]}..{ell[-1]} ({len(ell)} values)")
    print(f"  Mini:            {mini_dir} ({mini_n} pts)")
    print()
    print(f"  Next: python scripts/validate_truth_cache.py")
    print(f"        python scripts/train_emulator_from_cache.py")
    print("=" * 70)

    return 0


def generate_nested_params(prior: PriorConfig, n_total: int) -> list:
    """
    Generate nested parameter samples using shuffled Latin hypercube.
    The sequence order guarantees that smaller prefixes are exact subsets.
    """
    unit_cube = _latin_hypercube(n_total, 4)

    # Deterministic permutation so that any prefix preserves Latin hypercube properties.
    rng = np.random.RandomState(RANDOM_SEED)
    order = np.arange(n_total)
    rng.shuffle(order)
    unit_cube = unit_cube[order]

    params = np.zeros((n_total, 4))
    params[:, 0] = unit_cube[:, 0] * (prior.Omega_m_max - prior.Omega_m_min) + prior.Omega_m_min
    params[:, 1] = unit_cube[:, 1] * (prior.h_max - prior.h_min) + prior.h_min
    params[:, 2] = unit_cube[:, 2] * (prior.q_max - prior.q_min) + prior.q_min
    params[:, 3] = unit_cube[:, 3] * (prior.kappa_max - prior.kappa_min) + prior.kappa_min

    return params.tolist()


if __name__ == "__main__":
    sys.exit(main())
