# Phase 3A-real Status: Basis/Product Gap

## Inspection Summary

| Item | Status | Details |
|------|--------|---------|
| Source repo | Extracted | `Cat_to_Obs_K1000_P1-master` from KiDS-WL, cloned previously |
| xi± real-space vector | Available | `xipm_*_nbins_9_*.asc` — 270 elements, one-per-line, no metadata |
| xi± fine-binned per-pair | Available | 15 × `XI_*_Bin*_Bin*.ascii` — 4000 theta bins each, includes `meanr`, `xip`, `xim` |
| n(z) | Available | `nofz/SOM_N_of_Z/` — 5 tomographic bins, `.asc` + `.fits` |
| COSEBIs covariance | Available | `Covariance_bestfit_3x2pt_*_nBins5.ascii` — 300×300, symmetric, COSEBIs mode space (previously misidentified as bandpower) |
| γ_t data vector | **Missing** | No pre-computed real-space gamma_t file found; only source code `calc_gt_w_treecorr.py` |
| w(θ) data vector | **Missing** | No pre-computed real-space wtheta file found; same code produces it |
| γ_t/w(θ) matching cov | **Missing** | No real-space 3×2pt covariance available (only bandpower version) |

## Basis Mismatch (Corrected)

```
    270-element xi± vector  ≠  300×300 covariance
    (real-space θ basis)        (COSEBIs mode-space basis)
```

Using these together in a likelihood would be incorrect. The 300 does not factor as 270 + extra — it is 15 source-bin pairs × 20 COSEBIs modes, a fundamentally different compression scheme (mode-space vs real-space). The covariance was previously labelled "bandpower" but is actually the **KiDS COSEBIs cosmic-shear covariance** (confirmed via source-code verification — see Phase 3B-1).

## Blocked Deliverable

**Full real-space 3×2pt row-order audit** is blocked until:

1. Real-space γ_t data vector (5 lens × 5 source = 25 bin pairs × θ bins)
2. Real-space w(θ) data vector (5 lens auto+cross = 15 bin pairs × θ bins)
3. A matching real-space 3×2pt covariance matrix covering all three probes

## Current Safe Deliverable

1. **xi± real-space standardization** — convert official KiDS xi± to standard CSV; can be audited independently (Phase 3A ✅)
2. **COSEBIs product audit** — 300-element vector + 300×300 covariance, row-order verified from source code, documented as cosmic-shear only (Phase 3B-1 ✅)

## γ_t/w(θ) Sourcing Options

| Option | Approach | Cost | Notes |
|--------|----------|------|-------|
| A | Find precomputed γ_t/w(θ) from BOSS/2dFLenS data release | Low-Med | Best if exists; check KiDS-1000 cosmology data products |
| B | Compute via `calc_gt_w_treecorr.py` from lens/source catalogues | Med-High | Requires BOSS/2dFLenS lens catalogues |
| C | Switch to bandpower-space 3×2pt likelihood | High | Cleaner match to existing covariance, but major theory-code change |
| D | Limit to 2×2pt-lite (ξ± + γ_t, skip w(θ)) | Low | Not full 3×2pt; acceptable for intermediate stage |

**Decision**: Priotise Option A (search for precomputed real-space γ_t/w(θ)) before committing to B, C, or D.

## Phase 3A-real Result Summary

```
xi± real-space standardization:      PASS (270-element vector standardized + 135 after cuts) (Phase 3A ✅)
xi± row-order audit:                 PASS (15 bin-pair × 9 θ-bins ordering verified from + fine files) (Phase 3A ✅)
COSEBIs covariance numerical audit:  PASS (300×300, symmetric, positive definite, Cholesky pass) (Phase 3A ✅)
COSEBIs row-order audit:             PASS (15 bin-pair × 20 modes, verified from source code) (Phase 3B-1 ✅)
full real-space 3×2pt audit:         BLOCKED
reason: missing precomputed γ_t/w(θ) vectors and no matching real-space 3×2pt covariance
```

---

*Status doc written 2026-05-30. Updated 2026-05-30: 300×300 covariance relabeled from "bandpower" to "COSEBIs" after source-code verification (MakeDataVectors.py:99-107, run_measure_cosebis_cats2stats.py:155).*
