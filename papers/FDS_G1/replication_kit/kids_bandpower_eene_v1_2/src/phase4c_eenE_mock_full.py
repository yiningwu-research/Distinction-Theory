
import os
import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy.optimize import minimize
from scipy.linalg import inv, cholesky

# --------------------------
# Setup
# --------------------------
seed_base = 42000
tie_threshold = 1e-6
#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
output_dir = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4c_noisy_mock_ensemble")

# Load data/cov
cov = np.load("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_covariance_200.npy")
data = pd.read_csv("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_200_standard.csv")["value"].values

# Validate Cholesky
L = cholesky(cov)
inv_cov = inv(cov)

# Load Stage 4B-2 bestfits
bestfits = {}
for model in ["lcdm", "m34", "mkappa"]:
    with open(f"/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4b_eenE_refit/local_refit_{model}.json", "r") as f:
        bestfits[model] = json.load(f)

# --------------------------
# Prediction function
# --------------------------
baseline_peeE = {}
for model in ["lcdm", "m34", "mkappa"]:
    pred_df = pd.read_csv(f"/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke/{model}_peeE_prediction.csv")
    baseline_peeE[model] = pred_df["prediction"].values

pneE_df = pd.read_csv("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/phase3i_pneE/g1_pneE_smoke_predictions.csv")
pneE_base = pneE_df["g1_prediction"].values
lens_bins = pneE_df["bin1"].values
mask_lens1 = (lens_bins == 1)
mask_lens2 = (lens_bins == 2)

def get_pred(model, theta):
    if model == "lcdm":
        Om, s8, A, m0, m1, m2, m3, m4, b0, b1 = theta
        peeE = baseline_peeE["lcdm"].copy()
        pneE = pneE_base.copy()
    elif model == "m34":
        Om, s8, s, A, m0, m1, m2, m3, m4, b0, b1 = theta
        peeE = baseline_peeE["m34"].copy()
        pneE = pneE_base.copy() * (s/2)
    elif model == "mkappa":
        Om, s8, s, k, A, m0, m1, m2, m3, m4, b0, b1 = theta
        peeE = baseline_peeE["mkappa"].copy()
        pneE = pneE_base.copy() * (s/2)*(1 -k)
    else:
        raise ValueError
    
    m_mean = np.mean([m0, m1, m2, m3, m4])
    peeE *= (1 + m_mean)
    
    pneE[mask_lens1] *= b0
    pneE[mask_lens2] *= b1
    
    return np.concatenate([pneE, peeE])

def chi2_fn(theta, model, mock):
    try:
        pred = get_pred(model, theta)
        if not np.all(np.isfinite(pred)):
            return np.inf
        res = mock - pred
        return res @ inv_cov @ res
    except Exception as e:
        return np.inf

def is_catastrophic(result, model, theta):
    if not result.success:
        return True
    if not np.all(np.isfinite(theta)):
        return True
    
    param_names = []
    if model == "lcdm":
        param_names = ["Omega_m", "sigma8", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
    elif model == "m34":
        param_names = ["Omega_m", "sigma8", "s", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
    else:
        param_names = ["Omega_m", "sigma8", "s", "kappa", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
    
    m_i_list = ["m_src0", "m_src1", "m_src2", "m_src3", "m_src4"]
    all_m_bound = True
    for m_p in m_i_list:
        idx = param_names.index(m_p)
        low, high = (-0.1, 0.1)
        if not (np.isclose(theta[idx], low, atol=1e-6) or np.isclose(theta[idx], high, atol=1e-6)):
            all_m_bound = False
            break
    if all_m_bound:
        return True
    
    for b_p in ["b_lens0", "b_lens1"]:
        idx = param_names.index(b_p)
        low, high = (0.2, 5.0)
        if np.isclose(theta[idx], low, atol=1e-6) or np.isclose(theta[idx], high, atol=1e-6):
            return True
    
    om_idx = param_names.index("Omega_m")
    om_low, om_high = (0.15, 0.45)
    if (np.isclose(theta[om_idx], om_low, atol=1e-6) or np.isclose(theta[om_idx], om_high, atol=1e-6)):
        chi2_improv = bestfits[model]["chi2_min"] - result.fun
        if chi2_improv < 0.1:
            return True
    return False

# --------------------------
# Get starting points and bounds
# --------------------------
def get_start(model):
    bf = bestfits[model]["params"]
    if model == "lcdm":
        return [bf["Omega_m"], bf["sigma8"], bf["A_IA"], bf["m_src0"], bf["m_src1"], bf["m_src2"], bf["m_src3"], bf["m_src4"], bf["b_lens0"], bf["b_lens1"]]
    elif model == "m34":
        return [bf["Omega_m"], bf["sigma8"], bf["s"], bf["A_IA"], bf["m_src0"], bf["m_src1"], bf["m_src2"], bf["m_src3"], bf["m_src4"], bf["b_lens0"], bf["b_lens1"]]
    else:
        return [bf["Omega_m"], bf["sigma8"], bf["s"], bf["kappa"], bf["A_IA"], bf["m_src0"], bf["m_src1"], bf["m_src2"], bf["m_src3"], bf["m_src4"], bf["b_lens0"], bf["b_lens1"]]

def get_bounds(model):
    if model == "lcdm":
        return [
            [0.15,0.45], [0.3,1.3], [-5,5], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [0.2,5.0], [0.2,5.0]
        ]
    elif model == "m34":
        return [
            [0.15,0.45], [0.3,1.3], [1.0,3.0], [-5,5], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [0.2,5.0], [0.2,5.0]
        ]
    else:
        return [
            [0.15,0.45], [0.3,1.3], [1.0,3.0], [0.0,1.5], [-5,5], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [-0.1,0.1], [0.2,5.0], [0.2,5.0]
        ]

# --------------------------
# Run
# --------------------------
truth_models = ["lcdm", "m34", "mkappa"]
test_models = ["lcdm", "m34", "mkappa"]

truth_preds = {}
for m in truth_models:
    truth_preds[m] = get_pred(m, get_start(m))

results = []

rng = np.random.default_rng(seed_base + 20000)

for truth in truth_models:
    tp = truth_preds[truth]
    print(f"Processing truth model: {truth}")
    for i in range(20):
        eps = rng.normal(size=200)
        mock = tp + L @ eps
        
        fit_chi2 = {}
        fit_results = {}
        for test in test_models:
            x0 = get_start(test)
            bnds = get_bounds(test)
            res = minimize(chi2_fn, x0=x0, args=(test, mock), method="L-BFGS-B", bounds=bnds, options={"maxiter":1000})
            fit_chi2[test] = res.fun
            fit_results[test] = res
        
        min_c2 = min(fit_chi2.values())
        winners = [k for k,v in fit_chi2.items() if np.isclose(v, min_c2, atol=tie_threshold)]
        if len(winners) == 1:
            w = winners[0]
        elif len(winners) == 2:
            if "m34" in winners and "mkappa" in winners:
                w = "tie_m34_mkappa"
            elif "lcdm" in winners and "m34" in winners:
                w = "tie_lcdm_m34"
            elif "lcdm" in winners and "mkappa" in winners:
                w = "tie_lcdm_mkappa"
            else:
                w = "tie_all"
        else:
            w = "tie_all"
        
        for test in test_models:
            dc2 = fit_chi2[test] - min_c2
            theta = fit_results[test].x
            param_names = []
            if test == "lcdm":
                param_names = ["Omega_m", "sigma8", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
            elif test == "m34":
                param_names = ["Omega_m", "sigma8", "s", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
            else:
                param_names = ["Omega_m", "sigma8", "s", "kappa", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
            
            boundary_hits = []
            for idx, p in enumerate(param_names):
                if test == "lcdm":
                    bnds = get_bounds("lcdm")
                elif test == "m34":
                    bnds = get_bounds("m34")
                else:
                    bnds = get_bounds("mkappa")
                low, high = bnds[idx]
                if np.isclose(theta[idx], low, atol=1e-6):
                    boundary_hits.append(f"{p}:low")
                elif np.isclose(theta[idx], high, atol=1e-6):
                    boundary_hits.append(f"{p}:high")
            
            is_cat = is_catastrophic(fit_results[test], test, theta)
            
            results.append({
                "truth_model": truth,
                "mock_id": i,
                "test_model": test,
                "chi2_min": fit_chi2[test],
                "delta_chi2_vs_best": dc2,
                "winner": w,
                "n_params": len(get_start(test)),
                "success": fit_results[test].success,
                "boundary_hits": ";".join(boundary_hits),
                "is_catastrophic": is_cat
            })

df_out = pd.DataFrame(results)
df_out.to_csv(output_dir / "mock_results_all_n20.csv", index=False)

# --------------------------
# Generate confusion matrix
# --------------------------
confusion = df_out.groupby(["truth_model", "winner"]).size().reset_index(name="count")
total_per_truth = confusion.groupby("truth_model")["count"].transform("sum")
confusion["frequency"] = confusion["count"] / total_per_truth
confusion.to_csv(output_dir / "mock_confusion_matrix.csv", index=False)

# --------------------------
# Generate delta chi2 summary
# --------------------------
delta_chi2_summary = df_out.groupby(["truth_model", "test_model"])["delta_chi2_vs_best"].agg(["mean", "std", "min", "max"]).reset_index()
delta_chi2_summary.to_csv(output_dir / "mock_delta_chi2_summary.csv", index=False)

# --------------------------
# Generate boundary hit summary
# --------------------------
boundary_hits_all = []
for idx, row in df_out.iterrows():
    if row["boundary_hits"]:
        hits = row["boundary_hits"].split(";")
        for h in hits:
            boundary_hits_all.append({
                "truth_model": row["truth_model"],
                "test_model": row["test_model"],
                "mock_id": row["mock_id"],
                "parameter_hit": h
            })
if boundary_hits_all:
    boundary_hit_df = pd.DataFrame(boundary_hits_all)
    boundary_hit_summary = boundary_hit_df.groupby(["parameter_hit"]).size().reset_index(name="count")
    boundary_hit_summary.to_csv(output_dir / "boundary_hit_summary.csv", index=False)

# --------------------------
# Generate manifest
# --------------------------
manifest = {
    "phase": "4C",
    "scope": "EE+nE BandPower noisy mock diagnostic",
    "n_data": 200,
    "truth_models": ["lcdm", "m34", "mkappa"],
    "test_models": ["lcdm", "m34", "mkappa"],
    "seed_base": seed_base,
    "tie_threshold_delta_chi2": tie_threshold,
    "covariance": "full EE+nE 200x200 including cross-covariance",
    "interpretation": "diagnostic only; not full 3x2pt; not production evidence"
}
with open(output_dir / "phase4c_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# --------------------------
# Generate summary markdown
# --------------------------
summary_text = """# Phase 4C: EE+nE Noisy Mock Ensemble Summary
## Status: Complete

## Key Boundary Text
Phase 4C is a diagnostic noisy mock ensemble on the validated EE+nE BandPower bridge. It is not full 3x2pt, not production evidence, and not a final false-positive rate estimate. The nn/clustering channel remains unavailable locally.

## Mock Details
- Seed base: {seed_base}
- Tie threshold Δχ²: {tie_threshold}
- Covariance: full EE+nE 200x200 including cross-covariance
- Interpretation: diagnostic only; not full 3x2pt; not production evidence
""".format(seed_base=seed_base, tie_threshold=tie_threshold)

with open(output_dir / "PHASE4C_EENE_NOISY_MOCK_ENSEMBLE.md", "w") as f:
    f.write(summary_text)

print("Phase 4C complete!")
