#!/usr/bin/env python3
"""
Project KiDS MAP bestfit shear Cℓ to 120-element PeeE BandPower vector.
Phase 3E-1: PeeE-only BandPower theory smoke.
"""
import numpy as np
import pandas as pd
from pathlib import Path

def project_cl_to_bandpower(ell: np.ndarray, cl: np.ndarray, bin_edges_low: list, bin_edges_high: list) -> np.ndarray:
    """
    Project Cℓ to ℓ bins using ℓ² Cℓ/(2π) average over each bin.
    Follows KiDS BandPower convention as verified in Phase 3B-2.
    """
    n_bins = len(bin_edges_low)
    bandpower = np.zeros(n_bins, dtype=float)
    
    for i in range(n_bins):
        ell_min = bin_edges_low[i]
        ell_max = bin_edges_high[i]
        mask = (ell >= ell_min) & (ell <= ell_max)
        if np.sum(mask) < 2:
            raise ValueError(f"Not enough ℓ points in bin {i}: {np.sum(mask)} points")
        
        ell_bin = ell[mask]
        cl_bin = cl[mask]
        vals = (ell_bin ** 2) * cl_bin / (2 * np.pi)
        bandpower[i] = np.mean(vals)
    
    return bandpower

if __name__ == "__main__":
    # Paths
    data_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/data")
    cl_dir = Path("/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/stage3_kids1000/raw/extracted/Cat_to_Obs_K1000_P1-master/Predictions/iterated_cov_MAP_BlindC/shear_cl")
    out_dir = Path("/Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_theory_smoke")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load verified PeeE order
    pee_order = pd.read_csv(data_dir / "peeE_subset" / "bandpower_PeeE_row_order_verified.csv")
    assert len(pee_order) == 120
    
    # Load verified KiDS BandPower bin edges (Phase 3B-2 validated)
    # 8 log bins, ℓ ∈ [100, 1500]
    bin_low = [100.0, 140.28505520066747, 196.79896712654315, 276.0795396678144,
               387.298334620742, 543.3216825139734, 762.1991222319227, 1069.2514593620554]
    bin_high = [140.28505520066747, 196.79896712654315, 276.0795396678144, 387.298334620742,
                543.3216825139734, 762.1991222319227, 1069.2514593620554, 1500.0]
    assert len(bin_low) == 8
    assert len(bin_high) == 8
    
    # Load ℓ grid from MAP directory
    ell = np.loadtxt(cl_dir / "ell.txt", comments="#")
    print(f"Loaded ℓ grid: {len(ell)} points, ℓ range = [{ell.min():.1f}, {ell.max():.1f}]: PASS")
    
    # Project each PeeE pair to 8 BandPower bins
    pee_pair_order = [tuple(row) for _, row in pee_order[["bin1", "bin2"]].drop_duplicates().iterrows()]
    assert len(pee_pair_order) == 15, f"Expected 15 PeeE pairs, got {len(pee_pair_order)}"
    print(f"Found 15 PeeE pairs in verified order: {pee_pair_order}")
    
    bandpower_pred = np.zeros(120, dtype=float)
    pred_rows = []
    
    for pair_idx, (bin1, bin2) in enumerate(pee_pair_order):
        # Load Cℓ: KiDS stores cross pairs as bin_{max}_{min}.txt
        file_bin1 = max(bin1, bin2)
        file_bin2 = min(bin1, bin2)
        cl_file = cl_dir / f"bin_{file_bin1}_{file_bin2}.txt"
        cl = np.loadtxt(cl_file, comments="#")
        assert len(cl) == len(ell), f"Mismatched Cℓ length for pair {bin1}_{bin2}"
        
        # Project to 8 BandPower bins
        bp = project_cl_to_bandpower(ell, cl, bin_low, bin_high)
        assert np.isfinite(bp).all(), f"Nonfinite values in pair {bin1}_{bin2} projection"
        
        # Fill 120-element vector
        start_idx = pair_idx * 8
        end_idx = start_idx + 8
        bandpower_pred[start_idx:end_idx] = bp
        
        # Build result rows
        for bin_idx, val in enumerate(bp):
            pred_rows.append({
                "statistic": "bandpower_E_peee",
                "bin1": bin1,
                "bin2": bin2,
                "angbin": bin_idx + 1,
                "ell_min": bin_low[bin_idx],
                "ell_max": bin_high[bin_idx],
                "value": val,
                "source": "KiDS_MAP_bestfit_projection"
            })
    
    # Verify finite values
    assert np.isfinite(bandpower_pred).all(), "Nonfinite values in predicted BandPower vector"
    print(f"Projected 15 PeeE pairs to 120-element BandPower vector, all finite: PASS")
    
    # Save results
    pred_df = pd.DataFrame(pred_rows)
    pred_df.to_csv(out_dir / "map_peeE_prediction.csv", index=False)
    np.save(out_dir / "map_peeE_prediction.npy", bandpower_pred)
    print(f"Saved MAP PeeE prediction to {out_dir}: DONE")
    
    # Compare ordering with observed data
    obs_data = pd.read_csv(data_dir / "peeE_subset" / "kids1000_bandpower_PeeE_data_120.csv")
    compare_cols = ["statistic", "bin1", "bin2", "angbin"]
    order_match = np.all(pred_df[compare_cols] == obs_data[compare_cols])
    print(f"Order match between prediction and observed data: {order_match}")
    assert order_match, "Prediction row order does not match observed data"
    
    # Compute residual summary
    obs_vals = obs_data["value"].to_numpy()
    residuals = bandpower_pred - obs_vals
    median_abs_resid = np.median(np.abs(residuals))
    max_abs_resid = np.max(np.abs(residuals))
    print(f"Median absolute residual: {median_abs_resid:.2e}")
    print(f"Max absolute residual: {max_abs_resid:.2e}")
    
    # Write residual summary
    summary_lines = [
        "# MAP PeeE Prediction Residual Summary",
        "",
        f"* Order match to observed data: {'PASS' if order_match else 'FAIL'}",
        f"* All projection values finite: PASS",
        f"* Median absolute residual: {median_abs_resid:.2e}",
        f"* Max absolute residual: {max_abs_resid:.2e}",
        "",
        "Note: Residuals are expected to be nonzero as this is a MAP prediction vs noisy observed data.",
        "The only validation criteria are finite values and matching row order."
    ]
    (out_dir / "map_peeE_residual_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
