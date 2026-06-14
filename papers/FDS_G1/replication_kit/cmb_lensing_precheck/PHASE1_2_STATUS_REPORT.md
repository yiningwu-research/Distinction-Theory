# ⚠️ ARCHIVED — PRE-ROUTING-FIX — SUPERSEDED

**This report was written before the model-routing bug was discovered on 2026-06-13.** 
The `model.name` routing bug caused all G1 branches to compute the same Weyl response (κ=0.75). 
The Δχ² = -6.6 and +3.3% enhancement claims are from pre-routing-fix computations.
All conclusions in this document are superseded by `PHASE3_FINAL_RESULTS.md`.

---

# FDS-G1 CMB Lensing: Phase 1 & 2 Status Report (ARCHIVED)
## Version: 1.0rc3
## Date: 2026-06-11
## Overall Status: PRE-RELEASE (all numerical results verified)

---

## Executive Summary

All numerical validation complete. Likelihood pipeline is fully
verified against CLASS native lensing and ACT DR6 bandpower conventions.

**Key verified result:** G1 m=34 predicts **3.3% more lensing power**
than ΛCDM at fixed σ₈ today, and is preferred by ACT DR6 lensing
data at Δχ² = -6.6 relative to Planck 2018 ΛCDM.

---

## Phase Status Summary

| Phase | Status | Result |
|-------|--------|--------|
| **Phase 1A: CLASS backend** | ✅ PASS | CLASS/Limber agreement verified |
| **Phase 1B: ACT interface** | ✅ PASS | D_L convention verified, χ² matches |
| **Phase 2: Fiducial G1 likelihood** | ✅ CANDIDATE | Δχ² = -6.6 verified numerically |

---

## Phase 1: Validation Gates ✅ COMPLETE

### Phase 1A: CLASS Power Spectrum Backend ✅
- Limber integration framework implemented and tested
- Cross-validation against CLASS native lensing
- G1/ΛCDM ratio calculation is robust (cancels normalization errors)

### Phase 1B: ACT DR6 Interface ✅ COMPLETE

#### Gate 1: Convention Verification
- **Verified:** ACT uses **D_L bandpower units**, not raw C_L
- χ²(raw C_L) = 1576 (impossible)
- χ²(D_L = L(L+1)C_L/(2π)) = 27.04 (plausible for 10 bins)

#### Gate 2: Likelihood Implementation
- **Verified:** Manual χ² calculation matches official `generic_lnlike` exactly
- Absolute difference: < 10⁻¹⁰
- Hartlap correction applied by ACT package (confirmed)

#### Gate 3: Band-by-band Pulls
- Pulls up to 3.9σ in specific bins
- Not a code bug: Planck 2018 template vs ACT fiducial differences
- Reduced χ² = 2.7 reflects known Planck/ACT lensing tension

---

## Phase 2: Fiducial Likelihood ✅ CANDIDATE

### Primary Result (Fixed σ₈ today)

| Quantity | Value |
|----------|-------|
| **G1/ΛCDM mean power ratio (ℓ=40–1000)** | **1.0325** |
| **Lensing amplitude enhancement** | **+3.3%** |
| χ² (ΛCDM, Planck template) | 27.04 |
| χ² (G1 m=34) | 20.43 |
| **Δχ² (G1 - ΛCDM)** | **-6.60** |

### Amplitude Scan Results

| Quantity | Value |
|----------|-------|
| Best-fit A for our Planck template | A_hat = 1.092 ± 0.028 |
| ACT official A_lens | 1.013 ± 0.023 |
| Difference | 0.079 (~2.8σ) |

**Interpretation:** Our Planck 2018 template and ACT's official
fiducial cosmology differ slightly. This is physical/systematic
tension, not a code bug.

### Normalization Mode Clarification

This result uses **FIXED σ₈ TODAY** normalization:
- D_G1(z=0) = D_LCDM(z=0)
- G1 has enhanced growth at early times (z > 1)
- Lensing kernel averages over this enhanced growth → +3.3% power

This is **NOT** the fixed-primordial normalization from Phase 1
(which gave R_L = 0.57–0.80). Both results are internally consistent;
they just answer different questions.

### Caveats (Required for Any Paper Claim)

1. **FIXED COSMOLOGY:** All parameters fixed at Planck 2018 values
2. **LENSING ONLY:** No primary CMB included
3. **TEMPLATE MISMATCH:** χ² = 27 for ΛCDM indicates it is not a perfect
   fit to ACT lensing data. The Δχ² = -6.6 is relative to this baseline.
4. **NO SYSTEMATICS:** ACT lensing systematic covariance not included
5. **NO PR4:** Planck lensing not yet included

---

## Key Files for Reproducibility

| File | Purpose |
|------|---------|
| `scripts/audit_phase2_final.py` | Full 5-gate closure verification |
| `scripts/run_phase2_final.py` | Official Phase 2 calculation |
| `PHASE2_FIDUCIAL_RESULTS.md` | Science write-up with full caveats |
| `outputs/audit_phase2/band_pulls_audit.csv` | Band-by-band pull audit |
| `outputs/audit_phase2/amplitude_scan.csv` | Amplitude scan results |

---

## Recommendation

**Phase 2 candidate result is ready for scientific interpretation.**

This is not a final claim but an internally verified pipeline result.
The Δχ² = -6.6 is numerically correct given the stated assumptions,
but physical conclusions require full parameter fitting and inclusion
of systematics covariance.

---

## Current Bugs Fixed

| Issue | Status |
|-------|--------|
| D_L vs C_L convention misunderstanding | ✅ Resolved |
| Calibration factor error in Limber | ✅ Fixed |
| Incorrect "Final" status labeling | ✅ Corrected to Candidate |
| S₈ tension claim overreach | ✅ Qualified properly |
| Amplitude mode confusion | ✅ Clarified |
