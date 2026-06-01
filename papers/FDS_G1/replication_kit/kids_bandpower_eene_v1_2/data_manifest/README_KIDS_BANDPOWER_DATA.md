# KiDS BandPower Data Manifest (v1.2 Diagnostic Layer)

## Data Status

KiDS-1000 shear data for the bandpower EE+nE diagnostic bridge is **not
redistributed** in this replication kit. Raw KiDS products are subject to
the KiDS data redistribution policy.

## What Is Included

- **Row-order conventions**: `row_order_conventions.md`
- **Covariance shapes and block structure**: `covariance_shapes.md`
- **Product inventory**: checksum manifest for products as processed
- **Expected SHA256 hashes**: for users who download the raw data

## What Is NOT Included

- Raw KiDS-1000 catalogs (restricted)
- Uncalibrated FITS files from the KiDS public release
- Full 3x2pt bandpower products with Pnn (these do not exist locally —
  see `phase5_nn_sourcing/`)
- 300×300 bandpower covariance matrices (beyond the first 200×200 rows
  that match EE+nE; see `phase5_nn_sourcing/`)

## For Users Who Want to Reproduce the Diagnostic Layer

1. Download KiDS-1000 data from the KiDS public release.
2. Run the product audit scripts in `../src/` to convert raw products
   to standardized CSV.
3. Verify output SHA256 against the expected hashes in this directory.
4. Run the EE+nE bandpower bridge and Phase 4 stress tests.

Contact the corresponding author for expected SHA256 values.
