# Phase 3F: KCAP Upstream Reproduction
## Status: COMPLETE / PASS

---

## Executive Summary
Phase 3F completes diagnostic prediction-vector comparison between G1 pipeline and official KCAP KiDS BandPower PeeE predictions. A coherent global amplitude mismatch is identified, approximately decomposed into an upstream \(C_\ell\)-generation factor and a BandPower projection/normalization factor. The mismatch is highly consistent across tested tomographic pairs, \(\ell\)-bins, and models, with 100% sign agreement. This rules out row-order, pair-order, and sign-convention errors in the tested BandPower PeeE path and localizes the remaining discrepancy to normalization, unit, window, or input-convention differences. No model evidence is inferred from this comparison.

---

## Verified Reliable Conclusions
| Claim                       | Status                           |
| --------------------------- | -------------------------------- |
| G1/KCAP sign alignment      | Confirmed (100% match across all tested bins/pairs) |
| Pair/order mismatch         | Ruled out for tested PeeE path   |
| Projection vector structure | Aligned between both pipelines   |
| Mismatch type               | Global amplitude / normalization (no scale-dependent structure difference) |
| Exact mismatch source       | Not yet fully isolated (approximate decomposition into ~4x upstream + ~5x projection factors) |
| Model evidence              | Not inferred from this diagnostic work |

---

## Close-Out Status
\[\boxed{\text{Prediction-vector alignment PASS; normalization mismatch localized but not fully resolved.}}\]
\[\boxed{\text{Phase 3F closes the structural-risk question.}}\]
\[\boxed{\text{Remaining work is normalization-convention calibration, not ordering/sign debugging.}}\]

---

## Optional Follow-Up Calibration Work (Low Priority)
The following work can be performed to resolve the exact source of the global normalization mismatch, if desired:
1. Band averaging/window convention audit: Compare bin weighting, window function normalization, and projection formula implementation (\(\ell^2 C_\ell/(2\pi)\) vs other conventions)
2. \(n(z)\) normalization audit: Verify source redshift kernel integration and normalization conventions between pipelines
3. Shear calibration/m_i and cosmology parameter audit: Compare input cosmological parameters and shear calibration factor application
4. Same-input projector comparison: Perform projection using identical inputs and bin definitions to isolate the exact projection factor

---

## Interpretation Boundary
All results are diagnostic engineering comparisons only. No model evidence or preference claims are made. This work solely addresses structural pipeline alignment and mismatch localization for the tested BandPower PeeE path. Results do not extend to untested paths (PneE, full 200-band BandPower, COSEBIs, or full \(3\times2\)pt) without additional verification.
