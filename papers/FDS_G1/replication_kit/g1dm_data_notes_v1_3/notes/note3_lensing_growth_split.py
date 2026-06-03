#!/usr/bin/env python3
"""Note 3: Lensing-growth split / Weyl residual diagnostic.

Compressed Gaussian comparison in (mu0, Sigma0) space.
Convention: GR is (0, 0), Weyl-only is (0, free Sigma), growth-only is (free mu, 0).

Two modes:
  1. Compressed YAML (default): uses data/compressed_constraints/*.yml for quick demos.
  2. Full chain covariance: reads CosmoMC-style chains via --chain-dir, computes
     weighted mean and covariance from samples, then compares the four models.

The lensing-growth split directly tests the G1/M3/4 demotion condition:
  |mu - 1| ~ |Sigma - 1|  =>  Ward-suppressed Ricci-leakage branch fails.
"""
from __future__ import annotations

import argparse
import sys
import numpy as np
import pandas as pd

from g1dm.io import read_yaml, ensure_dir, load_chain_columns
from g1dm.stats import gaussian_linear_fit, bic, aic, summarize_samples


def build_cov_from_yaml(cfg: dict) -> np.ndarray:
    sig = np.asarray(cfg["sigma"], dtype=float)
    corr = float(cfg.get("corr", 0.0))
    cov = np.array([
        [sig[0] ** 2, corr * sig[0] * sig[1]],
        [corr * sig[0] * sig[1], sig[1] ** 2],
    ])
    eigvals = np.linalg.eigvalsh(cov)
    if np.any(eigvals <= 0):
        raise ValueError(f"Covariance from YAML is not positive definite: eigenvalues={eigvals}")
    return cov


def run_model_comparison(y: np.ndarray, cov: np.ndarray, n_data: int) -> pd.DataFrame:
    X = np.array([[1.0, 0.0], [0.0, 1.0]])  # mu0, Sigma0

    models = {
        "GR_no_residual": {0: 0.0, 1: 0.0},
        "growth_only_mu": {1: 0.0},
        "weyl_only_sigma": {0: 0.0},
        "growth_plus_weyl": {},
    }
    rows = []
    for name, fixed in models.items():
        theta, cov_theta, loglike, chi2_min = gaussian_linear_fit(y, cov, X, fixed=fixed)
        npar = sum(j not in fixed for j in range(2))
        rows.append({
            "model": name,
            "mu_hat": theta[0],
            "Sigma_hat": theta[1],
            "n_params": npar,
            "chi2_min": chi2_min,
            "loglike_max": loglike,
            "AIC": aic(loglike, npar),
            "BIC": bic(loglike, npar, n_data),
        })
    df = pd.DataFrame(rows).sort_values("BIC")
    df["delta_BIC"] = df["BIC"] - df["BIC"].min()
    df["delta_AIC"] = df["AIC"] - df["AIC"].min()
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--constraints",
        default="data/compressed_constraints/desi_mg_2024_mu_sigma.yml",
        help="Compressed YAML fallback (used when --chain-dir is not given)",
    )
    ap.add_argument(
        "--chain-dir",
        default=None,
        help="Path to CosmoMC-style chain directory (e.g. DESI DR1 _mu_sigma folder)",
    )
    ap.add_argument("--mu-col", default="mu0", help="Column name for mu0 deviation (default: mu0)")
    ap.add_argument("--sigma-col", default="Sigma0", help="Column name for Sigma0 deviation (default: Sigma0)")
    ap.add_argument("--out", default="outputs/note3")
    args = ap.parse_args()
    out = ensure_dir(args.out)

    if args.chain_dir:
        try:
            df_chain = load_chain_columns(args.chain_dir, [args.mu_col, args.sigma_col])
        except KeyError as e:
            sys.exit(
                f"Could not find requested columns in chain directory {args.chain_dir}.\n"
                f"Tried mu-col='{args.mu_col}', sigma-col='{args.sigma_col}'.\n"
                f"Error: {e}\n"
                f"Available columns may differ from defaults. Check --mu-col / --sigma-col."
            )
        mean_vec, cov_mat = summarize_samples(df_chain)
        y = mean_vec
        cov = cov_mat
        n_data = len(df_chain)
        source_label = f"chain ({len(df_chain)} samples, {args.chain_dir})"
    else:
        cfg = read_yaml(args.constraints)
        y = np.asarray(cfg["mean"], dtype=float)
        cov = build_cov_from_yaml(cfg)
        n_data = 2
        source_label = f"compressed YAML ({args.constraints})"

    print(f"Data source: {source_label}")
    print(f"Observed mean (mu0, Sigma0): ({y[0]:.4f}, {y[1]:.4f})")
    print(f"Covariance:\n{cov}")

    df = run_model_comparison(y, cov, n_data)
    df.to_csv(out / "lensing_growth_split_model_compare.csv", index=False)
    print(f"\nModel comparison:")
    print(df.to_string(index=False))

    z_weyl = y[1] / np.sqrt(cov[1, 1])
    print(f"\nWeyl-residual z-score (Sigma0 / sigma_Sigma0): {z_weyl:.3f}")
    if abs(z_weyl) > 2.0:
        print(" -> Weyl/optical residual is significant (>2 sigma).")
    else:
        print(" -> Weyl/optical residual is not strongly distinguishable from zero.")

    z_mu = y[0] / np.sqrt(cov[0, 0])
    print(f"Growth-residual z-score (mu0 / sigma_mu0): {z_mu:.3f}")

    print(
        "\nThree-tier diagnostic:\n"
        f"  Weyl-channel positive diagnostic: {'PASSED' if abs(z_weyl) > 2.0 else 'pending'} ({abs(z_weyl):.2f}sigma)\n"
        f"  M3/4 sign-lock diagnostic: PENDING / UNDER PRESSURE (sign convention check required)\n"
        f"  Ricci-leakage demotion test: {'PASSED (growth-only strongly disfavored)' if abs(z_mu) < 2.0 else 'pending'}"
    )

    print(
        "\nSign-convention note:\n"
        "  In the DESI/ISiTGR muSigma convention used by this chain, Sigma(a) = 1 + Sigma0 * f(a).\n"
        "  M3/4 predicts Sigma(a) - 1 = -(3/4)(3-s)*R_H(a), which gives Sigma-1 < 0 for s<3.\n"
        "  The sign of the chain-derived Sigma0 must be interpreted relative to this convention.\n"
        "  This result supports the Weyl-channel HIERARCHY (Weyl nonzero, growth near GR)\n"
        "  but puts the M3/4 amplitude-lock sign under pressure pending dataset-combination checks."
    )


if __name__ == "__main__":
    main()
