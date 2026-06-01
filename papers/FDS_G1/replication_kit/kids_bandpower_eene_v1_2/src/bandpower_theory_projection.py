#!/usr/bin/env python3
"""
BandPower theory projection and validation for KiDS-1000 BandPower product.
Phase 3E: BandPower theory-smoke / projector validation.
"""
from __future__ import annotations
import argparse, yaml, json, numpy as np, pandas as pd
from pathlib import Path

def load_config(config_path: Path) -> dict:
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg

def load_official_map_predictions(cfg: dict) -> (pd.DataFrame, np.ndarray):
    """Load official KiDS BlindC MAP predictions and order into 200-vector."""
    rows = []
    full_vector = []
    # Load PneE first (lens-source pairs, 10 pairs × 8 bins)
    pnee_path = Path(cfg['inputs']['map_predictions']['PneE_path'])
    pnee_pairs = cfg['row_order']['PneE_rows']['pairs']
    
    for pair_idx, (bin1, bin2) in enumerate(pnee_pairs):
        fname = pnee_path / f"bin_{bin1}_{bin2}.txt"
        vals = np.loadtxt(fname, comments='#')
        for angbin_idx, val in enumerate(vals):
            angbin = angbin_idx + 1
            idx = pair_idx * 8 + angbin_idx
            full_vector.append(val)
            rows.append({
                'index': idx,
                'statistic': 'bandpower_E_pnee',
                'bin1': bin1,
                'bin2': bin2,
                'angbin': angbin,
                'ell_min': cfg['ell_bins']['ell_min'][angbin_idx],
                'ell_max': cfg['ell_bins']['ell_max'][angbin_idx],
                'value': val,
                'source': 'official_MAP'
            })
    
    # Load PeeE (source-source pairs, 15 pairs × 8 bins)
    peee_path = Path(cfg['inputs']['map_predictions']['PeeE_path'])
    peee_pairs = cfg['row_order']['PeeE_rows']['pairs']
    
    for pair_idx, (bin1, bin2) in enumerate(peee_pairs):
        # Map (i,j) to file name bin_{max(i,j)}_{min(i,j)}.txt
        file_bin1 = max(bin1, bin2)
        file_bin2 = min(bin1, bin2)
        fname = peee_path / f"bin_{file_bin1}_{file_bin2}.txt"
        vals = np.loadtxt(fname, comments='#')
        for angbin_idx, val in enumerate(vals):
            angbin = angbin_idx + 1
            idx = 80 + pair_idx * 8 + angbin_idx
            full_vector.append(val)
            rows.append({
                'index': idx,
                'statistic': 'bandpower_E_peee',
                'bin1': bin1,
                'bin2': bin2,
                'angbin': angbin,
                'ell_min': cfg['ell_bins']['ell_min'][angbin_idx],
                'ell_max': cfg['ell_bins']['ell_max'][angbin_idx],
                'value': val,
                'source': 'official_MAP'
            })
    
    df = pd.DataFrame(rows)
    full_vector = np.array(full_vector, dtype=np.float64)
    return df, full_vector

def project_Cell_to_bandpower(ell_input: np.ndarray, Cell: np.ndarray, cfg: dict, mode: str = 'peee') -> np.ndarray:
    """
    Project Cℓ (ℓ vs Cℓ) onto KiDS 8 bandpower bins.
    mode: 'peee' = shear-shear, 'pnee' = galaxy-shear.
    Returns: 8 element array of bandpower values.
    """
    ell_bins = cfg['ell_bins']
    bandpower_vals = np.zeros(8)
    ell_input = ell_input.astype(float)
    Cell = Cell.astype(float)
    
    for i in range(8):
        lmin = ell_bins['ell_min'][i]
        lmax = ell_bins['ell_max'][i]
        # Select ℓ in bin
        mask = (ell_input >= lmin) & (ell_input <= lmax)
        ell_bin = ell_input[mask]
        Cell_bin = Cell[mask]
        
        if len(ell_bin) < 2:
            raise ValueError(f"Not enough ℓ points in bin {i}: need at least 2, got {len(ell_bin)}.")
        
        # Compute average ℓ² Cℓ/(2π) over bin (diagnostic log-bin average per config)
        vals = (ell_bin ** 2) * Cell_bin / (2 * np.pi)
        bandpower_vals[i] = np.mean(vals)
    
    return bandpower_vals

def compute_full_200_vector(Cell_peee_dict: dict, Cell_pnee_dict: dict, cfg: dict) -> (pd.DataFrame, np.ndarray):
    """
    Compute full 200-element BandPower vector from Cℓ dictionaries.
    Cell_peee_dict: { (bin1, bin2): (ell, C_ggℓ) } for source-source pairs.
    Cell_pnee_dict: { (lens_bin, source_bin): (ell, C_gEℓ) } for lens-source pairs.
    """
    peee_pairs = cfg['row_order']['PeeE_rows']['pairs']
    pnee_pairs = cfg['row_order']['PneE_rows']['pairs']
    
    rows = []
    full_vector = []
    
    # Process PneE first
    for pair_idx, (bin1, bin2) in enumerate(pnee_pairs):
        ell, Cell = Cell_pnee_dict[(bin1, bin2)]
        vals = project_Cell_to_bandpower(ell, Cell, cfg, mode='pnee')
        for angbin_idx, val in enumerate(vals):
            angbin = angbin_idx + 1
            idx = pair_idx * 8 + angbin_idx
            full_vector.append(val)
            rows.append({
                'index': idx,
                'statistic': 'bandpower_E_pnee',
                'bin1': bin1,
                'bin2': bin2,
                'angbin': angbin,
                'ell_min': cfg['ell_bins']['ell_min'][angbin_idx],
                'ell_max': cfg['ell_bins']['ell_max'][angbin_idx],
                'value': val,
                'source': 'G1_projection'
            })
    
    # Process PeeE next
    for pair_idx, (bin1, bin2) in enumerate(peee_pairs):
        ell, Cell = Cell_peee_dict[(bin1, bin2)]
        vals = project_Cell_to_bandpower(ell, Cell, cfg, mode='peee')
        for angbin_idx, val in enumerate(vals):
            angbin = angbin_idx + 1
            idx = 80 + pair_idx * 8 + angbin_idx
            full_vector.append(val)
            rows.append({
                'index': idx,
                'statistic': 'bandpower_E_peee',
                'bin1': bin1,
                'bin2': bin2,
                'angbin': angbin,
                'ell_min': cfg['ell_bins']['ell_min'][angbin_idx],
                'ell_max': cfg['ell_bins']['ell_max'][angbin_idx],
                'value': val,
                'source': 'G1_projection'
            })
    
    df = pd.DataFrame(rows)
    full_vector = np.array(full_vector, dtype=np.float64)
    return df, full_vector

def validate_map_reproduction(map_df: pd.DataFrame, map_vec: np.ndarray, cfg: dict, outdir: Path) -> dict:
    """Validate that our ordering reproduces the official MAP vector correctly."""
    # First, cross-compare with KiDS data vector to confirm units match
    kid_data = pd.read_csv(outdir.parent.parent / 'data' / 'kids1000_bandpower_200_standard.csv')
    
    # Compare row ordering
    order_match_cols = ['statistic', 'bin1', 'bin2', 'angbin']
    order_match = np.all(map_df[order_match_cols] == kid_data[order_match_cols])
    
    # Compute difference
    map_values = map_df['value'].values
    kid_values = kid_data['value'].values
    
    # Compute stats
    abs_diff = np.abs(map_values - kid_values)
    abs_frac_diff = abs_diff / (np.abs(kid_values) + 1e-30)
    median_frac_error = np.median(abs_frac_diff)
    max_frac_error = np.max(abs_frac_diff)
    tolerance = cfg['checks']['reproduction_max_fractional_error_tolerance']
    within_tolerance = median_frac_error < tolerance
    
    # Create summary
    result = {
        'row_order_match': bool(order_match),
        'median_abs_fractional_error': float(median_frac_error),
        'max_abs_fractional_error': float(max_frac_error),
        'within_tolerance': bool(within_tolerance),
        'tolerance': tolerance
    }
    
    # Write summary
    summary_lines = [
        "# KiDS BlindC MAP Prediction Reproduction Summary",
        "",
        "## Key Results",
        f"* Row order match with KiDS data vector: {'✅ PASS' if order_match else '❌ FAIL'}",
        f"* Median absolute fractional error: {median_frac_error:.3e}",
        f"* Max absolute fractional error: {max_frac_error:.3e}",
        f"* Within {tolerance*100:.0f}% tolerance: {'✅ PASS' if within_tolerance else '❌ FAIL'}",
        "",
        "## Notes",
        "* The KiDS data vector is the observed BlindC data.",
        "* The MAP prediction is the best fit model from the KiDS analysis.",
        "* Expected non-zero difference due to noise and cosmology difference.",
    ]
    (outdir / cfg['outputs']['reproduction_summary']).write_text('\n'.join(summary_lines), encoding='utf-8')
    
    # Write reproduction CSV
    repro_df = pd.DataFrame({
        'index': map_df['index'],
        'statistic': map_df['statistic'],
        'bin1': map_df['bin1'],
        'bin2': map_df['bin2'],
        'angbin': map_df['angbin'],
        'MAP_prediction': map_values,
        'KiDS_data': kid_values,
        'abs_diff': abs_diff,
        'abs_frac_diff': abs_frac_diff
    })
    repro_df.to_csv(outdir / cfg['outputs']['reproduction_csv'], index=False)
    
    return result

def compute_chi2(vector: np.ndarray, cov_mat: np.ndarray) -> float:
    """Compute chi-squared: (vec)^T cov^{-1} vec."""
    # Symmetrize
    cov_sym = (cov_mat + cov_mat.T) / 2.0
    # Add small jitter for stability
    cov_jittered = cov_sym + np.eye(len(cov_sym)) * 1e-20
    inv_cov = np.linalg.inv(cov_jittered)
    chi2 = float(np.dot(vector.T, np.dot(inv_cov, vector)))
    return chi2

def main():
    parser = argparse.ArgumentParser(description="KiDS BandPower theory projection and validation")
    parser.add_argument("--config", type=str, default="configs/kids_bandpower_theory_smoke.yaml", help="Config file path")
    parser.add_argument("--validate_map", action="store_true", help="First run MAP reproduction validation (priority step)")
    parser.add_argument("--project_peee_only", action="store_true", help="Only project PeeE (120 elements) for smoke test")
    args = parser.parse_args()
    
    cfg = load_config(Path(args.config))
    outdir = Path(cfg['outputs']['outdir'])
    outdir.mkdir(parents=True, exist_ok=True)
    
    if args.validate_map:
        print("Running official BlindC MAP prediction reproduction validation...")
        map_df, map_vec = load_official_map_predictions(cfg)
        repro_result = validate_map_reproduction(map_df, map_vec, cfg, outdir)
        print(f"Reproduction validation result: {repro_result}")
        print(f"Row order match: {repro_result['row_order_match']}")
        print(f"Median fractional error: {repro_result['median_abs_fractional_error']:.3e}")
        print(f"Max fractional error: {repro_result['max_abs_fractional_error']:.3e}")
        print(f"Within tolerance {repro_result['tolerance']}: {repro_result['within_tolerance']}")
        print(f"Outputs written to {outdir}")
        return

    # TODO: Add Cℓ loading from G1 pipeline outputs
    # TODO: Add full projection and chi2 smoke test
    print("Projection mode not fully implemented yet. Run --validate_map first to confirm ordering.")

if __name__ == "__main__":
    raise SystemExit(main())
