#!/usr/bin/env python3
"""Note 4: Source--Response--Optics sparse evidence audit.

Supports raw y/sigma input and standardized z-score input.
Phase 1a is a populated compressed sanity check, NOT production evidence.
Phase 2 adds an independent S8 tension proxy with r-grid sensitivity.
"""
from __future__ import annotations

import argparse
import copy
import numpy as np
import pandas as pd

from g1dm.io import read_yaml, ensure_dir
from g1dm.stats import gaussian_linear_fit, bic, aic, model_mask_grid


def resolve_design_value(val, r_value: float = 0.0) -> float:
    """Resolve design matrix entries.

    If val is a float/int, return it directly.
    If val is the string 'r', return r_value.
    If val is the string '1-r', return 1.0 - r_value.
    """
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip()
        if s == "r":
            return r_value
        if s in ("1-r", "1 - r"):
            return 1.0 - r_value
    return 0.0


def build_data_vector(cfg: dict, cap_source_z: float | None = None, r_value: float = 0.0) -> tuple:
    """Extract y, sigma, design matrix from config.

    If cfg['observables'][i] has key 'z', use y = z, sigma = 1.0
    (standardized z-score vector).
    If a cap_source_z is given and > 0, clip any observable with role == 'hard_floor'
    to at most cap_source_z.
    Design values of 'r' or '1-r' are resolved via resolve_design_value(r_value).
    """
    comps = cfg.get("components", ["source", "response", "optics"])
    obs = cfg["observables"]
    y_vals = []
    sig_vals = []
    for o in obs:
        if "z" in o:
            y_vals.append(float(o["z"]))
            sig_vals.append(1.0)
        else:
            y_vals.append(float(o["y"]))
            sig_vals.append(float(o["sigma"]))
    y = np.array(y_vals, dtype=float)
    sig = np.array(sig_vals, dtype=float)

    if cap_source_z is not None and cap_source_z > 0:
        for i, o in enumerate(obs):
            if o.get("role") == "hard_floor" and y[i] > cap_source_z:
                y[i] = float(cap_source_z)

    cov = np.diag(sig**2)
    X = np.array([[resolve_design_value(o.get("design", {}).get(c, 0.0), r_value) for c in comps] for o in obs], dtype=float)
    return y, cov, X, comps, obs


def run_audit(y, cov, X, comps, n_data, out_dir, tag=""):
    rows = []
    for mask in model_mask_grid(len(comps)):
        fixed = {j: 0.0 for j, m in enumerate(mask) if not m}
        theta, cov_theta, loglike, chi2_min = gaussian_linear_fit(y, cov, X, fixed=fixed)
        npar = sum(mask)
        label = "+".join([c for c, m in zip(comps, mask) if m])
        has_source = mask[0] if len(mask) > 0 else False
        rows.append({
            "model": label,
            **{f"theta_{c}": theta[j] for j, c in enumerate(comps)},
            "n_params": npar,
            "has_source": has_source,
            "chi2_min": chi2_min,
            "loglike_max": loglike,
            "AIC": aic(loglike, npar),
            "BIC": bic(loglike, npar, n_data),
        })
    df = pd.DataFrame(rows).sort_values("BIC")
    df["delta_BIC"] = df["BIC"] - df["BIC"].min()
    df["delta_AIC"] = df["AIC"] - df["AIC"].min()
    suffix = f"_{tag}" if tag else ""
    df.to_csv(out_dir / f"sro_sparse_model_compare{suffix}.csv", index=False)
    return df


def print_interpretation(df, r_value: float | None = None):
    best = df.iloc[0]
    print(f"\nBest model by BIC: {best['model']} (delta_BIC = {best['delta_BIC']:.2f})")
    print()

    no_source_models = df[~df["has_source"].astype(bool)]
    if len(no_source_models) > 0:
        print(
            "Models without source channel are ranked poorly, as expected from the\n"
            "carrier-floor diagnostic (Planck requires Omega_c h^2 != 0)."
        )
        print()

    source_admissible = df[df["has_source"].astype(bool)]
    if len(source_admissible) > 0:
        best_src = source_admissible.iloc[0]
        print(f"Among source-admissible masks, best is: {best_src['model']}")
        has_extra = best_src["model"] != "source"
        if has_extra:
            delta = source_admissible.iloc[0]["BIC"] - source_admissible[
                source_admissible["model"] == "source"
            ].iloc[0]["BIC"] if "source" in source_admissible["model"].values else float("nan")
            if not np.isnan(delta):
                print(f"  vs source-only: delta_BIC = {delta:.2f}")
        else:
            print(
                "  -> Source-admissible masks do not require an additional response or\n"
                "     optics component after parameter penalty."
            )

    if r_value is not None:
        print(f"\n  (r = {r_value:.2f}: S8 proxy assigns {r_value:.0%} to response, {1-r_value:.0%} to optics)")
        if r_value > 0.5:
            print(
                "  NOTE: At high r, S8 tension is assigned to response.  If response channel\n"
                "  becomes selected, this reflects artificial response pressure, not a\n"
                "  growth-leakage detection (DESI mu0 row remains near zero)."
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--observables", default="data/templates/sro_observables_template.yml")
    ap.add_argument("--out", default="outputs/note4")
    ap.add_argument("--cap-source-z", type=float, default=None,
                    help="Cap hard_floor source z-score for robustness display (e.g. 10)")
    ap.add_argument("--r-value", type=float, default=None,
                    help="Override r in design matrix: response loading fraction for S8 proxy (0=all optics, 1=all response)")
    ap.add_argument("--scenario-label", default=None,
                    help="Label for output file tagging (e.g. kids_r0, desy3_r025)")
    args = ap.parse_args()
    out = ensure_dir(args.out)

    cfg = read_yaml(args.observables)

    # Determine r_value from CLI, then from config, then default 0
    r_value = args.r_value
    if r_value is None:
        r_grid = cfg.get("observables", [{}])[-1].get("r_grid", [0.0]) if cfg.get("observables") else [0.0]
        r_value = r_grid[0] if r_grid else 0.0

    phase = cfg.get("phase", "")
    label = cfg.get("label", "")
    scenario = cfg.get("scenario", "")
    notes = cfg.get("notes", "")
    scenario_tag = args.scenario_label or ""

    print(f"Note 4 SRO Sparse Audit")
    if label:
        print(f"  {label}")
    if scenario:
        print(f"  Scenario: {scenario}")
    if scenario_tag:
        print(f"  Run tag: {scenario_tag}")
    print(f"  r = {r_value:.2f}")
    if notes:
        for line in notes.strip().split("\n"):
            print(f"  {line.strip()}")
    print()

    y, cov, X, comps, obs = build_data_vector(cfg, r_value=r_value)
    print("Observable z-score vector:")
    for i, o in enumerate(obs):
        z_val = o.get("z", o.get("y", "?"))
        role = o.get("role", "")
        design_vals = [f"{X[i,j]:.2f}" for j in range(len(comps))]
        print(f"  {o['name']:35s} z = {y[i]:8.2f}  [{o['channel']:15s}]  {role:20s}  X={design_vals}")
    print()

    tag = scenario_tag if scenario_tag else (f"r{int(r_value*100)}" if args.r_value is not None else "")
    df = run_audit(y, cov, X, comps, n_data=len(y), out_dir=out, tag=tag)
    print(f"Model comparison ({'z-scores, diagonal cov' if 'z' in obs[0] else 'raw values'}):")
    print(df.to_string(index=False))

    print_interpretation(df, r_value=r_value)

    cap_val = args.cap_source_z or cfg.get("source_floor_cap")
    if cap_val and cap_val > 0:
        y_cap, cov_cap, X_cap, comps_cap, obs_cap = build_data_vector(cfg, cap_source_z=float(cap_val), r_value=r_value)
        print(f"\n--- Robustness display: source z-score capped at {cap_val:.0f} ---")
        df_cap = run_audit(y_cap, cov_cap, X_cap, comps_cap, n_data=len(y_cap), out_dir=out, tag=f"{tag}_cap{int(cap_val)}")
        print(df_cap.to_string(index=False))
        print_interpretation(df_cap, r_value=r_value)

    print("\n---")
    phase_label = cfg.get("phase", "1a")
    print(f"This is Note 4 Phase {phase_label} — a compressed SRO audit.")
    print("It is NOT a production multi-probe evidence audit.")


if __name__ == "__main__":
    main()
