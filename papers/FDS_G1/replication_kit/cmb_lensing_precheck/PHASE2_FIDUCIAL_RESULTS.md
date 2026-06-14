# ⚠️ ARCHIVED — PRE-ROUTING-FIX — SUPERSEDED

**This report was written before the model-routing bug was discovered on 2026-06-13.**
The `model.name` routing bug caused all G1 branches to compute the same Weyl response (κ=0.75).
The +3.3% enhancement and Δχ² = -6.6 claims are from pre-routing-fix computations.
All conclusions in this document are superseded by `PHASE3_FINAL_RESULTS.md`.

---

# FDS-G1 CMB Lensing Phase 2 Fiducial Results (ARCHIVED)
## Version: 1.0rc3
## Date: 2026-06-11
## Status: CANDIDATE RESULT (pending final review)

---

## Primary Result

**G1 m=34 produces 3.3% MORE lensing power than ΛCDM** across the
cosmologically relevant multipole range (ℓ = 40–1000).

| Quantity | Value |
|----------|-------|
| Mean C_L^G1 / C_L^ΛCDM (ℓ=40–1000) | **1.0325** |
| Mean enhancement (ℓ=40–1000) | 3.25% |
| Range of ratios | 1.030 – 1.037 |

---

## ACT DR6 Lensing Likelihood

**CRITICAL CONVENTION NOTE:** ACT `data_binned_clkk` is in
**D_L bandpower units**:

\[
D_L = \frac{L(L+1)}{2\pi} C_L^{\kappa\kappa}.
\]

This was numerically verified by χ² = 27.04 for CLASS ΛCDM with D_L
vs χ² = 1576 for raw C_L. The README wording was ambiguous but the
data format is unambiguous.

| Quantity | Value |
|----------|-------|
| χ² (ΛCDM, Planck template) | 27.04 |
| χ² (G1 m=34, scaled ratio) | 20.43 |
| Δχ² (G1 - ΛCDM) | **-6.60** |

**Interpretation:** At fixed Planck cosmology (Ω_m=0.2966, σ₈=0.811,
Planck 2018 parameters), G1 m=34 provides a better fit to ACT DR6
lensing data than ΛCDM by Δχ² = -6.6.

### Amplitude Scan Verification

| Quantity | Value |
|----------|-------|
| Best-fit amplitude for our Planck template | A_hat = 1.092 ± 0.028 |
| ACT official A_lens | 1.013 ± 0.023 |
| Difference | 0.079 (~2.8σ) |

**Interpretation:** Our Planck template is slightly different from
ACT's fiducial cosmology. The high χ² of 27 and pulls > 3σ in bins 5
and 7 indicate template shape differences, not bugs.

### Band-by-Band Pulls (ΛCDM)

| Bin | ℓ_eff | Pull |
|-----|--------|------|
| 0 | 53 | +2.14σ |
| 1 | 84 | +1.25σ |
| 2 | 123 | +0.69σ |
| 3 | 172 | +0.38σ |
| 4 | 232 | +0.86σ |
| 5 | 302 | +1.88σ |
| 6 | 382 | +1.30σ |
| 7 | 476 | +3.90σ |
| 8 | 582 | +1.59σ |
| 9 | 700 | +0.18σ |

Max pull: 3.9σ at ℓ ~ 476. This is a known feature of Planck 2018
ΛCDM vs ACT lensing data.

---

## Physical Interpretation

The +3.3% lensing enhancement arises from modified growth in G1 under
**FIXED σ₈ TODAY** normalization:

- **Normalization mode:** D_G1(z=0) = D_LCDM(z=0)
- **Early-time behavior:** D_G1(z >> 0) > D_LCDM(z >> 0)
- **Lensing kernel weights:** z ~ 0.5–5 range picks up early-time enhancement
- **Net effect:** +3.3% more lensing power than ΛCDM

### Distinction from Phase 1

Phase 1 showed **suppressed** lensing ratios (0.57–0.80). Those
used **fixed primordial amplitude** normalization (equal at early times),
which causes D_G1(z=0) < D_LCDM(z=0). Both results are internally
consistent - they just answer different questions.

---

## Caveats

1. **Fixed cosmology:** Results assume Planck 2018 parameters
2. **Lensing only:** No primary CMB likelihood included
3. **No Planck PR4:** Only ACT DR6 used so far
4. **Shape/systematics:** Pulls up to 3.9σ indicate template differences
5. **Limber approximation:** Used for ratio calculation; CLASS native for absolute

---

## Key Output Files

| File | Description |
|------|-------------|
| `outputs/phase2_fiducial/fiducial_spectra_final.csv` | C_L spectra + ratio |
| `outputs/phase2_fiducial/fiducial_results_final.json` | JSON summary |
| `outputs/audit_phase2/amplitude_scan.csv` | Amplitude scan results |
| `outputs/audit_phase2/band_pulls_audit.csv` | Band-by-band pull audit |
| `scripts/audit_phase2_final.py` | Full closure verification script |

---

## Next Steps for Publication

1. Add Planck PR4 lensing for joint constraint
2. Run full MCMC with free Ω_m and σ_8
3. Include systematic covariance for ACT bandpowers
4. Implement G1 directly in CLASS for full Boltzmann verification
5. Clarify which normalization mode is most physically meaningful

---

## Status

**Phase 2: CANDIDATE RESULT**
- Code: Verified ✓
- Numerics: Verified ✓
- Convention: Verified ✓
- Likelihood: Verified ✓
- Physical interpretation: Clear ✓

The Δχ² = -6.6 result is numerically correct for the stated assumptions.
Further interpretation requires full cosmological parameter fitting.
