import os
import yaml
import pandas as pd
import numpy as np

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def index_kcap_bandpower_peeE(kcap_root, inventory_rows):
    """Index KCAP BandPower PeeE predictions"""
    bp_dir = os.path.join(kcap_root, 'iterated_cov_MAP_BlindC/bandpower_shear_e/')
    
    # Get all bin pair files
    files = [f for f in os.listdir(bp_dir) if f.startswith('bin_') and f.endswith('.txt') and not f.startswith('index_bin_')]
    
    for f in files:
        # Example filename: bin_1_1.txt
        parts = f.split('_')
        bin1 = int(parts[1])
        bin2 = int(parts[2].split('.')[0])
        file_path = os.path.join(bp_dir, f)
        
        # Read to get number of rows
        try:
            data = np.loadtxt(file_path)
            n_rows = len(data)
            inventory_rows.append({
                'product': 'bandpower_peeE',
                'path': file_path,
                'n_rows': n_rows,
                'statistic': 'PeeE',
                'bin_pair': f'({bin1}, {bin2})',
                'mode_bin_count': n_rows,
                'note': f'ℓ bin count: {n_rows}'
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    return inventory_rows

def index_kcap_xipm(kcap_root, inventory_rows):
    """Index KCAP ξ± predictions"""
    xi_dir = os.path.join(kcap_root, 'kcap_xi/outputs/test_output_S8_fid_test/')
    
    files = [f for f in os.listdir(xi_dir) if f.endswith('.txt') and ('xi_p' in f or 'xi_m' in f)]
    
    for f in files:
        file_path = os.path.join(xi_dir, f)
        statistic = 'xi+' if 'xi_p' in f else 'xi-'
        try:
            data = np.loadtxt(file_path)
            n_rows = len(data)
            # Extract bin pair from filename
            # Example filename: xi_p_bin_1_1.txt
            parts = f.split('_')
            bin1 = int(parts[-2])
            bin2 = int(parts[-1].split('.')[0])
            inventory_rows.append({
                'product': 'xipm',
                'path': file_path,
                'n_rows': n_rows,
                'statistic': statistic,
                'bin_pair': f'({bin1}, {bin2})',
                'mode_bin_count': n_rows,
                'note': f'theta bin count: {n_rows}'
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    return inventory_rows

def index_kcap_cosebis(kcap_root, inventory_rows):
    """Index KCAP COSEBIs predictions if available"""
    # Look for COSEBIs files in predictions directory
    cosebis_files = []
    for root, dirs, files in os.walk(kcap_root):
        for f in files:
            if ('cosebi' in f.lower() or 'COSEBI' in f) and f.endswith('.txt'):
                cosebis_files.append(os.path.join(root, f))
    
    for file_path in cosebis_files:
        try:
            data = np.loadtxt(file_path)
            n_rows = len(data)
            inventory_rows.append({
                'product': 'cosebis',
                'path': file_path,
                'n_rows': n_rows,
                'statistic': 'COSEBIs',
                'bin_pair': 'unknown',
                'mode_bin_count': n_rows,
                'note': f'mode count: {n_rows}'
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    return inventory_rows

def main(config_path):
    config = load_config(config_path)
    kcap_root = config['input_paths']['kcap_predictions_root']
    out_dir = config['output_paths']['out_dir']
    out_file = os.path.join(out_dir, config['output_paths']['inventory_file'])
    
    inventory_rows = []
    
    print("Indexing KCAP BandPower PeeE predictions...")
    inventory_rows = index_kcap_bandpower_peeE(kcap_root, inventory_rows)
    
    print("Indexing KCAP ξ± predictions...")
    inventory_rows = index_kcap_xipm(kcap_root, inventory_rows)
    
    print("Indexing KCAP COSEBIs predictions...")
    inventory_rows = index_kcap_cosebis(kcap_root, inventory_rows)
    
    # Convert to DataFrame and save
    inventory_df = pd.DataFrame(inventory_rows)
    inventory_df.to_csv(out_file, index=False)
    
    print(f"\nKCAP prediction inventory completed: {len(inventory_df)} files indexed")
    print(f"Inventory saved to: {out_file}")
    print("\nSummary:")
    print(inventory_df.groupby('product').size().reset_index(name='file_count'))
    
    return inventory_df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to KCAP reproduction config file")
    args = parser.parse_args()
    main(args.config)
