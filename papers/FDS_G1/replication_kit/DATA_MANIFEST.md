# Data Manifest
# FDS-G1 Complete Series

## v1.2 Additions

### Production evidence outputs

Files in `production_evidence_v1_2/outputs_medium_8seed/`:

| File | Description |
|---|---|
| `per_seed_json/*.json` | 56 per-seed nested-evidence JSONs (7 models × 8 seeds) |
| `production_8seed_summary.csv` | Per-model aggregated statistics |
| `production_8seed_table3.csv` | Table 3 formatted output |
| `production_8seed_manifest.json` | Full provenance manifest |
| `logs_summary/n2_completed_jobs.csv` | Per-job metadata (logZ, ncall, eff, final dlogZ) |

### KiDS BandPower EE+nE diagnostic data

**Status**: diagnostic validation layer, not optimized likelihood or
production model evidence. Raw KiDS-1000 data is **not redistributed**.

See `kids_bandpower_eene_v1_2/data_manifest/` for:
- Row-order conventions
- Covariance shapes
- Expected SHA256 hashes (for independently obtained data)
- Download instructions

### Full 3×2pt status

No real nn clustering vector or Pnn bandpower product is available locally
or publicly. Full 3×2pt remains **blocked**. See `phase5_nn_sourcing/` for
the complete sourcing audit.

---

## v1.1-rc1 (Original Kit Content)

## Processed data files

All files are in processed_data/. SHA256 hashes recorded in
processed_data/sha256.txt.

### Pantheon+ SN Ia
  File: pantheon_plus.csv
  Cov:  pantheon_plus_cov.txt
  Source: Pantheon+SH0ES.dat + Pantheon+SH0ES_STAT+SYS.cov
  URL: https://github.com/PantheonPlusSH0ES/DataRelease

### DESI DR2 BAO
  File: desi_dr2_bao.csv
  Cov:  desi_dr2_bao_cov.txt
  Source: DESI DR2 BAO compressed data
  URL: https://data.desi.lbl.gov/

### Growth/RSD curated (v0 non-overlapping subset)
  File: growth_curated_nonoverlap_v0.csv
  Cov:  growth_curated_nonoverlap_v0_cov.txt
  Source: Growth Table II + WiggleZ 3x3 covariance
  Curation algorithm documented in spec/likelihood_conventions/rsd_curated.yaml

### E_G compressed points
  File: eg_amons2018_kids_2dflens_gama.csv
  Source: Amon et al. 2018 (KiDS+2dFLenS+GAMA)
  URL: https://doi.org/10.1093/mnras/sty2024

## Data preparation notes

- Pantheon+ and DESI data are used as-is after format conversion.
- Growth curation creates a non-overlapping subset as described in
  spec/likelihood_conventions/rsd_curated.yaml.
- E_G uses diagonal errors from the published measurement uncertainties.

## Reproducibility

If data redistribution is restricted, use the SHA256 hashes to verify
that independently obtained data matches the version used here.

## KiDS-1000 shear-only diagnostic data (new in v1.1-rc1)

Files:
- kids_shear_only/data/row_order_270.csv
- kids_shear_only/data/scale_cut_mask_135.csv

**Status**: shear-only diagnostic, not full 3x2pt.
Galaxy-galaxy lensing and angular clustering are not included.

The full KiDS-1000 data vector, covariance, and n(z) are **not redistributed**
in this repository.  See kids_shear_only/data/DOWNLOAD_INSTRUCTIONS.md for
download and verification instructions.

Expected SHA256 hashes: kids_shear_only/data/expected_sha256.txt
