#!/usr/bin/env python3
"""
Phase 3D COSEBIs calibration: convention scan + amplitude fit + KCAP comparison.

Tests:
  1. Convention scan (72 variants × 2 models = 144 runs)
  2. Amplitude-only calibration (analytic A* embedded in each variant)
  3a. KCAP direct comparison (existing 5-mode predictions)
  3b. Same-Cℓ isolated comparison (only if 3a inconclusive)

Usage:
  python src/cosebis_convention_scan.py --config configs/kids_cosebis_calibration.yaml
"""
from __future__ import annotations
import argparse, json, itertools, sys, yaml
import numpy as np, pandas as pd
from pathlib import Path
import scipy.linalg as la

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "fds_g1_stage3_kids_pipeline"))
from cosebis_filters import load_roots_norms, Tplus, Tminus, ARCMIN

BIN_PAIRS = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,1),(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(3,3),(3,4),(4,4)]
N_MODES = 20
AUTO_PAIRS = [(0,0),(1,1),(2,2),(3,3),(4,4)]
KCAP_LABELS = {"(0,0)": "bin_1_1", "(0,1)": "bin_2_1", "(1,1)": "bin_2_2",
               "(0,2)": "bin_3_1", "(1,2)": "bin_3_2", "(2,2)": "bin_3_3",
               "(0,3)": "bin_4_1", "(1,3)": "bin_4_2", "(2,3)": "bin_4_3",
               "(3,3)": "bin_4_4", "(0,4)": "bin_5_1", "(1,4)": "bin_5_2",
               "(2,4)": "bin_5_3", "(3,4)": "bin_5_4", "(4,4)": "bin_5_5"}

def resolve_path(base_dir, p):
    pobj = Path(p)
    return pobj if pobj.is_absolute() else (base_dir / pobj).resolve()

def load_config(config_path):
    cp = Path(config_path)
    with open(cp) as f:
        cfg = yaml.safe_load(f)
    cfg["_config_dir"] = cp.parent
    return cfg

def make_theta_grid(theta_min, theta_max, n, spacing="log"):
    if spacing == "log":
        return np.geomspace(theta_min, theta_max, n)
    return np.linspace(theta_min, theta_max, n)

def build_pars_from_bestfit(bestfit_path):
    with open(bestfit_path) as f:
        bf = json.load(f)
    return dict(bf["params"])

def tminus_original(tp_func, y, z):
    return 4.0 * tp_func(y) * (np.exp(2.0 * (y - z)) - 3.0 * np.exp(4.0 * (y - z)))

def tminus_flipped(tp_func, y, z):
    return 4.0 * tp_func(y) * (3.0 * np.exp(4.0 * (y - z)) - np.exp(2.0 * (y - z)))

def precompute_Tminus(theta_arcmin, theta_min, theta_max, n_modes, norms, roots_list,
                      branch_func):
    z = np.log(theta_arcmin / theta_min)
    n_theta = len(theta_arcmin)
    Tm = np.zeros((n_modes, n_theta))
    from scipy.interpolate import interp1d
    from scipy.special.orthogonal import p_roots
    xG, wG = p_roots(21)

    for n in range(n_modes):
        roots = roots_list[n]
        norm = norms[n]
        tp = Tplus(theta_arcmin, theta_min, theta_max, n, norm, roots)
        tp_func = interp1d(np.log(theta_arcmin / theta_min), tp,
                           bounds_error=False, fill_value=0.0)
        tm = tp.copy()
        integ_limits = np.insert(roots / theta_min, 0, 0.0)
        for iz in range(len(z)):
            good = integ_limits <= z[iz]
            limits_good = integ_limits[good]
            result = 0.0
            for il in range(1, len(limits_good)):
                lo = limits_good[il - 1]
                hi = limits_good[il]
                delta = hi - lo
                y = 0.5 * delta * xG + 0.5 * (hi + lo)
                mask = y >= 0.0
                result += delta * 0.5 * np.sum(wG[mask] * branch_func(tp_func, y[mask], z[iz]))
            lo = limits_good[-1]
            hi = z[iz]
            delta = hi - lo
            y = 0.5 * delta * xG + 0.5 * (hi + lo)
            mask = y >= 0.0
            result += delta * 0.5 * np.sum(wG[mask] * branch_func(tp_func, y[mask], z[iz]))
            tm[iz] += result
        Tm[n] = tm
    return Tm

def compute_En_from_xi(xi_plus, xi_minus, theta_arcmin, Tp, Tm):
    n_modes = Tp.shape[0]
    En = np.zeros(n_modes)
    for n in range(n_modes):
        integ = (xi_plus * Tp[n] + xi_minus * Tm[n]) * theta_arcmin
        integral = np.trapz(integ, theta_arcmin)
        En[n] = 0.5 * integral / ARCMIN / ARCMIN
    return En

def chi2_block(delta, cov_cho):
    return float(delta @ la.cho_solve(cov_cho, delta))

def sign_match(pred, data):
    return np.mean(np.sign(pred) == np.sign(data))

def median_abs_ratio(pred, data):
    m = np.abs(data) > 1e-30
    if m.sum() == 0:
        return np.nan
    return float(np.median(np.abs(pred[m]) / np.abs(data[m])))

def bestfit_amplitude(m, d, cov_cho):
    Cm = la.cho_solve(cov_cho, m)
    Cd = la.cho_solve(cov_cho, d)
    mm = float(m @ Cm)
    md = float(m @ Cd)
    dd = float(d @ Cd)
    if mm <= 0:
        return 1.0, dd, dd, md, 0.0
    A = md / mm
    chi2_at_A = dd - 2 * A * md + A * A * mm
    return A, dd, mm, md, chi2_at_A

def sample_en_from_xi_all_pairs(xi_store, theta_arcmin, Tp, Tm):
    En_all = np.full(len(BIN_PAIRS) * N_MODES, np.nan)
    for idx, (i, j) in enumerate(BIN_PAIRS):
        xip, xim = xi_store[(i, j)]
        En = compute_En_from_xi(xip, xim, theta_arcmin, Tp, Tm)
        En_all[idx * N_MODES:(idx + 1) * N_MODES] = En
    return En_all

def load_kcap_predictions(kcap_dir):
    n_kcap_pairs = len(KCAP_LABELS)
    kcap = {}
    for px_idx, (pair_str, kcap_bin) in enumerate(KCAP_LABELS.items()):
        vals = np.loadtxt(str(Path(kcap_dir) / f"{kcap_bin}.txt"))
        kcap[px_idx] = vals
    return kcap

def build_kcap_comparison(en_pred_flat, kcap_preds, n_modes_kcap=5):
    rows = []
    for px_idx, vals in kcap_preds.items():
        i, j = BIN_PAIRS[px_idx]
        for n in range(n_modes_kcap):
            pred_val = en_pred_flat[px_idx * N_MODES + n]
            rows.append({"pair_idx": px_idx, "bin1": i, "bin2": j,
                         "mode": n + 1, "my_pred": float(pred_val),
                         "kcap_pred": float(vals[n])})
    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser(description="COSEBIs convention scan + calibration")
    ap.add_argument("--config", default="configs/kids_cosebis_calibration.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    cdir = cfg["_config_dir"]

    # -- Load data --
    data_path = resolve_path(cdir, cfg["data"]["vector"])
    cov_path = resolve_path(cdir, cfg["data"]["covariance"])
    data_df = pd.read_csv(data_path)
    cov = np.load(cov_path)
    data_vector = data_df["value"].to_numpy(float)
    cov_cho = la.cho_factor(cov)
    print(f"Data: {len(data_vector)} vector, {cov.shape} covariance")

    # -- Filters --
    fc = cfg["filters"]
    roots_path = resolve_path(cdir, fc["roots_path"])
    norms_path = resolve_path(cdir, fc["norms_path"])
    n_modes = int(fc.get("n_modes", N_MODES))
    tmin = float(fc["theta_min_arcmin"])
    tmax = float(fc["theta_max_arcmin"])
    roots_list, norms = load_roots_norms(str(roots_path), str(norms_path), n_modes)

    tg = cfg["theta_grid"]
    theta_min = float(tg.get("theta_min_arcmin", tmin))
    theta_max = float(tg.get("theta_max_arcmin", tmax))
    n_theta = int(tg.get("n_theta", 1024))
    spacing = tg.get("spacing", "log")
    theta_fine = make_theta_grid(theta_min, theta_max, n_theta, spacing)
    print(f"Theta: {n_theta} {spacing} pts [{theta_min}', {theta_max}']")

    # Precompute T+ base and both T- branches
    print("Precomputing T+ filter matrix ...")
    Tp_base = np.zeros((n_modes, n_theta))
    for n in range(n_modes):
        Tp_base[n] = Tplus(theta_fine, tmin, tmax, n, norms[n], roots_list[n])

    print("Precomputing T- (original branch) ...")
    Tm_orig = precompute_Tminus(theta_fine, tmin, tmax, n_modes, norms, roots_list,
                                 tminus_original)

    print("Precomputing T- (flipped branch) ...")
    Tm_flip = precompute_Tminus(theta_fine, tmin, tmax, n_modes, norms, roots_list,
                                 tminus_flipped)

    # -- G1 pipeline --
    gc = cfg["g1_pipeline"]
    config_path = Path(gc["stage3_config"])
    theory_backend = gc.get("theory_backend", "class")

    from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood
    like = Stage3Lensing3x2ptLikelihood(str(config_path), theory_backend=theory_backend,
                                         class_nk=128, class_nz=64)
    ell = like.ell_grid
    print(f"G1 pipeline: {len(ell)} ell bins, backend={theory_backend}")

    # -- KCAP predictions --
    kcap_dir = cfg.get("kcap", {}).get("cosebis_dir")
    kcap_preds = load_kcap_predictions(kcap_dir) if kcap_dir else None
    if kcap_preds is not None:
        print(f"Loaded KCAP predictions: {len(kcap_preds)} bin files")

    cs = cfg["convention_scan"]
    scales = cs.get("scales", [0.1, 1, 10])
    tminus_signs = cs.get("tminus_signs", [1, -1])
    tplus_factors_list = cs.get("tplus_factors", [1])
    mode_orders = cs.get("mode_orders", ["forward"])
    tminus_branches = cs.get("tminus_branches", ["original"])
    tplus_factors_labels = {1: "1 (KiDS)", 0.1591549430918953: "1/(2pi)",
                            6.283185307179586: "2pi"}

    outdir = resolve_path(cdir, cfg["outputs"]["outdir"])
    outdir.mkdir(parents=True, exist_ok=True)

    results_rows = []
    kcap_compare_rows = []

    for model_key, model_cfg in cfg["models"].items():
        bf_path = Path(model_cfg["bestfit"])
        print(f"\n{'='*60}\nModel: {model_key}")
        pars = build_pars_from_bestfit(bf_path)
        print(f"  Omega_m={pars['Omega_m']:.4f}, sigma8={pars['sigma8']:.4f}" +
              (f", s={pars['s']:.4f}" if "s" in pars else ""))

        # Compute xi± once for all pairs (expensive, CLASS + realspace)
        theta_rad = theta_fine / ARCMIN
        xi_store = {}
        print("  Computing xi± for all 15 bin pairs ...")
        for idx, (i, j) in enumerate(BIN_PAIRS):
            si, sj = f"src{i}", f"src{j}"
            cl = like._compute_cl_pair(model_key, pars, "xip", si, sj, ell)
            xi_plus = like._realspace_from_cl(ell, cl, "xip", theta_rad)
            xi_minus = like._realspace_from_cl(ell, cl, "xim", theta_rad)
            xi_store[(i, j)] = (xi_plus, xi_minus)
            if idx % 5 == 4:
                print(f"    {idx+1}/15 done")
        print("  xi± computed for all pairs")

        # Data vector subsets for block diagnostics
        d = data_vector

        # Enumerate variants
        variant_idx = 0
        for scale, tminus_sign, tplus_factor, mode_order, tminus_branch in itertools.product(
                scales, tminus_signs, tplus_factors_list, mode_orders, tminus_branches):

            # Select T- branch
            Tm_base = Tm_orig if tminus_branch == "original" else Tm_flip

            # Apply T+ factor and T- sign
            Tp = Tp_base * tplus_factor
            Tm = Tm_base * tminus_sign

            # Mode order
            if mode_order == "reverse":
                Tp = Tp[::-1, :]  # reverse mode order 0..19 → 19..0
                Tm = Tm[::-1, :]

            # Project to Eₙ for all pairs
            En_pred = sample_en_from_xi_all_pairs(xi_store, theta_fine, Tp, Tm)

            # Apply scale factor
            En_pred_scaled = En_pred * scale

            # Check finiteness
            finite = np.isfinite(En_pred_scaled)
            n_finite = int(finite.sum())
            if n_finite < 300:
                print(f"  Variant {variant_idx}: only {n_finite}/300 finite, skipping")
                # Still record with sentinel chi2
                En_pred_scaled[~finite] = 0.0

            delta = d - En_pred_scaled

            # Block indices
            mode_col = data_df["mode"].to_numpy()
            pair_col = (data_df["bin1"].astype(str) + "_" + data_df["bin2"].astype(str)).to_numpy()
            is_auto = np.array([p in [f"{a}_{a}" for a in range(5)] for p in pair_col])
            low_modes = mode_col <= 9
            high_modes = mode_col >= 10
            first5 = mode_col <= 5
            modes_1_to_9_mask = mode_col <= 9
            modes_10_to_20_mask = mode_col >= 10

            # Chi2 blocks
            chi2_total = chi2_block(delta, cov_cho)
            chi2_first5 = chi2_block(delta[first5], la.cho_factor(cov[np.ix_(first5, first5)])) if first5.sum() > 0 else np.nan
            chi2_m1_9 = chi2_block(delta[modes_1_to_9_mask], la.cho_factor(cov[np.ix_(modes_1_to_9_mask, modes_1_to_9_mask)])) if modes_1_to_9_mask.sum() > 0 else np.nan
            chi2_m10_20 = chi2_block(delta[modes_10_to_20_mask], la.cho_factor(cov[np.ix_(modes_10_to_20_mask, modes_10_to_20_mask)])) if modes_10_to_20_mask.sum() > 0 else np.nan

            # Sign match
            s_tot = sign_match(En_pred_scaled, d)
            s_auto = sign_match(En_pred_scaled[is_auto], d[is_auto])
            s_cross = sign_match(En_pred_scaled[~is_auto], d[~is_auto])
            s_low = sign_match(En_pred_scaled[low_modes], d[low_modes])
            s_high = sign_match(En_pred_scaled[high_modes], d[high_modes])

            # Median abs ratio
            med_rat = median_abs_ratio(En_pred_scaled, d)

            # Amplitude calibration
            A_star, chi2_data, chi2_model, chi2_cross, chi2_at_A = bestfit_amplitude(
                En_pred_scaled, d, cov_cho)
            chi2_improvement = chi2_total - chi2_at_A

            # Combined prediction (A * m)
            En_pred_A = En_pred_scaled * A_star
            delta_A = d - En_pred_A
            chi2_combined = chi2_block(delta_A, cov_cho)

            tplus_label = tplus_factors_labels.get(tplus_factor, f"{tplus_factor:.6f}")

            result = {
                "variant": variant_idx,
                "model": model_key,
                "scale": scale,
                "tminus_sign": tminus_sign,
                "tplus_factor": tplus_factor,
                "tplus_label": tplus_label,
                "mode_order": mode_order,
                "tminus_branch": tminus_branch,
                "n_finite": n_finite,
                "chi2_total": chi2_total,
                "chi2_first5_modes": chi2_first5,
                "chi2_modes_1_to_9": chi2_m1_9,
                "chi2_modes_10_to_20": chi2_m10_20,
                "sign_match_total": s_tot,
                "sign_match_auto": s_auto,
                "sign_match_cross": s_cross,
                "sign_match_low_modes": s_low,
                "sign_match_high_modes": s_high,
                "median_abs_ratio": med_rat,
                "A_star": A_star,
                "chi2_at_Astar": chi2_at_A,
                "chi2_improvement": chi2_improvement,
                "chi2_combined": chi2_combined,
                "chi2_data_only": chi2_data,
                "chi2_model_only": chi2_model,
                "chi2_cross": chi2_cross,
            }
            results_rows.append(result)

            if variant_idx % 20 == 0:
                print(f"  Variant {variant_idx}: χ²={chi2_total:.1f}, A*={A_star:.4f}, sign={s_tot:.3f}")

            variant_idx += 1

        # -- KCAP comparison (first 5 modes only) --
        if kcap_preds is not None:
            print("  Building KCAP comparison table ...")
            # Use default convention (scale=1, tminus_sign=1, tplus_factor=1, forward, original)
            Tp_default = Tp_base.copy()
            Tm_default = Tm_orig.copy()
            En_default = sample_en_from_xi_all_pairs(xi_store, theta_fine, Tp_default, Tm_default)
            kcap_df = build_kcap_comparison(En_default, kcap_preds, 5)
            kcap_df["model"] = model_key
            kcap_compare_rows.append(kcap_df)

            # Print quick comparison summary
            for px_idx, vals in kcap_preds.items():
                i, j = BIN_PAIRS[px_idx]
                my5 = En_default[px_idx * N_MODES: px_idx * N_MODES + 5]
                kcap5 = vals
                ratios = my5 / kcap5
                print(f"    Pair ({i},{j}): my/KCAP ratios = " +
                      "  ".join(f"{r:.3f}" for r in ratios))

    # -- Write results --
    results_df = pd.DataFrame(results_rows)
    results_path = outdir / "convention_scan.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\nWrote convention scan: {results_path} ({len(results_df)} variants)")

    if kcap_compare_rows:
        kcap_compare_df = pd.concat(kcap_compare_rows, ignore_index=True)
        kcap_path = outdir / "kcap_direct_comparison.csv"
        kcap_compare_df.to_csv(kcap_path, index=False)
        print(f"Wrote KCAP comparison: {kcap_path}")

    # -- Best variant summary --
    best_by_model = {}
    for model in results_df["model"].unique():
        sub = results_df[results_df["model"] == model].copy()
        best_idx = sub["chi2_total"].idxmin()
        best = sub.loc[best_idx]
        best_by_model[model] = {
            "best_variant": int(best["variant"]),
            "scale": best["scale"],
            "tminus_sign": best["tminus_sign"],
            "tplus_label": best["tplus_label"],
            "mode_order": best["mode_order"],
            "tminus_branch": best["tminus_branch"],
            "chi2_total": best["chi2_total"],
            "A_star": best["A_star"],
            "chi2_at_Astar": best["chi2_at_Astar"],
            "sign_match_total": best["sign_match_total"],
        }

    summary_lines = [
        "# COSEBIs Calibration: Convention Scan + KCAP Comparison",
        "",
        f"Generated: 2026-05-30",
        f"Data: {len(data_vector)}-element COSEBIs vector, {cov.shape[0]}×{cov.shape[1]} covariance",
        f"Theta grid: {n_theta} {spacing} points [{theta_min}', {theta_max}']",
        f"Filters: {n_modes} COSEBIs modes (roots/norms for θ∈[{tmin}',{tmax}'])",
        "",
        "## Convention Variants",
        "",
        f"| Dimension | Values |",
        f"|-----------|--------|",
        f"| scale | {scales} |",
        f"| T⁻ final sign | {tminus_signs} |",
        f"| T⁺ factor | {list(tplus_factors_labels.values())} |",
        f"| mode order | {mode_orders} |",
        f"| T⁻ internal branch | {tminus_branches} |",
        f"| **Total** | **{len(results_rows)}** |",
        "",
        "## Best Variant by Model (min χ²)",
        "",
        "| Model | variant | scale | T⁻ sign | T⁺ factor | mode order | T⁻ branch | χ² | A* | χ²(A*) | sign match |",
        "|-------|---------|-------|---------|------------|------------|-----------|------|-----|--------|------------|",
    ]
    for model, info in best_by_model.items():
        summary_lines.append(
            f"| {model} | {info['best_variant']} | {info['scale']} | {info['tminus_sign']} | "
            f"{info['tplus_label']} | {info['mode_order']} | {info['tminus_branch']} | "
            f"{info['chi2_total']:.1f} | {info['A_star']:.4f} | {info['chi2_at_Astar']:.1f} | "
            f"{info['sign_match_total']:.3f} |"
        )

    summary_lines.extend([
        "",
        "## KCAP Direct Comparison Summary",
        "",
        "KCAP predictions from: Predictions/kcap_xi/outputs/test_output_S8_fid_test/cosebis/",
        "KCAP uses S8_fid_test cosmology (different from LCDM/M3/4 xi± bestfits).",
        "Direct comparison is a qualitative convention check, not a precision test.",
        "",
    ])
    if kcap_compare_rows:
        kcap_df = pd.concat(kcap_compare_rows, ignore_index=True)
        kcap_df["abs_ratio"] = np.abs(kcap_df["my_pred"] / kcap_df["kcap_pred"])
        summary_lines.append(f"- Total compared pairs: {len(kcap_df)}")
        summary_lines.append(f"- Median |my/KCAP| ratio: {kcap_df['abs_ratio'].median():.3f}")
        summary_lines.append(f"- Sign match fraction: {(np.sign(kcap_df['my_pred']) == np.sign(kcap_df['kcap_pred'])).mean():.3f}")
        summary_lines.append("")

    summary_lines.extend([
        "## Interpretation",
        "",
        "1. **Convention scan** tests 72 variants to find the convention that best matches the data.",
        "2. **A* amplitude** shows whether the mismatch is a pure normalization (A* far from 1) vs sign/convention.",
        "3. **Block chi2** diagnostics (first 5, 1-9, 10-20 modes) target the sign-flip around mode 10.",
        "4. **KCAP comparison** validates against an independent COSEBIs implementation.",
        "5. If best variant still has χ² >> 300, the issue is upstream (Cℓ shape, n(z), IA, m-bias), not Tₙ.",
        "",
        "*Phase 3D COSEBIs calibration, convention-scan + amplitude-fit, 2026-05-30*",
    ])
    summary_path = outdir / "best_variant_summary.md"
    (outdir / "best_variant_summary.md").write_text("\n".join(summary_lines))
    print(f"Wrote summary: {summary_path}")

    # Print best variant inline
    print("\n" + "=" * 60)
    print("BEST VARIANT BY MODEL:")
    for model, info in best_by_model.items():
        print(f"  {model}: variant {info['best_variant']} "
              f"(scale={info['scale']}, T⁻sign={info['tminus_sign']}, "
              f"T⁺={info['tplus_label']}, order={info['mode_order']}, "
              f"T⁻branch={info['tminus_branch']})"
              f"  χ²={info['chi2_total']:.1f}, A*={info['A_star']:.4f}, "
              f"χ²(A*)={info['chi2_at_Astar']:.1f}")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
