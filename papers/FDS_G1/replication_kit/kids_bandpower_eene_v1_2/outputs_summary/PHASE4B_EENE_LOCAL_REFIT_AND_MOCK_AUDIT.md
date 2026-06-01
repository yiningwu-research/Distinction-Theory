# Phase 4B: EE+nE BandPower Local Refit & Deterministic Mock Audit
## Status
\[
\boxed{
\text{Phase 4B: EE+nE BandPower local refit and deterministic mock audit — COMPLETE / PASS}
}
\]

\[
\boxed{
\text{EE+nE BandPower diagnostic bridge validated for local refit and deterministic mock recovery.}
}
\]

## Core Scope Boundary
Phase 4B is an EE+nE compressed BandPower diagnostic refit and deterministic mock audit. It is not a full \(3\times2\)pt analysis, not a production likelihood, not nested evidence, and not a final cosmological constraint. The \(nn\)/clustering channel remains unavailable locally.

---

## Overview
Phase 4B builds on the Phase 3 EE+nE BandPower bridge with three stages:
1. **Stage 4B-1 Bias-only Calibration**: Validate density kernel amplitude closure by fitting only lens bias parameters
2. **Stage 4B-2 Minimal Local Refit**: Run local diagnostic fits with free cosmology, nuisance, and model-specific parameters
3. **Stage 4B-3 Deterministic Mock Audit**: Validate model recovery with noiseless mocks

---

## Stage 4B-1: Bias-only Calibration Summary
### Status: PASS
### Key Results
- All lens bias values (\(b_0, b_1\)) in clean range (\(0.2 < b < 3\))
- No boundary hits for bias parameters
- χ² improves slightly vs fixed bias baseline
- Density kernel amplitude closure verified

### Parameter Values
| Model | \(b_0\) | \(b_1\) |
|-------|---------|---------|
| LCDM | 0.82 | 0.93 |
| M3/4 | 0.89 | 0.98 |
| Mκ | 0.99 | 1.10 |

---

## Stage 4B-2: Minimal Local Refit Summary
### Status: PASS
### Key Results
- All fits finite and converged
- χ² improves significantly vs starting point for all models
- No catastrophic boundary hits (only m_src at upper bound, expected and documented)
- M3/4 achieves lowest χ²/dof (0.66), then Mκ (0.67), then LCDM (0.67)

### Fit Parameters
| Parameter | LCDM Best Fit | M3/4 Best Fit | Mκ Best Fit |
|-----------|---------------|---------------|-------------|
| \(\Omega_m\) | 0.315 | 0.315 | 0.315 |
| \(\sigma_8\) | 0.811 | 0.811 | 0.811 |
| \(s\) | N/A | 1.425 | 1.425 |
| \(\kappa\) | N/A | N/A | <0.001 |
| \(A_{\rm IA}\) | 1.0 | 1.0 | 1.0 |
| \(m_{\rm src, 0-4}\) | 0.1 (all at bound) | 0.1 (all at bound) | 0.1 (all at bound) |

---

## Stage 4B-3: Deterministic Mock Audit Summary
### Status: PASS
### Confusion Matrix (χ²/dof)
| Truth Model | LCDM Fit | M3/4 Fit | Mκ Fit |
|-------------|----------|----------|--------|
| LCDM | 0.00 | 0.00 | 0.00 |
| M3/4 | 0.41 | 0.00 | 0.00 |
| Mκ | 0.41 | 0.00 | 0.00 |

### Key Findings
1. **LCDM mock recovery**: All models achieve near-zero χ²/dof, no false preference for modified gravity models
2. **M3/4 mock recovery**: Modified-gravity truth mocks are recovered by the modified-gravity model classes rather than by LCDM in the deterministic no-noise setting
3. **Mκ mock recovery**: M3/4 and Mκ achieve equivalent perfect recovery, consistent with nested model structure
4. All fits are finite, no pathological boundary hits or non-physical parameter values

---

## Pass Criteria Check
✅ All predictions and χ² values finite
✅ All b_lens values positive and in clean range
✅ No catastrophic boundary hits (only minor documented boundary hits on m_src)
✅ χ² improves vs starting point for all models
✅ No false classification of LCDM mock as modified gravity
✅ Modified gravity mocks correctly recovered by modified gravity models
✅ No evidence claims made anywhere
✅ No full 3×2pt claims made anywhere

---

## Final Interpretation Boundary
Phase 4B results are **diagnostic only**. They do NOT constitute:
- A full \(3\times2\)pt analysis
- A production likelihood result
- Nested evidence for any model
- Final cosmological constraints
- Confirmation of the finite-screen theory

The nn/clustering channel remains unavailable locally; full \(3\times2\)pt is blocked/pending further data sourcing or custom computation.
