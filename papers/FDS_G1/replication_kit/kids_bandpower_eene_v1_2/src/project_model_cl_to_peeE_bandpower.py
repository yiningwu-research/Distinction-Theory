#!/usr/bin/env python3
"""
Project G1 LCDM/M3/M4 Cℓ to 120-element PeeE BandPower vector.
Phase 3E-1: PeeE-only BandPower theory smoke.
"""
import sys, yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict

# Add pipeline path to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "fds_g1_stage3_kids_pipeline"))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

def project_cl_to_bandpower(ell: np.ndarray, cl: np.ndarray, bin_edges_low: list, bin_edges_high: list) -> np.ndarray:
    """Same projection as MAP, follows KiDS convention."""
    n_bins = len(bin_edges_low)
    bandpower = np.zeros(n_bins, dtype=float)
    
    for i in range(n_bins):
        ell_min = bin_edges_low[i]
        ell_max = bin_edges_high[i]
        mask = (ell >= ell_min) & (ell <= ell_max)
        if np.sum(mask) < 2:
            raise ValueError(f"Not enough ℓ points in bin {i}: {np.sum(mask)} points")
        
        ell_bin = ell[mask]
        cl_bin = cl[mask]
        vals = (ell_bin ** 2) * cl_bin / (2 * np.pi)
        bandpower[i] = np.mean(vals)
    
    return bandpower

def load_model_params(model_name: str) -> Dict[str, float]:
    """Load bestfit parameters for each model from configs."""
#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
    params_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/configs/parameter_sets")
    param_file = params_dir / f"{model_name}_bestfit.yaml"
    if not param_file.exists():
        raise FileNotFoundError(f"Parameter file not found: {param_file}")
    
    with open(param_file) as f:
        params = yaml.safe_load(f)
    return params

def compute_model_peeE_vector(likelihood: Stage3Lensing3x2ptLikelihood, model: str,
                              theta: list, bin_low: list, bin_high: list,
                              pee_pairs: list) -> np.ndarray:
    """Compute full 120-element PeeE BandPower vector for a given model."""
    pars = likelihood.theta_to_dict(model, theta)
    ell = likelihood.ell_grid
    
    pred_vector = np.zeros(120, dtype=float)
    for pair_idx, (bin1, bin2) in enumerate(pee_pairs):
        # Cℓ for xip/xim is the shear EE power spectrum
        cl = likelihood._compute_cl_pair(model, pars, "xip", str(bin1), str(bin2), ell)
        if not np.isfinite(cl).all():
            raise ValueError(f"Nonfinite Cℓ for {model} pair {bin1}_{bin2}")
        
        # Project to 8 BandPower bins
        bp = project_cl_to_bandpower(ell, cl, bin_low, bin_high)
        assert np.isfinite(bp).all(), f"Nonfinite projection for {model} pair {bin1}_{bin2}"
        
        # Fill vector
        start_idx = pair_idx * 8
        end_idx = start_idx + 8
        pred_vector[start_idx:end_idx] = bp
    
    return pred_vector

if __name__ == "__main__":
    # Paths
    config_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/configs")
    data_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data")
    out_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_theory_smoke")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load verified data
    pee_order = pd.read_csv(data_dir / "peeE_subset" / "bandpower_PeeE_row_order_verified.csv")
    obs_data = pd.read_csv(data_dir / "peeE_subset" / "kids1000_bandpower_PeeE_data_120.csv")
    cov_pee = np.load(data_dir / "peeE_subset" / "kids1000_bandpower_PeeE_covariance_120.npy")
    obs_vals = obs_data["value"].to_numpy()
    
    # Load verified BandPower bin edges
    bin_low = [100.0, 140.28505520066747, 196.79896712654315, 276.0795396678144,
               387.298334620742, 543.3216825139734, 762.1991222319227, 1069.2514593620554]
    bin_high = [140.28505520066747, 196.79896712654315, 276.0795396678144, 387.298334620742,
                543.3216825139734, 762.1991222319227, 1069.2514593620554, 1500.0]
    
    # Get verified PeeE pair order
    pee_pair_order = [tuple(row) for _, row in pee_order[["bin1", "bin2"]].drop_duplicates().iterrows()]
    assert len(pee_pair_order) == 15
    
    # Load G1 likelihood using existing verified config
    # Use Phase 3A xipm config as base, since it has the correct tracer setup
    likelihood_config_path = config_dir / "kids_xipm_real_audit.yaml"
    likelihood = Stage3Lensing3x2ptLikelihood(str(likelihood_config_path))
    print(f"Loaded G1 likelihood, ℓ grid has {len(likelihood.ell_grid)} points: PASS")

    
    # Precompute inverse covariance for χ²
    cov_sym = (cov_pee + cov_pee.T) / 2.0
    inv_cov = np.linalg.inv(cov_sym + np.eye(120) * 1e-20)
    print("Inverted PeeE covariance: PASS")
    
    # Process each model
    models = ["lcdm", "m3", "m4"]
    chi2_results = {}
    vector_results = {}
    
    for model in models:
        print(f"\nProcessing {model.upper()}...")
        # Load bestfit parameters
        params = load_model_params(model)
        # Convert to theta vector in pipeline expected order
        theta = [params[k] for k in likelihood.param_names]
        assert len(theta) == len(likelihood.param_names), f"Mismatched param count for {model}"
        
        # Compute projected BandPower vector
        pred = compute_model_peeE_vector(likelihood, model, theta, bin_low, bin_high, pee_pair_order)
        assert len(pred) == 120
        assert np.isfinite(pred).all()
        vector_results[model] = pred
        
        # Compute χ²
        diff = obs_vals - pred
        chi2 = float(diff.T @ inv_cov @ diff)
        chi2_results[model] = chi2
        print(f"{model.upper()} χ² = {chi2:.2f}")
    
    # Also compute MAP χ² from earlier projection
    map_pred = np.load(out_dir / "map_peeE_prediction.npy")
    diff_map = obs_vals - map_pred
    chi2_map = float(diff_map.T @ inv_cov @ diff_map)
    chi2_results["map"] = chi2_map
    print(f"\nMAP χ² = {chi2_map:.2f}")
    
    # Save predicted vectors
    for model in models:
        pred_df = pd.DataFrame({
            "statistic": "bandpower_E_peee",
            "bin1": pee_order["bin1"],
            "bin2": pee_order["bin2"],
            "angbin": pee_order["angbin"],
            "ell_min": np.tile(bin_low, 15),
            "ell_max": np.tile(bin_high, 15),
            "value": vector_results[model],
            "source": f"{model}_bestfit_projection"
        })
        pred_df.to_csv(out_dir / f"{model}_peeE_prediction.csv", index=False)
        np.save(out_dir / f"{model}_peeE_prediction.npy", vector_results[model])
    
    # Generate χ² summary
    chi2_lines = [
        "# PeeE-only BandPower χ² Smoke Summary",
        "",
        "## Results (120 degrees of freedom):",
        f"* MAP: {chi2_map:.2f}",
        f"* LCDM: {chi2_results['lcdm']:.2f}",
        f"* M3: {chi2_results['m3']:.2f}",
        f"* M4: {chi2_results['m4']:.2f}",
        "",
        "## Important Interpretation Note:",
        "These values are PeeE-only theory-smoke diagnostics. They are not optimized BandPower likelihood results and should not be interpreted as model evidence.",
        "",
        "The differences between models represent relative consistency between the model predictions and the observed data vector only at the fixed bestfit parameter points, not a full likelihood analysis."
    ]
    (out_dir / "peeE_chi2_summary.md").write_text("\n".join(chi2_lines), encoding="utf-8")
    
    # Generate final manifest
    manifest = {
        "phase": "3E-1",
        "scope": "PeeE-only BandPower theory smoke",
        "data_rows": 120,
        "covariance_shape": [120, 120],
        "row_selection": "statistic == PeeE from verified BandPower row-order metadata",
        "pnee_status": "pending density-kernel integration",
        "full_200_status": "pending PneE theory projection",
        "map_prediction_check": "finite/order-only; residuals vs data expected",
        "model_chi2_interpretation": "smoke only, not evidence",
        "chi2_results": chi2_results
    }
    (out_dir / "bandpower_theory_manifest.json").write_text(pd.io.json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nAll outputs saved to {out_dir}: DONE")
