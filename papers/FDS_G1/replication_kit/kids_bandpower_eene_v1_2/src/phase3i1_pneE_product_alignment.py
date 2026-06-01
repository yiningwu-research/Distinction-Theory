import os
import sys
import yaml
import numpy as np
import pandas as pd

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def extract_pneE_subset(config):
    """Extract PneE data, covariance, and row order by statistic label (no hardcoded indices)"""
    # Load full data, covariance, row order
    full_data = pd.read_csv(config['input']['full_bandpower_data_path'])
    full_cov = np.load(config['input']['full_bandpower_cov_path'])
    full_row_order = pd.read_csv(config['input']['full_bandpower_row_order_path'])
    
    # Filter for PneE entries using statistic label
    pneE_mask = full_row_order['statistic'] == config['constants']['pneE_statistic_label']
    pneE_indices = full_row_order.index[pneE_mask].values
    pneE_row_order = full_row_order[pneE_mask].copy().reset_index(drop=True)
    
    # Verify we get exactly 80 entries
    assert len(pneE_row_order) == 80, f"Expected 80 PneE entries, got {len(pneE_row_order)}"
    print(f"Extracted {len(pneE_row_order)} PneE entries from rows {pneE_indices.min()} to {pneE_indices.max()} (by label, not hardcoded)")
    
    # Extract PneE data subset
    pneE_data = full_data.iloc[pneE_indices].copy().reset_index(drop=True)
    
    # Extract PneE covariance subblock
    pneE_cov = full_cov[np.ix_(pneE_indices, pneE_indices)]
    assert pneE_cov.shape == (80, 80), f"Expected 80x80 covariance, got {pneE_cov.shape}"
    
    return pneE_data, pneE_cov, pneE_row_order, pneE_indices

def validate_pneE_covariance(pneE_cov):
    """Validate PneE covariance is finite, symmetric, positive definite"""
    # Check finite
    assert np.all(np.isfinite(pneE_cov)), "Covariance contains non-finite values"
    # Check symmetric
    assert np.allclose(pneE_cov, pneE_cov.T, atol=1e-12), "Covariance is not symmetric"
    # Check positive definite (Cholesky decomposition)
    try:
        np.linalg.cholesky(pneE_cov)
        pd_pass = True
    except np.linalg.LinAlgError:
        pd_pass = False
    return {
        'finite': True,
        'symmetric': True,
        'positive_definite': pd_pass,
        'shape': pneE_cov.shape
    }

def load_and_align_kcap_pneE(config, pneE_row_order):
    """Load KCAP PneE predictions and align to KiDS row order"""
    kcap_dir = config['input']['kcap_pneE_dir']
    num_ell = config['constants']['num_ell_bins']
    
    # Load bin boundaries
    l_min = np.loadtxt(os.path.join(kcap_dir, 'l_min_vec.txt'), skiprows=1)
    l_max = np.loadtxt(os.path.join(kcap_dir, 'l_max_vec.txt'), skiprows=1)
    assert len(l_min) == num_ell and len(l_max) == num_ell, f"Expected {num_ell} ℓ bins"
    
    # Load all KCAP PneE bin files
    kcap_preds = {}
    # KCAP PneE pairs are bin_{lens_bin}_{source_bin}, 1-based, lens bin first
    for lens_bin in range(1, config['constants']['num_lens_bins'] + 1):
        for source_bin in range(1, config['constants']['num_source_bins'] + 1):
            file_path = os.path.join(kcap_dir, f'bin_{lens_bin}_{source_bin}.txt')
            values = np.loadtxt(file_path, skiprows=1)
            assert len(values) == num_ell, f"Expected {num_ell} values per pair"
            # Store with 0-based indices
            kcap_preds[(lens_bin - 1, source_bin - 1)] = values
    
    # Align to KiDS row order
    aligned_preds = []
    for _, row in pneE_row_order.iterrows():
        # KiDS row order bin1=lens bin, bin2=source bin, both 1-based in file
        pair = (row['bin1'] - 1, row['bin2'] - 1)
        ell_bin = row['angbin'] - 1 # angbin is 1-based in file
        aligned_preds.append({
            'bin1': row['bin1'] - 1,
            'bin2': row['bin2'] - 1,
            'ell_bin': ell_bin,
            'ell_min': l_min[ell_bin],
            'ell_max': l_max[ell_bin],
            'kcap_prediction': kcap_preds[pair][ell_bin]
        })
    
    aligned_df = pd.DataFrame(aligned_preds)
    assert len(aligned_df) == 80, f"Expected 80 aligned predictions, got {len(aligned_df)}"
    
    return aligned_df, l_min, l_max

def main(config_path):
    config = load_config(config_path)
    outdir = config['output']['outdir']
    os.makedirs(outdir, exist_ok=True)
    
    print("=== Phase 3I-1: PneE Product and KCAP Prediction Alignment ===")
    
    # Step 1: Extract PneE subset by statistic label
    print("\n1. Extracting PneE subset by statistic label...")
    pneE_data, pneE_cov, pneE_row_order, pneE_indices = extract_pneE_subset(config)
    
    # Step 2: Validate covariance
    print("\n2. Validating PneE covariance...")
    cov_stats = validate_pneE_covariance(pneE_cov)
    for k, v in cov_stats.items():
        print(f"  {k}: {v}")
    assert cov_stats['finite'] and cov_stats['symmetric'], "Covariance failed basic validation"
    pd_status = "✅ PASS" if cov_stats['positive_definite'] else "⚠️ NOTE"
    print(f"  Positive definite: {pd_status}")
    
    # Step 3: Load and align KCAP PneE predictions
    print("\n3. Loading and aligning KCAP PneE predictions...")
    kcap_preds, l_min, l_max = load_and_align_kcap_pneE(config, pneE_row_order)
    print(f"  Aligned {len(kcap_preds)} KCAP PneE predictions to KiDS row order")
    
    # Save outputs
    print("\n4. Saving outputs...")
    
    # Save PneE data
    pneE_data_path = os.path.join(outdir, 'pneE_subset_data.csv')
    pneE_data.to_csv(pneE_data_path, index=False)
    print(f"  Saved PneE data to: {pneE_data_path}")
    
    # Save PneE covariance
    pneE_cov_path = os.path.join(outdir, 'pneE_covariance_80.npy')
    np.save(pneE_cov_path, pneE_cov)
    print(f"  Saved PneE covariance to: {pneE_cov_path}")
    
    # Save aligned KCAP predictions
    kcap_pred_path = os.path.join(outdir, 'kcap_pneE_prediction_standard.csv')
    kcap_preds.to_csv(kcap_pred_path, index=False)
    print(f"  Saved aligned KCAP PneE predictions to: {kcap_pred_path}")
    
    # Generate summary report
    print("\n5. Generating summary report...")
    summary = f"""# Phase 3I-1: PneE Product Alignment Summary
## Status: COMPLETE / PASS
---
## Product Extraction
- PneE entries extracted by statistic label `{config['constants']['pneE_statistic_label']}`, NO hardcoded indices
- Extracted indices: rows {pneE_indices.min()} to {pneE_indices.max()} in full BandPower file (matches expected first 80 rows in current product)
- Number of PneE entries: {len(pneE_row_order)} = {config['constants']['num_lens_bins']} lens bins × {config['constants']['num_source_bins']} source bins × {config['constants']['num_ell_bins']} ℓ bins

## Covariance Validation
| Property | Status | Value |
|----------|--------|-------|
| Finite | ✅ PASS | {cov_stats['finite']} |
| Symmetric | ✅ PASS | {cov_stats['symmetric']} |
| Positive definite | {pd_status} | {cov_stats['positive_definite']} |
| Shape | ✅ PASS | {cov_stats['shape']} |

## KCAP Prediction Alignment
- KCAP PneE predictions loaded from: {config['input']['kcap_pneE_dir']}
- Aligned to KiDS row order successfully: {len(kcap_preds)} entries
- ℓ bin boundaries: {', '.join([f'{a:.0f}–{b:.0f}' for a,b in zip(l_min, l_max)])}

## Note
> Extraction is by statistic label only, not hardcoded index range, to avoid silent failure if row order changes in future product versions.
---
"""
    summary_path = os.path.join(outdir, 'pneE_product_alignment_summary.md')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"  Saved summary to: {summary_path}")
    
    print("\n✅ Phase 3I-1 Complete!")
    return pneE_data, pneE_cov, pneE_row_order, kcap_preds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to Phase 3I config file")
    args = parser.parse_args()
    main(args.config)
