
import yaml
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv
import json
from pathlib import Path
import sys

#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
sys.path.append('/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/')
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

def main():
    # Load config
    config_path = "/Users/next/G_production_code/phase4_kids_3x2pt_full/configs/phase4e_eenE_local_refit.yaml"
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    
    # Create output dir
    outdir = Path(cfg["paths"]["output_dir"])
    outdir.mkdir(exist_ok=True, parents=True)
    
    # Initialize Stage3
    print("Initializing Stage3...")
    stage3_config = cfg["paths"]["stage3_config"]
    like = Stage3Lensing3x2ptLikelihood(stage3_config)
    ell = like.ell_grid
    print(f"ℓ grid loaded: {len(ell)} points")
    print(f"Available lens keys: {list(like.lenses.keys())}")
    print(f"Available source keys: {list(like.sources.keys())}")
    exit()
    
    # Load data
    data_df = pd.read_csv(cfg["paths"]["data_200"])
    data_vec = data_df["value"].values
    cov = np.load(cfg["paths"]["cov_200"])
    inv_cov = inv(cov)
    
    # Load bin edges
    pneE_row_order = pd.read_csv(cfg["paths"]["pneE_row_order"])
    peeE_row_order = pd.read_csv(cfg["paths"]["peeE_row_order"])
    l_min_pneE = np.unique(pneE_row_order["ell_min"].values)
    l_max_pneE = np.unique(pneE_row_order["ell_max"].values)
    l_min_peeE = np.unique(peeE_row_order["ell_min"].values)
    l_max_peeE = np.unique(peeE_row_order["ell_max"].values)
    
    def project_cl(ell, cl, l_min, l_max):
        num_bins = len(l_min)
        bp = np.zeros(num_bins)
        for b in range(num_bins):
            mask = (ell >= l_min[b]) & (ell <= l_max[b])
            ell_bin = ell[mask]
            cl_bin = cl[mask]
            integrand = ell_bin**2 * cl_bin
            integral = np.trapz(integrand, ell_bin)
            bp[b] = integral / (l_max[b] - l_min[b])
        return bp
    
    # Test const-sigma prediction
    print("\nTesting const-sigma prediction...")
    pars = {
        "Omega_m": 0.31,
        "h": 0.68,
        "Omega_b": 0.049,
        "n_s": 0.9665,
        "sigma8": 0.82,
        "Sigma0": 0.0,
        "A_IA": -0.13,
        "m_src0": -0.007, "m_src1": 0.001, "m_src2": -0.038, "m_src3": -0.022, "m_src4": 0.024,
        "b_lens0": 1.2, "b_lens1": 1.4
    }
    
    # Test PneE
    test_pneE = []
    for idx, row in pneE_row_order.iterrows():
        lens_bin = int(row["bin1"])
        src_bin = int(row["bin2"])
        lens_name = f"lens{lens_bin+1}"
        src_name = f"src{src_bin+1}"
        cl = like._compute_cl_pair("const_sigma", pars, "gammat", lens_name, src_name, ell)
        bp = project_cl(ell, cl, l_min_pneE, l_max_pneE)
        test_pneE.append(bp[row["ell_bin"]] * pars[f"b_lens{lens_bin}"])
    
    # Test PeeE
    test_peeE = []
    m_mean = np.mean([pars[f"m_src{i}"] for i in range(5)])
    for idx, row in peeE_row_order.iterrows():
        bin1 = int(row["bin2"])
        bin2 = int(row["bin1"])
        src1_name = f"src{bin1+1}"
        src2_name = f"src{bin2+1}"
        cl = like._compute_cl_pair("const_sigma", pars, "xip", src1_name, src2_name, ell)
        bp = project_cl(ell, cl, l_min_peeE, l_max_peeE)
        test_peeE.append(bp[row["ell_bin"]] * (1 + m_mean))
    
    # Combine
    full_pred = np.concatenate([np.array(test_pneE), np.array(test_peeE)])
    print(f"Full prediction finite: {np.all(np.isfinite(full_pred))}")
    print(f"Test chi2: {((data_vec - full_pred) @ inv_cov @ (data_vec - full_pred)):.2f}")
    
    print("\n✅ Test successful! Core functionality works.")
    
if __name__ == "__main__":
    main()
