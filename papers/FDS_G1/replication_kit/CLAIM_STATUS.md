# FDS-G1 Complete Series — CLAIM STATUS

## v1.2 Update

**Production-refined seven-model medium-prior nested-evidence audit
(v1.2, all models 8 seeds, dlogZ=0.1): COMPLETE.**

The v1.2 audit is the current canonical evidence table for the FDS-G1 v1.2
paper. It supersedes the v1.1 3-seed homogeneous audit for model ranking.

**Important note on G1DE-1 and G1DE-2 scatter:** Both models have seed
scatter slightly above the strict 0.15 target (G1DE-1: 0.180, G1DE-2:
0.191). However, their evidence gaps from the reference model (M3/4) are
large — ΔlogZ ≈ 7.4 and 6.5 respectively — so the ranking is unaffected.
These models are marked as "stable in ranking but higher seed scatter."

**Full 3×2pt remains BLOCKED.** The EE+nE bandpower bridge is a diagnostic
validation layer only (see `kids_bandpower_eene_v1_2/` and
`phase5_nn_sourcing/`). No full 3×2pt model constraints are reported.

The stage-2d exact likelihood (SN + DESI DR2 BAO + RSD fσ₈ + E_G) is the
sole source of production model evidence.

---

## v1.1-rc1 (Original Kit Content)

### Current status (v1.0-rc3 exact-pilot evidence)

The M_{3/4} projection-locked branch is selected by AIC, BIC, and
medium-prior nested evidence over five controls (M_kappa, const-Sigma,
G1DE-2, CPL, LCDM). Top-control wide-prior sensitivity confirms the
ranking is stable.

### v1.1 KiDS shear-only diagnostic status

| Claim | Status |
|-------|--------|
| M3/4 evidence-selected under homogeneous medium-prior nested evidence | exact-pilot, not production |
| KiDS shear-only Weyl-channel stress test supports M3/4 vs LCDM under m_i+dz_i+A_IA | diagnostic shear-only, not full 3x2pt |
| Free-kappa returns kappa approx 0.746 | projection-lock diagnostic support |
| Deterministic mock injection does NOT misclassify LCDM/const-Sigma/binned-Sigma truths as M3/4 | deterministic false-positive audit passed; noisy ensemble pending |
| R_bH(a) exact shape is production-confirmed | not claimed; under controlled stress from binned-Sigma |

### Claim level

  Exact-pilot evidence-selected + KiDS shear-only stress-tested.
  (Superseded by v1.2 production-refined audit for model ranking.)

### Pending (as of v1.2)

  - ~~Full production nested evidence with dlogz <= 0.1 and >= 8-10 seeds~~ **COMPLETE in v1.2**
  - Full 3x2pt lensing likelihoods including galaxy-galaxy lensing and clustering
  - Noisy mock ensembles
  - Full baseline wide-prior sensitivity (all 6 models)
  - Independent replication

### Demotion conditions

  If any of the following hold under future data:

  1. Free-kappa decisively beats M_{3/4} -> 3/4 lock demoted
  2. Constant-Sigma decisively beats M_{3/4} -> output-shape not resolved
  3. |mu-1| ~ |Sigma-1| -> Ward suppression fails
  4. Free A(a,k) required -> leaves G1DE class
  5. CPL or LCDM wins -> observational branch demoted
  6. Expanded lensing does not support Weyl signal -> dark-sector interpretation fails

### Model assumptions

All six demotion paths are pre-specified. M_{3/4} is a paradigm-level
candidate, not an incremental parameterization. Its distinguishing claim
is prediction lock: 3 parameters reproduce the expansion history plus
the Weyl response simultaneously from a single finite-screen coefficient.
