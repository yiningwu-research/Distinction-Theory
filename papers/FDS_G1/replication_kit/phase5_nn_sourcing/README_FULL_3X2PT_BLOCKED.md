# Full 3×2pt: Blocked Status (v1.2)

## Summary

The v1.2 paper includes the **KiDS BandPower EE+nE diagnostic bridge**
(Phase 3–4) as an infrastructure and validation layer. However, **full
3×2pt likelihood evaluation including galaxy-galaxy lensing and clustering
(nn channel) remains unavailable.**

## Why It Is Blocked

1. The 300×300 bandpower covariance exists, and the first 200×200 rows
   (EE + nE) have been validated and used in the EE+nE bridge.

2. Rows 200–299 (nn block) of the covariance cannot be paired with a
   usable real nn data vector — no precomputed Pnn BandPower HDU was
   found in any local or public release.

3. Catalog-level recomputation was deferred to a separate high-cost branch
   (Phase 5C) and is not part of the v1.2-dev release.

## What This Means for Claims

- The EE+nE bridge is a **diagnostic validation layer**, not an optimized
  likelihood and not production model evidence.
- No full 3×2pt model constraints are reported in v1.2.
- The stage-2d exact likelihood (SN + DESI DR2 BAO + RSD fσ₈ + E_G)
  remains the sole source of production model evidence.

## Timeline

Full 3×2pt integration is planned for a future release once:
- A real nn clustering vector is obtained, or
- Catalog-level recomputation is completed (Phase 5C).
