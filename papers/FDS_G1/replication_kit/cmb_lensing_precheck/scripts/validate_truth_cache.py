#!/usr/bin/env python3
"""
Validate truth cache integrity. EXIT CODE 1 ON ANY FAILURE.

Checks (all MUST pass):
  1. All files present and SHA256 match
  2. Parameter ranges within declared bounds
  3. Train / test / special sets disjoint
  4. Null tests: q=0 → R_total=1, kappa=0 → R_Weyl=1
  5. No NaN/Inf in any array
  6. All R values strictly positive
  7. Ell grid strictly monotonic
  8. Production-resolution flag present in manifest
  9. Array shapes consistent with manifest
  10. Coarse vs production resolution diagnostic comparison
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import hashlib
import json
import numpy as np

from cmb_lensing_precheck.mcmc import G1LensingRatio


def fail(msg: str):
    print(f"  ✗ {msg}")
    return False


def ok(msg: str):
    print(f"  ✓ {msg}")
    return True


def main():
    cachedir = Path(__file__).parent.parent / "outputs" / "emulator_cache"

    if not cachedir.exists():
        fail("Cache directory not found. Run generate_truth_cache.py first.")
        return 1

    print("=" * 70)
    print("  TRUTH CACHE VALIDATION")
    print("=" * 70)
    print()

    exit_code = 0

    # ── 1. Manifest/file integrity ──────────────────────────────────────
    print("1. File integrity (SHA256 + manifest)")

    if not (cachedir / "SHA256SUMS").exists():
        exit_code = 1
        fail("SHA256SUMS missing")
    elif not (cachedir / "manifest.json").exists():
        exit_code = 1
        fail("manifest.json missing")
    else:
        with open(cachedir / "SHA256SUMS") as f:
            expected = {}
            for line in f:
                parts = line.strip().split("  ")
                if len(parts) == 2:
                    expected[parts[1]] = parts[0]

        with open(cachedir / "manifest.json") as f:
            manifest = json.load(f)

        all_ok = True
        for fname in expected:
            fpath = cachedir / fname
            if not fpath.exists():
                all_ok = fail(f"MISSING: {fname}"); exit_code = 1
                continue
            with open(fpath, "rb") as f:
                actual = hashlib.sha256(f.read()).hexdigest()
            if actual != expected[fname]:
                all_ok = fail(f"HASH MISMATCH: {fname}"); exit_code = 1
        if all_ok:
            ok(f"All {len(expected)} files present with correct SHA256")

    print()

    # ── 2. Production resolution flag ───────────────────────────────────
    print("2. Resolution class check")

    res_class = manifest.get("truth_resolution_class", "unknown")
    is_production = res_class == "production"
    if is_production:
        ok(f"truth_resolution_class = {res_class}")
    else:
        exit_code = 1
        fail(f"truth_resolution_class = {res_class} (expected 'production')")

    engine_cfg = manifest.get("engine_config", {})
    print(f"    n_z={engine_cfg.get('n_z','?')}, "
          f"ΔL={engine_cfg.get('ell_step','?')}, "
          f"ell={engine_cfg.get('ell_min','?')}..{engine_cfg.get('ell_max','?')}")
    print()

    # ── 3. Construct arrays ─────────────────────────────────────────────
    print("3. Data loading and basic sanity")

    try:
        params_train   = np.load(cachedir / "params_train.npy")
        params_test    = np.load(cachedir / "params_test.npy")
        params_special = np.load(cachedir / "params_special.npy")
        ell            = np.load(cachedir / "ell.npy")
        R_total_train  = np.load(cachedir / "R_total_train.npy")
        R_bg_train     = np.load(cachedir / "R_bg_train.npy")
        R_Weyl_train   = np.load(cachedir / "R_Weyl_train.npy")
    except (FileNotFoundError, ValueError) as e:
        exit_code = 1
        fail(f"Load error: {e}")
        print("\n  CACHE VALIDATION FAILED ✗")
        return exit_code

    oks = 0
    failures = 0

    # NaN/Inf check
    all_arrays = {
        "params_train": params_train,
        "params_test": params_test,
        "params_special": params_special,
        "ell": ell,
        "R_total_train": R_total_train,
        "R_bg_train": R_bg_train,
        "R_Weyl_train": R_Weyl_train,
    }
    for name, arr in all_arrays.items():
        if np.any(~np.isfinite(arr)):
            exit_code = 1; failures += 1
            fail(f"NaN/Inf in {name}")
    if failures == 0:
        oks += 1; ok(f"No NaN/Inf in {len(all_arrays)} arrays")

    # R > 0
    for name in ["R_total_train", "R_bg_train", "R_Weyl_train"]:
        if np.any(all_arrays[name] <= 0):
            exit_code = 1; failures += 1
            fail(f"Non-positive values in {name}")
    if failures == oks - 1:
        oks += 1; ok("All R arrays strictly positive")

    # Ell grid monotonic
    if not np.all(np.diff(ell) > 0):
        exit_code = 1; failures += 1
        fail("Ell grid not strictly monotonic")
    else:
        oks += 1; ok(f"Ell grid monotonic: {ell[0]}..{ell[-1]} ({len(ell)} values)")

    print()

    # ── 4. Parameter range check ────────────────────────────────────────
    print("4. Parameter ranges")

    bounds = manifest.get("parameter_bounds", {})
    p_keys = ["Omega_m", "h", "q", "kappa"]
    p_arrays = [params_train, params_test, params_special]
    p_labels = ["train", "test", "special"]

    all_in_bounds = True
    for col, key in enumerate(p_keys):
        if key not in bounds:
            all_in_bounds = fail(f"Missing bounds for {key}"); exit_code = 1
            continue
        lo, hi = bounds[key]
        for arr, label in zip(p_arrays, p_labels):
            col_vals = arr[:, col]
            below = col_vals < lo
            above = col_vals > hi
            if np.any(below | above):
                all_in_bounds = fail(
                    f"{key} in {label}: min={col_vals.min():.4f}, max={col_vals.max():.4f} "
                    f"(bounds [{lo:.4f}, {hi:.4f}])"); exit_code = 1
            else:
                ok(f"{key} ({label}): [{col_vals.min():.4f}, {col_vals.max():.4f}] within bounds")

    print()

    # ── 5. Set disjointness ─────────────────────────────────────────────
    print("5. Set disjointness (train / test / special)")

    # Round to 6 decimal places for set comparison
    round_digits = 6
    train_set = {tuple(np.round(p, round_digits)) for p in params_train}
    test_set  = {tuple(np.round(p, round_digits)) for p in params_test}
    spec_set  = {tuple(np.round(p, round_digits)) for p in params_special}

    train_test_overlap = train_set & test_set
    train_spec_overlap = train_set & spec_set
    test_spec_overlap  = test_set & spec_set

    if train_test_overlap:
        exit_code = 1; fail(f"train/test overlap: {len(train_test_overlap)} shared points")
    else:
        ok(f"Train × Test: DISJOINT")

    if train_spec_overlap:
        exit_code = 1; fail(f"train/special overlap: {len(train_spec_overlap)} shared points")
    else:
        ok(f"Train × Special: DISJOINT")

    if test_spec_overlap:
        exit_code = 1; fail(f"test/special overlap: {len(test_spec_overlap)} shared points")
    else:
        ok(f"Test × Special: DISJOINT")

    print()

    # ── 6. Null tests on cached data (FAIL-CLOSED) ───────────────────────
    print("6. Null tests on cached data (special set must cover exact nulls)")

    R_total_special = np.load(cachedir / "R_total_special.npy")
    R_Weyl_special  = np.load(cachedir / "R_Weyl_special.npy")

    # Exact q=0 check (special set MUST have q=0 points)
    q_zero_mask = np.abs(params_special[:, 2]) < 0.001
    if not np.any(q_zero_mask):
        exit_code = 1
        fail("exact q=0 null: FAILED - special set contains no q=0 points")
    else:
        max_err = float(np.max(np.abs(R_total_special[q_zero_mask] - 1.0)))
        if max_err < 1e-8:
            ok(f"exact q=0 null: max|R-1| = {max_err:.2e} "
               f"({np.sum(q_zero_mask)} special points)")
        else:
            exit_code = 1
            fail(f"exact q=0 null: FAILED - max|R-1| = {max_err:.2e} (threshold 1e-8)")

    # Exact kappa=0 check (special set MUST have kappa=0 points)
    k_zero_mask = np.abs(params_special[:, 3]) < 0.001
    if not np.any(k_zero_mask):
        exit_code = 1
        fail("exact kappa=0 null: FAILED - special set contains no kappa=0 points")
    else:
        max_err = float(np.max(np.abs(R_Weyl_special[k_zero_mask] - 1.0)))
        if max_err < 1e-8:
            ok(f"exact kappa=0 null: max|R_Weyl-1| = {max_err:.2e} "
               f"({np.sum(k_zero_mask)} special points)")
        else:
            exit_code = 1
            fail(f"exact kappa=0 null: FAILED - max|R_Weyl-1| = {max_err:.2e} (threshold 1e-8)")

    # Asymptotic scaling check (training set small-q/q and small-kappa/kappa)
    q_small = (params_train[:, 2] > 0) & (params_train[:, 2] < 0.05)
    if np.any(q_small):
        q_vals = params_train[q_small, 2]
        R_errs = np.max(np.abs(R_total_train[q_small] - 1.0), axis=1)
        ratio = np.max(R_errs / np.maximum(q_vals, 1e-12))
        ok(f"q→0 scaling: max|R-1|/q = {ratio:.2f}")
        if ratio > 10.0:
            exit_code = 1
            fail(f"q→0 scaling anomaly: {ratio:.2f} > 10")

    k_small = (params_train[:, 3] > 0) & (params_train[:, 3] < 0.05)
    if np.any(k_small):
        k_vals = params_train[k_small, 3]
        W_errs = np.max(np.abs(R_Weyl_train[k_small] - 1.0), axis=1)
        ratio = np.max(W_errs / np.maximum(k_vals, 1e-12))
        ok(f"kappa→0 scaling: max|R_Weyl-1|/kappa = {ratio:.2f}")
        if ratio > 10.0:
            exit_code = 1
            fail(f"kappa→0 scaling anomaly: {ratio:.2f} > 10")

    # R_total = R_bg * R_Weyl reconstruction
    max_recon_err = float(np.max(np.abs(R_total_train - R_bg_train * R_Weyl_train)))
    if max_recon_err < 1e-12:
        ok(f"R_total = R_bg * R_Weyl: max err = {max_recon_err:.2e}")
    else:
        exit_code = 1
        fail(f"R_total = R_bg * R_Weyl: max err = {max_recon_err:.2e} (threshold 1e-12)")

    print()

    # ── 7. Array shape consistency ──────────────────────────────────────
    print("7. Array shape consistency")

    arrays_info = manifest.get("arrays", [])
    for info in arrays_info:
        fname = info["name"]
        fpath = cachedir / fname
        if not fpath.exists():
            continue
        arr = np.load(fpath)
        expected_shape = tuple(info["shape"])
        actual_shape = arr.shape
        if actual_shape != expected_shape:
            exit_code = 1
            fail(f"Shape mismatch for {fname}: expected {expected_shape}, got {actual_shape}")
        else:
            ok(f"{fname}: shape={actual_shape}, dtype={arr.dtype}")

    print()

    # ── 8. Coarse vs production resolution comparison (diagnostic) ──────
    print("8. Coarse-resolution engine comparison (informational)")

    engine_coarse = G1LensingRatio(amplitude_mode=manifest["amplitude_mode"])
    engine_coarse._base_cfg["integration"]["n_z"] = 200
    engine_coarse._base_cfg["integration"]["ell_step"] = 4

    n_compare = min(10, len(params_test))
    np.random.seed(999)
    idx = np.random.choice(len(params_test), n_compare, replace=False)

    max_ratio_err = 0.0
    rms_ratio_err2 = 0.0

    for i in idx:
        Omega_m, h, q, kappa = params_test[i]
        s = 3.0 - q
        result = engine_coarse.compute(Omega_m, h, s, kappa)
        R_coarse = np.interp(
            ell.astype(float), result.ell.astype(float), result.R_total,
            left=1.0, right=1.0,
        )
        R_prod = np.load(cachedir / "R_total_test.npy")[i]
        ratio_err = (R_coarse - R_prod) / np.maximum(R_prod, 1e-30)
        max_ratio_err = max(max_ratio_err, np.max(np.abs(ratio_err)))
        rms_ratio_err2 += np.mean(ratio_err ** 2)

    rms_pct = np.sqrt(rms_ratio_err2 / n_compare) * 100
    max_pct = max_ratio_err * 100

    print(f"    Coarse (n_z=200,ΔL=4) vs production (n_z={engine_cfg.get('n_z','?')},"
          f"ΔL={engine_cfg.get('ell_step','?')})")
    print(f"    RMS = {rms_pct:.4f}%, max = {max_pct:.4f}%")
    if rms_pct < 0.05:
        ok("Coarse/full RMS << 0.05% total error budget")
    else:
        print(f"    ⚠  WARNING: contributes non-trivially to total error budget")

    print()

    # ── Summary ─────────────────────────────────────────────────────────
    print("=" * 70)
    if exit_code == 0:
        print("  CACHE VALIDATION PASSED ✓")
        print(f"  Ready: python scripts/train_emulator_from_cache.py")
    else:
        print("  CACHE VALIDATION FAILED ✗")
        print(f"  Fix issues before using this cache.")
    print("=" * 70)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
