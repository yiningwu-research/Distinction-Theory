
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv
import json
from pathlib import Path

# --------------------------
# Fully aligned to Phase4B parameter configuration
# --------------------------
# Fixed cosmological parameters, fully matched to Phase4B
OMEGA_M = 0.315
SIGMA8 = 0.811

# Load data, fully matched to Phase4B
data_path = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_200_standard.csv"
cov_path = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_covariance_200.npy"
pne_baseline_path = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/phase3i_pneE/g1_pneE_smoke_predictions.csv"
pee_baseline_lcdm_path = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke/lcdm_peeE_prediction.csv"

# Output directory
outdir = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4e_adversarial_controls_corrected/")
outdir.mkdir(exist_ok=True, parents=True)

# Load data and covariance
data_df = pd.read_csv(data_path)
data_vec = data_df["value"].values
cov = np.load(cov_path)
inv_cov = inv(cov)
n_data = len(data_vec)
print(f"Data loaded: {n_data}-element vector, covariance shape {cov.shape}")

# Load baseline predictions
pne_baseline_df = pd.read_csv(pne_baseline_path)
pne_baseline = pne_baseline_df["g1_prediction"].values
lens_bins_pne = pne_baseline_df["bin1"].values
mask_lens0 = (lens_bins_pne == 0)
mask_lens1 = (lens_bins_pne == 1)
n_pne = len(pne_baseline)
print(f"Load Pne baseline: {n_pne} rows")

pee_baseline_lcdm_df = pd.read_csv(pee_baseline_lcdm_path)
pee_baseline_lcdm = pee_baseline_lcdm_df["prediction"].values
n_pee = len(pee_baseline_lcdm)
print(f"Load Pee baseline: {n_pee} rows")

# Parameter definitions, fully aligned to Phase4B
# binsigma2 parameter order: Sigma_bin0, Sigma_bin1, A_IA, m0,m1,m2,m3,m4, b0,b1
PARAM_NAMES = ["Sigma_bin0", "Sigma_bin1", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"]
N_PARAMS = len(PARAM_NAMES)
# Parameter bounds, fully aligned to Phase4B
BOUNDS = [
    (-0.5, 0.5),   # Sigma_bin0: corresponds to s ∈ [1, 3], valid range
    (-0.5, 0.5),   # Sigma_bin1: corresponds to s ∈ [1, 3], valid range
    (-10.0, 10.0), # A_IA: same as Phase4B
    (-0.1, 0.1),   # m_src0: same as Phase4B
    (-0.1, 0.1),   # m_src1: same as Phase4B
    (-0.1, 0.1),   # m_src2: same as Phase4B
    (-0.1, 0.1),   # m_src3: same as Phase4B
    (-0.1, 0.1),   # m_src4: same as Phase4B
    (0.2, 5.0),    # b_lens0: same as Phase4B
    (0.2, 5.0),    # b_lens1: same as Phase4B
]
# Starting values, aligned to Phase4B
X0 = np.array([
    0.0,    # Sigma_bin0 initial value 0
    0.0,    # Sigma_bin1 initial value 0
    1.0,    # A_IA initial value: Phase4B best-fit 1.0
    0.012,  # m_src initial values: Phase4B default 0.012
    0.012,
    0.012,
    0.012,
    0.012,
    0.85,   # b_lens0 initial value: Phase4B LCDM best-fit
    0.93,   # b_lens1 initial value: Phase4B LCDM best-fit
])

# Prediction function
def predict(theta):
    Sigma_bin0, Sigma_bin1, A_IA, m0, m1, m2, m3, m4, b0, b1 = theta
    # Compute mean m, same as Phase4B
    mean_m = np.mean([m0, m1, m2, m3, m4])
    # Compute mean Sigma for Pee approximate scaling (Pee is source-source cross, use average Sigma of two bins)
    mean_Sigma = (Sigma_bin0 + Sigma_bin1) / 2.0
    # Pee scaling: (1+mean_m) * (1+mean_Sigma)^2
    pee = pee_baseline_lcdm * (1 + mean_m) * ((1 + mean_Sigma) ** 2)
    # Pne scaling: multiply by b_i * (1 + Sigma_bini) per lens bin
    pne = pne_baseline.copy()
    pne[mask_lens0] *= b0 * (1 + Sigma_bin0)
    pne[mask_lens1] *= b1 * (1 + Sigma_bin1)
    # Combine vectors, order: Pne (80 rows) + Pee (120 rows), fully matched to Phase4B
    full_pred = np.concatenate([pne, pee])
    return full_pred

# Chi2 objective function
def chi2(theta):
    pred = predict(theta)
    if not np.all(np.isfinite(pred)):
        return np.inf
    res = data_vec - pred
    return res @ inv_cov @ res

# Compute initial chi2
chi2_start = chi2(X0)
print(f"Initial chi2: {chi2_start:.2f}")

# Run fit, fully aligned to Phase4B configuration
print("Running binned-sigma2 fit...")
res = minimize(
    chi2,
    x0=X0,
    bounds=BOUNDS,
    method="L-BFGS-B",
    options={
        "maxiter": 1000,
        "ftol": 1e-6,
        "gtol": 1e-6,
        "disp": 1
    }
)

# Process results
x_best = res.x
chi2_min = res.fun
delta_chi2 = chi2_start - chi2_min
chi2_per_dof = chi2_min / (n_data - N_PARAMS)
params_best = dict(zip(PARAM_NAMES, [float(v) for v in x_best]))

# Check for boundary hits
at_bounds = {}
for i, p in enumerate(PARAM_NAMES):
    low, high = BOUNDS[i]
    val = x_best[i]
    if np.isclose(val, low, rtol=1e-3) or np.isclose(val, high, rtol=1e-3):
        at_bounds[p] = {
            "value": float(val),
            "bound": "low" if np.isclose(val, low) else "high"
        }

# Finite check
finite = np.all(np.isfinite(predict(x_best)))
success = res.success
b_positive = (params_best["b_lens0"] > 0) and (params_best["b_lens1"] > 0)

# Save results
result = {
    "model": "binsigma2",
    "stage": "4E_corrected",
    "scope": "EE+nE BandPower adversarial local refit, fully aligned to Phase4B configuration",
    "chi2_start": float(chi2_start),
    "chi2_min": float(chi2_min),
    "delta_chi2": float(delta_chi2),
    "chi2_per_dof": float(chi2_per_dof),
    "n_data": n_data,
    "n_params": N_PARAMS,
    "params": params_best,
    "at_bounds": at_bounds,
    "finite": bool(finite),
    "success": bool(success),
    "b_positive": bool(b_positive),
    "interpretation": "diagnostic only, not evidence, not full 3×2pt"
}

# Print results
with open(outdir / "binsigma2_fit_corrected.json", "w") as f:
    json.dump(result, f, indent=2)

print("\nFit completed!")
print(f"Success: {success}, Finite: {finite}, Positive b: {b_positive}")
print(f"Best chi2: {chi2_min:.2f}, chi2/dof: {chi2_per_dof:.2f}")
print(f"Boundary hits: {list(at_bounds.keys())}")
print(f"Best parameters: {params_best}")
