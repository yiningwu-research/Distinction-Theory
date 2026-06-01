import os
import yaml
import numpy as np
import pandas as pd

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_kcap_bandpower_peeE(kcap_root):
    """Load all KCAP BandPower PeeE predictions and align to 0-based bin order"""
    bp_dir = os.path.join(kcap_root, 'iterated_cov_MAP_BlindC/bandpower_shear_e/')
    
    # Load ℓ bin boundaries
    l_min = np.loadtxt(os.path.join(bp_dir, 'l_min_vec.txt'))
    l_max = np.loadtxt(os.path.join(bp_dir, 'l_max_vec.txt'))
    assert len(l_min) == 8 and len(l_max) == 8, "Expected 8 ℓ bins"
    
    # 15 source-source pairs: (0,0), (0,1), (0,2), (0,3), (0,4), (1,1), (1,2), (1,3), (1,4), (2,2), (2,3), (2,4), (3,3), (3,4), (4,4)
    pairs = [(i,j) for i in range(5) for j in range(i, 5)]
    kcap_predictions = []
    
    for (i,j) in pairs:
        # KCAP uses 1-based bin indices, and filenames are bin_{max}_{min}
        kcap_a = max(i+1, j+1)
        kcap_b = min(i+1, j+1)
        file_path = os.path.join(bp_dir, f'bin_{kcap_a}_{kcap_b}.txt')
        
        # Load data: only the predicted P_ee values
        data = np.loadtxt(file_path, skiprows=1)  # skip header line
        assert len(data) == 8, f"Expected 8 ℓ bins for pair ({i},{j}), got {len(data)}"
        
        for ell_bin in range(8):
            kcap_predictions.append({
                'statistic': 'PeeE',
                'bin1': i,
                'bin2': j,
                'ell_bin': ell_bin,
                'ell_min_kcap': l_min[ell_bin],
                'ell_max_kcap': l_max[ell_bin],
                'kcap_prediction': data[ell_bin]
            })
    
    kcap_df = pd.DataFrame(kcap_predictions)
    assert len(kcap_df) == 120, f"Expected 120 rows, got {len(kcap_df)}"
    return kcap_df

def load_g1_bandpower_peeE(g1_pred_dir, model_name='m34'):
    """Load G1 BandPower PeeE predictions for specified model"""
    pred_file = os.path.join(g1_pred_dir, f'{model_name}_peeE_prediction.csv')
    g1_df = pd.read_csv(pred_file)
    
    assert len(g1_df) == 120, f"Expected 120 rows, got {len(g1_df)}"
    g1_df = g1_df.rename(columns={'prediction': 'g1_prediction'})
    return g1_df

def compute_comparison_metrics(merged_df):
    """Compute comparison metrics between KCAP and G1 predictions"""
    merged_df['ratio'] = merged_df['g1_prediction'] / merged_df['kcap_prediction']
    merged_df['delta'] = merged_df['g1_prediction'] - merged_df['kcap_prediction']
    merged_df['abs_frac_diff'] = np.abs(merged_df['delta'] / merged_df['kcap_prediction'])
    
    # Global metrics
    global_metrics = {
        'median_abs_frac_diff': np.median(merged_df['abs_frac_diff']),
        'mean_abs_frac_diff': np.mean(merged_df['abs_frac_diff']),
        'max_abs_frac_diff': np.max(merged_df['abs_frac_diff']),
        'sign_match_fraction': np.mean(np.sign(merged_df['g1_prediction']) == np.sign(merged_df['kcap_prediction'])),
        'rms_frac_diff': np.sqrt(np.mean(merged_df['abs_frac_diff']**2))
    }
    
    # Per-bin-pair metrics
    pair_metrics = merged_df.groupby(['bin1', 'bin2']).agg(
        rms_frac_diff=('abs_frac_diff', lambda x: np.sqrt(np.mean(x**2))),
        mean_abs_frac_diff=('abs_frac_diff', 'mean'),
        median_abs_frac_diff=('abs_frac_diff', 'median')
    ).reset_index()
    
    # Per-ℓ-bin metrics
    ell_metrics = merged_df.groupby('ell_bin').agg(
        rms_frac_diff=('abs_frac_diff', lambda x: np.sqrt(np.mean(x**2))),
        mean_abs_frac_diff=('abs_frac_diff', 'mean'),
        median_abs_frac_diff=('abs_frac_diff', 'median')
    ).reset_index()
    
    return merged_df, global_metrics, pair_metrics, ell_metrics

def generate_summary_report(global_metrics, pair_metrics, ell_metrics, output_path, model_name='m34'):
    """Generate markdown summary report"""
    report = f"""# BandPower PeeE KCAP vs G1 Comparison Summary
## Model: {model_name}

### Global Metrics
| Metric | Value |
|--------|-------|
| Median absolute fractional difference | {global_metrics['median_abs_frac_diff']:.4f} |
| Mean absolute fractional difference | {global_metrics['mean_abs_frac_diff']:.4f} |
| RMS fractional difference | {global_metrics['rms_frac_diff']:.4f} |
| Max absolute fractional difference | {global_metrics['max_abs_frac_diff']:.4f} |
| Sign match fraction | {global_metrics['sign_match_fraction']:.2%} |

### Key Observations
1. **Fractional difference magnitude**: Median {global_metrics['median_abs_frac_diff']:.1%} difference between G1 and KCAP predictions
2. **Sign consistency**: {global_metrics['sign_match_fraction']:.0%} of predictions have matching signs
3. **Extreme differences**: Maximum difference of {global_metrics['max_abs_frac_diff']:.1%}

### Per-Bin-Pair RMS Fractional Differences
| bin1 | bin2 | rms_frac_diff | mean_abs_frac_diff | median_abs_frac_diff |
|------|------|---------------|---------------------|-----------------------|
"""
    
    for _, row in pair_metrics.iterrows():
        report += f"| {int(row['bin1'])} | {int(row['bin2'])} | {row['rms_frac_diff']:.4f} | {row['mean_abs_frac_diff']:.4f} | {row['median_abs_frac_diff']:.4f} |\n"
    
    report += "\n\n### Per-ℓ-Bin RMS Fractional Differences\n"
    report += "| ell_bin | rms_frac_diff | mean_abs_frac_diff | median_abs_frac_diff |\n"
    report += "|---------|---------------|---------------------|-----------------------|\n"
    
    for _, row in ell_metrics.iterrows():
        report += f"| {int(row['ell_bin'])} | {row['rms_frac_diff']:.4f} | {row['mean_abs_frac_diff']:.4f} | {row['median_abs_frac_diff']:.4f} |\n"
    
    report += """
---
## Interpretation Boundary
This is a diagnostic engineering comparison only. No model evidence or preference claims are made. The differences are used to identify upstream pipeline mismatches only.
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"Summary report saved to: {output_path}")
    return report

def main(config_path, model_name='m34'):
    config = load_config(config_path)
    out_dir = config['output_paths']['out_dir']
    
    print(f"Loading KCAP BandPower PeeE predictions...")
    kcap_df = load_kcap_bandpower_peeE(config['input_paths']['kcap_predictions_root'])
    
    print(f"Loading G1 BandPower PeeE predictions for model {model_name}...")
    g1_df = load_g1_bandpower_peeE(
        os.path.join(config['input_paths']['g1_predictions_root'], config['products']['bandpower_peeE']['g1_path']),
        model_name=model_name
    )
    
    print("Merging predictions...")
    merged_df = pd.merge(
        kcap_df,
        g1_df,
        on=['statistic', 'bin1', 'bin2', 'ell_bin'],
        how='inner'
    )
    assert len(merged_df) == 120, f"Expected 120 merged rows, got {len(merged_df)}"
    
    print("Computing comparison metrics...")
    merged_df, global_metrics, pair_metrics, ell_metrics = compute_comparison_metrics(merged_df)
    
    # Save comparison data
    comparison_out_path = os.path.join(out_dir, f'bandpower_peeE_kcap_vs_g1_{model_name}.csv')
    merged_df.to_csv(comparison_out_path, index=False)
    print(f"Comparison data saved to: {comparison_out_path}")
    
    # Generate summary report
    summary_out_path = os.path.join(out_dir, f'bandpower_peeE_comparison_summary_{model_name}.md')
    generate_summary_report(global_metrics, pair_metrics, ell_metrics, summary_out_path, model_name=model_name)
    
    print("\nGlobal comparison results:")
    for k, v in global_metrics.items():
        print(f"{k}: {v:.4f}")
    
    return merged_df, global_metrics

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to KCAP reproduction config file")
    parser.add_argument("--model", default="m34", help="G1 model to compare (lcdm/m34/mkappa)")
    args = parser.parse_args()
    main(args.config, model_name=args.model)
