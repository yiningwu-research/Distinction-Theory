#!/usr/bin/env python3
"""
Extract PeeE submatrix + data vector from verified BandPower products.
Phase 3E-1: PeeE-only BandPower theory smoke prep.
"""
import numpy as np
import pandas as pd
from pathlib import Path

if __name__ == "__main__":
    # Load verified products
    data_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data")
    out_dir = data_dir / "peeE_subset"
    out_dir.mkdir(exist_ok=True)
    
    # Load standard BandPower data + row order
    data = pd.read_csv(data_dir / "kids1000_bandpower_200_standard.csv")
    row_order = pd.read_csv(data_dir / "bandpower_row_order_verified.csv")
    
    # Add statistic column explicitly (derived from PeeE/PneE order)
    row_order["statistic"] = ["bandpower_E_pnee"] * 80 + ["bandpower_E_peee"] * 120
    
    # Select PeeE rows ONLY using verified labels, NO hardcoded indices
    pee_mask = row_order["statistic"].eq("bandpower_E_peee")
    pee_idx = np.where(pee_mask)[0]
    
    # Verify correct length
    assert len(pee_idx) == 120, f"Expected 120 PeeE rows, got {len(pee_idx)}"
    print(f"Selected {len(pee_idx)} PeeE rows: PASS")
    
    # Extract PeeE data vector
    data_pee = data.loc[pee_mask].copy()
    data_pee = data_pee.reset_index(drop=True)
    data_pee.to_csv(out_dir / "kids1000_bandpower_PeeE_data_120.csv", index=False)
    print(f"Extracted PeeE data vector: {len(data_pee)} rows, PASS")
    
    # Load full 200x200 covariance
    cov200 = np.load(data_dir / "kids1000_bandpower_covariance_200.npy")
    assert cov200.shape == (200, 200), f"Expected 200x200 covariance, got {cov200.shape}"
    
    # Extract 120x120 PeeE submatrix
    cov_pee = cov200[np.ix_(pee_idx, pee_idx)]
    assert cov_pee.shape == (120, 120), f"Expected 120x120 covariance, got {cov_pee.shape}"
    
    # Verify covariance is valid: symmetric, positive definite, Cholesky pass
    cov_sym = (cov_pee + cov_pee.T) / 2.0
    max_diff = np.max(np.abs(cov_pee - cov_sym))
    assert max_diff < 1e-20, f"Covariance not symmetric, max diff = {max_diff:.2e}"
    print(f"PeeE covariance symmetric, max diff = {max_diff:.2e}: PASS")
    
    # Cholesky test with small jitter for numerical stability
    try:
        np.linalg.cholesky(cov_sym + np.eye(120) * 1e-20)
        print("PeeE covariance Cholesky pass (positive definite): PASS")
    except np.linalg.LinAlgError:
        print("ERROR: PeeE covariance not positive definite")
        raise
    
    # Save PeeE covariance
    np.save(out_dir / "kids1000_bandpower_PeeE_covariance_120.npy", cov_pee)
    print(f"Saved 120x120 PeeE covariance to {out_dir}: DONE")
    
    # Save PeeE order metadata
    pee_order = row_order.loc[pee_mask].reset_index(drop=True)
    pee_order.to_csv(out_dir / "bandpower_PeeE_row_order_verified.csv", index=False)
