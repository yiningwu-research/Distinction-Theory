#!/usr/bin/env python3
"""Note 4b-lite: KiDS-1000 BandPower covariance readiness check.

Phase 4b-lite: covariance readiness check.
NOT an SRO evidence test.
NOT an S8 residual test.
NOT a source-vs-optics model comparison.

Full Phase 4b SRO template fitting is BLOCKED until model vectors
m_Planck and m_KiDS are generated via KCAP/CosmoSIS.
"""
from __future__ import annotations

import argparse
import numpy as np
from pathlib import Path

from g1dm.io import ensure_dir


DATA_FITS = (
    "data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release/"
    "data_fits/bp_KIDS1000_BlindC_with_m_bias_V1.0.0A_ugriZYJHKs_photoz_"
    "SG_mask_LF_svn_309c_2Dbins_v2_goldclasses_Flag_SOM_Fid.fits"
)


def load_bandpower(fits_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load BandPower data vector and covariance.

    Returns
    -------
    d : ndarray, shape (200,)
        Data vector: PneE (80) + PeeE (120) concatenated.
    C : ndarray, shape (200, 200)
        Covariance matrix.
    """
    from astropy.io import fits
    with fits.open(fits_path) as hdul:
        covmat = np.array(hdul["COVMAT"].data, dtype=float)
        pnee = hdul["PneE"].data
        peee = hdul["PeeE"].data
    # Concatenate PneE + PeeE values (both have a 'VALUE' column)
    d_pnee = np.array(pnee["VALUE"], dtype=float)
    d_peee = np.array(peee["VALUE"], dtype=float)
    d = np.concatenate([d_pnee, d_peee])
    return d, covmat


def check_covariance(C: np.ndarray) -> dict:
    """Diagnose covariance positive definiteness and condition."""
    eigvals = np.linalg.eigvalsh(C)
    n_neg = int(np.sum(eigvals < -1e-12))
    n_zero = int(np.sum(np.abs(eigvals) <= 1e-12))
    lam_min = eigvals.min()
    lam_max = eigvals.max()
    cond = lam_max / max(lam_min, 1e-300)

    pd = n_neg == 0 and n_zero == 0

    try:
        L = np.linalg.cholesky(C)
        chol_ok = True
    except np.linalg.LinAlgError:
        L = None
        chol_ok = False

    return {
        "shape": C.shape,
        "n_neg": n_neg,
        "n_zero": n_zero,
        "pd": pd,
        "lam_min": lam_min,
        "lam_max": lam_max,
        "condition_number": cond,
        "cholesky_ok": chol_ok,
    }


def whitening_stats(d: np.ndarray, C: np.ndarray, L: np.ndarray) -> dict:
    """Whiten data vector and report statistics."""
    w = np.linalg.solve(L, d)
    abs_w = np.abs(w)
    return {
        "w_mean": float(np.mean(w)),
        "w_std": float(np.std(w)),
        "w_max_abs": float(abs_w.max()),
        "n_w_gt_5": int(np.sum(abs_w > 5)),
    }


def total_shear_sn(d: np.ndarray, C: np.ndarray) -> float:
    """Total S/N of data vector against zero-shear null.

    This is a shear-null detection statistic, NOT an S8 residual.
    """
    return float(np.sqrt(d @ np.linalg.solve(C, d)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fits", default=DATA_FITS, help="Path to KiDS BandPower FITS file")
    ap.add_argument("--out", default="outputs/note4b_bp_covariance_ready")
    args = ap.parse_args()
    out = ensure_dir(args.out)

    print("=" * 60)
    print("Phase 4b-lite: covariance readiness check")
    print("NOT an SRO evidence test.")
    print("NOT an S8 residual test.")
    print("NOT a source-vs-optics model comparison.")
    print("=" * 60)
    print()

    fits_path = Path(args.fits)
    if not fits_path.exists():
        print(f"FITS file not found: {fits_path}")
        print("Download KiDS-1000 tarball per docs/KIDS1000_DOWNLOAD_PLAN.md")
        return

    d, C = load_bandpower(str(fits_path))
    print(f"BandPower data vector: {len(d)} elements ({80} PneE + {120} PeeE)")
    print(f"Covariance shape: {C.shape}")
    print()

    diag = check_covariance(C)
    print("Covariance diagnostics:")
    print(f"  Positive definite: {diag['pd']}")
    print(f"  Cholesky: {'OK' if diag['cholesky_ok'] else 'FAILED'}")
    print(f"  n_neg = {diag['n_neg']}, n_zero = {diag['n_zero']}")
    print(f"  lambda_min = {diag['lam_min']:.2e}")
    print(f"  lambda_max = {diag['lam_max']:.2e}")
    print(f"  condition number = {diag['condition_number']:.1e}")
    print()

    if not diag["pd"]:
        print("WARNING: Covariance is not positive definite. SRO fit blocked.")
        print("  COSEBIs and xi_pm share this issue; see Phase 4a results.")
        return

    L = np.linalg.cholesky(C)
    wstats = whitening_stats(d, C, L)
    print("Whitened data vector (w = L^{-1} d):")
    print(f"  mean = {wstats['w_mean']:.3f}")
    print(f"  std  = {wstats['w_std']:.3f}")
    print(f"  max |w| = {wstats['w_max_abs']:.2f}")
    print(f"  |w| > 5: {wstats['n_w_gt_5']} components")
    print()

    sn = total_shear_sn(d, C)
    print(f"Shear-null S/N = sqrt(d^T C^{-1} d) = {sn:.1f}")
    print("  (Detection against zero-shear null, NOT an S8 residual.)")
    print()

    print("Phase 4b-lite: PASSED.")
    print("BandPower covariance is ready for template-level inference.")
    print()
    print("BLOCKED: Full Phase 4b SRO fit requires model vectors m_Planck, m_KiDS.")
    print("  Generate via KCAP/CosmoSIS using the config files in:")
    print("  chains_and_config_files/main_chains_iterative_covariance/bp/config/")
    print("  (values.ini, pipeline.ini, priors.ini)")
    print("  Then compute r = d - m_0 and fit SRO templates under C.")

    import json
    summary = {
        "phase": "4b-lite",
        "label": "covariance readiness check, NOT SRO evidence",
        "n_data": 200,
        "shear_null_sn": sn,
        **diag,
        **wstats,
    }
    with open(out / "phase4b_covariance_ready.json", "w") as f:
        json.dump(summary, f, indent=2, default=float)


if __name__ == "__main__":
    main()
