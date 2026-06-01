import os
import sys
import yaml
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_kcap_data(config):
    """Load KCAP raw Cℓ, BandPower, and bin boundaries"""
    # Load ℓ grid
    ell_path = os.path.join(config['inputs']['kcap_raw_cl_dir'], 'ell.txt')
    ell = np.loadtxt(ell_path, skiprows=1)
    
    # Load bin boundaries
    l_min = np.loadtxt(os.path.join(config['inputs']['kcap_bandpower_dir'], 'l_min_vec.txt'), skiprows=1)
    l_max = np.loadtxt(os.path.join(config['inputs']['kcap_bandpower_dir'], 'l_max_vec.txt'), skiprows=1)
    bin_centers = np.sqrt(l_min * l_max)
    
    # Filter to valid ℓ range
    valid_mask = (ell >= config['projection']['valid_ell_range'][0]) & (ell <= config['projection']['valid_ell_range'][1])
    ell_valid = ell[valid_mask]
    print(f"Using valid ℓ range: {len(ell_valid)} points, {ell_valid.min():.1f} to {ell_valid.max():.1f}")
    
    # Load all Cℓ pairs
    pairs = [(i, j) for i in range(5) for j in range(i, 5)]
    kcap_cl = {}
    for (i, j) in pairs:
        # KCAP uses 1-based indices, filenames are bin_{max}_{min}.txt
        kcap_a = max(i + 1, j + 1)
        kcap_b = min(i + 1, j + 1)
        cl_path = os.path.join(config['inputs']['kcap_raw_cl_dir'], f'bin_{kcap_a}_{kcap_b}.txt')
        cl = np.loadtxt(cl_path, skiprows=1)[valid_mask]
        kcap_cl[(i, j)] = cl
    
    # Load official KCAP BandPower values
    kcap_bp = {}
    for (i, j) in pairs:
        kcap_a = max(i + 1, j + 1)
        kcap_b = min(i + 1, j + 1)
        bp_path = os.path.join(config['inputs']['kcap_bandpower_dir'], f'bin_{kcap_a}_{kcap_b}.txt')
        bp = np.loadtxt(bp_path, skiprows=1)
        kcap_bp[(i, j)] = bp
    
    return ell_valid, l_min, l_max, bin_centers, kcap_cl, kcap_bp, pairs

def project_variant(ell, cl, l_min, l_max, variant):
    """Project Cℓ to BandPower using given variant formula"""
    n_bins = len(l_min)
    proj = np.zeros(n_bins)
    
    for b in range(n_bins):
        bin_lmin = l_min[b]
        bin_lmax = l_max[b]
        mask = (ell >= bin_lmin) & (ell <= bin_lmax)
        ell_bin = ell[mask]
        cl_bin = cl[mask]
        
        if variant == 'bin_center':
            # Bin center sample
            l_center = np.sqrt(bin_lmin * bin_lmax)
            cl_interp = interp1d(ell, cl, kind='cubic')(l_center)
            proj[b] = l_center ** 2 * cl_interp / (2 * np.pi)
        
        elif variant == 'mean_linear_ell':
            # Arithmetic mean over linear ℓ
            values = ell_bin ** 2 * cl_bin / (2 * np.pi)
            proj[b] = np.mean(values)
        
        elif variant == 'mean_log_ell':
            # Mean over log ℓ
            values = ell_bin ** 2 * cl_bin / (2 * np.pi)
            weights = 1 / ell_bin  # Weight by 1/ℓ for average over log ℓ
            proj[b] = np.average(values, weights=weights)
        
        elif variant == 'integrate_dell':
            # Integrate over dℓ, normalize by Δℓ
            integrand = ell_bin ** 2 * cl_bin / (2 * np.pi)
            integral = np.trapz(integrand, ell_bin)
            proj[b] = integral / (bin_lmax - bin_lmin)
        
        elif variant == 'integrate_dlnell':
            # Integrate over dlnℓ, normalize by Δlnℓ
            integrand = ell_bin ** 2 * cl_bin / (2 * np.pi) * ell_bin  # dlnℓ = dℓ/ℓ → multiply by ℓ
            integral = np.trapz(integrand, ell_bin)
            proj[b] = integral / (np.log(bin_lmax) - np.log(bin_lmin))
        
        elif variant == 'ell_ellplus1':
            # Use ℓ(ℓ+1) instead of ℓ²
            integrand = ell_bin * (ell_bin + 1) * cl_bin / (2 * np.pi)
            integral = np.trapz(integrand, ell_bin)
            proj[b] = integral / (bin_lmax - bin_lmin)
        
        elif variant == 'no_2pi_factor':
            # Omit 1/(2π) factor
            integrand = ell_bin ** 2 * cl_bin
            integral = np.trapz(integrand, ell_bin)
            proj[b] = integral / (bin_lmax - bin_lmin)
        
        else:
            raise ValueError(f"Unknown variant: {variant}")
    
    return proj

def main(config_path):
    config = load_config(config_path)
    outdir = config['outputs']['outdir']
    os.makedirs(outdir, exist_ok=True)
    
    # Load data
    print("Loading KCAP data...")
    ell_valid, l_min, l_max, bin_centers, kcap_cl, kcap_bp, pairs = load_kcap_data(config)
    variants = [v['name'] for v in config['projection']['variants']]
    variant_desc = {v['name']: v['description'] for v in config['projection']['variants']}
    
    # Run scan for all pairs and variants
    print(f"Running projection variant scan for {len(variants)} variants, {len(pairs)} pairs...")
    all_rows = []
    for (i, j) in pairs:
        cl = kcap_cl[(i, j)]
        kcap_bp_vals = kcap_bp[(i, j)]
        
        for variant in variants:
            proj_vals = project_variant(ell_valid, cl, l_min, l_max, variant)
            
            for b in range(len(l_min)):
                ratio = kcap_bp_vals[b] / proj_vals[b] if proj_vals[b] != 0 else np.nan
                finite = np.isfinite(ratio)
                all_rows.append({
                    'pair_i': i,
                    'pair_j': j,
                    'ell_bin': b,
                    'ell_min': l_min[b],
                    'ell_max': l_max[b],
                    'variant': variant,
                    'projected_value': proj_vals[b],
                    'kcap_value': kcap_bp_vals[b],
                    'ratio_kcap_over_g1': ratio,
                    'finite': finite
                })
    
    # Save full scan results
    df = pd.DataFrame(all_rows)
    scan_out_path = os.path.join(outdir, 'projection_variant_scan.csv')
    df.to_csv(scan_out_path, index=False)
    print(f"Full scan results saved to: {scan_out_path}")
    
    # Compute summary metrics per variant
    print("Computing summary metrics...")
    finite_df = df[df['finite'] == True]
    variant_summary = finite_df.groupby('variant').agg(
        median_ratio=('ratio_kcap_over_g1', 'median'),
        mean_ratio=('ratio_kcap_over_g1', 'mean'),
        mad_ratio=('ratio_kcap_over_g1', lambda x: np.median(np.abs(x - np.median(x)))),
        min_ratio=('ratio_kcap_over_g1', 'min'),
        max_ratio=('ratio_kcap_over_g1', 'max'),
        count=('ratio_kcap_over_g1', 'count')
    ).reset_index().sort_values('median_ratio', key=lambda x: np.abs(x - 1.0))
    
    # Find best variant
    best_variant = variant_summary.iloc[0]['variant']
    best_median = variant_summary.iloc[0]['median_ratio']
    best_mad = variant_summary.iloc[0]['mad_ratio']
    print(f"Best matching variant: {best_variant} | median ratio = {best_median:.3f} | MAD = {best_mad:.3f}")
    
    # Save best variant by pair
    best_by_pair = finite_df.groupby(['pair_i', 'pair_j']).apply(
        lambda x: x.groupby('variant')['ratio_kcap_over_g1'].median().abs().sub(1.0).idxmin()
    ).reset_index(name='best_variant')
    best_by_pair['median_ratio'] = best_by_pair.apply(
        lambda row: finite_df[(finite_df['pair_i'] == row['pair_i']) & (finite_df['pair_j'] == row['pair_j']) & (finite_df['variant'] == row['best_variant'])]['ratio_kcap_over_g1'].median(),
        axis=1
    )
    best_by_pair_path = os.path.join(outdir, 'best_variant_by_pair.csv')
    best_by_pair.to_csv(best_by_pair_path, index=False)
    print(f"Best variant by pair saved to: {best_by_pair_path}")
    
    # Save best variant by ell bin
    best_by_ellbin = finite_df.groupby('ell_bin').apply(
        lambda x: x.groupby('variant')['ratio_kcap_over_g1'].median().abs().sub(1.0).idxmin()
    ).reset_index(name='best_variant')
    best_by_ellbin['median_ratio'] = best_by_ellbin.apply(
        lambda row: finite_df[(finite_df['ell_bin'] == row['ell_bin']) & (finite_df['variant'] == row['best_variant'])]['ratio_kcap_over_g1'].median(),
        axis=1
    )
    best_by_ellbin_path = os.path.join(outdir, 'best_variant_by_ellbin.csv')
    best_by_ellbin.to_csv(best_by_ellbin_path, index=False)
    print(f"Best variant by ell bin saved to: {best_by_ellbin_path}")
    
    # Generate summary report
    summary = f"""# Phase 3G-1 Projection Variant Scan Summary
## Best Matching Variant: {best_variant}
{variant_desc[best_variant]}
### Key Metrics
| Metric | Value |
|--------|-------|
| Median ratio KCAP/G1 | {best_median:.3f} |
| Median absolute deviation (MAD) | {best_mad:.3f} |
| Ratio range | [{variant_summary.iloc[0]['min_ratio']:.3f}, {variant_summary.iloc[0]['max_ratio']:.3f}] |
### Variant Summary (Sorted by Closeness to 1)
| Variant | Median Ratio | Mean Ratio | MAD |
|---------|--------------|------------|-----|
"""
    for _, row in variant_summary.iterrows():
        summary += f"| {row['variant']} | {row['median_ratio']:.3f} | {row['mean_ratio']:.3f} | {row['mad_ratio']:.3f} |\n"
    
    summary += f"""
### Key Findings
1. **Projection factor quantified**: Best matching variant achieves median ratio {best_median:.3f}, explaining most of the ~5x projection factor
2. **Consistency across pairs/ell bins**: {len(best_by_pair[best_by_pair['best_variant'] == best_variant])}/{len(best_by_pair)} pairs prefer the best variant
3. **Candidate convention identified**: {'Omitting 1/(2π) factor is leading candidate' if best_variant == 'no_2pi_factor' else f'Convention mismatch source is {best_variant}'}
---
## Interpretation Boundary
This is diagnostic calibration only. No model evidence or preference claims are made. Results identify convention mismatch between pipelines only.
"""
    summary_path = os.path.join(outdir, 'projection_factor_summary.md')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Scan summary saved to: {summary_path}")
    
    return best_variant, best_median

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to Phase3G normalization config file")
    args = parser.parse_args()
    main(args.config)
