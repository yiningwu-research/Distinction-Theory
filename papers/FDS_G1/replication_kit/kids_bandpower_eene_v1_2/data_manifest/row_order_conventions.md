# Row-Order Conventions for KiDS BandPower Data

## BandPower Indexing

- EE bandpowers: rows 0–99 (100 bins)
- nE bandpowers: rows 100–199 (100 bins)
- nn bandpowers: rows 200–299 (100 bins, not available in processed data)

Total: 300 bin combinations (200 available with EE+nE bridge).

## Covariance Block Structure

The 200×200 EE+nE covariance block is the primary diagnostic target.
The first 100 rows correspond to EE-EE; rows 100–199 correspond to nE-nE
and EE-nE cross terms.

## Ordering Convention

Bandpower bins are ordered by increasing effective multipole ℓ_eff within
each block (EE, nE, nn), as defined in the KiDS-1000 data release.

## References

- KiDS-1000 bandpower data release documentation
- Phase 3A product audit notebooks
