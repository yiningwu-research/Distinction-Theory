# CLAIM_STATUS.md
# FDS-G1 Complete Series v1.1-rc1

## Current status (v1.0-rc3 exact-pilot evidence)

The M_{3/4} projection-locked branch is selected by AIC, BIC, and
medium-prior nested evidence over five controls (M_kappa, const-Sigma,
G1DE-2, CPL, LCDM). Top-control wide-prior sensitivity confirms the
ranking is stable.

## v1.1 KiDS shear-only diagnostic status

| Claim | Status |
|-------|--------|
| M3/4 evidence-selected under homogeneous medium-prior nested evidence | exact-pilot, not production |
| KiDS shear-only Weyl-channel stress test supports M3/4 vs LCDM under m_i+dz_i+A_IA | diagnostic shear-only, not full 3x2pt |
| Free-kappa returns kappa approx 0.746 | projection-lock diagnostic support |
| Deterministic mock injection does NOT misclassify LCDM/const-Sigma/binned-Sigma truths as M3/4 | deterministic false-positive audit passed; noisy ensemble pending |
| R_bH(a) exact shape is production-confirmed | not claimed; under controlled stress from binned-Sigma |

## Claim level

  Exact-pilot evidence-selected + KiDS shear-only stress-tested.
  Not yet production-confirmed.

## Pending

  - Full production nested evidence with dlogz <= 0.1 and >= 8-10 seeds
  - Full 3x2pt lensing likelihoods including galaxy-galaxy lensing and clustering
  - Noisy mock ensembles
  - Full baseline wide-prior sensitivity (all 6 models)
  - Independent replication

## Demotion conditions

  If any of the following hold under future data:

  1. Free-kappa decisively beats M_{3/4} -> 3/4 lock demoted
  2. Constant-Sigma decisively beats M_{3/4} -> output-shape not resolved
  3. |mu-1| ~ |Sigma-1| -> Ward suppression fails
  4. Free A(a,k) required -> leaves G1DE class
  5. CPL or LCDM wins -> observational branch demoted
  6. Expanded lensing does not support Weyl signal -> dark-sector interpretation fails

## Model assumptions

All six demotion paths are pre-specified. M_{3/4} is a paradigm-level
candidate, not an incremental parameterization. Its distinguishing claim
is prediction lock: 3 parameters reproduce the expansion history plus
the Weyl response simultaneously from a single finite-screen coefficient.
