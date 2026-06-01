
import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy.optimize import minimize
from scipy.linalg import inv

#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
output_dir = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4d_nuisance_robustness")

bestfits = {}
for model in ["lcdm", "m34", "mkappa"]:
    with open(f"/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4b_eenE_refit/local_refit_{model}.json", "r") as f:
        bestfits[model] = json.load(f)

cov = np.load("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_covariance_200.npy")
data = pd.read_csv("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_200_standard.csv")["value"].values
inv_cov = inv(cov)

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
        Om, s8, s_val, A, m0, m1, m2, m3, m4, b0, b1 = theta
        peeE = baseline_peeE["m34"].copy()
        pneE = pneE_base.copy() * (s_val / 2.0)
    elif model == "mkappa":
        Om, s8, s_val, k_val, A, m0, m1, m2, m3, m4, b0, b1 = theta
        peeE = baseline_peeE["mkappa"].copy()
        pneE = pneE_base.copy() * (s_val / 2.0) * (1 - k_val)
    else:
        raise ValueError
    
    m_mean = np.mean([m0, m1, m2, m3, m4])
    peeE *= (1 + m_mean)
    
    pneE[mask_lens1] *= b0
    pneE[mask_lens2] *= b1
    
    return np.concatenate([pneE, peeE])

def chi2_fn(theta, model):
    try:
        pred = get_pred(model, theta)
        if not np.all(np.isfinite(pred)):
            return np.inf
        res = data - pred
        return res @ inv_cov @ res
    except Exception as e:
        return np.inf

def get_start(model, m_bounds_low, m_bounds_high):
    bf = bestfits[model]["params"]
    orig = {}
    clipped = {}
    if model == "lcdm":
        m0 = bf["m_src0"]
        m1 = bf["m_src1"]
        m2 = bf["m_src2"]
        m3 = bf["m_src3"]
        m4 = bf["m_src4"]
        orig = {"m_src0": m0, "m_src1": m1, "m_src2": m2, "m_src3": m3, "m_src4": m4}
        m0_clipped = np.clip(m0, m_bounds_low, m_bounds_high)
        m1_clipped = np.clip(m1, m_bounds_low, m_bounds_high)
        m2_clipped = np.clip(m2, m_bounds_low, m_bounds_high)
        m3_clipped = np.clip(m3, m_bounds_low, m_bounds_high)
        m4_clipped = np.clip(m4, m_bounds_low, m_bounds_high)
        clipped = {"m_src0": m0_clipped, "m_src1": m1_clipped, "m_src2": m2_clipped, "m_src3": m3_clipped, "m_src4": m4_clipped}
        return [bf["Omega_m"], bf["sigma8"], bf["A_IA"], m0_clipped, m1_clipped, m2_clipped, m3_clipped, m4_clipped, bf["b_lens0"], bf["b_lens1"]], orig, clipped
    elif model == "m34":
        m0 = bf["m_src0"]
        m1 = bf["m_src1"]
        m2 = bf["m_src2"]
        m3 = bf["m_src3"]
        m4 = bf["m_src4"]
        orig = {"m_src0": m0, "m_src1": m1, "m_src2": m2, "m_src3": m3, "m_src4": m4}
        m0_clipped = np.clip(m0, m_bounds_low, m_bounds_high)
        m1_clipped = np.clip(m1, m_bounds_low, m_bounds_high)
        m2_clipped = np.clip(m2, m_bounds_low, m_bounds_high)
        m3_clipped = np.clip(m3, m_bounds_low, m_bounds_high)
        m4_clipped = np.clip(m4, m_bounds_low, m_bounds_high)
        clipped = {"m_src0": m0_clipped, "m_src1": m1_clipped, "m_src2": m2_clipped, "m_src3": m3_clipped, "m_src4": m4_clipped}
        return [bf["Omega_m"], bf["sigma8"], bf["s"], bf["A_IA"], m0_clipped, m1_clipped, m2_clipped, m3_clipped, m4_clipped, bf["b_lens0"], bf["b_lens1"]], orig, clipped
    else:
        m0 = bf["m_src0"]
        m1 = bf["m_src1"]
        m2 = bf["m_src2"]
        m3 = bf["m_src3"]
        m4 = bf["m_src4"]
        orig = {"m_src0": m0, "m_src1": m1, "m_src2": m2, "m_src3": m3, "m_src4": m4}
        m0_clipped = np.clip(m0, m_bounds_low, m_bounds_high)
        m1_clipped = np.clip(m1, m_bounds_low, m_bounds_high)
        m2_clipped = np.clip(m2, m_bounds_low, m_bounds_high)
        m3_clipped = np.clip(m3, m_bounds_low, m_bounds_high)
        m4_clipped = np.clip(m4, m_bounds_low, m_bounds_high)
        clipped = {"m_src0": m0_clipped, "m_src1": m1_clipped, "m_src2": m2_clipped, "m_src3": m3_clipped, "m_src4": m4_clipped}
        return [bf["Omega_m"], bf["sigma8"], bf["s"], bf["kappa"], bf["A_IA"], m0_clipped, m1_clipped, m2_clipped, m3_clipped, m4_clipped, bf["b_lens0"], bf["b_lens1"]], orig, clipped

def get_bounds(model, m_bounds_low, m_bounds_high):
    if model == "lcdm":
        return [[0.15,0.45], [0.3,1.3], [-5,5], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [0.2,5.0], [0.2,5.0]]
    elif model == "m34":
        return [[0.15,0.45], [0.3,1.3], [1.0,3.0], [-5,5], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [0.2,5.0], [0.2,5.0]]
    else:
        return [[0.15,0.45], [0.3,1.3], [1.0,3.0], [0.0,1.5], [-5,5], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [m_bounds_low, m_bounds_high], [0.2,5.0], [0.2,5.0]]

results = []
clipped_starts = {}

test_runs = [("m_conservative", -0.05, 0.05), ("m_baseline", -0.1, 0.1), ("m_stress", -0.2, 0.2)]
models = ["lcdm", "m34", "mkappa"]

for run_id, m_low, m_high in test_runs:
    print(f"Processing run: {run_id}")
    clipped_starts[run_id] = {}
    for model in models:
        print(f"  Fitting model: {model}")
        x0, orig_m, clipped_m = get_start(model, m_low, m_high)
        clipped_starts[run_id][model] = {"original": orig_m, "clipped": clipped_m}
        bnds = get_bounds(model, m_low, m_high)
        res = minimize(chi2_fn, x0=x0, args=(model,), method="L-BFGS-B", bounds=bnds, options={"maxiter":1000})
        chi2_min = res.fun
        chi2_start = bestfits[model]["chi2_min"]
        delta_chi2 = chi2_min - chi2_start
        
        theta = res.x
        if model == "lcdm":
            Om, s8, A, m0, m1, m2, m3, m4, b0, b1 = theta
            s_val = None
            k_val = None
        elif model == "m34":
            Om, s8, s_val, A, m0, m1, m2, m3, m4, b0, b1 = theta
            k_val = None
        else:
            Om, s8, s_val, k_val, A, m0, m1, m2, m3, m4, b0, b1 = theta
        
        param_names = []
        if model == "lcdm":
            param_names = ["Omega_m", "sigma8", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
        elif model == "m34":
            param_names = ["Omega_m", "sigma8", "s", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
        else:
            param_names = ["Omega_m", "sigma8", "s", "kappa", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
        
        boundary_hits = []
        for idx, p in enumerate(param_names):
            low, high = bnds[idx]
            if np.isclose(theta[idx], low, atol=1e-6):
                boundary_hits.append(f"{p}:low")
            elif np.isclose(theta[idx], high, atol=1e-6):
                boundary_hits.append(f"{p}:high")
        
        all_m_at_bound = True
        for m_p in ["m_src0", "m_src1", "m_src2", "m_src3", "m_src4"]:
            has_hit = False
            for bh in boundary_hits:
                if m_p in bh:
                    has_hit = True
                    break
            if not has_hit:
                all_m_at_bound = False
                break
        
        all_m_same_sign = True
        m_vals = [m0, m1, m2, m3, m4]
        first_sign = np.sign(m_vals[0])
        for m in m_vals[1:]:
            if not np.isclose(np.sign(m), first_sign, atol=1e-6):
                all_m_same_sign = False
                break
        
        is_cat = False
        if not res.success:
            is_cat = True
        if not np.all(np.isfinite(theta)):
            is_cat = True
        if all_m_at_bound:
            is_cat = True
        if (chi2_min > chi2_start + 10) and (len(boundary_hits) > 3):
            is_cat = True
        
        results.append({
            "stress_family": "shear_m",
            "run_id": run_id,
            "model": model,
            "chi2_start": chi2_start,
            "chi2_min": chi2_min,
            "delta_chi2": delta_chi2,
            "n_params": len(x0),
            "Omega_m": Om,
            "sigma8": s8,
            "s": s_val,
            "kappa": k_val,
            "A_IA": A,
            "b_lens0": b0,
            "b_lens1": b1,
            "m_src0": m0,
            "m_src1": m1,
            "m_src2": m2,
            "m_src3": m3,
            "m_src4": m4,
            "boundary_hits": ";".join(boundary_hits),
            "catastrophic_boundary": is_cat,
            "success": res.success
        })

df_out = pd.DataFrame(results)
df_out.to_csv(output_dir / "shear_m_prior_stress.csv", index=False)

with open(output_dir / "phase4d_manifest.json", "r") as f:
    manifest = json.load(f)

manifest["subphase"] = "4D-1,4D-2"
manifest["test_runs"].extend([
    {"run_id": "m_conservative", "bounds": "[-0.05,0.05]"},
    {"run_id": "m_baseline", "bounds": "[-0.10,0.10]"},
    {"run_id": "m_stress", "bounds": "[-0.20,0.20]"}
])
manifest["baseline_consistency_tolerance_chi2"] = 1e-4
manifest["clipped_starting_params"] = clipped_starts

with open(output_dir / "phase4d_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
