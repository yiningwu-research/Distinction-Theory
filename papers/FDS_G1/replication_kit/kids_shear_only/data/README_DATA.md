# KiDS-1000 Data for Shear-Only Diagnostic Tests

## Data policy

KiDS-1000 survey data products are owned by the KiDS collaboration.
**We do not redistribute processed data vectors, covariance matrices, or n(z) files
in this repository.** See DOWNLOAD_INSTRUCTIONS.md for how to obtain and verify them.

## Files included in this directory (safe to distribute)

| File | Description |
|------|-------------|
| `row_order_270.csv` | Row index map for the 270-element xi_pm data vector. Columns: row_id, kind (xip/xim), bin_i, bin_j, theta_arcmin. No survey data. |
| `scale_cut_mask_135.csv` | Boolean mask mapping 270 rows to 135 kept rows after scale cuts. Derived from config, no survey data. |
| `expected_sha256.txt` | Expected SHA256 hashes for all data files (for verification after independent download). |
| `DOWNLOAD_INSTRUCTIONS.md` | Step-by-step download and verification guide. |

## Data files NOT redistributed (download required)

| File | Source | Role |
|------|--------|------|
| `kids1000_xipm_270_vector.csv` | KiDS-1000 | 270-element xi_pm data vector |
| `kids1000_xipm_covariance_270.txt` | KiDS-1000 | 270x270 covariance matrix |
| `nz_source_bin{0..4}.csv` | KiDS-1000 | Source redshift distributions (5 bins) |

Run `../scripts/00_prepare_kids_data.sh` to download and verify these files.
