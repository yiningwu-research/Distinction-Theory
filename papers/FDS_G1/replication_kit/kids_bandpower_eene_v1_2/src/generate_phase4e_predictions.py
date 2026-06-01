
import os
import sys
import yaml
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Add G1 stage3 pipeline path
sys.path.append('/Users/next/G_production_code/fds_g1_stage3_kids_pipeline/')
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood


def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def project_cl_to_bandpower(ell, cl, l_min, l_max):
    """Project Cℓ to BandPower using KCAP convention: <ℓ² Cℓ> (no 1/(2π) factor)
    Args:
        ell: ℓ grid
        cl: Cℓ array
        l_min: lower ℓ bin boundaries
        l_max: upper ℓ bin boundaries
    Returns:
        bandpower: projected BandPower array
    """
    num_bins = len(l_min)
    bandpower = np.zeros(num_bins)
    for b in range(num_bins):
        mask = (ell >= l_min[b]) & (ell <= l_max[b])
        ell_bin = ell[mask]
        cl_bin = cl[mask]
        integrand = ell_bin**2 * cl_bin
        integral = np.trapz(integrand, ell_bin)
        bandpower[b] = integral / (l_max[b] - l_min[b])
    return bandpower


def main(config_path):
    config = load_config(config_path)
    outdir = Path(config['output']['outdir'])
    outdir.mkdir(exist_ok=True, parents=True)

    print("=== Phase4E: Generate Adversarial Model Predictions ===")
    print("  ⚠️  All predictions are diagnostic only, not evidence!")
    print("  ⚠️  No full 3×2pt (no nn/clustering)!")

    # Step 1: Initialize G1 Stage3 pipeline
    print("\n1. Initializing Stage3 pipeline...")
    stage3_config = config['g1_pipeline']['stage3_config']
    like = Stage3Lensing3x2ptLikelihood(stage3_config)

    # Step 2: Load data row orders and bin boundaries
    print("\n2. Loading data row orders and bin boundaries...")
    # PeeE row order
    peeE_row_order = pd.read_csv(config['data']['peeE_row_order'])
    l_min_peeE = np.unique(peeE_row_order['ell_min'].values)
    l_max_peeE = np.unique(peeE_row_order['ell_max'].values)
    # PneE row order
    pneE_row_order = pd.read_csv(config['data']['pneE_row_order'])
    l_min_pneE = np.unique(pneE_row_order['ell_min'].values)
    l_max_pneE = np.unique(pneE_row_order['ell_max'].values)

    # Step3: Process each model
    print("\n3. Processing models...")
    all_model_results = {}

    for model_name, model_info in config['models'].items():
        print(f"\n  Processing {model_name}...")
        internal_name = model_info['internal_name']
        # Load fixed parameters
        with open(model_info['fixed_params_json'], 'r') as f:
            fixed_data = json.load(f)
        fixed_params = fixed_data.get('params', fixed_data)
        # Convert to dict, keep only needed cosmology params for Stage3
        stage3_pars = {}
        for p in ['Omega_m', 'h', 'Omega_b', 'sigma8', 'n_s']:
            if p in fixed_params:
                stage3_pars[p] = fixed_params[p]
            elif p in config['g1_pipeline']['fixed_params']:
                stage3_pars[p] = config['g1_pipeline']['fixed_params'][p]
        # Add model-specific params
        if internal_name == 'const_sigma':
            stage3_pars['Sigma0'] = 0.0  # We'll scale later or just compute with fixed Sigma0 for baseline
        elif internal_name == 'binned_sigma':
            edges = config['models'][model_name].get('sigma_bin_edges', [0.0, 0.5, 3.0])
            for i in range(len(edges)-1):
                stage3_pars[f'Sigma_bin{i}'] = 0.0

        # Generate PeeE predictions
        print(f"    Generating PeeE predictions...")
        ell = like.ell_grid
        peeE_preds = []
        for idx, row in peeE_row_order.iterrows():
            bin1 = row['bin2']  # PeeE row order is source bin1 < bin2
            bin2 = row['bin1']
            # Get source bin names (Stage3 uses 1-based string names like 'src1')
            src1_name = f'src{bin1+1}'
            src2_name = f'src{bin2+1}'
            # Compute Cℓ EE
            cl_ee = like._compute_cl_pair(internal_name, stage3_pars, 'xip', src1_name, src2_name, ell)
            # Project to bandpower
            bp = project_cl_to_bandpower(ell, cl_ee, l_min_peeE, l_max_peeE)
            # Add all 8 ell bins for this pair
            for ell_bin in range(len(bp)):
                peeE_preds.append({
                    'statistic': 'PeeE',
                    'bin1': bin1,
                    'bin2': bin2,
                    'ell_bin': ell_bin,
                    'ell_min': l_min_peeE[ell_bin],
                    'ell_max': l_max_peeE[ell_bin],
                    'prediction': bp[ell_bin]
                })
        peeE_df = pd.DataFrame(peeE_preds)
        # Align row order with data
        merged_peeE = pd.merge(
            peeE_row_order[['statistic', 'bin1', 'bin2', 'ell_bin']],
            peeE_df,
            on=['statistic', 'bin1', 'bin2', 'ell_bin'],
            how='left'
        )
        assert len(merged_peeE) == 120, f"Expected 120 PeeE predictions for {model_name}, got {len(merged_peeE)}"
        peeE_out_path = outdir / f'{model_name}_peeE_prediction.csv'
        merged_peeE.to_csv(peeE_out_path, index=False)
        print(f"      Saved PeeE predictions to {peeE_out_path}")

        # Generate PneE predictions
        print(f"    Generating PneE predictions...")
        pneE_preds = []
        for idx, row in pneE_row_order.iterrows():
            lens_bin = row['bin1']
            source_bin = row['bin2']
            # Get bin names (Stage3 uses 1-based: 'lens1', 'lens2', 'src1'-'src5')
            lens_name = f'lens{lens_bin+1}'
            src_name = f'src{source_bin+1}'
            # Compute Cℓ nE (gammat)
            cl_ne = like._compute_cl_pair(internal_name, stage3_pars, 'gammat', lens_name, src_name, ell)
            # Project to bandpower
            bp = project_cl_to_bandpower(ell, cl_ne, l_min_pneE, l_max_pneE)
            # Add all 8 ell bins for this pair
            for ell_bin in range(len(bp)):
                pneE_preds.append({
                    'statistic': 'PneE',
                    'bin1': lens_bin,
                    'bin2': source_bin,
                    'ell_bin': ell_bin,
                    'ell_min': l_min_pneE[ell_bin],
                    'ell_max': l_max_pneE[ell_bin],
                    'prediction': bp[ell_bin]
                })
        pneE_df = pd.DataFrame(pneE_preds)
        merged_pneE = pd.merge(
            pneE_row_order[['statistic', 'bin1', 'bin2', 'ell_bin']],
            pneE_df,
            on=['statistic', 'bin1', 'bin2', 'ell_bin'],
            how='left'
        )
        assert len(merged_pneE) == 80, f"Expected 80 PneE predictions for {model_name}, got {len(merged_pneE)}"
        pneE_out_path = outdir / f'{model_name}_pneE_baseline.csv'
        merged_pneE.to_csv(pneE_out_path, index=False)
        print(f"      Saved PneE baseline predictions to {pneE_out_path}")

        all_model_results[model_name] = {
            'internal_name': internal_name,
            'peeE_prediction_file': str(peeE_out_path),
            'pneE_baseline_file': str(pneE_out_path)
        }

    # Step4: Save manifest
    print("\n4. Saving manifest...")
    manifest = {
        'dataset_name': config['dataset_name'],
        'scope': config['scope'],
        'interpretation': config['interpretation'],
        'sigma_application': {
            'PeeE': 'recomputed_kernel_full_prediction',
            'PneE': 'recomputed_kernel_full_prediction'
        },
        'scaling_approximation_used': False,
        'models': all_model_results
    }
    manifest_path = outdir / 'phase4e_predictions_manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  Saved manifest to {manifest_path}")

    print("\n✅ Phase4E prediction generation complete!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to Phase4E predictions config file")
    args = parser.parse_args()
    main(args.config)
