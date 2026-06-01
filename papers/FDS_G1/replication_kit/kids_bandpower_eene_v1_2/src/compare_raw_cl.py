import os
import sys
import yaml
import json
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Add G1 stage3 pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "fds_g1_stage3_kids_pipeline"))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_kcap_raw_cl(kcap_root):
    """Load KCAP raw shear Cℓ for all 15 source-source pairs"""
    cl_dir = os.path.join(kcap_root, 'kcap_xi/outputs/test_output_S8_fid_test/shear_cl/')
    
    # Load ℓ grid
    ell_kcap = np.loadtxt(os.path.join(cl_dir, 'ell.txt'), skiprows=1)
    assert len(ell_kcap) == 200, f"Expected 200 ℓ values, got {len(ell_kcap)}"
    
    # 15 source-source pairs: (0,0), (0,1), (0,2), (0,3), (0,4), (1,1), (1,2), (1,3), (1,4), (2,2), (2,3), (2,4), (3,3), (3,4), (4,4)
    pairs = [(i,j) for i in range(5) for j in range(i, 5)]
    kcap_cl = {}
    
    for (i,j) in pairs:
        # KCAP uses 1-based bin indices, filenames are bin_{max}_{min}
        kcap_a = max(i+1, j+1)
        kcap_b = min(i+1, j+1)
        file_path = os.path.join(cl_dir, f'bin_{kcap_a}_{kcap_b}.txt')
        
        # Load raw Cℓ values
        cl = np.loadtxt(file_path, skiprows=1)
        assert len(cl) == 200, f"Expected 200 Cℓ values for pair ({i},{j}), got {len(cl)}"
        
        kcap_cl[(i,j)] = cl
    
    return ell_kcap, kcap_cl

def compute_g1_raw_cl(like, model_name, pars, ell_g1, ell_kcap):
    """Compute G1 raw Cℓ for all 15 source-source pairs, interpolated to KCAP ℓ grid"""
    pairs = [(i,j) for i in range(5) for j in range(i, 5)]
    g1_cl = {}
    
    for (i,j) in pairs:
        # Compute raw Cℓ for this pair
        cl = like._compute_cl_pair(model_name, pars, 'xip', f'src{i}', f'src{j}', ell_g1)
        
        # Interpolate to KCAP ℓ grid
        interp = interp1d(ell_g1, cl, kind='cubic', fill_value='extrapolate')
        cl_interp = interp(ell_kcap)
        
        g1_cl[(i,j)] = cl_interp
    
    return g1_cl

def compute_ratio_metrics(ratio_df):
    """Compute summary metrics for Cℓ ratios"""
    # Global metrics
    finite_mask = np.isfinite(ratio_df['ratio_kcap_over_g1'])
    finite_ratios = ratio_df.loc[finite_mask, 'ratio_kcap_over_g1']
    
    global_metrics = {
        'median_ratio': np.median(finite_ratios),
        'sqrt_median_ratio': np.sqrt(np.median(finite_ratios)),
        'mad_ratio': np.median(np.abs(finite_ratios - np.median(finite_ratios))),
        'min_ratio': np.min(finite_ratios),
        'max_ratio': np.max(finite_ratios),
        'mean_ratio': np.mean(finite_ratios),
        'std_ratio': np.std(finite_ratios),
        'sign_match_fraction': np.mean(np.sign(ratio_df.loc[finite_mask, 'g1_cl']) == np.sign(ratio_df.loc[finite_mask, 'kcap_cl'])),
        'finite_fraction': np.mean(finite_mask)
    }
    
    # Per-pair metrics
    pair_metrics = ratio_df.groupby(['pair_i', 'pair_j']).apply(
        lambda x: pd.Series({
            'median_ratio': np.median(x.loc[np.isfinite(x['ratio_kcap_over_g1']), 'ratio_kcap_over_g1']),
            'mean_ratio': np.mean(x.loc[np.isfinite(x['ratio_kcap_over_g1']), 'ratio_kcap_over_g1']),
            'std_ratio': np.std(x.loc[np.isfinite(x['ratio_kcap_over_g1']), 'ratio_kcap_over_g1'])
        })
    ).reset_index()
    
    # Per-ℓ-bin metrics (group ℓ into 10 log bins for summary)
    ratio_df['ell_bin'] = np.floor(np.log10(ratio_df['ell']))
    ell_metrics = ratio_df.groupby('ell_bin').apply(
        lambda x: pd.Series({
            'median_ratio': np.median(x.loc[np.isfinite(x['ratio_kcap_over_g1']), 'ratio_kcap_over_g1']),
            'mean_ratio': np.mean(x.loc[np.isfinite(x['ratio_kcap_over_g1']), 'ratio_kcap_over_g1'])
        })
    ).reset_index()
    
    return global_metrics, pair_metrics, ell_metrics

def generate_summary_report(all_results, out_dir):
    """Generate markdown summary report for raw Cℓ comparison"""
    report = "# Raw Cℓ Comparison Summary: KCAP vs G1\n\n"
    
    for model_name, (global_metrics, pair_metrics, ell_metrics) in all_results.items():
        report += f"## Model: {model_name}\n\n"
        report += "### Global Metrics\n"
        report += "| Metric | Value |\n|--------|-------|\n"
        for k, v in global_metrics.items():
            if isinstance(v, float):
                report += f"| {k} | {v:.4f} |\n"
            else:
                report += f"| {k} | {v} |\n"
        
        report += f"\n### Key Observations for {model_name}\n"
        report += f"1. Median ratio KCAP/G1: {global_metrics['median_ratio']:.2f} (sqrt: {global_metrics['sqrt_median_ratio']:.2f})\n"
        report += f"2. Ratio range: {global_metrics['min_ratio']:.2f} to {global_metrics['max_ratio']:.2f}\n"
        report += f"3. Sign match fraction: {global_metrics['sign_match_fraction']:.2%}\n"
        report += f"4. MAD ratio: {global_metrics['mad_ratio']:.4f} (very small variation indicates global mismatch)\n\n"
    
    report += "## Overall Conclusion\n"
    median_ratios = [v[0]['median_ratio'] for v in all_results.values()]
    mean_median_ratio = np.mean(median_ratios)
    
    if np.allclose(median_ratios, 14, rtol=0.1):
        report += f"✅ **Raw Cℓ mismatch confirmed**: Global ratio KCAP/G1 ≈ {mean_median_ratio:.2f} across all models. Mismatch is upstream of BandPower projection.\n"
    elif np.allclose(median_ratios, 1, rtol=0.2):
        report += f"✅ **Raw Cℓ matched**: Global ratio KCAP/G1 ≈ {mean_median_ratio:.2f} across all models. Mismatch is in BandPower projection layer.\n"
    else:
        report += f"⚠️ **Variable ratio**: Median ratio varies from {np.min(median_ratios):.2f} to {np.max(median_ratios):.2f}. Mismatch is not purely global.\n"
    
    report += "\n---\n## Interpretation Boundary\n"
    report += "This is a diagnostic engineering comparison only. No model evidence or preference claims are made. Results are used solely to localize pipeline normalization mismatches.\n"
    
    summary_path = os.path.join(out_dir, 'raw_cl_comparison_summary.md')
    with open(summary_path, 'w') as f:
        f.write(report)
    
    print(f"Summary report saved to: {summary_path}")
    return report

def main(config_path):
    config = load_config(config_path)
    kcap_root = config['input_paths']['kcap_predictions_root']
    out_dir = config['output_paths']['out_dir']
    
    print("Loading KCAP raw Cℓ...")
    ell_kcap, kcap_cl = load_kcap_raw_cl(kcap_root)
    
    print("Initializing G1 Stage3 pipeline...")
#
# Release note: archived from internal diagnostic pipeline.
# Hardcoded paths below are local to the production machine.
# For reruns, replace with env-var-based paths (FDS_G1_REPO_ROOT, FDS_G1_DATA_ROOT).
#
    stage3_config = "/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/stage3_kids1000_xipm_270/stage3_kids1000_xipm_270_config_cuts_mdz_ia.yaml"
    like = Stage3Lensing3x2ptLikelihood(stage3_config)
    ell_g1 = like.ell_grid
    print(f"G1 ℓ grid: {len(ell_g1)} points, range {ell_g1.min():.1f} to {ell_g1.max():.1f}")
    print(f"KCAP ℓ grid: {len(ell_kcap)} points, range {ell_kcap.min():.4f} to {ell_kcap.max():.2f}")
    
    # Models to process
    model_paths = {
        'lcdm': "/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/warmstart_ia_lcdm.json",
        'm34': "/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/warmstart_ia_m34.json",
        'mkappa': "/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/warmstart_ia_mkappa.json"
    }
    
    all_results = {}
    all_rows = []
    
    for model_name, param_path in model_paths.items():
        print(f"\nProcessing model: {model_name}...")
        
        # Load best-fit parameters
        with open(param_path, 'r') as f:
            param_data = json.load(f)
            pars = param_data['params']
        
        # Compute G1 raw Cℓ interpolated to KCAP grid
        g1_cl = compute_g1_raw_cl(like, model_name, pars, ell_g1, ell_kcap)
        
        # Compute ratios for all pairs and ℓ
        pairs = [(i,j) for i in range(5) for j in range(i, 5)]
        # Only compare in overlapping ℓ range (G1 ℓ range: 2.0 to 5000.0)
        valid_ell_mask = (ell_kcap >= 2.0) & (ell_kcap <= 5000.0)
        valid_ell_idx = np.where(valid_ell_mask)[0]
        if model_name == list(model_paths.keys())[0]:
            print(f"Comparing in valid overlapping ℓ range: {len(valid_ell_idx)} points, 2.0 ≤ ℓ ≤ 5000.0")
        
        for (i,j) in pairs:
            for ell_idx in valid_ell_idx:
                ell = ell_kcap[ell_idx]
                g1_val = g1_cl[(i,j)][ell_idx]
                kcap_val = kcap_cl[(i,j)][ell_idx]
                ratio = kcap_val / g1_val if g1_val != 0 else np.nan
                finite = np.isfinite(ratio)
                
                all_rows.append({
                    'model': model_name,
                    'pair_i': i,
                    'pair_j': j,
                    'ell': ell,
                    'g1_cl': g1_val,
                    'kcap_cl': kcap_val,
                    'ratio_kcap_over_g1': ratio,
                    'finite': finite
                })
        
        # Compute metrics for this model
        model_df = pd.DataFrame([r for r in all_rows if r['model'] == model_name])
        global_metrics, pair_metrics, ell_metrics = compute_ratio_metrics(model_df)
        all_results[model_name] = (global_metrics, pair_metrics, ell_metrics)
        
        print(f"  {model_name} median ratio: {global_metrics['median_ratio']:.2f}, sign match: {global_metrics['sign_match_fraction']:.2%}")
    
    # Save full ratio data
    ratio_df = pd.DataFrame(all_rows)
    ratio_path = os.path.join(out_dir, 'raw_cl_ratio_check.csv')
    ratio_df.to_csv(ratio_path, index=False)
    print(f"\nFull ratio data saved to: {ratio_path}")
    
    # Generate summary report
    generate_summary_report(all_results, out_dir)
    
    return ratio_df, all_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to KCAP reproduction config file")
    args = parser.parse_args()
    main(args.config)
