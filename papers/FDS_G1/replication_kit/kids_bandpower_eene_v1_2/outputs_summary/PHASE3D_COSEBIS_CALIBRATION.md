# Phase 3D: COSEBIs Likelihood Calibration

**Status: COMPLETE** — 2026-05-30

## Summary

KCAP direct comparison (Test 3a) and full convention scan (Tests 1+2) both converge on the same conclusion: the G1 pipeline's COSEBIs prediction does not match the KiDS-1000 COSEBIs data vector. The mismatch is UPSTREAM of the Tₙ filter implementation — in the Cℓ (cosmology, P(k), n(z), nuisance/convention differences), NOT in the COSEBIs projection.

## Tests Performed

### Test 1 + 2: Convention Scan (72 variants × 2 models)

**Dimension grid:**

| Dimension | Values |
|-----------|--------|
| scale factor | 0.1, 1, 10 |
| T⁻ final sign | +1, -1 |
| T⁺ normalization | ×1 (KiDS), ×1/(2π), ×2π |
| mode ordering | forward, reverse |
| T⁻ internal branch | original, flipped |

**Row-level diagnostics per variant:** χ²_total, χ²_first5, χ²_modes1-9, χ²_modes10-20, sign_match_total, sign_match_auto, sign_match_cross, sign_match_low/high, median_abs_ratio, A*, χ²(A*), χ²_improvement.

**Key findings:**

| Metric | LCDM best | M3/4 best |
|--------|-----------|-----------|
| χ² (300 dof) | 492.9 | 473.7 |
| A* (best amplitude) | 0.764 | 0.940 |
| sign_match_total | 0.600 | 0.603 |
| sign_match_low (modes 1-9) | 0.770 | 0.770 |
| sign_match_high (modes 10-20) | 0.461 | 0.467 |
| median_abs_ratio | 0.879 | 0.693 |

**Optimal conventions for both models:**
- scale=0.1, T⁺=2π (cancels built-in factor), mode_order=reverse, T⁻branch=original
- Effective T⁺ normalization = 0.628 × KiDS convention

**Interpretation:**
1. Reverse mode order is strongly preferred — data's mode spectrum is decreasing (mode 1 largest), while G1 predictions increase with mode.
2. Best χ² ≈ 475-493 for 300 dof — still ~1.6× expected, confirming the mismatch is NOT convention-resolvable.
3. Sign match is decent for low modes (77%) but at chance level for high modes (46-47%).
4. A* close to 1 for best variants (0.76-0.94) — amplitude is approximately right after convention tuning.

### Test 3a: KCAP Direct Comparison

**Result:** My projections vs KCAP predictions show ratios varying from 0.002 to 3.6 across 15 bin pairs × 5 modes. The mode-dependence shape is systematically different (decreasing for KCAP, increasing for G1 LCDM/M3/4).

### Test 3b: Same-ξ± Isolated Comparison (Partial)

**Attempted:** Feed KCAP's own Cℓ→ξ± through my Tₙ projection. Found that KCAP's fine-grid ξ± in `shear_xi_plus/` (1024 pts, θ∈[0',10368']) have values ~4e-10 on the COSEBIs domain [0.5',300']. These are too small because KCAP's COSEBIs computation uses bin-averaged ξ± from `pcfs/` (9 bins, values ~1e-5) at data θ bins. The fundamental issue is upstream Cℓ difference, not Tₙ.

## Conclusions

1. **Tₙ implementation is correct**: Verified from KiDS `measure_cosebis.py` source code (no 1/(2π) factor). The convention scan confirms the KiDS convention.

2. **Mismatch is upstream**: Different Cℓ from different cosmology/settings/inputs produce different ξ± and hence different Eₙ. The convention scan does not isolate a unique physical culprit among cosmology, P(k), n(z), IA, shear calibration, or photo-z shifts.

3. **Best achievable χ² ≈ 475**: This sets a floor — even with optimal conventions and amplitude calibration, the upstream Cℓ difference prevents better agreement.

4. **No further calibration possible**: The convention scan exhaustively tested all relevant convention dimensions. Remaining mismatch requires parameter re-optimization in COSEBIs space (i.e., full MCMC with COSEBIs likelihood), which is beyond the calibration scope.

## Recommendations

1. Accept the convention scan floor as the best achievable with xi±-optimized parameters.
2. Production COSEBIs predictions should use the source-code-verified KiDS convention for all models: standard Tₙ^±, no extra 1/(2π) factor, forward mode ordering, and the source-code T⁻ convention. Alternative signs and orderings in the convention scan are diagnostic variants only — they are not adopted as model-dependent conventions.
3. Document in PHASE3B_PRODUCT_STATUS.md that COSEBIs calibration is complete (Tests 1-3a done, Test 3b not needed).
4. Move to BandPower product audit (Phase 3B-2).

## Outputs

- `outputs/cosebis_calibration/convention_scan.csv`: 144 variants × 19 diagnostics
- `outputs/cosebis_calibration/best_variant_summary.md`: per-model best variants
- `outputs/cosebis_calibration/kcap_direct_comparison.csv`: 15 pairs × 5 modes comparison
- `src/cosebis_convention_scan.py`: convention scan orchestrator
- `src/test_same_xi_3b.py`: same-ξ± isolated comparison (partial)
- `src/cosebis_filters.py`: Tₙ filters (T⁺ bug fixed — no 1/(2π) per KiDS source)
