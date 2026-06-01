#!/usr/bin/env python3
"""
COSEBIs theory-smoke: project G1 pipeline predictions to COSEBIs E_n.

Uses:
  1. G1 pipeline CLASS backend for C_ell
  2. _realspace_from_cl() for fine-resolution xi_±(theta)
  3. COSEBIs filters T_n^+, T_n^- for E_n projection

Config-first, CLI-overridable.
"""
from __future__ import annotations
import argparse, json, sys, yaml, numpy as np, pandas as pd
from pathlib import Path
import scipy.linalg as la

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "fds_g1_stage3_kids_pipeline"))
from cosebis_filters import load_roots_norms, Tplus, Tminus, compute_En, ARCMIN

BIN_PAIRS = [(0,0),(0,1),(0,2),(0,3),(0,4),(1,1),(1,2),(1,3),(1,4),(2,2),(2,3),(2,4),(3,3),(3,4),(4,4)]
N_MODES = 20


def resolve_path(base_dir: Path, p: str) -> Path:
    pobj = Path(p)
    return pobj if pobj.is_absolute() else (base_dir / pobj).resolve()


def load_config(config_path: str | Path) -> dict:
    cp = Path(config_path)
    with open(cp) as f:
        cfg = yaml.safe_load(f)
    cfg["_config_dir"] = cp.parent
    return cfg


def make_theta_grid(theta_min: float, theta_max: float, n: int, spacing: str = "log") -> np.ndarray:
    if spacing == "log":
        return np.geomspace(theta_min, theta_max, n)
    return np.linspace(theta_min, theta_max, n)


def build_pars_from_bestfit(bestfit_path: Path) -> dict:
    with open(bestfit_path) as f:
        bf = json.load(f)
    return dict(bf["params"])


def compute_cosebis_prediction(like, model: str, pars: dict,
                                ell: np.ndarray, theta_fine: np.ndarray,
                                Tp: np.ndarray, Tm: np.ndarray) -> np.ndarray:
    n_pairs = len(BIN_PAIRS)
    n_modes = Tp.shape[0]
    En_all = np.full(n_pairs * n_modes, np.nan, dtype=float)
    theta_rad = theta_fine / ARCMIN

    for idx, (i, j) in enumerate(BIN_PAIRS):
        si, sj = f"src{i}", f"src{j}"
        cl = like._compute_cl_pair(model, pars, "xip", si, sj, ell)
        if np.any(~np.isfinite(cl)):
            print(f"  WARNING: C_ell not finite for ({i},{j}), skipping")
            continue

        xi_plus = like._realspace_from_cl(ell, cl, "xip", theta_rad)
        xi_minus = like._realspace_from_cl(ell, cl, "xim", theta_rad)
        if np.any(~np.isfinite(xi_plus)) or np.any(~np.isfinite(xi_minus)):
            print(f"  WARNING: xi not finite for ({i},{j}), skipping")
            continue

        En = compute_En(xi_plus, xi_minus, theta_fine, Tp, Tm)
        En_all[idx * n_modes:(idx + 1) * n_modes] = En

    return En_all


def convergence_check(like, model: str, pars: dict,
                       ell: np.ndarray, theta_min: float, theta_max: float,
                       roots_list: list[np.ndarray], norms: np.ndarray,
                       n_list: list[int]) -> pd.DataFrame:
    rows = []
    for n_theta in n_list:
        th = make_theta_grid(theta_min, theta_max, n_theta, "log")
        Tp = np.zeros((N_MODES, n_theta))
        Tm = np.zeros((N_MODES, n_theta))
        for n in range(N_MODES):
            Tp[n] = Tplus(th, theta_min, theta_max, n, norms[n], roots_list[n])
            Tm[n] = Tminus(th, theta_min, theta_max, n, norms[n], roots_list[n])
        En = compute_cosebis_prediction(like, model, pars, ell, th, Tp, Tm)
        idx_pair0 = 0
        for n in range(N_MODES):
            rows.append({"n_theta": n_theta, "mode": n + 1, "En": float(En[idx_pair0 * N_MODES + n])})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="COSEBIs theory-smoke projection")
    ap.add_argument("--config", default="configs/kids_cosebis_theory_smoke.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    cdir = cfg["_config_dir"]

    # -- Load COSEBIs data --
    data_path = resolve_path(cdir, cfg["data"]["vector"])
    cov_path = resolve_path(cdir, cfg["data"]["covariance"])
    row_path = resolve_path(cdir, cfg["data"]["row_order"])

    data_df = pd.read_csv(data_path)
    cov = np.load(cov_path)
    row_order = pd.read_csv(row_path)
    print(f"Data: {len(data_df)} rows, Cov: {cov.shape}")

    # -- Load COSEBIs filters --
    fc = cfg["filters"]
    roots_path = resolve_path(cdir, fc["roots_path"])
    norms_path = resolve_path(cdir, fc["norms_path"])
    n_modes = int(fc.get("n_modes", N_MODES))
    tmin = float(fc["theta_min_arcmin"])
    tmax = float(fc["theta_max_arcmin"])

    roots_list, norms = load_roots_norms(str(roots_path), str(norms_path), n_modes)
    print(f"Loaded {len(roots_list)} COSEBIs modes from filters")

    # Pre-compute T+ and T- on a representative fine grid for verification
    # (actual T+/T- computed per theta grid in compute_En)
    print(f"  theta range: {tmin}' - {tmax}', roots/norms loaded")

    # -- Initialize G1 pipeline --
    gc = cfg["g1_pipeline"]
    config_path = Path(gc["stage3_config"])
    theory_backend = gc.get("theory_backend", "class")

    from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood
    like = Stage3Lensing3x2ptLikelihood(str(config_path), theory_backend=theory_backend,
                                         class_nk=128, class_nz=64)
    ell = like.ell_grid
    print(f"G1 pipeline initialized: {len(ell)} ell bins, backend={theory_backend}")

    # -- Theta grid --
    tg = cfg["theta_grid"]
    theta_min = float(tg.get("theta_min_arcmin", tmin))
    theta_max = float(tg.get("theta_max_arcmin", tmax))
    n_theta = int(tg.get("n_theta", 1024))
    spacing = tg.get("spacing", "log")
    theta_fine = make_theta_grid(theta_min, theta_max, n_theta, spacing)
    print(f"Theta grid: {n_theta} {spacing} points [{theta_min}', {theta_max}']")

    # Pre-compute T+ and T- matrices for this theta grid
    Tp = np.zeros((n_modes, n_theta))
    Tm = np.zeros((n_modes, n_theta))
    for n in range(n_modes):
        Tp[n] = Tplus(theta_fine, tmin, tmax, n, norms[n], roots_list[n])
        Tm[n] = Tminus(theta_fine, tmin, tmax, n, norms[n], roots_list[n])
    print(f"COSEBIs filter matrices computed: T+ {Tp.shape}, T- {Tm.shape}")

    # -- Models --
    outdir = resolve_path(cdir, cfg["outputs"]["outdir"])
    outdir.mkdir(parents=True, exist_ok=True)

    data_vector = data_df["value"].to_numpy(float)
    cho_cov = np.linalg.cholesky(cov)

    results = {}

    for model_key, model_cfg in cfg["models"].items():
        bf_path = Path(model_cfg["bestfit"])
        label = model_cfg["label"]
        print(f"\n=== Model: {model_key} ({label}) ===")

        pars = build_pars_from_bestfit(bf_path)
        print(f"  params: Omega_m={pars['Omega_m']:.4f}, sigma8={pars['sigma8']:.4f}" +
              (f", s={pars['s']:.4f}" if "s" in pars else ""))

        En_pred = compute_cosebis_prediction(like, model_key, pars, ell,
                                              theta_fine, Tp, Tm)
        n_finite = int(np.sum(np.isfinite(En_pred)))
        print(f"  COSEBIs prediction: {n_finite}/{len(En_pred)} finite")

        # Write prediction CSV
        pred_rows = []
        for idx, (i, j) in enumerate(BIN_PAIRS):
            for n in range(n_modes):
                pred_rows.append({
                    "statistic": "cosebi_E", "bin1": i, "bin2": j,
                    "mode": n + 1, "prediction": float(En_pred[idx * n_modes + n]),
                })
        pred_df = pd.DataFrame(pred_rows)
        pred_path = outdir / f"{label}_prediction.csv"
        pred_df.to_csv(pred_path, index=False)
        print(f"  Wrote prediction to {pred_path}")

        # Chi-squared
        delta = data_vector - En_pred
        bad = ~np.isfinite(delta)
        if bad.any():
            print(f"  WARNING: {bad.sum()} non-finite residuals, setting chi2=inf")
            chi2 = np.inf
        else:
            try:
                chi2 = float(delta @ la.cho_solve((cho_cov, True), delta))
            except la.LinAlgError:
                chi2 = np.inf

        ndof = int(np.sum(np.isfinite(En_pred)))
        print(f"  chi2 = {chi2:.2f}, ndof = {ndof}, chi2/ndof = {chi2/ndof:.3f}" if np.isfinite(chi2) else f"  chi2 = inf")

        results[label] = {"chi2": chi2, "ndof": ndof, "n_finite": n_finite}

    # -- Convergence check --
    print(f"\n=== Convergence check ===")
    n_list = [512, 1024, 2048]
    conv_rows = []
    for model_key, model_cfg in cfg["models"].items():
        bf_path = Path(model_cfg["bestfit"])
        pars = build_pars_from_bestfit(bf_path)
        conv = convergence_check(like, model_key, pars, ell, theta_min, theta_max, roots_list, norms, n_list)
        conv["model"] = model_key
        conv_rows.append(conv)
    conv_df = pd.concat(conv_rows, ignore_index=True)
    conv_path = outdir / "grid_convergence.csv"
    conv_df.to_csv(conv_path, index=False)
    print(f"Wrote convergence check to {conv_path}")

    # Show convergence for mode 1 (0,0)
    for model_key in cfg["models"]:
        sub = conv_df[(conv_df["model"] == model_key) & (conv_df["mode"] == 1)]
        if len(sub) >= 2:
            vals = sub.sort_values("n_theta")["En"].values
            print(f"  {model_key} mode 1: 512={vals[0]:.4e}, 1024={vals[1]:.4e}" +
                  (f", 2048={vals[2]:.4e}" if len(vals) > 2 else "") +
                  (f", rel_diff(512→1024)={abs(vals[1]-vals[0])/max(abs(vals[1]),1e-30)*100:.2f}%" if len(vals) >= 2 else ""))

    # -- Write manifest --
    manifest = {
        "dataset": cfg["dataset_name"],
        "product": cfg["product"],
        "basis": "COSEBIs_mode_space",
        "theta_grid": {"n_theta": n_theta, "theta_min": theta_min, "theta_max": theta_max, "spacing": spacing},
        "filters": {"n_modes": n_modes, "roots_file": str(roots_path), "norms_file": str(norms_path)},
        "g1_backend": theory_backend,
        "models": {},
    }
    for label, r in results.items():
        manifest["models"][label] = {
            "chi2": r["chi2"],
            "ndof": r["ndof"],
            "chi2_per_dof": round(r["chi2"] / r["ndof"], 4) if np.isfinite(r["chi2"]) and r["ndof"] > 0 else None,
            "n_finite": r["n_finite"],
        }
    manifest_path = outdir / "kids1000_cosebis_theory_manifest.json"
    (outdir / "kids1000_cosebis_theory_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote manifest to {manifest_path}")

    # -- Write summary --
    summary_lines = [
        "# COSEBIs Theory-Smoke Summary",
        "",
        f"- **Data**: {len(data_df)}-element COSEBIs vector, {cov.shape[0]}×{cov.shape[1]} covariance",
        f"- **Theta grid**: {n_theta} {spacing} points [{theta_min}', {theta_max}']",
        f"- **Filters**: {n_modes} COSEBIs modes (n=1..{n_modes})",
        f"- **G1 backend**: {theory_backend}",
        "",
        "## Results",
        "",
        "| Model | chi2 | ndof | chi2/dof | finite |",
        "|-------|------|------|----------|--------|",
    ]
    for label, r in results.items():
        chi2_str = f"{r['chi2']:.2f}" if np.isfinite(r["chi2"]) else "inf"
        chi2dof = f"{r['chi2']/r['ndof']:.3f}" if np.isfinite(r["chi2"]) and r["ndof"] > 0 else "N/A"
        summary_lines.append(f"| {label} | {chi2_str} | {r['ndof']} | {chi2dof} | {r['n_finite']}/{len(data_df)} |")
    summary_lines.extend([
        "",
        "## Caveats",
        "",
        "1. This is a convention smoke-test, not a precision cosmology result.",
        "2. The COSEBIs filters are ported from KiDS `measure_cosebis.py` with roots/norms for θ∈[0.5',300'].",
        "3. The G1 pipeline uses its internal CLASS + Limber + Σ_lensing(Ω_m, s, model) stack.",
        "4. Parameter values are the xi±-only best-fits from v1.1 — not re-optimized in COSEBIs space.",
        "5. A large χ² may indicate unit/normalization mismatch between the COSEBIs filter convention",
        "   and the G1 pipeline's xi± prediction, not necessarily a physical model failure.",
        "6. The covariance is the official KiDS COSEBIs covariance (bestfit == blindC).",
        "",
        "*Generated by Phase 3C COSEBIs theory-smoke, 2026-05-30*",
    ])
    summary_path = outdir / "chi2_smoke_summary.md"
    (outdir / "chi2_smoke_summary.md").write_text("\n".join(summary_lines))
    print(f"Wrote summary to {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
