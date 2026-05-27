# Data Manifest
# FDS-G1 Complete Series v1.0-rc3

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
