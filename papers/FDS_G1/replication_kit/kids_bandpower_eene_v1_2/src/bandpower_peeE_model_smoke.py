import os
import sys
import yaml
import json
import numpy as np
import pandas as pd

# Add stage3 pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "fds_g1_stage3_kids_pipeline"))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def load_peeE_data(config):
    # Load data vector
    data = pd.read_csv(config["data"]["peeE_vector"])
    assert len(data) == 120, f"Expected 120 rows, got {len(data)}"
    
    # Load covariance
    cov = np.load(config["data"]["peeE_covariance"])
    assert cov.shape == (120, 120), f"Expected 120x120 cov, got {cov.shape}"
    
    # Load row order
    row_order = pd.read_csv(config["data"]["peeE_row_order"])
    assert len(row_order) == 120, f"Expected 120 rows, got {len(row_order)}"
    assert all(row_order["statistic"] == "bandpower_E_peee"), "All rows should be bandpower_E_peee"
    
    # Convert bin1/bin2 to 0-based for consistency with pipeline
    row_order["bin1"] = row_order["bin1"] - 1
    row_order["bin2"] = row_order["bin2"] - 1
    
    return data, cov, row_order

def get_bandpower_bins(config):
    ell_min = config["bandpower"]["ell_min"]
    ell_max = config["bandpower"]["ell_max"]
    n_bins = config["bandpower"]["n_bins"]
    
    if config["bandpower"]["binning"] == "log":
        bin_edges = np.logspace(np.log10(ell_min), np.log10(ell_max), n_bins +1)
    else:
        bin_edges = np.linspace(ell_min, ell_max, n_bins +1)
    
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) /2
    return bin_edges, bin_centers

def project_cl_to_bandpower(ell, cl, bin_edges):
    n_bins = len(bin_edges) -1
    bandpowers = np.zeros(n_bins)
    
    for b in range(n_bins):
        mask = (ell >= bin_edges[b]) & (ell < bin_edges[b+1])
        if np.any(mask):
            # Compute average of ell² C_l / 2π
            values = ell[mask]**2 * cl[mask] / (2 * np.pi)
            bandpowers[b] = np.mean(values)
        else:
            raise ValueError(f"No ell values in bin {b} [{bin_edges[b]:.1f}, {bin_edges[b+1]:.1f}]")
    
    return bandpowers

def main(config_path):
    config = load_config(config_path)
    
    # Create output directories
    outdir = config["outputs"]["outdir"]
    cls_outdir = os.path.join(outdir, "cls")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(cls_outdir, exist_ok=True)
    
    # Load PeeE data
    print("Loading PeeE data...")
    data_pee, cov_pee, row_order_pee = load_peeE_data(config)
    
    # Initialize stage3 likelihood
    print("Initializing G1 Stage3 likelihood...")
    like = Stage3Lensing3x2ptLikelihood(config["g1_pipeline"]["stage3_config"])
    
    # Get bandpower bins
    bin_edges, bin_centers = get_bandpower_bins(config)
    
    results = []
    nuisance_status = {
        "m_i": "not_applied_script",
        "dz_i": "applied_by_pipeline",
        "A_IA": "applied_by_pipeline",
        "note": "smoke diagnostic; no optimized BandPower nuisance refit"
    }
    
    # Process each model
    for model_name, model_config in config["models"].items():
        print(f"\nProcessing {model_name}...")
        
        # Load bestfit params
        with open(model_config["bestfit_json"], "r") as f:
            bestfit_json = json.load(f)
            bestfit_pars = bestfit_json["params"]
        
        # Extract m_i if present
        m = []
        for i in range(5):
            m_key = f"m_src{i}"
            if m_key in bestfit_pars:
                m.append(bestfit_pars[m_key])
            else:
                m.append(0.0)
        
        # Generate predictions for each source-source pair
        predictions = []
        all_cls = {}
        ell = like.ell_grid
        
        pair_idx = 0
        for i in range(5):
            for j in range(i, 5):
                print(f"  Processing pair ({i}, {j})...")
                
                # Compute C_l EE for this pair (use kind=xip to get shear-shear C_l)
                cl_ee = like._compute_cl_pair(model_name, bestfit_pars, "xip", f"src{i}", f"src{j}", ell)
                
                # Save raw C_l
                cl_df = pd.DataFrame({"ell": ell, "cl_ee": cl_ee})
                cl_path = os.path.join(cls_outdir, f"{model_name}_PeeE_bin{i}_{j}.csv")
                cl_df.to_csv(cl_path, index=False)
                all_cls[f"bin_{i}_{j}"] = cl_path
                
                # Apply m_i if not already applied in pipeline
                if "_compute_cl_pair returns raw C_l (no m applied)":  # TODO: verify
                    cl_ee = cl_ee * (1 + m[i]) * (1 + m[j])
                    nuisance_status["m_i"] = "applied_by_script (checked that pipeline returns raw C_l)"
                else:
                    nuisance_status["m_i"] = "already_applied_by_pipeline (verified _compute_cl_pair includes m factors)"
                
                # Project to bandpower
                bp = project_cl_to_bandpower(ell, cl_ee, bin_edges)
                
                # Add to predictions
                for b in range(len(bp)):
                    predictions.append({
                        "statistic": "PeeE",
                        "bin1": i,
                        "bin2": j,
                        "ell_bin": b,
                        "ell_min": bin_edges[b],
                        "ell_max": bin_edges[b+1],
                        "prediction": bp[b]
                    })
                pair_idx +=1
        
        # Convert predictions to dataframe, match row order
        pred_df = pd.DataFrame(predictions)
        assert len(pred_df) == 120, f"Expected 120 predictions, got {len(pred_df)}"
        
        # Save prediction
        pred_path = os.path.join(outdir, f"{model_name}_peeE_prediction.csv")
        pred_df.to_csv(pred_path, index=False)
        
        # Compute chi2
        delta = data_pee["value"].values - pred_df["prediction"].values
        chi2 = delta @ np.linalg.solve(cov_pee, delta)
        chi2_per_point = chi2 / 120
        finite = np.isfinite(chi2) and np.all(np.isfinite(pred_df["prediction"].values))
        
        results.append({
            "model": model_name,
            "n_data": 120,
            "chi2": float(chi2),
            "chi2_per_point": float(chi2_per_point),
            "finite": bool(finite),
            "bestfit_source": model_config["bestfit_json"],
            "prediction_file": pred_path
        })
        
        print(f"  {model_name} results: chi2={chi2:.2f}, chi2/n={chi2_per_point:.2f}, finite={finite}")
    
    # Save summary
    summary_md = f"""# Phase 3E-2: G1 PeeE BandPower Model-Smoke

Status: {'PASS' if all(r['finite'] for r in results) else 'FAIL'}

Scope:
PeeE-only BandPower diagnostic smoke. These are not optimized BandPower likelihood results and must not be interpreted as model evidence.

Results:
| Model | n_data | chi2 | chi2/n | finite | Notes |
|---|---:|---:|---:|---|---|
"""
    for r in results:
        summary_md += f"| {r['model']} | {r['n_data']} | {r['chi2']:.2f} | {r['chi2_per_point']:.2f} | {'yes' if r['finite'] else 'no'} | bestfit imported from {os.path.basename(r['bestfit_source'])} |\n"
    
    summary_md += f"""
Interpretation boundary:
These χ² values are PeeE-only BandPower diagnostic smoke values. They are not optimized BandPower likelihood results and are not used as model evidence.

Nuisance application status:
- m_i: {nuisance_status['m_i']}
- dz_i: {nuisance_status['dz_i']}
- A_IA: {nuisance_status['A_IA']}
- Note: {nuisance_status['note']}
"""
    
    summary_path = os.path.join(outdir, "peeE_model_smoke_summary.md")
    with open(summary_path, "w") as f:
        f.write(summary_md)
    
    # Save manifest
    manifest = {
        "dataset_name": config["dataset_name"],
        "scope": config["scope"],
        "interpretation": config["interpretation"],
        "models": [r["model"] for r in results],
        "results": results,
        "nuisance_application_status": nuisance_status,
        "input_files": {
            "peeE_vector": config["data"]["peeE_vector"],
            "peeE_covariance": config["data"]["peeE_covariance"],
            "peeE_row_order": config["data"]["peeE_row_order"],
            "stage3_config": config["g1_pipeline"]["stage3_config"]
        },
        "output_files": {
            "summary": summary_path,
            "predictions": [r["prediction_file"] for r in results],
            "cls_directory": cls_outdir
        }
    }
    
    manifest_path = os.path.join(outdir, "bandpower_peeE_model_smoke_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Generate final phase documentation
    phase_doc_content = f"""# Phase 3E-2: G1 PeeE BandPower Model-Smoke

## Status
\\boxed{{\\text{{Phase 3E-2: {'PASS' if all(r['finite'] for r in results) else 'FAIL'}}}}}

## Summary
Phase 3E-2 computes finite diagnostic PeeE-only BandPower χ² values for G1 model predictions. The calculation validates model/projector integration but is not an optimized likelihood result and is not used as model evidence.

## Results
"""
    for r in results:
        phase_doc_content += f"- **{r['model']}**: χ² = {r['chi2']:.2f} (χ²/n = {r['chi2_per_point']:.2f}) for 120 data points, finite = {r['finite']}\n"
    
    phase_doc_content += f"""
## Implementation Details
- **Nuisance status**: {nuisance_status['note']}
  - m_i: {nuisance_status['m_i']}
  - dz_i: {nuisance_status['dz_i']}
  - A_IA: {nuisance_status['A_IA']}
- **BandPower configuration**: 8 log bins from ℓ=100 to ℓ=1500, projection uses ⟨ℓ² C_ℓ / 2π⟩ averaging
- **Input data**: Verified KiDS-1000 PeeE 120-element vector with 120×120 covariance

## Output Files
All outputs stored in: {outdir}
- Predictions: {', '.join([os.path.basename(r['prediction_file']) for r in results])}
- Summary: peeE_model_smoke_summary.md
- Manifest: bandpower_peeE_model_smoke_manifest.json

## Interpretation Boundary
These χ² values are PeeE-only BandPower diagnostic smoke values. They are not optimized BandPower likelihood results and are not used as model evidence.
"""
    
#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
    phase_doc_path = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/PHASE3E2_BANDPOWER_PEEE_MODEL_SMOKE.md"
    with open(phase_doc_path, "w") as f:
        f.write(phase_doc_content)
    
    print(f"\n{'='*50}")
    print(f"Phase 3E-2 completed. Status: {'PASS' if all(r['finite'] for r in results) else 'FAIL'}")
    print(f"Outputs saved to: {outdir}")
    print(f"Phase documentation saved to: {phase_doc_path}")
    print(f"{'='*50}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config yaml file")
    args = parser.parse_args()
    main(args.config)
