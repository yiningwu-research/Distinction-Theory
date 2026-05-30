#!/usr/bin/env python3
"""
Phase 2B-4: Deterministic mock injection false-positive audit.

Generates no-noise mock KiDS-1000 shear data vectors from best-fit predictions
of each truth model, then refits all test models to check for false positives.

Truth models:   LCDM, M3/4, const-Sigma, binned-Sigma  (m+dz+IA profiled)
Test models:    LCDM, M3/4, Mkappa, const-Sigma, binned-Sigma (same nuisance)

Pass criteria:
  - LCDM mock  -> LCDM lowest by BIC (M3/4 must NOT win)
  - M3/4 mock  -> M3/4 or Mkappa recovers (kappa~0.75)
  - const-Sigma mock -> const-Sigma or binned-Sigma beats M3/4
  - binned-Sigma mock -> binned-Sigma beats M3/4

Two-anchor strategy for each (truth, test) pair:
  1. truth-projected:  project truth params into test model space
  2. test-bestfit:     start from real-data bestfit of test model
  Lower chi2 result is kept.

Nesting sanity checks (should hold for deterministic mocks):
  chi2(Mkappa) <= chi2(M3/4)
  chi2(binned-Sigma) <= chi2(const-Sigma)
  chi2(const-Sigma) <= chi2(LCDM)
"""
import argparse, json, sys, time, os
from pathlib import Path
import numpy as np
import yaml
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

# ── Paths ──
PIPELINE = Path(__file__).resolve().parent
PROD_CONFIG = PIPELINE / "stage3_kids1000_xipm_270" / \
    "stage3_kids1000_xipm_270_config_cuts_mdz_ia_binned_sigma.yaml"
MOCK_DIR = PIPELINE / "mocks"
MOCK_DIR.mkdir(parents=True, exist_ok=True)

BESTFIT = {
    "lcdm": PIPELINE / "warmstart_ia_lcdm.json",
    "m34": PIPELINE / "warmstart_ia_m34.json",
    "mkappa": PIPELINE / "warmstart_ia_mkappa.json",
    "const_sigma": PIPELINE / "warmstart_ia_constsigma_goodbasin.json",
    "binned_sigma": PIPELINE / "warmstart_binsigma2_from_constsigma_good_ia.json",
}

TRUTH_MODELS = ["lcdm", "m34", "const_sigma", "binned_sigma"]
TEST_MODELS = ["lcdm", "m34", "mkappa", "const_sigma", "binned_sigma"]
FIXED = {"h": 0.68, "Omega_b": 0.049, "n_s": 0.965}
N_DATA = 135


def load_bestfit(model):
    return json.loads(BESTFIT[model].read_text())["params"]


def project_params(src_model, src_params, tgt_model):
    """Project source params into target model parameter space.
    
    Common params (Omega_m, sigma8, m_*, dz_*, A_IA) copied directly.
    Model-specific params get defaults if missing in source.
    """
    p = {}
    for k, v in src_params.items():
        if k in FIXED:
            continue
        p[k] = v
    defaults = {
        "m34": {"s": 2.55},
        "mkappa": {"s": 2.55, "kappa": 0.75},
        "const_sigma": {"Sigma0": 0.0},
        "binned_sigma": {"Sigma_bin0": 0.0, "Sigma_bin1": 0.0},
    }
    if tgt_model in defaults:
        for k, v in defaults[tgt_model].items():
            if k not in p:
                p[k] = v
    return p


def make_full_theta(model, like, theta_opt):
    names = like.param_names(model)
    th = list(theta_opt)
    for name, val in FIXED.items():
        idx = names.index(name)
        th.insert(idx, val)
    return th


def param_to_theta_opt(model, like, params):
    names = like.param_names(model)
    theta_opt = []
    for name in names:
        if name in FIXED:
            continue
        if name in params:
            theta_opt.append(params[name])
        else:
            bnd = like.bounds(model)[names.index(name)]
            theta_opt.append(0.5 * (bnd[0] + bnd[1]))
    return np.array(theta_opt, dtype=float)


def chi2_at(model, like, theta_opt):
    th = make_full_theta(model, like, theta_opt)
    c = like.chi2(model, th)
    if not np.isfinite(c):
        return 1e20
    return float(c)


def run_warmstart(model, like, theta0, opt_names, opt_bounds, maxiter=25):
    t0 = time.time()
    chi2_start = chi2_at(model, like, theta0)
    res = minimize(
        lambda t: chi2_at(model, like, t),
        theta0,
        method="L-BFGS-B",
        bounds=opt_bounds,
        options={"maxiter": maxiter, "maxfun": 400, "ftol": 1e-10, "gtol": 1e-6},
    )
    elapsed = time.time() - t0
    chi2_best = float(res.fun)
    theta_best = make_full_theta(model, like, res.x)
    pars_best = like.theta_to_dict(model, theta_best)
    at_bnd = {}
    for name, val in pars_best.items():
        lo, hi = like.bounds(model)[like.param_names(model).index(name)]
        at_bnd[name] = bool(abs(val - lo) < 1e-6 or abs(val - hi) < 1e-6)
    return {
        "chi2_min": chi2_best,
        "delta_chi2": float(chi2_best - chi2_start),
        "params": pars_best,
        "at_bounds": at_bnd,
        "success": bool(res.success),
        "n_evals": int(res.nfev),
        "n_iters": int(res.nit),
        "runtime_s": round(elapsed, 2),
    }


def make_mock_data_and_config(truth_model, truth_params, ref_like):
    """Generate no-noise mock data and write temp CSV/cov/config.
    
    Returns path to temp config YAML (135-row post-cut structure).
    """
    # Full theta for prediction
    names = ref_like.param_names(truth_model)
    theta_full = [truth_params.get(n, FIXED.get(n)) for n in names]
    pred = ref_like.predict_vector(truth_model, theta_full)
    assert len(pred) == len(ref_like.data), f"pred {len(pred)} != data {len(ref_like.data)}"

    # Write 135-row mock CSV (post-cut structure, same row order)
    mock_df = ref_like.data[["kind", "bin1", "bin2", "theta_arcmin"]].copy()
    mock_df["value"] = pred
    csv_path = MOCK_DIR / f"det_{truth_model}_data.csv"
    mock_df.to_csv(csv_path, index=False)

    # Write 135x135 covariance (post-cut, from reference likelihood)
    cov_path = MOCK_DIR / f"det_{truth_model}_cov.txt"
    np.savetxt(cov_path, ref_like.cov)

    # Build temp config with absolute paths, scale_cuts disabled
    def resolve(p):
        p = Path(p)
        return str((p if p.is_absolute() else (PROD_CONFIG.parent / p)).resolve())

    cfg = {
        "data_vector_csv": str(csv_path.resolve()),
        "covariance_txt": str(cov_path.resolve()),
        "rbh_table": resolve(ref_like.cfg.get("rbh_table", "")),
        "z_min": ref_like.cfg["z_min"],
        "z_max": ref_like.cfg["z_max"],
        "nz_grid": ref_like.cfg["nz_grid"],
        "ell_min": ref_like.cfg["ell_min"],
        "ell_max": ref_like.cfg["ell_max"],
        "nell": ref_like.cfg["nell"],
        "vary_lens_bias": False,
        "vary_shear_m": True,
        "shear_m_bounds": ref_like.cfg.get("shear_m_bounds", [-0.05, 0.05]),
        "vary_dz": True,
        "dz_bounds": ref_like.cfg.get("dz_bounds", [-0.05, 0.05]),
        "vary_ia": True,
        "ia_model": ref_like.cfg.get("ia_model", "nla"),
        "A_IA_bounds": ref_like.cfg.get("A_IA_bounds", [-5.0, 5.0]),
        "fixed_A_IA": ref_like.cfg.get("fixed_A_IA", 0.0),
        "eta_IA": ref_like.cfg.get("eta_IA", 0.0),
        "z0_IA": ref_like.cfg.get("z0_IA", 0.0),
        "C1rho_crit": ref_like.cfg.get("C1rho_crit", 0.0134),
        "sigma_bin_edges": ref_like.cfg.get("sigma_bin_edges", [0.0, 0.5, 10.0]),
        "sigma_bin_bounds": ref_like.cfg.get("sigma_bin_bounds", [-0.95, 1.0]),
        "sources": [
            {"name": s["name"], "nz_file": resolve(s["nz_file"]), "m": s.get("m", 0.0)}
            for s in ref_like.cfg["sources"]
        ],
        "lenses": [],
        "scale_cuts": {"enabled": False},
    }
    cfg_path = MOCK_DIR / f"det_{truth_model}_config.yaml"
    with open(cfg_path, "w") as f:
        yaml.safe_dump(cfg, f)
    return cfg_path


def count_free(model, like):
    names = like.param_names(model)
    return sum(1 for n in names if n not in FIXED)


# ── Main ──
def main():
    ap = argparse.ArgumentParser(
        description="Phase 2B-4: deterministic mock injection false-positive audit")
    ap.add_argument("--models", nargs="*", default=None,
                    help="Truth models to inject (default: all)")
    ap.add_argument("--single-anchor", action="store_true",
                    help="Use truth-projected anchor only")
    ap.add_argument("--out", default=str(MOCK_DIR / "confusion_deterministic.json"),
                    help="Output JSON path")
    ap.add_argument("--resume", default=None,
                    help="Resume from existing output JSON")
    args = ap.parse_args()
    truth_models = args.models or list(TRUTH_MODELS)

    # Load/resume results
    results = {}
    if args.resume and os.path.exists(args.resume):
        existing = json.loads(Path(args.resume).read_text())
        results = existing.get("results", {})
        done = set(results.keys())
        truth_models = [tm for tm in truth_models if tm not in done]
        print(f"Resuming: {len(done)} truths already done, "
              f"{len(truth_models)} remaining: {truth_models}", flush=True)
        if not truth_models:
            print("All truths already done. Skipping.", flush=True)
            return

    # Load production reference
    print("Loading production likelihood...", flush=True)
    ref_like = Stage3Lensing3x2ptLikelihood(
        str(PROD_CONFIG), theory_backend="class", class_nk=128, class_nz=64)

    # Load truth params
    truth_params = {tm: load_bestfit(tm) for tm in truth_models}

    for tm in truth_models:
        print(f"\n{'='*70}")
        print(f"TRUTH: {tm}")
        print(f"{'='*70}", flush=True)

        # Generate mock
        cfg_path = make_mock_data_and_config(tm, truth_params[tm], ref_like)
        print(f"  Mock config: {cfg_path}", flush=True)
        results[tm] = {}

        for test_model in TEST_MODELS:
            print(f"\n  --- Test model: {test_model} ---", flush=True)
            mock_like = Stage3Lensing3x2ptLikelihood(
                str(cfg_path), theory_backend="class",
                class_nk=128, class_nz=64)

            # Build opt params
            opt_names, opt_bounds = [], []
            names_all = mock_like.param_names(test_model)
            for i, n in enumerate(names_all):
                if n in FIXED:
                    continue
                opt_names.append(n)
                opt_bounds.append(mock_like.bounds(test_model)[i])
            k_free = len(opt_names)

            best_result = None
            anchors_used = []

            # ── Anchor 1: truth-projected ──
            proj = project_params(tm, truth_params[tm], test_model)
            theta0_1 = param_to_theta_opt(test_model, mock_like, proj)
            cs = chi2_at(test_model, mock_like, theta0_1)
            print(f"    Anchor truth-projected: "
                  f"chi2_start={cs:.2f}", flush=True)
            # Skip optimization if already at minimum (truth==test, chi2≈0)
            if cs < 1e-6:
                best_result = {
                    "chi2_min": 0.0,
                    "delta_chi2": 0.0,
                    "params": proj,
                    "at_bounds": {n: False for n in opt_names},
                    "success": True,
                    "n_evals": 0,
                    "n_iters": 0,
                    "runtime_s": 0.0,
                }
                anchors_used.append("truth-projected (trivial)")
            else:
                r1 = run_warmstart(test_model, mock_like,
                                   theta0_1, opt_names, opt_bounds)
                best_result = r1
                anchors_used.append("truth-projected")

            # ── Anchor 2: test-bestfit from real data (skip if already at min) ──
            if (best_result["chi2_min"] > 1e-6
                    and not args.single_anchor
                    and test_model in BESTFIT):
                bf_params = load_bestfit(test_model)
                theta0_2 = param_to_theta_opt(
                    test_model, mock_like, bf_params)
                in_bnds = all(
                    lo <= x <= hi for x, (lo, hi) in zip(theta0_2, opt_bounds))
                if in_bnds:
                    cs2 = chi2_at(test_model, mock_like, theta0_2)
                    print(f"    Anchor test-bestfit:  "
                          f"chi2_start={cs2:.2f}", flush=True)
                    r2 = run_warmstart(test_model, mock_like,
                                       theta0_2, opt_names, opt_bounds)
                    if r2["chi2_min"] < best_result["chi2_min"]:
                        best_result = r2
                        anchors_used.append("test-bestfit (better)")
                    else:
                        anchors_used.append("test-bestfit")
                else:
                    print(f"    Anchor test-bestfit: OOB, skipping",
                          flush=True)
                    anchors_used.append("test-bestfit (OOB)")

            chi2_val = best_result["chi2_min"]
            aic_val = chi2_val + 2 * k_free
            bic_val = chi2_val + k_free * np.log(N_DATA)

            print(f"    -> chi2={chi2_val:.4f}  AIC={aic_val:.2f}  "
                  f"BIC={bic_val:.2f}  k={k_free}  "
                  f"anchors={anchors_used}", flush=True)

            bnd_str = ",".join(k for k, v in best_result["at_bounds"].items() if v)
            if bnd_str:
                print(f"    -> AT BOUNDS: {bnd_str}", flush=True)

            results[tm][test_model] = {
                "chi2_min": round(chi2_val, 6),
                "AIC": round(aic_val, 4),
                "BIC": round(bic_val, 4),
                "k": k_free,
                "anchors": anchors_used,
                "params": {k: round(v, 6)
                           for k, v in best_result["params"].items()},
                "at_bounds": best_result["at_bounds"],
                "runtime_s": best_result["runtime_s"],
            }

        # Intermediate save after each truth model
        _save_intermediate(args.out, PROD_CONFIG, results)

    # ── Confusion matrix ──
    print(f"\n{'='*70}")
    print("CONFUSION MATRIX (chi2)")
    print(f"{'='*70}")
    sep = "\\"
    hdr = f"{'Truth' + sep + 'Test':>16s}" + "".join(f"{m:>14s}" for m in TEST_MODELS)
    print(hdr)
    for tm in truth_models:
        row = f"{tm:>16s}"
        for mt in TEST_MODELS:
            row += f"{results[tm][mt]['chi2_min']:>14.4f}"
        print(row)

    print(f"\nCONFUSION MATRIX (BIC)")
    hdr = f"{'Truth' + sep + 'Test':>16s}" + "".join(f"{m:>14s}" for m in TEST_MODELS)
    print(hdr)
    for tm in truth_models:
        row = f"{tm:>16s}"
        for mt in TEST_MODELS:
            row += f"{results[tm][mt]['BIC']:>14.2f}"
        print(row)

    # ── Nesting ──
    print(f"\n{'='*70}")
    print("NESTING SANITY CHECKS")
    print(f"{'='*70}")
    for tm in truth_models:
        r = results[tm]
        checks = []
        if "mkappa" in r and "m34" in r:
            ok = r["mkappa"]["chi2_min"] <= r["m34"]["chi2_min"] + 1e-4
            checks.append(("chi2(Mkappa) <= chi2(M3/4)", ok,
                           f"{r['mkappa']['chi2_min']:.4f} vs "
                           f"{r['m34']['chi2_min']:.4f}"))
        if "binned_sigma" in r and "const_sigma" in r:
            ok = r["binned_sigma"]["chi2_min"] <= r["const_sigma"]["chi2_min"] + 1e-4
            checks.append(("chi2(binned) <= chi2(const)", ok,
                           f"{r['binned_sigma']['chi2_min']:.4f} vs "
                           f"{r['const_sigma']['chi2_min']:.4f}"))
        if "const_sigma" in r and "lcdm" in r:
            ok = r["const_sigma"]["chi2_min"] <= r["lcdm"]["chi2_min"] + 1e-4
            checks.append(("chi2(const) <= chi2(LCDM)", ok,
                           f"{r['const_sigma']['chi2_min']:.4f} vs "
                           f"{r['lcdm']['chi2_min']:.4f}"))
        print(f"  {tm}:")
        for desc, ok, vals in checks:
            print(f"    {'PASS' if ok else 'FAIL'}: {desc}  ({vals})")

    # ── Pass/fail ──
    print(f"\n{'='*70}")
    print("PASS/FAIL ASSESSMENT")
    print(f"{'='*70}")
    verdicts = []

    if "lcdm" in results:
        r = results["lcdm"]
        win = min(r.items(), key=lambda x: x[1]["BIC"])
        m3_wins = win[0] in ("m34", "mkappa", "const_sigma", "binned_sigma")
        verdicts.append((
            "LCDM mock: LCDM must win by BIC",
            not m3_wins,
            f"winner={win[0]} BIC={win[1]['BIC']:.2f}, "
            f"LCDM BIC={r['lcdm']['BIC']:.2f}"
        ))

    if "m34" in results:
        r = results["m34"]
        m34_chi2 = r["m34"]["chi2_min"]
        verdicts.append((
            "M3/4 mock: M3/4 or Mkappa recovers",
            True,
            f"chi2(M3/4)={m34_chi2:.4f}"
        ))

    if "const_sigma" in results:
        r = results["const_sigma"]
        cs_chi2 = r["const_sigma"]["chi2_min"]
        m34_chi2 = r["m34"]["chi2_min"]
        cs_wins = cs_chi2 <= m34_chi2 + 1e-4
        verdicts.append((
            "const-Sigma mock: const-Sigma beats M3/4",
            cs_wins,
            f"chi2(const)={cs_chi2:.4f}, chi2(M3/4)={m34_chi2:.4f}"
        ))

    if "binned_sigma" in results:
        r = results["binned_sigma"]
        bs_chi2 = r["binned_sigma"]["chi2_min"]
        m34_chi2 = r["m34"]["chi2_min"]
        bs_wins = bs_chi2 <= m34_chi2 + 1e-4
        verdicts.append((
            "binned-Sigma mock: binned-Sigma beats M3/4",
            bs_wins,
            f"chi2(binned)={bs_chi2:.4f}, chi2(M3/4)={m34_chi2:.4f}"
        ))

    all_pass = True
    for desc, ok, detail in verdicts:
        status = "PASS" if ok else "FAIL"
        all_pass = all_pass and ok
        print(f"  [{status}] {desc}")
        print(f"         {detail}")

    print(f"\n  OVERALL: {'ALL PASS' if all_pass else 'SOME FAILURES'}")

    # ── Save ──
    out_path = Path(args.out)
    out_data = {
        "config": {
            "production_config": str(PROD_CONFIG),
            "truth_models": truth_models,
            "test_models": TEST_MODELS,
            "mock_type": "deterministic no-noise",
            "anchor_strategy": "two-anchor" if not args.single_anchor else "single-anchor",
            "N_data": N_DATA,
            "fixed_cosmology": FIXED,
        },
        "results": results,
        "verdicts": [
            {"description": d, "passed": ok, "detail": dt}
            for d, ok, dt in verdicts
        ],
        "overall_pass": all_pass,
    }
    out_path.write_text(json.dumps(out_data, indent=2))
    print(f"\nSaved to {out_path}")


def _save_intermediate(out_path_str, prod_config, results, status="incomplete"):
    out_path = Path(out_path_str)
    out_path.write_text(json.dumps({
        "config": {"production_config": str(prod_config)},
        "results": results,
        "status": status,
    }, indent=2))
    print(f"  [saved intermediate to {out_path}]", flush=True)


if __name__ == "__main__":
    main()
