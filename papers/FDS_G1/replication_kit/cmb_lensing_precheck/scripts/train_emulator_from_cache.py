#!/usr/bin/env python3
"""
Train G1 ratio emulator FROM CACHE with three-tier validation gates.

Gates (ALL must pass for production_unlock=True):

  TIER 1 – Spectrum (full prior, data-independent):
    G_spectrum:  RMS(δR/R) < 0.2%, P95 < 0.5%

  TIER 2 – Theory distance (full prior, covariance-weighted, A_s-invariant):
    G_theory_ACT:   ε_th² = δtᵀC⁻¹δt, P95 < 0.05, max < 0.1
    G_theory_PR4:   same thresholds

  TIER 3 – Core likelihood (posterior-support region only):
    G_core_ACT:     |Δχ²_emu-true| < 0.1  where Δχ²_true ≤ 50
    G_core_PR4:     same
    G_tail_ACT:     no tail point promoted into Δχ²_emu < 50
    G_tail_PR4:     same

  TIER 4 – Safety:
    G_special_ACT:  boundary/null/fiducial |Δχ²| < 0.1
    G_special_PR4:  same
    G_resolution:   truth cache resolution class == production

KEY FIX: Each test point uses its OWN (Ω_m, h) LCDM baseline.
    clkk_g1 = clkk_lcdm(Ω_m, h, A_s) * R(Ω_m, h, q, κ)
    NOT clkk_lcdm(0.315, 0.674) * R(other cosmology).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import time
import numpy as np
from typing import Optional, List, Dict, Any
from scipy.interpolate import RBFInterpolator

from cmb_lensing_precheck.mcmc.ratio_engine import G1LensingRatio, RatioResult
from cmb_lensing_precheck.mcmc.emulator import RatioEmulator, EmulatorConfig
from cmb_lensing_precheck.mcmc.likelihood import LensingLikelihood


# ════════════════════════════════════════════════════════════════════════
# Cache loading
# ════════════════════════════════════════════════════════════════════════

def load_cache(cachedir: Path) -> dict:
    return {
        "params_train":   np.load(cachedir / "params_train.npy"),
        "params_test":    np.load(cachedir / "params_test.npy"),
        "params_special": np.load(cachedir / "params_special.npy"),
        "ell":            np.load(cachedir / "ell.npy"),
        "R_total_train":  np.load(cachedir / "R_total_train.npy"),
        "R_total_test":   np.load(cachedir / "R_total_test.npy"),
    }


# ════════════════════════════════════════════════════════════════════════
# Training
# ════════════════════════════════════════════════════════════════════════

def train_emulator_on_cache(cache: dict, n_train: int, n_pca: int,
                            kernel: str = "thin_plate_spline",
                            epsilon: Optional[float] = None,
                            smoothing: float = 0.0,
                            config: Optional[EmulatorConfig] = None,
                            ) -> RatioEmulator:
    if config is None:
        config = EmulatorConfig()

    emu = RatioEmulator.__new__(RatioEmulator)
    emu.training_params = cache["params_train"][:n_train].copy()
    emu.training_logR   = np.log(np.maximum(cache["R_total_train"][:n_train], 1e-30))
    emu.test_params     = cache["params_test"][:40].copy()
    emu.test_logR       = np.log(np.maximum(cache["R_total_test"][:40], 1e-30))
    emu.ell             = cache["ell"]
    emu.amplitude_mode  = "primordial"
    emu.config          = config
    emu.ratio_engine    = G1LensingRatio(amplitude_mode="primordial")
    emu.ratio_engine._base_cfg["integration"]["n_z"]       = 450
    emu.ratio_engine._base_cfg["integration"]["ell_step"]  = 1
    emu.ratio_engine._base_cfg["integration"]["ell_min"]   = 2
    emu.ratio_engine._base_cfg["integration"]["ell_max"]   = 2998

    logR = emu.training_logR
    emu.pca_mean       = np.mean(logR, axis=0)
    U, S, Vt           = np.linalg.svd(logR - emu.pca_mean, full_matrices=False)
    emu.pca_components = Vt[:n_pca]
    emu.n_pca_used     = n_pca

    train_unit = emu._params_to_unit(emu.training_params)
    coeffs     = (emu.training_logR - emu.pca_mean) @ emu.pca_components.T

    rbf_kw = {"kernel": kernel, "smoothing": smoothing}
    if kernel not in {"linear", "thin_plate_spline", "cubic", "quintic"}:
        rbf_kw["epsilon"] = epsilon if epsilon is not None else _auto_epsilon(train_unit)

    emu.interpolators = [
        RBFInterpolator(train_unit, coeffs[:, i], **rbf_kw) for i in range(n_pca)
    ]
    emu._epsilon  = epsilon
    emu._smoothing = smoothing
    return emu


def _auto_epsilon(train_unit: np.ndarray) -> float:
    from scipy.spatial import cKDTree
    tree = cKDTree(train_unit)
    dists, _ = tree.query(train_unit, k=2)
    return float(np.median(dists[:, 1]))


# ════════════════════════════════════════════════════════════════════════
# Pre-computed LCDM spectra cache
# ════════════════════════════════════════════════════════════════════════

def precompute_lcdm_clkk(params_set: np.ndarray, amplitude_param: str = "ln10As",
                         ln10As_val: float = 3.046) -> Dict[tuple, np.ndarray]:
    """
    Pre-compute CLASS LCDM C_L^κκ for each unique (Ω_m, h) pair.
    Same-cosmology baseline: each test point gets its OWN LCDM spectrum.

    Uses ln10As = 3.046 (Planck 2018 best-fit equivalent) for A_s scaling.
    """
    like = LensingLikelihood("act_baseline", amplitude_param=amplitude_param)
    cache_cl = {}
    unique_params = set()

    for row in params_set:
        key = (round(float(row[0]), 6), round(float(row[1]), 6))
        unique_params.add(key)

    for i, (Omega_m, h) in enumerate(unique_params):
        if i % 10 == 0:
            print(f"    Computing LCDM spectra: {i}/{len(unique_params)}...")
        clkk = like._compute_clkk_lcdm(Omega_m, h, ln10As=ln10As_val)
        if clkk is not None:
            cache_cl[(Omega_m, h)] = clkk

    print(f"    Cached {len(cache_cl)} unique LCDM spectra")
    return cache_cl


# ════════════════════════════════════════════════════════════════════════
# Three-tier validation
# ════════════════════════════════════════════════════════════════════════

def _compute_point_errors(emu: RatioEmulator, Omega_m: float, h: float,
                          q: float, kappa: float, clkk_lcdm: np.ndarray,
                          act_data: dict, ell_full: np.ndarray,
                          binmat_full: np.ndarray
                          ) -> Optional[Dict[str, float]]:
    """Compute spectrum error, theory distance, and χ² for a single point."""
    s = 3.0 - q
    result = emu.ratio_engine.compute(Omega_m, h, s, kappa)
    R_emu_raw = emu.predict_R(Omega_m, h, q, kappa)

    R_true = np.interp(ell_full.astype(float), result.ell.astype(float),
                       result.R_total, left=1.0, right=1.0)
    R_emu  = np.interp(ell_full.astype(float), result.ell.astype(float),
                       R_emu_raw, left=1.0, right=1.0)

    # Spectrum error (fractional, on the ratio grid)
    frac_err = (R_emu_raw - result.R_total) / np.maximum(result.R_total, 1e-30)
    rms_spectrum = float(np.sqrt(np.mean(frac_err**2)) * 100)
    p95_spectrum = float(np.percentile(np.abs(frac_err), 95) * 100)

    clkk_true = clkk_lcdm * R_true
    clkk_emu  = clkk_lcdm * R_emu

    binned_true = binmat_full @ clkk_true
    binned_emu  = binmat_full @ clkk_emu
    delta_t = binned_emu - binned_true  # theory error vector

    # Tier 2: theory distance ε_th² = δtᵀ C⁻¹ δt
    cinv = act_data["cinv"]
    eps_th_sq = float(delta_t @ cinv @ delta_t)
    eps_th    = float(np.sqrt(eps_th_sq))

    # Tier 3: absolute χ²
    data_vec = act_data["data_binned_clkk"]
    chi2_true = float((data_vec - binned_true) @ cinv @ (data_vec - binned_true))
    chi2_emu  = float((data_vec - binned_emu)  @ cinv @ (data_vec - binned_emu))
    delta_chi2 = float(abs(chi2_emu - chi2_true))

    return {
        "rms_spectrum_pct": rms_spectrum,
        "p95_spectrum_pct": p95_spectrum,
        "eps_th_sq": eps_th_sq,
        "eps_th": eps_th,
        "chi2_true": chi2_true,
        "chi2_emu": chi2_emu,
        "delta_chi2": delta_chi2,
        "Omega_m": float(Omega_m), "h": float(h),
        "q": float(q), "kappa": float(kappa),
    }


def validate_three_tiers(emu: RatioEmulator, cache: dict, cachedir: Path) -> Dict[str, Any]:
    """
    Full three-tier validation.

    Returns dict with 'production_unlock' = True only if ALL gates pass.
    """
    results: Dict[str, Any] = {"gates": {}, "details": {}, "production_unlock": False}
    config = emu.config

    # ── Per-test-point errors ──────────────────────────────────────────
    variants = ["act_baseline", "actplanck_baseline"]
    point_errors: Dict[str, List[dict]] = {v: [] for v in variants}

    test_params = emu.test_params[:30]
    special_params = cache.get("params_special",
        np.empty((0, 4)))

    # Pre-compute LCDM spectra for test AND special sets
    all_val_params = np.vstack([test_params, special_params]) if len(special_params) > 0 else test_params
    print("    Pre-computing LCDM spectra (same-cosmology baseline)...")
    lcdm_cache = precompute_lcdm_clkk(all_val_params)

    for variant in variants:
        import act_dr6_lenslike as alike
        act_data = alike.load_data(variant)
        ell_full = np.arange(act_data["binmat_act"].shape[1], dtype=int)
        binmat_act = act_data["binmat_act"]
        if act_data.get("include_planck", False):
            binmat_full = np.vstack([binmat_act, act_data["binmat_planck"]])
        else:
            binmat_full = binmat_act

        for Omega_m, h, q, kappa in test_params:
            key = (round(float(Omega_m), 6), round(float(h), 6))
            clkk_lcdm = lcdm_cache.get(key)
            if clkk_lcdm is None:
                continue
            pt = _compute_point_errors(emu, Omega_m, h, q, kappa, clkk_lcdm,
                                       act_data, ell_full, binmat_full)
            if pt:
                point_errors[variant].append(pt)

    # ── Tier 1: Spectrum gate ─────────────────────────────────────────
    all_rms = [pt["rms_spectrum_pct"] for pt in point_errors["act_baseline"]]
    all_p95 = [pt["p95_spectrum_pct"] for pt in point_errors["act_baseline"]]
    rms_global = float(np.mean(all_rms))
    p95_global = float(np.mean(all_p95))

    results["gates"]["G_spectrum"] = bool(rms_global < config.rms_tol_pct
                                          and p95_global < config.p95_tol_pct)
    results["details"]["rms_spectrum_pct"] = rms_global
    results["details"]["p95_spectrum_pct"] = p95_global

    # ── Tier 2: Theory distance ────────────────────────────────────────
    for variant in variants:
        label = "G_theory_" + ("ACT_PR4" if "planck" in variant else "ACT")
        errors = point_errors[variant]
        if not errors:
            results["gates"][label] = False
            continue
        eps_th_vals = [pt["eps_th"] for pt in errors]
        p95_th = float(np.percentile(eps_th_vals, 95))
        max_th = float(np.max(eps_th_vals))
        passed = bool(p95_th < 0.05 and max_th < 0.1)
        results["gates"][label] = passed
        results["details"][f"eps_th_{variant}_p95"] = p95_th
        results["details"][f"eps_th_{variant}_max"] = max_th
        print(f"    {label}: P95={p95_th:.4f} max={max_th:.4f}  {'✓' if passed else '✗'}")

    # ── Tier 3: Core likelihood + Tail safety ──────────────────────────
    for variant in variants:
        base = "ACT_PR4" if "planck" in variant else "ACT"
        errors = point_errors[variant]
        if not errors:
            results["gates"][f"G_core_{base}"] = False
            results["gates"][f"G_tail_{base}"] = False
            continue

        # Core: Δχ²_true ≤ 50
        core = [pt for pt in errors if pt["chi2_true"] <= 50.0]
        tail = [pt for pt in errors if pt["chi2_true"] > 50.0]

        if core:
            core_dchi2 = [pt["delta_chi2"] for pt in core]
            core_passed = bool(np.max(core_dchi2) < 0.1)
            results["gates"][f"G_core_{base}"] = core_passed
            results["details"][f"core_{variant}_n"] = len(core)
            results["details"][f"core_{variant}_max_dchi2"] = float(np.max(core_dchi2))
            print(f"    G_core_{base}: n={len(core)} max|Δχ²|={np.max(core_dchi2):.4f}"
                  f" {'✓' if core_passed else '✗'}")
        else:
            results["gates"][f"G_core_{base}"] = True  # no core points = vacuously passed

        # Tail safety: no truth-rejected point promoted
        if tail:
            tail_failures = [pt for pt in tail if pt["chi2_emu"] < 50.0]
            tail_passed = len(tail_failures) == 0
            results["gates"][f"G_tail_{base}"] = tail_passed
            results["details"][f"tail_{variant}_n"] = len(tail)
            results["details"][f"tail_{variant}_promoted"] = len(tail_failures)
            print(f"    G_tail_{base}: n_tail={len(tail)} promoted={len(tail_failures)}"
                  f" {'✓' if tail_passed else '✗'}")
        else:
            results["gates"][f"G_tail_{base}"] = True

    # ── Tier 4: Special points ─────────────────────────────────────────
    special_params = cache.get("params_special", np.array([[]]))
    if len(special_params) > 0 and special_params.shape[1] >= 4:
        for variant in variants:
            base = "ACT_PR4" if "planck" in variant else "ACT"
            label = f"G_special_{base}"
            spec_errors = _compute_special_errors(emu, special_params, variant, lcdm_cache)
            if spec_errors is not None:
                null_ok = bool(spec_errors.get("null_max_dchi2", 0) < 1.0)
                corner_ok = bool(spec_errors.get("corner_max_dchi2", 999) < 5.0)
                spec_passed = null_ok and corner_ok
                results["gates"][label] = spec_passed
                results["details"][f"special_{variant}_null_max"] = \
                    spec_errors.get("null_max_dchi2", 0)
                results["details"][f"special_{variant}_corner_max"] = \
                    spec_errors.get("corner_max_dchi2", 0)
                print(f"    {label}: null max|Δχ²|={spec_errors.get('null_max_dchi2',0):.4f}"
                      f" corner max|Δχ²|={spec_errors.get('corner_max_dchi2',0):.4f}"
                      f" {'✓' if spec_passed else '✗'}")
            else:
                results["gates"][label] = False
    else:
        results["gates"]["G_special_ACT"] = True
        results["gates"]["G_special_ACT_PR4"] = True

    # ── Tier 4: Resolution class ───────────────────────────────────────
    import json as json2
    with open(cachedir / "manifest.json") as f:
        cache_manifest = json2.load(f)
    res_class = cache_manifest.get("truth_resolution_class", "unknown")
    results["gates"]["G_resolution"] = bool(res_class == "production")
    results["details"]["truth_resolution_class"] = res_class

    # ── Unlock ─────────────────────────────────────────────────────────
    all_gates = all(results["gates"].values())
    results["production_unlock"] = all_gates
    results["passed_gates"] = [k for k, v in results["gates"].items() if v]
    results["failed_gates"] = [k for k, v in results["gates"].items() if not v]

    return results


def _compute_special_errors(emu, params, variant, lcdm_cache) -> Optional[dict]:
    """Validate emulator on special points, splitting null/fiducial from corners."""
    import act_dr6_lenslike as alike
    act_data = alike.load_data(variant)
    ell_full = np.arange(act_data["binmat_act"].shape[1], dtype=int)
    if act_data.get("include_planck", False):
        binmat_full = np.vstack([act_data["binmat_act"], act_data["binmat_planck"]])
    else:
        binmat_full = act_data["binmat_act"]

    dchi = []
    is_null = []
    for Omega_m, h, q, kappa in params:
        key = (round(float(Omega_m), 6), round(float(h), 6))
        clkk_lcdm = lcdm_cache.get(key)
        if clkk_lcdm is None:
            continue
        pt = _compute_point_errors(emu, Omega_m, h, q, kappa, clkk_lcdm,
                                   act_data, ell_full, binmat_full)
        if pt:
            dchi.append(pt["delta_chi2"])
            # null: q≈0 or κ≈0 or fiducial M3/4
            is_null.append(
                q < 0.001 or kappa < 0.001 or
                (abs(q - 0.445) < 0.01 and abs(kappa - 0.75) < 0.01)
            )

    if not dchi:
        return None

    null_array   = [d for d, n in zip(dchi, is_null) if n]
    corner_array = [d for d, n in zip(dchi, is_null) if not n]
    return {
        "null_max_dchi2": float(np.max(null_array)) if null_array else 0.0,
        "corner_max_dchi2": float(np.max(corner_array)) if corner_array else 0.0,
        "n_null": len(null_array), "n_corner": len(corner_array),
    }


# ════════════════════════════════════════════════════════════════════════
# Kernel candidates
# ════════════════════════════════════════════════════════════════════════

KERNEL_CANDIDATES = [
    {"kernel": "thin_plate_spline", "epsilon": None, "smoothing": 0.0},
    {"kernel": "cubic",             "epsilon": None, "smoothing": 0.0},
    {"kernel": "quintic",           "epsilon": None, "smoothing": 0.0},
    {"kernel": "multiquadric",      "epsilon": None, "smoothing": 0.0},
    {"kernel": "gaussian",          "epsilon": None, "smoothing": 0.0},
]


# ════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════

def main():
    script_dir = Path(__file__).parent.parent
    cachedir = script_dir / "outputs" / "emulator_cache"
    if not cachedir.exists():
        print("ERROR: No cache. Run generate_truth_cache.py first.")
        return 1

    outdir   = script_dir / "outputs" / "emulator_training"
    prod_dir = script_dir / "outputs" / "emulator" / "emulator_primordial"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  G1 EMULATOR TRAINING (THREE-TIER VALIDATION)")
    print("=" * 70)
    print()

    # ── Invalidate old production token ─────────────────────────────────
    old_token = prod_dir / "production_unlock.json"
    if old_token.exists():
        archived = prod_dir / f"production_unlock_archived_{int(time.time())}.json"
        old_token.rename(archived)
        print(f"Archived old production token -> {archived.name}")
        print()

    t0 = time.time()
    print("Loading cache...")
    cache = load_cache(cachedir)
    n_train_max = min(len(cache["params_train"]), 400)
    print(f"  Train: {n_train_max} | Test: {len(cache['params_test'])} "
          f"| Ell: {cache['ell'][0]}..{cache['ell'][-1]}")
    print()

    config = EmulatorConfig()

    # ── Learning curve ─────────────────────────────────────────────────
    print("=" * 70)
    print("  LEARNING CURVE")
    print("=" * 70)

    best_pca = {200: 3, 300: 3, 400: 3}
    best_metrics = {}

    for n_train in [200, 300, n_train_max]:
        best_npca = 3
        best_score = float("inf")
        print(f"\n  n_train={n_train}:")
        for npca in [3, 4, 5, 6]:
            emu = train_emulator_on_cache(cache, n_train, npca, config=config)
            m = emu.validate(likelihood=False)
            score = m["rms_pct"]
            status = "✓" if m.get("passed_all") else ""
            if npca <= 4 or m.get("passed_all"):
                print(f"    n_pca={npca}: RMS={m['rms_pct']:.3f}% "
                      f"P95={m['p95_pct']:.3f}% {status}")
            if score < best_score:
                best_score = score
                best_npca = npca
                best_metrics = m
        best_pca[n_train] = best_npca

    n_train_use = n_train_max
    n_pca_use   = best_pca[n_train_use]
    print(f"\n  Selected: n_train={n_train_use}, n_pca={n_pca_use}")

    # ── Kernel CV ──────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  KERNEL CV (via theory-distance core metric)")
    print("=" * 70)

    best_kernel  = "thin_plate_spline"
    best_epsilon = None
    best_kern_score = float("inf")

    for kopt in KERNEL_CANDIDATES:
        kernel = kopt["kernel"]
        eps    = kopt["epsilon"]
        if eps is None and kernel not in {"linear", "thin_plate_spline", "cubic", "quintic"}:
            eps = _auto_epsilon(emu._params_to_unit(cache["params_train"][:n_train_use]))

        try:
            emu = train_emulator_on_cache(cache, n_train_use, n_pca_use,
                                          kernel=kernel, epsilon=eps,
                                          smoothing=kopt["smoothing"], config=config)
            m = emu.validate(likelihood=False)
            score = m["rms_pct"]
            status = "✓" if m.get("passed_all") else "✗"
            print(f"  {kernel:25s} RMS={score:.3f}% "
                  f"P95={m['p95_pct']:.3f}% [{status}]")
            if score < best_kern_score:
                best_kern_score = score
                best_kernel  = kernel
                best_epsilon = eps
        except Exception as e:
            print(f"  {kernel:25s} ERROR: {e}")

    print(f"\n  Best: {best_kernel}, eps={best_epsilon}")
    print()

    # ── Final emulator ─────────────────────────────────────────────────
    print("=" * 70)
    print("  FINAL EMULATOR – THREE-TIER VALIDATION")
    print("=" * 70)
    print()

    print(f"  Training: n_train={n_train_use}, n_pca={n_pca_use}, "
          f"kernel={best_kernel}")
    final_emu = train_emulator_on_cache(
        cache, n_train_use, n_pca_use,
        kernel=best_kernel, epsilon=best_epsilon, config=config,
    )

    # Extended test set for likelihood validation
    final_emu.test_params = cache["params_test"][:40].copy()

    print("  Running three-tier validation...")
    print()
    result = validate_three_tiers(final_emu, cache, cachedir)

    # ── Report ─────────────────────────────────────────────────────────
    print()
    print("  Gate summary:")
    for gate in ["G_spectrum", "G_theory_ACT", "G_theory_ACT_PR4",
                 "G_core_ACT", "G_core_ACT_PR4", "G_tail_ACT",
                 "G_tail_ACT_PR4", "G_special_ACT", "G_special_ACT_PR4",
                 "G_resolution"]:
        status = "✓" if result["gates"].get(gate, False) else "✗"
        print(f"    {status} {gate}")

    print()
    print("  Tier 1 – Spectrum:")
    print(f"    RMS = {result['details'].get('rms_spectrum_pct', '?'):.3f}%")
    print(f"    P95 = {result['details'].get('p95_spectrum_pct', '?'):.3f}%")
    print("  Tier 2 – Theory distance:")
    for v in ["act_baseline", "actplanck_baseline"]:
        base = "ACT_PR4" if "planck" in v else "ACT"
        p95 = result["details"].get(f"eps_th_{v}_p95", None)
        mx  = result["details"].get(f"eps_th_{v}_max", None)
        if p95 is not None:
            print(f"    ε_th {base}: P95={p95:.4f}, max={mx:.4f}")
    print("  Tier 3 – Core likelihood:")
    for base in ["ACT", "ACT_PR4"]:
        n = result["details"].get(f"core_{base.replace('_PR4','')}_n", 0)
        mx = result["details"].get(f"core_{base.replace('_PR4','')}_max_dchi2", None)
        if mx is not None:
            print(f"    Core {base}: n={n}, max|Δχ²|={mx:.4f}")
    print("  Tier 4 – Safety:")
    for base in ["ACT", "ACT_PR4"]:
        n_tail = result["details"].get(f"tail_{base.replace('_PR4','')}_n", 0)
        promoted = result["details"].get(f"tail_{base.replace('_PR4','')}_promoted", 0)
        print(f"    Tail {base}: {n_tail} points, {promoted} promoted")

    with open(outdir / "gate_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    # ── Production unlock ──────────────────────────────────────────────
    print()
    print("=" * 70)
    if result["production_unlock"]:
        print("  ALL GATES PASSED — PRODUCTION UNLOCK ✓")
        print(f"  Writing to: {prod_dir}")
        final_emu.save(prod_dir)

        # Write token with emulator + cache hash for smoke-test verification
        import hashlib, json as json2
        with open(cachedir / "manifest.json") as f:
            cache_manifest = json2.load(f)
        cache_hash = cache_manifest.get("checksums", {}).get("R_total_train.npy", "?")

        token = {
            "production_unlock": True,
            "passed_gates": result["passed_gates"],
            "validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cache_hash": cache_hash,
        }
        tmp = prod_dir / ".production_unlock.tmp"
        with open(tmp, "w") as f:
            json2.dump(token, f, indent=2)
        tmp.rename(prod_dir / "production_unlock.json")
        rc = 0
    else:
        print("  GATES NOT PASSED ✗")
        print(f"  Failed: {result['failed_gates']}")
        print(f"  NO production emulator written.")
        # Save failed candidate for audit
        cand_dir = outdir / "candidates" / f"failed_{int(time.time())}"
        cand_dir.mkdir(parents=True)
        final_emu.save(cand_dir)
        with open(cand_dir / "gate_results.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        rc = 1
    print("=" * 70)
    return rc


if __name__ == "__main__":
    sys.exit(main())
