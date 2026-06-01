
import yaml
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv
import json
from pathlib import Path

# Load config
config_path = "/Users/next/G_production_code/phase4_kids_3x2pt_full/configs/phase4e_eenE_local_refit.yaml"
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

outdir = Path(cfg["paths"]["output_dir"])
outdir.mkdir(exist_ok=True, parents=True)

# Load data
data_df = pd.read_csv(cfg["paths"]["data_200"])
data_vec = data_df["value"].values
cov = np.load(cfg["paths"]["cov_200"])
inv_cov = inv(cov)
n_data = len(data_vec)
print(f"Loaded data and covariance: {n_data} elements")

# Load baselines
pneE_baseline_df = pd.read_csv("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/phase3i_pneE/g1_pneE_smoke_predictions.csv")
pneE_baseline = pneE_baseline_df["g1_prediction"].values
lens_bins_pneE = pneE_baseline_df["bin1"].values
mask_lens1 = (lens_bins_pneE == 0)
mask_lens2 = (lens_bins_pneE == 1)

peeE_baseline_lcdm = pd.read_csv("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke/lcdm_peeE_prediction.csv")["prediction"].values

# Prediction function for binned sigma (2 bins)
def predict_binsigma2(theta):
    Omega_m, sigma8, Sigma0, Sigma1, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    # Scale predictions
    pneE = pneE_baseline.copy()
    pneE[mask_lens1] *= (1 + Sigma0)
    pneE[mask_lens2] *= (1 + Sigma1)
    avg_Sigma = (Sigma0 + Sigma1) / 2.0
    peeE = peeE_baseline_lcdm.copy() * (1 + avg_Sigma)**2
    # Apply nuisance
    mean_m = np.mean([m0, m1, m2, m3, m4])
    peeE *= (1 + mean_m)
    pneE[mask_lens1] *= b0
    pneE[mask_lens2] *= b1
    # Combine
    return np.concatenate([pneE, peeE])

# Objective
def chi2(theta):
    pred = predict_binsigma2(theta)
    if not np.all(np.isfinite(pred)):
        return np.inf
    res = data_vec - pred
    return res @ inv_cov @ res

# Params
param_names = ["Omega_m", "sigma8", "Sigma_bin0", "Sigma_bin1", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
bounds = [
    (0.15, 0.45),    # Omega_m
    (0.3, 1.3),      # sigma8
    (-0.95, 1.0),    # Sigma_bin0
    (-0.95, 1.0),    # Sigma_bin1
    (-10.0, 10.0),   # A_IA
    (-0.2, 0.2),     # m0
    (-0.2, 0.2),     # m1
    (-0.2, 0.2),     # m2
    (-0.2, 0.2),     # m3
    (-0.2, 0.2),     # m4
    (0.05, 10.0),    # b0
    (0.05, 10.0)     # b1
]
x0 = [
    0.31, 0.82, 0.0, 0.0, -0.13,
    -0.007, 0.001, -0.038, -0.022, 0.024,
    1.2, 1.4
]

# Run fit
print("\nRunning binned-sigma (2 bins) fit...")
res = minimize(chi2, x0=x0, bounds=bounds, method="L-BFGS-B", options={"maxiter":200, "disp":1})

# Save results
result = {
    "model": "binsigma2",
    "chi2_min": float(res.fun),
    "chi2_per_dof": float(res.fun/(n_data - len(param_names))),
    "success": bool(res.success),
    "params": dict(zip(param_names, [float(v) for v in res.x]))
}

with open(outdir / "binsigma2_fit.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"\nBinned-sigma fit done! Chi2 = {res.fun:.2f}, success = {res.success}")
print(f"Best-fit Sigma_bin0 = {res.x[2]:.3f}, Sigma_bin1 = {res.x[3]:.3f}")
