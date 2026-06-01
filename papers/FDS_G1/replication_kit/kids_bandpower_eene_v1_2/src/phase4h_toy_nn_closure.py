#!/usr/bin/env python3
"""
Phase 4H: Toy nn Closure Diagnostic
Boundary statement:
Phase 4H uses synthetic toy nn data to test whether adding a clustering-like b² channel 
can break the b-Σ amplitude degeneracy seen in EE+nE. It is not a KiDS full 3x2pt result, 
not production evidence, and not a final cosmological constraint.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv
from scipy.interpolate import interp1d
import json
from pathlib import Path
import random
import warnings
warnings.filterwarnings("ignore")

# ==============================================
# GLOBAL CONFIG
# ==============================================
BASELINE_SIGMA_BOUNDS = (-0.5, 0.5)
RANDOM_SEED = 1234
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Guardrails
SYNTHETIC_NN = True
OBSERVED_NN_DATA = False

# Prior definitions (same as Phase4G)
PRIOR_MU_M = 0.0
PRIOR_SIGMA_M = 0.015
PRIOR_MU_B = 1.0
PRIOR_SIGMA_B = 0.3
PRIOR_MU_AIA = 1.0
PRIOR_SIGMA_AIA = 0.5

# Data paths
DATA_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_200_standard.csv"
COV_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data/kids1000_bandpower_covariance_200.npy"
PNE_BASELINE_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/phase3i_pneE/g1_pneE_smoke_predictions.csv"
PEE_BASELINE_PATH = "/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke/"
KCAP_DIR = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/external/Predictions/iterated_cov_MAP_BlindC/")

OUTDIR = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4h_toy_nn_closure/")
OUTDIR.mkdir(exist_ok=True, parents=True)
SRCDIR = Path("/Users/next/G_production_code/phase4_kids_3x2pt_full/outputs/phase4g_prior_regularized_refit/")

# ==============================================
# Load existing EE+nE data
# ==============================================
n_pne = 80
n_pee = 120
cov_200 = np.load(COV_PATH)
assert cov_200.shape == (200, 200)
inv_cov_200 = inv(cov_200)

cov_EE = cov_200[n_pne:, n_pne:]
cov_nE = cov_200[:n_pne, :n_pne]
inv_cov_EE = inv(cov_EE)
inv_cov_nE = inv(cov_nE)
Q_200 = inv_cov_200
Q_EE = Q_200[n_pne:, n_pne:]
Q_nE = Q_200[:n_pne, :n_pne]
Q_EN = Q_200[n_pne:, :n_pne]

# Load baseline predictions
pne_baseline_df = pd.read_csv(PNE_BASELINE_PATH)
pne_baseline = pne_baseline_df["g1_prediction"].values
lens_bins_pne = pne_baseline_df["bin1"].values
mask_lens0 = (lens_bins_pne == 0)
mask_lens1 = (lens_bins_pne == 1)

pee_baseline = {}
for model in ["lcdm", "m34", "mkappa"]:
    df = pd.read_csv(Path(PEE_BASELINE_PATH) / f"{model}_peeE_prediction.csv")
    pee_baseline[model] = df["prediction"].values

# Load data vector
data_df = pd.read_csv(DATA_PATH)
data_200 = data_df["value"].values
assert len(data_200) == 200

# ==============================================
# Toy nn generation from KCAP predictions
# ==============================================
def load_kcap_matter_power(kcap_dir):
    k_h = np.loadtxt(kcap_dir / "matter_power_nl/k_h.txt", comments="#")
    p_k_data = np.loadtxt(kcap_dir / "matter_power_nl/p_k.txt", comments="#")
    z_pk = np.loadtxt(kcap_dir / "matter_power_nl/z.txt", comments="#")
    return k_h, p_k_data, z_pk

def load_kcap_gg_power(kcap_dir):
    k_h = np.loadtxt(kcap_dir / "galaxy_galaxy_power_spectrum_pt/k_h.txt", comments="#")
    p_k_data = np.loadtxt(kcap_dir / "galaxy_galaxy_power_spectrum_pt/p_k.txt", comments="#")
    z_pk = np.loadtxt(kcap_dir / "galaxy_galaxy_power_spectrum_pt/z.txt", comments="#")
    return k_h, p_k_data, z_pk

def load_lens_nz(kcap_dir, bin_idx):
    z_nz = np.loadtxt(kcap_dir / "nz_lens/z.txt", comments="#")
    nz = np.loadtxt(kcap_dir / f"nz_lens/bin_{bin_idx+1}.txt", comments="#")
    return z_nz, nz

# Cosmological constants
C = 299792.458  # km/s
H0 = 67.77  # km/s/Mpc
h = H0 / 100.0
def chi_of_z(z):
    """Simple comoving distance: chi = c/H0 * integral dz/E(z), assume flat LCDM with Omega_m=0.3"""
    omega_m = 0.3
    omega_l = 0.7
    n_pts = 500
    z_grid = np.linspace(0, z, n_pts)
    E_z = np.sqrt(omega_m * (1 + z_grid)**3 + omega_l)
    dz = z / (n_pts - 1)
    integral = np.sum(1.0 / E_z) * dz - 0.5/E_z[0] * dz - 0.5/E_z[-1] * dz
    return C / H0 * integral  # Mpc

def build_nn_kernel():
    """
    Build 100-element nn kernel (at unit bias = 1) and the pair index mapping.
    Returns:
        nn_kernel: 100-element array with nn at b=1
        pair_start_end: list of (start_idx, end_idx) for each lens-lens pair
    """
    k_h, p_k_data, z_pk = load_kcap_matter_power(KCAP_DIR)
    z_nz, nz0 = load_lens_nz(KCAP_DIR, 0)
    _, nz1 = load_lens_nz(KCAP_DIR, 1)
    
    interp_per_z = []
    for iz in range(len(z_pk)):
        interp_per_z.append(interp1d(k_h, p_k_data[iz, :], bounds_error=False, fill_value=0.0, kind="linear"))
    
    if np.sum(nz0) > 0:
        nz0_n = nz0 / np.trapz(nz0, z_nz)
    else:
        nz0_n = nz0
    if np.sum(nz1) > 0:
        nz1_n = nz1 / np.trapz(nz1, z_nz)
    else:
        nz1_n = nz1
    
    nz_interp = {
        0: interp1d(z_nz, nz0_n, bounds_error=False, fill_value=0.0, kind="linear"),
        1: interp1d(z_nz, nz1_n, bounds_error=False, fill_value=0.0, kind="linear")
    }
    
    pair_list = [(0, 0), (0, 1), (1, 1)]
    bp_per_pair = [34, 33, 33]
    nn_kernel = np.zeros(100)
    pair_start_end = []
    ell_range_all = np.linspace(100, 1500, 100)
    
    idx = 0
    for pair_idx, (l1, l2) in enumerate(pair_list):
        n_bp = bp_per_pair[pair_idx]
        ell_centers = ell_range_all[idx:idx+n_bp]
        pair_start_end.append((idx, idx + n_bp))
        
        for ei, ell in enumerate(ell_centers):
            z_eff = np.trapz(z_pk * nz_interp[l1](z_pk) * nz_interp[l2](z_pk), z_pk)
            z_eff = max(z_eff, 0.1) if np.isfinite(z_eff) else 0.3
            chi_eff = chi_of_z(z_eff)
            k_eff = ell / (chi_eff * h) if chi_eff > 0 else 0.01
            
            iz_eff = np.argmin(np.abs(z_pk - z_eff))
            iz_eff = max(0, min(iz_eff, len(z_pk) - 1))
            p_eff = float(interp_per_z[iz_eff](k_eff))
            
            dz_dchi_eff = H0 / C * np.sqrt(0.3 * (1 + z_eff)**3 + 0.7)
            kernel_int = np.trapz(nz_interp[l1](z_nz) * nz_interp[l2](z_nz), z_nz)
            
            Cl_val = p_eff * kernel_int * dz_dchi_eff / (chi_eff**2) if chi_eff > 0 else 0.0
            bp_val = ell * (ell + 1) * Cl_val / (2 * np.pi)
            nn_kernel[idx + ei] = bp_val
        
        idx += n_bp
    
    nn_kernel = np.clip(nn_kernel, 0, None)
    return nn_kernel, pair_start_end

# Build kernel once
NN_KERNEL, NN_PAIR_SE = build_nn_kernel()

def predict_nn(theta, param_names):
    """Predict nn bandpowers from model parameters using nn kernel."""
    b0 = None
    b1 = None
    for name, val in zip(param_names, theta):
        if name == "b_lens0":
            b0 = val
        elif name == "b_lens1":
            b1 = val
    
    if b0 is None or b1 is None:
        return np.zeros(100)
    
    nn_pred = np.zeros(100)
    pair_bias_map = [(b0, b0), (b0, b1), (b1, b1)]
    for pi, (ba, bb) in enumerate(pair_bias_map):
        s, e = NN_PAIR_SE[pi]
        nn_pred[s:e] = NN_KERNEL[s:e] * ba * bb
    
    return nn_pred

def build_toy_nn(bias_lens0, bias_lens1, truth_label):
    """Generate 100-element toy nn data from kernel + biases."""
    nn_data = np.zeros(100)
    pair_bias_map = [(bias_lens0, bias_lens0), (bias_lens0, bias_lens1), (bias_lens1, bias_lens1)]
    for pi, (ba, bb) in enumerate(pair_bias_map):
        s, e = NN_PAIR_SE[pi]
        nn_data[s:e] = NN_KERNEL[s:e] * ba * bb
    return nn_data

# ==============================================
# Construct toy 300-vector and covariance
# ==============================================
def construct_toy_300(bias_lens0, bias_lens1, truth_label):
    nn_toy = build_toy_nn(bias_lens0, bias_lens1, truth_label)
    data_300 = np.concatenate([data_200, nn_toy])
    
    cov_300 = np.zeros((300, 300))
    cov_300[:200, :200] = cov_200
    cov_300[200:, 200:] = np.eye(100) * np.var(nn_toy) * 0.1
    inv_cov_300 = inv(cov_300)
    return data_300, inv_cov_300, cov_300

def construct_toy_300_nominal(bias_lens0, bias_lens1, truth_label):
    nn_toy = build_toy_nn(bias_lens0, bias_lens1, truth_label)
    data_300 = np.concatenate([data_200, nn_toy])
    cov_300 = np.zeros((300, 300))
    cov_300[:200, :200] = cov_200
    cov_300[200:, 200:] = np.eye(100) * np.var(nn_toy) * 0.05
    inv_cov_300 = inv(cov_300)
    return data_300, inv_cov_300, cov_300

# ==============================================
# Prediction functions (same as Phase4B/4G)
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
        "predict_func_200": predict_lcdm,
        "base_bounds": [
            (-10.0, 10.0), (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1),
            (-0.1, 0.1), (0.2, 5.0), (0.2, 5.0)]
    },
    "m34": {
        "param_names": ["s", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func_200": predict_m34,
        "base_bounds": [
            (1.0, 3.0), (-10.0, 10.0), (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1),
            (-0.1, 0.1), (-0.1, 0.1), (0.2, 5.0), (0.2, 5.0)]
    },
    "mkappa": {
        "param_names": ["s", "kappa", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func_200": predict_mkappa,
        "base_bounds": [
            (1.0, 3.0), (0.0, 1.5), (-10.0, 10.0), (-0.1, 0.1), (-0.1, 0.1),
            (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1), (0.2, 5.0), (0.2, 5.0)]
    },
    "constsigma": {
        "param_names": ["Sigma0", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func_200": predict_constsigma,
        "base_bounds": [
            BASELINE_SIGMA_BOUNDS, (-10.0, 10.0), (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1),
            (-0.1, 0.1), (-0.1, 0.1), (0.2, 5.0), (0.2, 5.0)]
    },
    "binsigma2": {
        "param_names": ["Sigma_bin0", "Sigma_bin1", "A_IA", "m_src0", "m_src1", "m_src2", "m_src3", "m_src4", "b_lens0", "b_lens1"],
        "predict_func_200": predict_binsigma2,
        "base_bounds": [
            BASELINE_SIGMA_BOUNDS, BASELINE_SIGMA_BOUNDS, (-10.0, 10.0), (-0.1, 0.1), (-0.1, 0.1),
            (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1), (0.2, 5.0), (0.2, 5.0)]
    }
}

# ==============================================
# Prior and Utility Functions
# ==============================================
def compute_prior_penalty(theta, param_names):
    m_vals, b_vals, a_ia_val = [], [], None
    for name, val in zip(param_names, theta):
        if name.startswith("m_src"): m_vals.append(val)
        elif name.startswith("b_lens"): b_vals.append(val)
        elif name == "A_IA": a_ia_val = val
    m_pulls = [(m - PRIOR_MU_M) / PRIOR_SIGMA_M for m in m_vals]
    b_pulls = [(b - PRIOR_MU_B) / PRIOR_SIGMA_B for b in b_vals]
    a_ia_pull = (a_ia_val - PRIOR_MU_AIA) / PRIOR_SIGMA_AIA if a_ia_val is not None else 0.0
    prior_chi2 = sum(p**2 for p in m_pulls) + sum(p**2 for p in b_pulls) + a_ia_pull**2
    pulls = {}
    for i, p in enumerate(m_pulls): pulls[f"pull_m_src{i}"] = float(p)
    for i, p in enumerate(b_pulls): pulls[f"pull_b_lens{i}"] = float(p)
    if a_ia_val is not None: pulls["pull_A_IA"] = float(a_ia_pull)
    pulls["max_pull"] = float(max(np.abs(list(pulls.values())))) if pulls else 0.0
    return float(prior_chi2), pulls

def compute_chi2(pred, data_vec, inv_cov):
    if not np.all(np.isfinite(pred)): return np.inf
    res = data_vec - pred
    return float(res @ inv_cov @ res)

def predict_nn_200(theta):
    """Generate 200-element EE+nE prediction from model params.
    nn block is NOT included for EE+nE-only baseline refits."""
    info = model_info.get("lcdm", model_info["lcdm"])
    param_names_lcdm = model_info["lcdm"]["param_names"]
    n_lcdm = len(param_names_lcdm)
    
    predict_func = None
    model_name = None
    for mn, mi in model_info.items():
        if len(theta) == len(mi["param_names"]):
            predict_func = mi["predict_func_200"]
            model_name = mn
            break
    
    if predict_func is None:
        raise ValueError(f"Cannot match theta len={len(theta)} to any model")
    
    return predict_func(theta)

def predict_300_no_nn(theta):
    pred_200 = predict_nn_200(theta)
    return np.concatenate([pred_200, np.zeros(100)])

def run_single_fit(model, start_theta, data_vec, inv_cov, with_prior=True):
    info = model_info[model]
    predict_func_200 = info["predict_func_200"]
    param_names = info["param_names"]
    bounds = info["base_bounds"]
    
    n_total = len(data_vec)
    use_nn = (n_total == 300)
    
    def objective(theta):
        pred_200 = predict_func_200(theta)
        if use_nn:
            pred_nn = predict_nn(theta, param_names)
            pred = np.concatenate([pred_200, pred_nn])
        else:
            pred = pred_200
        chi2_d = compute_chi2(pred, data_vec, inv_cov)
        chi2_p, _ = compute_prior_penalty(theta, param_names) if with_prior else (0.0, {})
        return chi2_d + chi2_p
    
    res = minimize(objective, x0=start_theta, bounds=bounds, method="L-BFGS-B",
                   options={"maxiter": 1000, "ftol": 1e-6, "gtol": 1e-6, "disp": False})
    
    x_best = res.x
    pred_best_200 = predict_func_200(x_best)
    if use_nn:
        pred_best_nn = predict_nn(x_best, param_names)
        pred_best = np.concatenate([pred_best_200, pred_best_nn])
    else:
        pred_best = pred_best_200
    
    chi2_data = compute_chi2(pred_best, data_vec, inv_cov)
    chi2_prior, pulls = compute_prior_penalty(x_best, param_names) if with_prior else (0.0, {})
    chi2_total = chi2_data + chi2_prior
    
    bound_hits = []
    for i, p in enumerate(param_names):
        low, high = bounds[i]
        val = x_best[i]
        if np.isclose(val, low, rtol=1e-3): bound_hits.append(f"{p}:low")
        elif np.isclose(val, high, rtol=1e-3): bound_hits.append(f"{p}:high")
    
    res_EE = (data_vec[n_pne:200] - pred_best[n_pne:200]) if n_total >= 200 else (data_vec[n_pne:] - pred_best[n_pne:])
    res_nE = (data_vec[:n_pne] - pred_best[:n_pne])
    chi2_EE_block = float(res_EE @ inv_cov_EE @ res_EE)
    chi2_nE_block = float(res_nE @ inv_cov_nE @ res_nE)
    chi2_EE_prec = float(res_EE @ Q_EE @ res_EE)
    chi2_nE_prec = float(res_nE @ Q_nE @ res_nE)
    chi2_cross_prec = float(2 * res_EE @ Q_EN @ res_nE)
    
    return {
        "model": model, "success": res.success,
        "chi2_data": chi2_data, "chi2_prior": chi2_prior, "chi2_total": chi2_total,
        "params": dict(zip(param_names, [float(v) for v in x_best])),
        "bound_hits": ";".join(bound_hits),
        **pulls,
        "chi2_EE_block": chi2_EE_block, "chi2_nE_block": chi2_nE_block,
        "chi2_EE_precision": chi2_EE_prec, "chi2_nE_precision": chi2_nE_prec,
        "chi2_cross_precision": chi2_cross_prec
    }

def generate_starting_points(model):
    info = model_info[model]
    param_names = info["param_names"]
    bounds = info["base_bounds"]
    phase4b_defaults = {
        "lcdm": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
        "m34": [2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
        "mkappa": [2.0, 0.75, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
        "constsigma": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
        "binsigma2": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
    }
    if model in phase4b_defaults:
        base = phase4b_defaults[model]
    else:
        base = [0.0] * len(param_names)
    start_points, start_labels = [base], ["default_start"]
    for i in range(5):
        rstart = [np.random.uniform(l, h) for (l, h) in bounds]
        start_points.append(rstart)
        start_labels.append(f"random_start_{i}")
    return start_points, start_labels

def run_all_fits(data_vec, inv_cov, label, all_models, with_prior=True):
    results = []
    for model in all_models:
        start_points, start_labels = generate_starting_points(model)
        best_res = None
        best_chi2 = np.inf
        for st, sl in zip(start_points, start_labels):
            res = run_single_fit(model, st, data_vec, inv_cov, with_prior=with_prior)
            if res["chi2_total"] < best_chi2:
                best_chi2 = res["chi2_total"]
                best_res = res
            res["start_label"] = sl
            results.append(res)
        if best_res:
            print(f"  {model}: data={best_res['chi2_data']:.2f} prior={best_res['chi2_prior']:.2f} total={best_res['chi2_total']:.2f}")
    return results

# ==============================================
# Main
# ==============================================
def main():
    print("Phase 4H: Toy nn Closure Diagnostic")
    print("=" * 80)
    print("Guardrails:")
    print(f"  synthetic_nn: {SYNTHETIC_NN}")
    print(f"  observed_nn_data: {OBSERVED_NN_DATA}")
    print(f"  full_3x2pt_claim: false")
    print(f"  production_evidence: false")
    
    all_models = ["lcdm", "m34", "mkappa", "constsigma", "binsigma2"]
    
    # 1. Load Phase4G LCDM best-fit for toy nn generation
    pg_results = pd.read_csv(SRCDIR / "multistart_best_by_model.csv")
    pg_lcdm = pg_results[pg_results["model"] == "lcdm"].iloc[0]
    lcdm_b0 = pg_lcdm["pull_b_lens0"] * 0.3 + 1.0  # Convert pull to physical
    lcdm_b1 = pg_lcdm["pull_b_lens1"] * 0.3 + 1.0
    
    pg_m34 = pg_results[pg_results["model"] == "m34"].iloc[0]
    m34_b0 = pg_m34["pull_b_lens0"] * 0.3 + 1.0
    m34_b1 = pg_m34["pull_b_lens1"] * 0.3 + 1.0
    
    print(f"\nLCDM best-fit biases: b0={lcdm_b0:.3f}, b1={lcdm_b1:.3f}")
    print(f"M3/4 best-fit biases: b0={m34_b0:.3f}, b1={m34_b1:.3f}")
    
    # 2. Generate toy nn data vectors
    print("\nGenerating toy nn data vectors...")
    toy_nn_lcdm = build_toy_nn(lcdm_b0, lcdm_b1, "lcdm")
    toy_nn_m34 = build_toy_nn(m34_b0, m34_b1, "m34")
    
    toy_df = pd.DataFrame({
        "index": np.arange(100),
        "toy_nn_lcdm_truth": toy_nn_lcdm,
        "toy_nn_m34_truth": toy_nn_m34
    })
    toy_df.to_csv(OUTDIR / "toy_nn_predictions.csv", index=False)
    
    # 3. Build nominal and weak 300-vectors
    data_300_lcdm_nom, inv_cov_nom, cov_nom = construct_toy_300_nominal(lcdm_b0, lcdm_b1, "lcdm")
    data_300_m34_nom, _, _ = construct_toy_300_nominal(m34_b0, m34_b1, "m34")
    data_300_lcdm_weak, inv_cov_weak, cov_weak = construct_toy_300(lcdm_b0, lcdm_b1, "lcdm")
    data_300_m34_weak, _, _ = construct_toy_300(m34_b0, m34_b1, "m34")
    
    # Save 300 vectors
    vector_df = pd.DataFrame({
        "index": np.arange(300),
        "eenE_observed": np.concatenate([data_200, np.zeros(100)]),
        "toy_nn_lcdm_truth_nominal": data_300_lcdm_nom,
        "toy_nn_m34_truth_nominal": data_300_m34_nom,
        "toy_nn_lcdm_truth_weak": data_300_lcdm_weak,
        "toy_nn_m34_truth_weak": data_300_m34_weak,
    })
    vector_df.to_csv(OUTDIR / "toy_300_vectors.csv", index=False)
    
    # 4. Run fits
    # 4a. EE+nE only baseline (already done in Phase4G, repeat for consistency)
    print("\n[Run A] EE+nE baseline (Phase4G-style):")
    results_a = run_all_fits(data_200, inv_cov_200, "eenE_baseline", all_models, with_prior=True)
    df_a = pd.DataFrame(results_a)
    df_a.to_csv(OUTDIR / "results_eenE_baseline.csv", index=False)
    
    # 4b. EE+nE + toy nn LCDM truth, nominal covariance
    print("\n[Run B] EE+nE + toy nn (LCDM truth, nominal):")
    results_b = run_all_fits(data_300_lcdm_nom, inv_cov_nom, "toy_nn_lcdm_nom", all_models, with_prior=True)
    df_b = pd.DataFrame(results_b)
    df_b.to_csv(OUTDIR / "results_toy_nn_lcdm_nominal.csv", index=False)
    
    # 4c. EE+nE + toy nn M3/4 truth, nominal covariance
    print("\n[Run C] EE+nE + toy nn (M3/4 truth, nominal):")
    results_c = run_all_fits(data_300_m34_nom, inv_cov_nom, "toy_nn_m34_nom", all_models, with_prior=True)
    df_c = pd.DataFrame(results_c)
    df_c.to_csv(OUTDIR / "results_toy_nn_m34_nominal.csv", index=False)
    
    # 4d. EE+nE + toy nn LCDM truth, weak covariance
    print("\n[Run D] EE+nE + toy nn (LCDM truth, weak):")
    results_d = run_all_fits(data_300_lcdm_weak, inv_cov_weak, "toy_nn_lcdm_weak", all_models, with_prior=True)
    df_d = pd.DataFrame(results_d)
    df_d.to_csv(OUTDIR / "results_toy_nn_lcdm_weak.csv", index=False)
    
    # 4e. EE+nE + toy nn M3/4 truth, weak covariance
    print("\n[Run E] EE+nE + toy nn (M3/4 truth, weak):")
    results_e = run_all_fits(data_300_m34_weak, inv_cov_weak, "toy_nn_m34_weak", all_models, with_prior=True)
    df_e = pd.DataFrame(results_e)
    df_e.to_csv(OUTDIR / "results_toy_nn_m34_weak.csv", index=False)
    
    # 5. Generate summary
    print("\nGenerating summary...")
    
    def get_best(df):
        best = {}
        for m in all_models:
            sub = df[df["model"] == m]
            if len(sub) == 0: continue
            best[m] = sub.loc[sub["chi2_total"].idxmin()].to_dict()
        return best
    
    manifest = {
        "phase": "4H",
        "synthetic_nn": True,
        "observed_nn_data": False,
        "full_3x2pt_claim": False,
        "production_evidence": False,
        "truth_models": ["lcdm", "m34"],
        "covariance_variants": ["nominal_full_300", "weak_blockdiag_nn_x4"],
        "data_vector_composition": "first 200 observed EE+nE, last 100 synthetic toy nn",
        "covariance_composition_nominal": "full 300x300 block-diagonal EE+nE block matches validated 200x200, nn block diagonal with target variance",
        "covariance_composition_weak": "same structure but nn block diagonal variance inflated 2x (factor 4 on covariance = wider)",
        "guardrails": {
            "synthetic_nn_marked": SYNTHETIC_NN,
            "observed_nn_data_denied": not OBSERVED_NN_DATA,
            "no_mainline_claim": True,
            "no_full_3x2pt_claim": True,
            "no_production_evidence": True
        },
        "random_seed": RANDOM_SEED,
        "toy_nn_generation": "Simplified Limber integral from KCAP matter power spectrum P_mm(k,z) with lens n(z) kernel and galaxy bias scaling",
        "result_files": {
            "toy_nn_predictions": str(OUTDIR / "toy_nn_predictions.csv"),
            "toy_300_vectors": str(OUTDIR / "toy_300_vectors.csv"),
            "eenE_baseline": str(OUTDIR / "results_eenE_baseline.csv"),
            "toy_nn_lcdm_nominal": str(OUTDIR / "results_toy_nn_lcdm_nominal.csv"),
            "toy_nn_m34_nominal": str(OUTDIR / "results_toy_nn_m34_nominal.csv"),
            "toy_nn_lcdm_weak": str(OUTDIR / "results_toy_nn_lcdm_weak.csv"),
            "toy_nn_m34_weak": str(OUTDIR / "results_toy_nn_m34_weak.csv"),
        },
        "boundary_statement": "Phase 4H uses synthetic toy nn data to test whether adding a clustering-like b^2 channel can break the b-Sigma amplitude degeneracy seen in EE+nE. It is not a KiDS full 3x2pt result, not production evidence, and not a final cosmological constraint.",
        "status": "complete"
    }
    
    with open(OUTDIR / "phase4h_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Generate summary markdown
    def best_val(best_dict, model, key):
        if model in best_dict:
            val = best_dict[model][key]
            if isinstance(val, (int, float, np.floating, np.integer)):
                return f"{val:.2f}"
            return str(val)
        return "N/A"
    
    def best_param(best_dict, model, key):
        if model in best_dict:
            val = best_dict[model][key]
            if isinstance(val, (int, float, np.floating, np.integer)):
                return f"{val:.3f}"
            return str(val)
        return "N/A"
    
    summary = "# Phase4H: Toy nn Closure Diagnostic Summary\n"
    summary += "## Status: COMPLETE\n\n"
    summary += "### Guardrail Statement\n"
    summary += "**synthetic_nn: true** — The last 100 entries are synthetic toy nn, not observed KiDS clustering data.\n\n"
    summary += "### Boundary Statement\n"
    summary += "> Phase 4H uses synthetic toy nn data to test whether adding a clustering-like $b^2$ channel can break the $b$-$\\Sigma$ amplitude degeneracy seen in EE+nE. It is not a KiDS full $3\\times2$pt result, not production evidence, and not a final cosmological constraint.\n\n"
    
    summary += "## Run A: EE+nE Baseline (Phase4G-style)\n"
    best_a = get_best(df_a)
    summary += "| Model | chi2_data | chi2_prior | chi2_total | max_pull | bound_hits |\n"
    summary += "|-------|-----------|------------|------------|----------|------------|\n"
    for m in all_models:
        summary += f"| {m} | {best_val(best_a, m, 'chi2_data')} | {best_val(best_a, m, 'chi2_prior')} | {best_val(best_a, m, 'chi2_total')} | {best_val(best_a, m, 'max_pull')} | {best_param(best_a, m, 'bound_hits')} |\n"
    
    for label, df, truth in [
        ("Run B: LCDM truth, nominal", df_b, "LCDM"),
        ("Run C: M3/4 truth, nominal", df_c, "M3/4"),
        ("Run D: LCDM truth, weak", df_d, "LCDM"),
        ("Run E: M3/4 truth, weak", df_e, "M3/4"),
    ]:
        best = get_best(df)
        summary += f"\n## {label}\n"
        summary += "| Model | chi2_data | chi2_prior | chi2_total | max_pull | bound_hits |\n"
        summary += "|-------|-----------|------------|------------|----------|------------|\n"
        for m in all_models:
            summary += f"| {m} | {best_val(best, m, 'chi2_data')} | {best_val(best, m, 'chi2_prior')} | {best_val(best, m, 'chi2_total')} | {best_val(best, m, 'max_pull')} | {best_param(best, m, 'bound_hits')} |\n"
    
    summary += "\n## Interpretation\n"
    summary += "Results are diagnostic only. All inferences are pending full review. No model evidence claims are made.\n"
    summary += "The `synthetic_nn: true` flag applies to all Runs B-E; they are not KiDS clustering data.\n"
    
    with open(OUTDIR / "PHASE4H_TOY_NN_CLOSURE_DIAGNOSTIC.md", "w") as f:
        f.write(summary)
    
    print(f"\nAll outputs saved to: {OUTDIR}")
    print("✅ Phase4H toy nn closure diagnostic completed!")

if __name__ == "__main__":
    main()
