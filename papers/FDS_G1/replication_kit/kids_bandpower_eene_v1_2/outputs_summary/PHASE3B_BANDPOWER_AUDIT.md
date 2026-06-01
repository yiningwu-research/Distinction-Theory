# Phase 3B-2: KiDS-1000 BandPower Product Audit

## Summary

**Status: PASS** ✅

The KiDS-1000 BandPower cosmic-shear product has been fully audited. Both the
200-element data vector and the 200×200 covariance matrix pass all numerical
and structural checks.

## Data Vector

- **Source**: `bp_K1000_ALL_BLIND_C_no_m_bias_*.asc` (200 lines)
- **Structure**: 25 source-source pairs × 8 ell-bins = 200
  - 10 PneE (lens-source) = 2 lens bins × 5 source bins × 8 ell-bins
  - 15 PeeE (source-source) = 5 source bins choose 2 (with replacement) × 8 ell-bins
- **Row order verified**: From FITS `PneE` and `PeeE` table headers
  - PneE: `lens_bin(1..2) × source_bin(1..5) × angbin(1..8)` — outer: lens, middle: source, inner: angbin
  - PeeE: `source_bin1(1..5) × source_bin2(bin1..5) × angbin(1..8)` — triangular pairs, angbin innermost
- **ASC vs FITS table match**: `True` — the `.asc` file values exactly match the FITS `PneE`/`PeeE` VALUE columns

## Covariance (COVMAT)

- **Source**: `bp_KIDS1000_BlindC_no_m_bias_*.fits` — HDU `COVMAT` (ImageHDU, `COVDATA=True`)
- **Shape**: 200×200
- **Finite**: yes
- **Symmetric**: yes (max abs diff = 0)
- **Diagonal range**: 3.4e-11 to 1.3e-05
- **Eigenvalue range**: 2.8e-11 to 1.3e-05
- **Positive definite**: yes
- **Cholesky**: pass (no jitter needed)
- **Partition**: Rows 0–79 = PneE (lens-source), Rows 80–199 = PeeE (source-source) — encoded in FITS headers `STRT_0`, `NAME_0`, `STRT_1`, `NAME_1`

## Cross-Check: FITS vs Iterative Covariance

The standard FITS covariance (`fits/`) was compared with the iterative
covariance version (`fits_iterative_covariance/`):

| Check | Value |
|-------|-------|
| Both 200×200 | yes |
| Max abs diff | 2.66e-07 |
| Match (< 1e-12) | no |

The 2.66e-07 difference is expected — the iterative covariance is a refined
estimate. The data vector values (PneE/PeeE) are **identical** between versions.

## Standardized Outputs

| File | Description |
|------|-------------|
| `data/kids1000_bandpower_200_standard.csv` | 200-row standard CSV |
| `data/kids1000_bandpower_covariance_200.npy` | 200×200 covariance (.npy) |
| `data/bandpower_row_order_verified.csv` | Row-order metadata |
| `outputs/bandpower_200_audit/kids1000_bandpower_manifest.json` | Full audit manifest |
| `outputs/bandpower_200_audit/bandpower_audit.md` | Audit report |
| `configs/kids_bandpower_audit.yaml` | Reproducible audit config |
| `src/audit_kids_bandpower.py` | Audit script |
| `src/convert_kids_bandpower_to_standard_csv.py` | Converter script |

## Notes

- The COVMAT is stored as a dense 200×200 float64 matrix in the FITS
  `ImageHDU`. The separate sparse `thps_cov_*_list.dat` file (224×224 with
  25200 entries) corresponds to a different binning scheme (7 effective bins
  with E+B modes) and is **not** the covariance for the 200-element data vector.
- The 200-element data vector uses 2 lens + 5 source bins directly,
  producing 200 = (2×5 + 5×6/2) × 8.
- No separate "bestfit" BandPower covariance exists in the official
  repository outputs — the FITS COVMAT is the canonical Blind C covariance.
