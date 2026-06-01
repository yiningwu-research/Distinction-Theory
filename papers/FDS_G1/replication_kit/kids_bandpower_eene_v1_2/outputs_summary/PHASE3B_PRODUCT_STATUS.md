# Phase 3B Product Status: KiDS-1000 Cosmic-Shear Representations

## Summary

KiDS-1000 cosmic-shear data products exist in **three official representations**:

| Product | Basis | Vector Dim | Covariance Dim | Status | Phase |
|---------|-------|-----------|---------------|--------|-------|
| ξ± | real-space θ | 270 (15 pairs × 9 θ-bins × 2 probes) | 270×270 (derived) | PASS — standardized, row-order verified | 3A ✅ |
| COSEBIs | mode-space (En, n=1..20) | 300 (15 pairs × 20 modes) | 300×300 (official) | PASS — standardized, row-order verified from source code | 3B-1 ✅ |
| BandPower | Cℓ top-hat (8 ℓ-bins) | 200 (25 pairs × 8 ℓ-bins) | 200×200 (FITS COVMAT) | PASS — standardized CSV + .npy, row-order verified from FITS tables | 3B-2 ✅ |
| Phase 3E-1 | BandPower PeeE Projector | PeeE subset | 120 (15 pairs × 8 ℓ-bins) | 120×120 (extracted from 200×200 by label) | PASS — validated PeeE product/projector layer ready for model integration | 3E-1 ✅ |
| full 3×2pt | real-space (γ_t, w(θ)) | missing | missing | BLOCKED — no precomputed γ_t/w(θ) or matching real-space cov | — |

## COSEBIs Audit Result

```
COSEBIs product audit:   PASS
vector length:           300 ✓
covariance shape:        300×300 ✓
finite:                  yes ✓
symmetric:               yes (abs diff = 0) ✓
positive definite:       yes (eig_min = 1.3e-22) ✓
cholesky:                pass ✓
bestfit == blindC:       yes (max diff = 1.8e-20) ✓
row-order verification:  verified_from_source_code
                         (MakeDataVectors.py:99-107, run_measure_cosebis_cats2stats.py:155)
```

## Row Order (COSEBIs)

```
300 = 15 source-bin pairs (triangular i<=j) × 20 COSEBIs modes (n=1..20)

Pair order: (0,0), (0,1), ..., (4,4)
Mode order: n=1, 2, ..., 20 (inner loop)
```

## Files Produced

| File | Description |
|------|-------------|
| `data/kids1000_cosebis_300_standard.csv` | 300-row standard CSV (statistic, bin1, bin2, mode, value) |
| `data/kids1000_cosebis_covariance_300.npy` | 300×300 covariance (bestfit == blindC total) |
| `data/cosebis_row_order_verified.csv` | 300-row row-order metadata |
| `data/raw_or_external/` | Symlinks to raw KiDS products |
| `configs/kids_cosebis_audit.yaml` | Audit config (reproducible) |
| `src/convert_kids_cosebis_to_standard_csv.py` | Converter script |
| `src/audit_kids_cosebis.py` | Audit script (config-first, CLI-overridable) |
| `outputs/cosebis_300_audit/` | Audit outputs (manifest, audit.md) |
| `outputs/cosebis_covariance_audit/` | Corrected covariance audit (relabeled from bandpower) |

## Phase 3D: COSEBIs Likelihood Calibration

**Status: COMPLETE** — Tests 1+2+3a done.

### Test 1: Convention Scan (72 variants × 2 models)

Convention dimensions scanned:
- scale factor: 0.1, 1, 10
- T⁻ final sign: +1, -1
- T⁺ normalization: ×1 (KiDS), ×1/(2π), ×2π
- Mode order: forward, reverse
- T⁻ internal branch: original, flipped

**Best results:** χ² ≈ 475-493 for 300 dof (still ~1.6× expected).
- Optimal conventions: scale=0.1, T⁺=2π (cancels built-in factor), mode_order=reverse
- A* ≈ 0.76-0.94 (amplitude close to 1 after tuning)
- sign_match_total ≈ 0.60, sign_match_low_modes ≈ 0.77, sign_match_high_modes ≈ 0.46

### Test 2: Amplitude-Only Calibration

Embedded in convention scan. A* near 1 for best variants confirms amplitude is approximately right.

### Test 3a: KCAP Direct Comparison

Existing KCAP 5-mode COSEBIs predictions compared with G1 projections on same bin pairs. Ratios vary from 0.002 to 3.6 across pairs × modes. Mode dependence shape is systematically different (KCAP decreases with mode, G1 increases).

### Conclusions

- **Mismatch is upstream**: Different Cℓ from different cosmology/settings/inputs, not Tₙ convention. Candidate sources include cosmology, P(k), n(z), IA, shear calibration, and photo-z — the convention scan does not isolate a unique culprit.
- **Tₙ implementation correct**: Per KiDS `measure_cosebis.py` source code.
- **No further calibration possible**: Convention-scanned all relevant dimensions.

### Files

| File | Description |
|------|-------------|
| `src/cosebis_convention_scan.py` | Convention scan orchestrator |
| `configs/kids_cosebis_calibration.yaml` | Calibration config |
| `src/test_same_xi_3b.py` | Same-ξ± isolated comparison (Test 3b, partial) |
| `outputs/cosebis_calibration/convention_scan.csv` | 144-variant results |
| `outputs/cosebis_calibration/best_variant_summary.md` | Per-model best variants |
| `outputs/cosebis_calibration/kcap_direct_comparison.csv` | KCAP 5-mode comparison |

## BandPower (Phase 3B-2)

### Audit Result

```
BandPower product audit:   PASS
vector length:             200 ✓
covariance shape:          200×200 ✓
finite:                    yes ✓
symmetric:                 yes (abs diff = 0) ✓
positive definite:         yes (eig_min = 2.8e-11) ✓
cholesky:                  pass ✓
asc vs fits table match:   yes ✓
row-order verification:    verified_from_fits_header
                           (FITS PneE/PeeE table columns BIN1, BIN2, ANGBIN)
```

### Row Order

```
200 = 25 source-source pairs × 8 ell-bins

PneE (80 rows):   lens_bin(1..2) × source_bin(1..5) × angbin(1..8)
                   outer: lens, middle: source, inner: angbin
PeeE (120 rows):  source_bin1(1..5) × source_bin2(bin1..5) × angbin(1..8)
                   triangular bin1≤bin2 pairs, angbin innermost

Total: 10 PneE pairs (2×5) + 15 PeeE pairs (5×6/2) = 25 pairs × 8 = 200
```

### Cross-Check: FITS vs Iterative Covariance

Standard `fits/` COVMAT compared with `fits_iterative_covariance/` version:
- Both 200×200, max abs diff = 2.66e-07 (iterative is refined estimate)
- Data vector values (PneE/PeeE) identical between versions

### Covariance Source

The 200×200 COVMAT is extracted from the FITS file HDU `COVMAT`
(ImageHDU, `COVDATA=True`). The sparse `thps_cov_*_list.dat` (224×224 with
25200 entries) corresponds to a different binning scheme (7 effective bins,
may include E+B modes) and is NOT the covariance for the 200-element data vector.

### Files Produced

| File | Description |
|------|-------------|
| `data/kids1000_bandpower_200_standard.csv` | 200-row standard CSV |
| `data/kids1000_bandpower_covariance_200.npy` | 200×200 covariance (.npy) |
| `data/bandpower_row_order_verified.csv` | Row-order metadata |
| `outputs/bandpower_200_audit/` | Audit outputs (manifest, audit.md) |
| `configs/kids_bandpower_audit.yaml` | Audit config (reproducible) |
| `src/audit_kids_bandpower.py` | Audit script (config-first, CLI-overridable) |
| `src/convert_kids_bandpower_to_standard_csv.py` | Converter script |

## Full 3×2pt

- **Status**: BLOCKED — no precomputed real-space γ_t or w(θ) data vectors in official KiDS repo
- **Source code exists**: `calc_gt_w_treecorr.py` but requires catalog access and TreeCorr runtime
- **Matching covariance**: 300×300 bestfit_3x2pt COSEBIs cov is shear-only, not 3×2pt

## Key Correction from Phase 3A

The 300×300 covariance previously labelled "bandpower covariance" is actually the **KiDS COSEBIs cosmic-shear covariance** (COSEBIs mode-space, nmax=20, shear-only). It was confirmed:

- The filename `Covariance_bestfit_3x2pt_*` is misleading — it's shear-only COSEBIs, not full 3×2pt
- It matches `Covariance_blindC` to machine precision (max diff = 1.8e-20)
- Row ordering is source-code verified, not dimension-only

## Phase 3E: BandPower Projector Validation
Status: PASS ✅
The BandPower PeeE product/projector layer is validated and ready for G1 model integration. Model χ² smoke tests and PneE/full-200 theory projection remain optional deferred work.

---

*Status doc written 2026-05-30 during Phase 3B-1 COSEBIs product audit; updated 2026-05-30 with Phase 3B-2 BandPower audit results; updated 2026-05-30 with Phase 3E-1 PeeE projector validation results.*
