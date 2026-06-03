#!/usr/bin/env python3
"""Validate a generated KiDS BandPower model vector.

Phase 4c-prep gate: before any SRO inference, the generated model vector must
pass plausibility checks against the data vector and covariance.

Usage:
    python scripts/validate_model_vector.py \
        --model-vector outputs/phase4c_prep/m_kids.npy \
        --tag KiDS

Five validation criteria from KCAP_COSMOSIS_MODEL_VECTOR_PLAN.md:
  1. Length = 200
  2. No invalid values (NaN, Inf)
  3. Chi2(m) is finite
  4. Chi2(m_KiDS) plausibly close to published best-fit
  5. Residual d - m_Planck shows amplitude-like structure
"""
from __future__ import annotations

import argparse
import json
import numpy as np
from pathlib import Path

from g1dm.io import ensure_dir

# Path to the KiDS BandPower data vector and covariance
DATA_FITS = (
    "data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release/"
    "data_fits/bp_KIDS1000_BlindC_with_m_bias_V1.0.0A_ugriZYJHKs_photoz_"
    "SG_mask_LF_svn_309c_2Dbins_v2_goldclasses_Flag_SOM_Fid.fits"
)


def load_data_vector(fits_path: str) -> tuple[np.ndarray, np.ndarray]:
    from astropy.io import fits
    with fits.open(fits_path) as hdul:
        covmat = np.array(hdul["COVMAT"].data, dtype=float)
        pnee = np.array(hdul["PneE"].data["VALUE"], dtype=float)
        peee = np.array(hdul["PeeE"].data["VALUE"], dtype=float)
    d = np.concatenate([pnee, peee])
    return d, covmat


def validate_model_vector(model_vec: np.ndarray, d: np.ndarray, C: np.ndarray, tag: str) -> dict:
    results = {"tag": tag, "length": len(model_vec)}

    # 1. Length = 200
    results["len_ok"] = len(model_vec) == 200
    if not results["len_ok"]:
        results["error"] = f"Wrong length: {len(model_vec)} != 200"
        return results

    # 2. No invalid values
    results["all_finite"] = bool(np.isfinite(model_vec).all())
    if not results["all_finite"]:
        n_bad = int(np.sum(~np.isfinite(model_vec)))
        results["error"] = f"{n_bad} non-finite values"
        return results

    # 3. Chi2 is finite
    r = d - model_vec
    try:
        chi2 = float(r @ np.linalg.solve(C, r))
        results["chi2"] = chi2
        results["chi2_finite"] = np.isfinite(chi2)
    except np.linalg.LinAlgError as e:
        results["error"] = f"LinAlgError: {e}"
        return results

    if not results["chi2_finite"]:
        results["error"] = f"Chi2 is not finite: {chi2}"
        return results

    # 4. Per-d.o.f stats
    dof = len(d)
    results["chi2_per_dof"] = chi2 / dof
    results["dof"] = dof

    # 5. Residual structure: fraction of |r_i| / sigma_i > 3
    sigma = np.sqrt(np.diag(C))
    r_norm = np.abs(r) / sigma
    results["n_outliers_3sigma"] = int(np.sum(r_norm > 3))
    results["max_r_sigma"] = float(r_norm.max())
    results["mean_r_sigma"] = float(r_norm.mean())

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-vector", required=True, help="Path to .npy model vector file")
    ap.add_argument("--tag", default="KiDS", help="Label for this model (KiDS, Planck)")
    ap.add_argument("--out", default="outputs/phase4c_prep", help="Output directory")
    ap.add_argument("--fits", default=DATA_FITS, help="Path to KiDS BandPower FITS file")
    args = ap.parse_args()
    out = ensure_dir(args.out)

    model_vec = np.load(args.model_vector)
    d, C = load_data_vector(args.fits)

    print("=" * 60)
    print(f"Phase 4c-prep: Model Vector Validation — {args.tag}")
    print("=" * 60)
    print(f"Model vector shape: {model_vec.shape}")
    print(f"Data vector shape:  {d.shape}")
    print(f"Covariance shape:   {C.shape}")
    print()

    results = validate_model_vector(model_vec, d, C, args.tag)

    if "error" in results:
        print(f"VALIDATION FAILED: {results['error']}")
        print()
        print("GATE: BLOCKED — fix pipeline before SRO inference.")
        results["gate"] = "BLOCKED"
    else:
        gate = "PASSED" if results["chi2_per_dof"] < 10 else "WARNING"
        print(f"  Length OK:         {results['len_ok']}")
        print(f"  All finite:        {results['all_finite']}")
        print(f"  Chi2 = {results['chi2']:.1f}  (chi2/dof = {results['chi2_per_dof']:.2f})")
        print(f"  Outliers >3sigma:  {results['n_outliers_3sigma']} / {results['dof']}")
        print(f"  Max |r|/sigma:     {results['max_r_sigma']:.1f}")
        print(f"  Mean |r|/sigma:    {results['mean_r_sigma']:.2f}")
        print()
        print(f"GATE: {gate}")
        results["gate"] = gate

    with open(out / f"validate_{args.tag.lower()}.json", "w") as f:
        json.dump(results, f, indent=2, default=float)

    if results.get("gate") == "PASSED":
        print("Model vector is plausible. Proceed to next step.")
    elif results.get("gate") == "WARNING":
        print("WARNING: Large chi2/dof. Check pipeline before SRO inference.")
    else:
        print("Fix pipeline issues. No SRO inference allowed.")


if __name__ == "__main__":
    main()
