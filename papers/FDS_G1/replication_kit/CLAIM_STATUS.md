# FDS-G1 Complete Series — CLAIM STATUS

## v1.3 G1DM / Companion G

**Compressed G1DM-C0 diagnostic layer (v1.3): COMPLETE at compressed-proxy level.**

The v1.3 release adds Companion G as the matter-sector / dark-matter ontology
companion and includes the G1DM-C0 carrier-floor strengthening section in the
main text.  The central compressed diagnostic is:

```
T_D != 0,  mu_grav ~= 1,  D_optics_S8 != 0  at compressed-proxy level.
```

### Note 1 — carrier floor

| Claim | Status |
|-------|--------|
| Planck 2018 Omega_c h^2 = 0.1200 +/- 0.0012 | published posterior reproduced |
| Omega_c h^2 = 0 excluded | >100 sigma |
| Pure Weyl-DM cannot replace full CDM | supported |

### Note 3 — growth leakage

| Claim | Status |
|-------|--------|
| DESI DR1 mu0 consistent with 0 (FS/BAO+Planck) | z_growth = 0.94 |
| DESI DR1 mu0 consistent with 0 (+DESY3joint) | z_growth = 0.17 |
| Growth-only disfavored in all combinations | supported |
| M3/4 Weyl sign-lock confirmed | NOT CONFIRMED (DESI Sigma0 > 0 opposite M3/4 sign; Planck-linked Weyl disappears with DESY3joint) |

### Note 4 Phase 2 — independent S8 compressed proxy

| Claim | Status |
|-------|--------|
| KiDS-1000 S8 tension vs Planck: 2.77 sigma | compressed proxy |
| DES Y3 S8 tension vs Planck: 2.57 sigma | compressed proxy |
| source+optics selected over source-only (r-stable) | supported at compressed-proxy level |

### v0.4 production path

| Claim | Status |
|-------|--------|
| KiDS-1000 ingestion and S8 validation | passed |
| BandPower covariance readiness | passed |
| Full SRO inference | BLOCKED pending KCAP/CosmoSIS model-vector generation |

### Not claimed (v1.3)

- Completed dark-matter solution
- Particle identity of dark matter
- Full 3x2pt SRO confirmation
- Production multi-probe G1DM evidence
- M3/4 Weyl sign/amplitude lock confirmed

---

## v1.2 Update (inherited)

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

---

## CMB Lensing — Pre-Production Implementation

**Status: Pre-production stress-test module available.**

### Completed

- Analytic linear Limber pipeline with shared early-time growth normalization
- Dual normalization audit (code-raw vs present-day-relative)
- Fixed-primordial and fixed-sigma8 diagnostic amplitude modes
- Fiducial M3/4 C_L^{phi phi} ratio benchmark (analytic)
- Generic bandpower NPZ likelihood interface
- Official ACT DR6 / Planck PR4 adapter code

### Current benchmark

- Broad C_L^{phi phi} suppression is present in the fiducial analytic run
- The result is a structural warning, not a production likelihood result
- Must not be interpreted as formal exclusion significance until full audit

### Pending (kill-test level, not completed for v1.x)

- CLASS backend validation with full modified Boltzmann integration
- Official ACT DR6 / Planck PR4 data run with proper covariance handling
- Primary TT/TE/EE likelihood and parameter refit
- Nonlinear and numerical-systematics audit
- BBN compatibility check

---

## Production Kill Tests

The following are pre-registered kill tests. Failure at any of these does
not automatically falsify the G1DE class, but removes it from consideration
as a complete dark-sector replacement. All of these are currently pending:

1. **CMB lensing**: Significant positive detection beyond systematic error budgets
   would falsify the locked M_{3/4} Weyl response amplitude.

2. **BBN compatibility**: Properly defined light-element-abundance constraints
   that cannot be accommodated within the G1 effective DE framework.

These tests must be evaluated at full production-Boltzmann level before any
official exclusion or confirmation claim can be made.
