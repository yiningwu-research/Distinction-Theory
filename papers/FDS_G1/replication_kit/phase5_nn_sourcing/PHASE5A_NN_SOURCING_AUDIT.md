# Phase 5A: NN Sourcing Audit (v1.2)

## Summary

A systematic search was conducted for the nn (clustering) bandpower product
and its covariance to enable full 3×2pt likelihood evaluation. This audit
documents the availability, provenance, and current status of the nn
clustering channel.

## Inventory

| Item | Status |
|---|---|
| 300×300 bandpower covariance | EXISTS — first 200×200 matches EE+nE |
| EE bandpower vector | AVAILABLE — used in EE+nE bridge |
| nE bandpower vector | AVAILABLE — used in EE+nE bridge |
| nn (clustering) bandpower vector | NOT FOUND locally |
| Real Pnn / w(theta) product | NOT FOUND locally or publicly |
| Catalog-level recomputation | DEFERRED (Phase 5C, separate branch) |

## Key Findings

1. The full 300×300 bandpower covariance exists. The first 200×200 rows
   (EE + nE blocks) have been validated and used in the EE+nE bridge.

2. Rows 200–299 (nn block) of the covariance exist but cannot be paired
   with a usable real nn data vector in any local or public release.

3. No precomputed Pnn BandPower HDU matching the KiDS-1000 release format
   was found in the processed data directories.

4. Catalog-level recomputation of the nn vector from KiDS-1000 shear
   catalogs was considered but deferred to a separate high-cost branch
   (Phase 5C, not in v1.2-dev).

## Conclusion

Full 3×2pt likelihood evaluation remains **blocked** pending availability
of a usable real nn clustering vector or catalog-level recomputation.
