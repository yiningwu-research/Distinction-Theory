# KiDS-1000 Data Download Instructions

## Option 1: Use the included download script

```bash
python ../src/kids1000_download_prepare.py
```

This script clones the public `Cat_to_Obs_K1000_P1` repository and builds a
manifest of available products. You will need to extract the specific files
listed below manually.

## Option 2: Manual download

1. Clone the KiDS-1000 public data repository:
   ```bash
   git clone https://github.com/KiDS-WL/Cat_to_Obs_K1000_P1.git
   ```

2. Locate the following files in the extracted repository:
   - `Cat_to_Obs_K1000_P1-master/data/kids/xipm/` — xi_pm measurements
   - `Cat_to_Obs_K1000_P1-master/data/kids/nofz/` — redshift distributions
   - `Cat_to_Obs_K1000_P1-master/data/covariance/` — covariance matrices

3. Convert to the CSV format expected by `stage3_lensing_3x2pt.py`.
   The `kids1000_download_prepare.py` script can automate this conversion.

## Verification

After obtaining the data, verify integrity with the expected SHA256 hashes:

```bash
sha256sum -c expected_sha256.txt
```

## References

- KiDS-1000 data products: https://kids.strw.leidenuniv.nl/
- KiDS-1000 cosmic shear paper: Asgari et al. 2021, A&A 645, A104
- Public data repository: https://github.com/KiDS-WL/Cat_to_Obs_K1000_P1
