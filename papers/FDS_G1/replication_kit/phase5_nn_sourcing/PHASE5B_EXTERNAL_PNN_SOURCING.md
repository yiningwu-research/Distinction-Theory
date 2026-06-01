# Phase 5B: External Pnn Sourcing Audit (v1.2)

## Summary

This audit documents the search for publicly available Pnn bandpower
products that could substitute for the locally unavailable nn clustering
vector.

## Search Results

| Source | Status |
|---|---|
| KiDS-1000 data release products | No Pnn BandPower HDU in processed data |
| KiDS-Legacy public data | Not yet available at time of audit |
| DES Y3 bandpower products | Different survey footprint and redshift distribution |
| Public covariance repositories | Covariance exists (300×300), nn block lacks paired data vector |

## Manifest

See `data_manifest/public_pnn_search_manifest.json` for the full inventory
of searched locations, file patterns, and search results.

## Conclusion

No suitable public Pnn product was found that:
- Matches the KiDS-1000 survey footprint and redshift binning,
- Provides a bandpower-format nn clustering vector,
- Can be paired with the existing 300×300 covariance.

Full 3×2pt remains **blocked** until a real nn clustering vector becomes
available or is recomputed from catalog level.
