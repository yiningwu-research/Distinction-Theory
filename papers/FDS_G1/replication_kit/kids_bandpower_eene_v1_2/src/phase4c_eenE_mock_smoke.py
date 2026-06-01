
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
# Prediction function (simplified)
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

# --------------------------
# Run 5 per truth
# --------------------------
rng = np.random.default_rng(seed_base + 5000)

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

truth_models = ["lcdm", "m34", "mkappa"]
test_models = ["lcdm", "m34", "mkappa"]

truth_preds = {}
for m in truth_models:
    truth_preds[m] = get_pred(m, get_start(m))

results = []

for truth in truth_models:
    tp = truth_preds[truth]
    for i in range(5):
        eps = rng.normal(size=200)
        mock = tp + L @ eps
        
        fit_chi2 = {}
        for test in test_models:
            x0 = get_start(test)
            bnds = get_bounds(test)
            res = minimize(chi2_fn, x0=x0, args=(test, mock), method="L-BFGS-B", bounds=bnds, options={"maxiter":1000})
            fit_chi2[test] = res.fun
        
        min_c2 = min(fit_chi2.values())
        winners = [k for k,v in fit_chi2.items() if np.isclose(v, min_c2, atol=tie_threshold)]
        if len(winners) == 1:
            w = winners[0]
        elif len(winners) == 2:
            if "m34" in winners and "mkappa" in winners:
                w = "tie_m34_mkappa"
            else:
                if "lcdm" in winners:
                    if "m34" in winners:
                        w = "tie_lcdm_m34"
                    else:
                        w = "tie_lcdm_mkappa"
                else:
                    w = "tie_all"
        else:
            w = "tie_all"
        
        for test in test_models:
            dc2 = fit_chi2[test] - min_c2
            results.append({
                "truth_model": truth,
                "mock_id": i,
                "test_model": test,
                "chi2_min": fit_chi2[test],
                "delta_chi2_vs_best": dc2,
                "winner": w
            })

df_out = pd.DataFrame(results)
df_out.to_csv(output_dir / "mock_results_smoke_n5.csv", index=False)
print("Smoke phase complete!")
