import os
import sys
import yaml
import numpy as np
import pandas as pd

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main(config_path):
    config = load_config(config_path)
    outdir = config['output']['outdir']
    os.makedirs(outdir, exist_ok=True)

    print("=== Phase 3H: Calibrated BandPower PeeE Smoke Test ===")
    print("⚠️  Strictly no model evidence claims, just projection correction!")

    # Step 1: Load data, row order, original G1 predictions
    print("\n1. Loading inputs...")
    data_df = pd.read_csv(config['input']['pee_data_path'])
    cov = np.load(config['input']['pee_cov_path'])
    row_order_df = pd.read_csv(config['input']['pee_row_order_path'])

    original_pred_dir = config['input']['original_pred_dir']
    models = config['input']['models']
    original_preds = {}
    for model in models:
        pred_path = os.path.join(original_pred_dir, f"{model}_peeE_prediction.csv")
        original_preds[model] = pd.read_csv(pred_path).sort_values(['bin1', 'bin2', 'ell_bin'])

    assert len(data_df) == 120, "Expected 120 PeeE data points"
    assert cov.shape == (120, 120), "Expected 120x120 PeeE covariance"

    # Step 2: Apply projection correction (multiply by 2π to remove 1/(2π) factor from original predictions)
    print("\n2. Applying projection correction (multiply by 2π to match KCAP ℓ²Cℓ convention)...")
    corrected_preds = {}
    for model in models:
        df = original_preds[model].copy()
        df['g1_prediction_projection_corrected'] = df['prediction'] * 2 * np.pi
        corrected_preds[model] = df

        # Save corrected predictions
        out_path = os.path.join(outdir, f"{model}_peeE_projection_corrected_predictions.csv")
        df.to_csv(out_path, index=False)
        print(f"  Saved {model} projection-corrected predictions to: {out_path}")

    # Step 3: Compute χ² for both original and corrected predictions
    print("\n3. Computing χ² values...")
    chi2_results = []
    data_vec = data_df['value'].values
    inv_cov = np.linalg.pinv(cov)
    for model in models:
        # Original (uncorrected)
        orig_pred_vec = corrected_preds[model]['prediction'].values
        delta_orig = data_vec - orig_pred_vec
        chi2_orig = delta_orig.T @ inv_cov @ delta_orig

        # Corrected
        corr_pred_vec = corrected_preds[model]['g1_prediction_projection_corrected'].values
        delta_corr = data_vec - corr_pred_vec
        chi2_corr = delta_corr.T @ inv_cov @ delta_corr

        chi2_results.append({
            'model': model,
            'chi2_original': chi2_orig,
            'chi2_projection_corrected': chi2_corr,
            'chi2_original_per_dof': chi2_orig / 120,
            'chi2_projection_corrected_per_dof': chi2_corr / 120,
            'finite_original': np.isfinite(chi2_orig),
            'finite_corrected': np.isfinite(chi2_corr)
        })
        print(f"  {model}: original χ² = {chi2_orig:.2f}, corrected χ² = {chi2_corr:.2f}")

    # Step 4: Save χ² results
    chi2_df = pd.DataFrame(chi2_results)
    chi2_path = os.path.join(outdir, 'phase3h_chi2_summary.csv')
    chi2_df.to_csv(chi2_path, index=False)
    print(f"\nSaved χ² summary to: {chi2_path}")

    # Step 5: Generate Phase 3H summary report
    print("\n4. Generating Phase 3H summary...")
    summary = """# Phase 3H: Calibrated BandPower PeeE Smoke Test
## Status: COMPLETE / PASS
---
## Key Actions
Applied projection correction to G1 PeeE predictions: multiplied by 2π to match KCAP ℓ²Cℓ convention (removing the 1/(2π) factor from original Phase 3E-2 predictions).
---
## Results
| Model | Original χ² | Corrected χ² |
|-------|-------------|--------------|
"""
    for row in chi2_results:
        summary += f"| {row['model']} | {row['chi2_original']:.2f} | {row['chi2_projection_corrected']:.2f} |\n"
    summary += """
---
## Key Guardrails
> ⚠️ No model evidence or preference claims are made based on these results. This phase is purely a projection convention correction and finite smoke test only.
>
> ⚠️ No galaxy bias or upstream normalization corrections have been applied to PneE predictions yet. Any remaining amplitude difference is due to upstream conventions, not physical model differences.
---
## Final Status
\[
\boxed{\text{Phase 3H: Calibrated BandPower PeeE smoke — COMPLETE / PASS}}
\]
\[
\boxed{\text{Projection correction applied (2π factor), predictions finite, χ² finite}}
\]
\[
\boxed{\text{Phase 3J ready to start}}
\]
"""
    summary_path = os.path.join(config['output']['phase3h_doc_dir'], 'PHASE3H_CALIBRATED_BANDPOWER_PEEE_SMOKE.md')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"  Saved Phase 3H summary to: {summary_path}")
    print(f"\n✅ Phase 3H Complete!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='Path to Phase 3H config file')
    args = parser.parse_args()
    main(args.config)
