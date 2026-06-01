#!/usr/bin/env python3
"""
Phase 4G: Prior-Regularized EE+nE Refit
Boundary statement:
Phase 4G is a diagnostic prior-regularized local refit on the validated EE+nE BandPower bridge. It is not full 3×2pt, not production evidence, not nested evidence, and not a final cosmological constraint. The nn/clustering channel remains unavailable locally.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv
import json
from pathlib import Path
import random

# ==============================================
# GLOBAL CONFIG
# ==============================================
BASELINE_SIGMA_BOUNDS = (-0.5, 0.5)
RANDOM_SEED = 1234
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Prior definitions (exact as approved)
PRIOR_MU_M = 0.0
PRIOR_SIGMA_M = 0.015
PRIOR_MU_B = 1.0
PRIOR_SIGMA_B = 0.3
PRIOR_MU_AIA = 1.0
PRIOR_SIGMA_AIA = 0.5

# Data paths (same as Phase4F, no changes)
DATA_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_200_standard.csv"
COV_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_covariance_200.npy"
PNE_BASELINE_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/phase3i_pneE/g1_pneE_smoke_predictions.csv"
PEE_BASELINE_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke/"

OUTDIR = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4g_prior_regularized_refit/")
OUTDIR.mkdir(exist_ok=True, parents=True)

# ==============================================
# Load data and precompute covariance components
# ==============================================
# Precompute component matrices for chi2 split
n_pne = 80
n_pee = 120
cov_full = np.load(COV_PATH)
inv_cov_full = inv(cov_full)
cov_EE = cov_full[n_pne:, n_pne:]
cov_nE = cov_full[:n_pne, :n_pne]
inv_cov_EE = inv(cov_EE)
inv_cov_nE = inv(cov_nE)
Q = inv_cov_full
Q_EE = Q[n_pne:, n_pne:]
Q_nE = Q[:n_pne, :n_pne]
Q_EN = Q[n_pne:, :n_pne]

# Load baseline predictions
pne_baseline_df = pd.read_csv(PNE_BASELINE_PATH)
pne_baseline = pne_baseline_df["g1_prediction"].values
lens_bins_pne = pne_baseline_df["bin1"].values
mask_lens0 = (lens_bins_pne == 0)
mask_lens1 = (lens_bins_pne == 1)

# Load PEE baselines per model
pee_baseline = {}
for model in ["lcdm", "m34", "mkappa"]:
    df = pd.read_csv(Path(PEE_BASELINE_PATH) / f"{model}_peeE_prediction.csv")
    pee_baseline[model] = df["prediction"].values

# ==============================================
# Prediction functions
# ==============================================
def predict_lcdm(theta):
    A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    mean_m = np.mean([m0, m1, m2, m3, m4])
    pee = pee_baseline["lcdm"] * (1 + mean_m)
    pne = pne_baseline.copy()
    pne[mask_lens0] *= b0
    pne[mask_lens1] *= b1
    return np.concatenate([pne, pee])

def predict_m34(theta):
    s, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    mean_m = np.mean([m0, m1, m2, m3, m4])
    pee = pee_baseline["m34"] * (1 + mean_m)
    pne = pne_baseline.copy() * (s / 2.0)
    pne[mask_lens0] *= b0
    pne[mask_lens1] *= b1
    return np.concatenate([pne, pee])

def predict_mkappa(theta):
    s, kappa, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    mean_m = np.mean([m0, m1, m2, m3, m4])
    pee = pee_baseline["mkappa"] * (1 + mean_m)
    pne = pne_baseline.copy() * (s / 2.0) * (1 - kappa)
    pne[mask_lens0] *= b0
    pne[mask_lens1] *= b1
    return np.concatenate([pne, pee])

def predict_constsigma(theta):
    Sigma0, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    mean_m = np.mean([m0, m1, m2, m3, m4])
    pee = pee_baseline["lcdm"] * (1 + mean_m) * ((1 + Sigma0) ** 2)
    pne = pne_baseline.copy() * (1 + Sigma0)
    pne[mask_lens0] *= b0
    pne[mask_lens1] *= b1
    return np.concatenate([pne, pee])

def predict_binsigma2(theta):
    Sigma_bin0, Sigma_bin1, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    mean_m = np.mean([m0, m1, m2, m3, m4])
    mean_Sigma = (Sigma_bin0 + Sigma_bin1) / 2.0
    pee = pee_baseline["lcdm"] * (1 + mean_m) * ((1 + mean_Sigma) ** 2)
    pne = pne_baseline.copy()
    pne[mask_lens0] *= b0 * (1 + Sigma_bin0)
    pne[mask_lens1] *= b1 * (1 + Sigma_bin1)
    return np.concatenate([pne, pee])

# ==============================================
# Model metadata
# ==============================================
model_info = {
    "lcdm": {
        "param_names": ["A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func": predict_lcdm,
        "base_bounds": [
            (-10.0, 10.0), # A_IA
            (-0.1, 0.1),   # m_src0
            (-0.1, 0.1),   # m_src1
            (-0.1, 0.1),   # m_src2
            (-0.1, 0.1),   # m_src3
            (-0.1, 0.1),   # m_src4
            (0.2, 5.0),    # b_lens0
            (0.2, 5.0),    # b_lens1
        ]
    },
    "m34": {
        "param_names": ["s", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func": predict_m34,
        "base_bounds": [
            (1.0, 3.0),     # s (Phase4B bound)
            (-10.0, 10.0), # A_IA
            (-0.1, 0.1),   # m_src0
            (-0.1, 0.1),   # m_src1
            (-0.1, 0.1),   # m_src2
            (-0.1, 0.1),   # m_src3
            (-0.1, 0.1),   # m_src4
            (0.2, 5.0),    # b_lens0
            (0.2, 5.0),    # b_lens1
        ]
    },
    "mkappa": {
        "param_names": ["s", "kappa", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func": predict_mkappa,
        "base_bounds": [
            (1.0, 3.0),     # s
            (0.0, 1.5),     # kappa (Phase4B bound)
            (-10.0, 10.0), # A_IA
            (-0.1, 0.1),   # m_src0
            (-0.1, 0.1),   # m_src1
            (-0.1, 0.1),   # m_src2
            (-0.1, 0.1),   # m_src3
            (-0.1, 0.1),   # m_src4
            (0.2, 5.0),    # b_lens0
            (0.2, 5.0),    # b_lens1
        ]
    },
    "constsigma": {
        "param_names": ["Sigma0", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func": predict_constsigma,
        "base_bounds": [
            BASELINE_SIGMA_BOUNDS, # Sigma0
            (-10.0, 10.0), # A_IA
            (-0.1, 0.1),   # m_src0
            (-0.1, 0.1),   # m_src1
            (-0.1, 0.1),   # m_src2
            (-0.1, 0.1),   # m_src3
            (-0.1, 0.1),   # m_src4
            (0.2, 5.0),    # b_lens0
            (0.2, 5.0),    # b_lens1
        ]
    },
    "binsigma2": {
        "param_names": ["Sigma_bin0", "Sigma_bin1", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func": predict_binsigma2,
        "base_bounds": [
            BASELINE_SIGMA_BOUNDS, # Sigma_bin0
            BASELINE_SIGMA_BOUNDS, # Sigma_bin1
            (-10.0, 10.0), # A_IA
            (-0.1, 0.1),   # m_src0
            (-0.1, 0.1),   # m_src1
            (-0.1, 0.1),   # m_src2
            (-0.1, 0.1),   # m_src3
            (-0.1, 0.1),   # m_src4
            (0.2, 5.0),    # b_lens0
            (0.2, 5.0),    # b_lens1
        ]
    }
}

# ==============================================
# Prior and Utility Functions
# ==============================================
def compute_prior_penalty(theta, param_names):
    """
    Compute exact Gaussian prior penalty as specified:
    chi2_prior = sum_i((m_i - 0)/0.015)^2 + sum_a((b_a - 1)/0.3)^2 + ((A_IA - 1)/0.5)^2
    Returns:
        - prior_chi2: total prior penalty
        - pulls: dict of individual parameter pulls
    """
    m_vals = []
    b_vals = []
    a_ia_val = None
    
    for name, val in zip(param_names, theta):
        if name.startswith("m_src"):
            m_vals.append(val)
        elif name.startswith("b_lens"):
            b_vals.append(val)
        elif name == "A_IA":
            a_ia_val = val
    
    # Compute individual terms
    m_pulls = [(m - PRIOR_MU_M) / PRIOR_SIGMA_M for m in m_vals]
    b_pulls = [(b - PRIOR_MU_B) / PRIOR_SIGMA_B for b in b_vals]
    a_ia_pull = (a_ia_val - PRIOR_MU_AIA) / PRIOR_SIGMA_AIA if a_ia_val is not None else 0.0
    
    chi2_m = sum(p**2 for p in m_pulls)
    chi2_b = sum(p**2 for p in b_pulls)
    chi2_aia = a_ia_pull**2 if a_ia_val is not None else 0.0
    
    prior_chi2 = chi2_m + chi2_b + chi2_aia
    
    # Collect all pulls
    pulls = {}
    for i, p in enumerate(m_pulls):
        pulls[f"pull_m_src{i}"] = float(p)
    for i, p in enumerate(b_pulls):
        pulls[f"pull_b_lens{i}"] = float(p)
    if a_ia_val is not None:
        pulls["pull_A_IA"] = float(a_ia_pull)
    
    # Compute max pull
    all_pulls = list(pulls.values())
    pulls["max_pull"] = float(max(np.abs(all_pulls))) if all_pulls else 0.0
    
    return float(prior_chi2), pulls

def compute_full_chi2(pred, data_vec):
    """Compute full chi2_data for prediction vector (no prior)"""
    if not np.all(np.isfinite(pred)):
        return np.inf
    res = data_vec - pred
    return float(res @ inv_cov_full @ res)

def compute_component_chi2(pred, data_vec):
    """Compute all chi2 components: block and precision matrix decomposition"""
    res = data_vec - pred
    r_E = res[n_pne:]
    r_N = res[:n_pne]
    
    # Block components (not summed to total, for diagnostic use)
    chi2_EE_block = float(r_E @ inv_cov_EE @ r_E)
    chi2_nE_block = float(r_N @ inv_cov_nE @ r_N)
    
    # Precision matrix components (sum exactly to total chi2)
    chi2_EE_prec = float(r_E @ Q_EE @ r_E)
    chi2_nE_prec = float(r_N @ Q_nE @ r_N)
    chi2_cross_prec = float(2 * r_E @ Q_EN @ r_N)
    
    return {
        "chi2_data": compute_full_chi2(pred, data_vec),
        "chi2_EE_block": chi2_EE_block,
        "chi2_nE_block": chi2_nE_block,
        "chi2_EE_precision": chi2_EE_prec,
        "chi2_nE_precision": chi2_nE_prec,
        "chi2_cross_precision": chi2_cross_prec
    }

def run_single_fit(model, start_theta, data_vec):
    """Run single L-BFGS-B fit for given model and starting parameters with prior regularization"""
    info = model_info[model]
    predict_func = info["predict_func"]
    param_names = info["param_names"]
    bounds = info["base_bounds"]
    
    # Objective function: chi2_total = chi2_data + chi2_prior
    def objective(theta):
        pred = predict_func(theta)
        chi2_data = compute_full_chi2(pred, data_vec)
        chi2_prior, _ = compute_prior_penalty(theta, param_names)
        return chi2_data + chi2_prior
    
    # Run fit
    res = minimize(
        objective,
        x0=start_theta,
        bounds=bounds,
        method="L-BFGS-B",
        options={"maxiter": 1000, "ftol": 1e-6, "gtol": 1e-6, "disp": False}
    )
    
    # Process results
    x_best = res.x
    pred_best = predict_func(x_best)
    
    chi2_total = res.fun
    chi2_data = compute_full_chi2(pred_best, data_vec)
    chi2_prior, pulls = compute_prior_penalty(x_best, param_names)
    success = res.success
    
    # Check boundary hits
    bound_hits = []
    for i, p in enumerate(param_names):
        low, high = bounds[i]
        val = x_best[i]
        if np.isclose(val, low, rtol=1e-3):
            bound_hits.append(f"{p}:low")
        elif np.isclose(val, high, rtol=1e-3):
            bound_hits.append(f"{p}:high")
    
    # Return full result dict
    components = compute_component_chi2(pred_best, data_vec)
    return {
        "model": model,
        "success": success,
        "chi2_data": chi2_data,
        "chi2_prior": chi2_prior,
        "chi2_total": chi2_total,
        "params": dict(zip(param_names, [float(v) for v in x_best])),
        "bound_hits": ";".join(bound_hits),
        **pulls,
        **components
    }

def generate_starting_points(model):
    """Generate all standardized starting points for each model"""
    info = model_info[model]
    param_names = info["param_names"]
    bounds = info["base_bounds"]
    start_points = []
    start_labels = []
    
    # 1. LCDM baseline starting point (shared nuisance defaults)
    if "Sigma0" in param_names or "Sigma_bin0" in param_names:
        # sigma models
        base_start = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]  # Sigma0=0, A_IA=1, m's=0, b's=1
        if model == "binsigma2":
            base_start = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]  # extra Sigma_bin1 param
        start_points.append(base_start)
        start_labels.append("lcdm_baseline_start")
        
        # 2. High sigma starting point
        if model == "constsigma":
            high_sigma_start = [0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
        elif model == "binsigma2":
            high_sigma_start = [0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
        else:
            # non-sigma models use phase4b bestfit as start
            phase4b_bestfit = {
                "m34": [2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
                "mkappa": [2.0, 0.75, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
                "lcdm": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
            }
            high_sigma_start = phase4b_bestfit[model]
        start_points.append(high_sigma_start)
        start_labels.append("high_sigma_start")
    else:
        # non-sigma models: start with phase4b bestfit
        phase4b_bestfit = {
            "m34": [2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
            "mkappa": [2.0, 0.75, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
            "lcdm": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
        }
        start_points.append(phase4b_bestfit[model])
        start_labels.append("phase4b_bestfit_start")
    
    # 3-12. 10 random uniform starting points
    for i in range(10):
        random_start = []
        for (low, high) in bounds:
            # sample uniformly between bounds
            val = np.random.uniform(low, high)
            random_start.append(val)
        start_points.append(random_start)
        start_labels.append(f"random_start_{i}")
    
    return start_points, start_labels

def main():
    print("Phase 4G: Prior-Regularized EE+nE Refit")
    print("=" * 80)
    
    # Load data
    print("Loading data...")
    data_df = pd.read_csv(DATA_PATH)
    data_vec = data_df["value"].values
    print(f"Loaded {len(data_vec)} data points")
    
    all_models = ["lcdm", "m34", "mkappa", "constsigma", "binsigma2"]
    results = []
    
    # ==============================================
    # Run multi-start fits for all models
    # ==============================================
    print("\nRunning multi-start fits for all models...")
    multistart_results = []
    
    for model in all_models:
        print(f"  Running fits for {model}...")
        start_points, start_labels = generate_starting_points(model)
        
        for start_idx, (start_theta, start_label) in enumerate(zip(start_points, start_labels)):
            res = run_single_fit(model, start_theta, data_vec)
            res["start_label"] = start_label
            multistart_results.append(res)
            if (start_idx + 1) % 5 == 0:
                print(f"    Completed {start_idx + 1}/{len(start_points)} fits")
    
    # Save multi-start results
    multistart_df = pd.DataFrame(multistart_results)
    multistart_path = OUTDIR / "multistart_results.csv"
    multistart_df.to_csv(multistart_path, index=False)
    print(f"  Saved multi-start results to {multistart_path}")
    
    # Extract best fit per model
    best_fits_per_model = {}
    for model in all_models:
        model_subset = multistart_df[multistart_df["model"] == model]
        best_idx = model_subset["chi2_total"].idxmin()
        best_fits_per_model[model] = multistart_df.loc[best_idx].to_dict()
        best_chi2 = best_fits_per_model[model]["chi2_total"]
        print(f"  Best {model} total chi2: {best_chi2:.2f} (data: {best_fits_per_model[model]['chi2_data']:.2f}, prior: {best_fits_per_model[model]['chi2_prior']:.2f})")
    
    # Save best fits per model
    best_fit_df = pd.DataFrame.from_records(list(best_fits_per_model.values()))
    best_fit_path = OUTDIR / "multistart_best_by_model.csv"
    best_fit_df.to_csv(best_fit_path, index=False)
    
    # ==============================================
    # Generate manifest
    # ==============================================
    print("\nGenerating manifest...")
    manifest = {
        "phase": "4G",
        "scope": "Prior-regularized EE+nE BandPower refit",
        "models_tested": all_models,
        "n_multi_start_per_model": len(start_points),
        "baseline_sigma_bounds": list(BASELINE_SIGMA_BOUNDS),
        "prior_parameters": {
            "m_mu": PRIOR_MU_M,
            "m_sigma": PRIOR_SIGMA_M,
            "b_mu": PRIOR_MU_B,
            "b_sigma": PRIOR_SIGMA_B,
            "A_IA_mu": PRIOR_MU_AIA,
            "A_IA_sigma": PRIOR_SIGMA_AIA
        },
        "random_seed": RANDOM_SEED,
        "result_files": {
            "multistart_results": str(multistart_path),
            "multistart_best_by_model": str(best_fit_path)
        },
        "boundary_statement": "Phase 4G is a diagnostic prior-regularized local refit on the validated EE+nE BandPower bridge. It is not full 3×2pt, not production evidence, not nested evidence, and not a final cosmological constraint. The nn/clustering channel remains unavailable locally.",
        "status": "complete"
    }
    
    manifest_path = OUTDIR / "phase4g_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Generate summary markdown
    print("\nGenerating summary document...")
    summary_content = "# Phase4G: Prior-Regularized EE+nE Refit Summary\n"
    summary_content += "## Status: COMPLETE\n\n"
    summary_content += "### Boundary Statement\n"
    summary_content += "> Phase 4G is a diagnostic prior-regularized local refit on the validated EE+nE BandPower bridge. It is not full 3×2pt, not production evidence, not nested evidence, and not a final cosmological constraint. The nn/clustering channel remains unavailable locally.\n\n"
    summary_content += "### Prior Setup\n"
    summary_content += "- Shear calibration (m_i): $\\mathcal{N}(0, 0.015)$\n"
    summary_content += "- Galaxy bias (b_a): $\\mathcal{N}(1.0, 0.3)$\n"
    summary_content += "- Intrinsic alignment (A_IA): $\\mathcal{N}(1.0, 0.5)$\n\n"
    summary_content += "## Best Fit Results by Model\n"
    summary_content += "| Model | $\\chi^2_{\\text{data}}$ | $\\chi^2_{\\text{prior}}$ | $\\chi^2_{\\text{total}}$ | Max Prior Pull | Bound Hits |\n"
    summary_content += "|-------|-------------------------|--------------------------|--------------------------|-----------------|------------|\n"
    for model in all_models:
        best = best_fits_per_model[model]
        summary_content += f"| {model} | {best['chi2_data']:.2f} | {best['chi2_prior']:.2f} | {best['chi2_total']:.2f} | {best['max_pull']:.2f} | {best['bound_hits'] if best['bound_hits'] else 'None'} |\n"
    
    # Add component chi2 breakdown
    summary_content += "\n## Component Chi2 Breakdown (Best Fits)\n"
    summary_content += "| Model | Total | EE Block | nE Block | EE Precision | nE Precision | Cross Precision |\n"
    summary_content += "|-------|-------|----------|----------|--------------|--------------|-----------------|\n"
    for model in all_models:
        best = best_fits_per_model[model]
        summary_content += f"| {model} | {best['chi2_data']:.2f} | {best['chi2_EE_block']:.2f} | {best['chi2_nE_block']:.2f} | {best['chi2_EE_precision']:.2f} | {best['chi2_nE_precision']:.2f} | {best['chi2_cross_precision']:.2f} |\n"
    
    summary_content += "\n## Interpretation\n"
    summary_content += "Results are diagnostic only. All inferences are pending full review. No model evidence claims are made.\n"
    
    summary_path = OUTDIR / "PHASE4G_SUMMARY.md"
    with open(summary_path, "w") as f:
        f.write(summary_content)
    
    print("\n" + "=" * 80)
    print("✅ Phase4G prior-regularized refit completed successfully!")
    print(f"All outputs saved to: {OUTDIR}")

if __name__ == "__main__":
    main()
