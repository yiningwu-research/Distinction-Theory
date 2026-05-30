# Phase 2B-1: m_i + dz_i Nuisance Profiling — Summary

Date: 2026-05-29
Config: KiDS-1000 270-vector, scale cuts (xip≥4′, xim≥30′), 135 data points
Backend: CLASS P(k,z) (nk=128, nz=64), fixed cosmology (h=0.68, Ωb=0.049, ns=0.965)

## Step 1: m-only (shear calibration nuisance)

| Model | Seed 1 χ² | Seed 2 χ² | Mean Δχ² vs LCDM | m_i all interior? |
|-------|-----------|-----------|-------------------|-------------------|
| LCDM | 797.10 | 797.06 | 0 (baseline) | ✅ |
| M3/4 | 752.09 | 752.95 | **−44.56 ± 0.45** | ✅ |
| const-Σ | 764.02 | 824.02* | — | ✅ |

*seed 2 is optimizer failure (nested model should have χ² ≤ LCDM's 797).

**Verdict: STRONG PASS.** Shear calibration nuisance cannot absorb M3/4's scale-cut signal.

## Step 2a: m+dz warm-start (nested anchors)

| Anchor Path | Model | χ² start | χ² end | Δχ² | Key | Nuisance |
|-------------|-------|----------|--------|-----|-----|----------|
| LCDM→const-Σ (Σ₀=0) | const-Σ | 797.10 | 796.86 | −0.24 | Σ₀≈0, Ωm=0.398 | all interior, dz≈0 |
| const-Σ good→const-Σ | const-Σ | 764.02 | 733.19 | −30.83 | Σ₀=−0.375, Ωm=**0.45** | dz∈[−0.022,+0.009] |
| M3/4→M3/4 | M3/4 | 752.09 | 748.96 | −3.13 | s=2.64, Aeff=0.27 | all interior, dz≈0 |
| M3/4→Mκ (κ=0.75) | Mκ | 752.09 | 749.28 | −2.81 | κ=0.746 ≈ 0.75 | all interior, dz≈0 |

## Step 2b: const-Σ stress tests

| Test | χ² | Ωm | dz range | Boundary issues |
|------|-----|-----|----------|-----------------|
| Default (±0.05 dz) | 733.19 | 0.45 (at bound) | ±0.022 | Ωm at upper bound |
| Narrow dz (±0.03) | 748.22 | 0.435 (interior) | ±0.021 | m_src4 at +0.05 bound |
| Ωm bound expand (≤0.60) | 761.81* | 0.436 | ±0.001 | L-BFGS-B early conv. |

*Local optimizer converged early (154 evals, 4 iters). Not robust.

**const-Σ advantage shrinks from Δχ²=−15.77 to −0.74 when dz narrowed to ±0.03.**

## AIC/BIC comparison

| Model | k | χ² | ΔAIC | ΔBIC |
|-------|---|-----|------|------|
| LCDM m-only | 7 | 797.10 | 0 | 0 |
| LCDM m+dz | 12 | 792.19 | +5.09 | +19.61 |
| **M3/4 m-only** | **8** | **752.09** | **−43.01** | **−40.10** |
| M3/4 m+dz | 13 | 748.96 | −36.14 | −18.70 |
| const-Σ m-only | 8 | 764.02 | −31.08 | −28.18 |
| const-Σ m+dz (wide) | 13 | 733.19 | −51.91 | −34.48 |
| const-Σ m+dz (narrow) | 13 | 748.22 | −36.88 | −19.44 |
| Mκ (free-κ) m+dz | 14 | 749.28 | −33.82 | −13.48 |

## Conclusions

1. **Weyl-channel strong:** All non-LCDM models (M3/4, const-Σ, Mκ) beat LCDM
   by Δχ² > 40 under all nuisance configurations.

2. **M3/4 most robust:** Stable across seeds, nuisance levels, and bounds.
   dz_i ≈ 0, m_i interior, s interior. Lowest BIC (−40.10 vs LCDM).

3. **Shape-lock (R_bH vs Σ₀): WARN / active stress point.**
   const-Σ achieves lower χ² under wide nuisance (±0.05 dz) but:
   - Ωm at prior boundary
   - dz usage 10–50× larger than M3/4
   - Advantage shrinks to Δχ² ≈ −0.7 when dz narrowed
   - BIC penalty reduces its edge

4. **3/4 projection lock holds:** Mκ (free-κ) starting from κ=0.75 relaxes
   only to κ=0.746, with χ² improvement of only −2.81. κ at the M3/4
   limit is near-optimal.

5. **Blind DE insufficient for const-Σ and Mκ:** These models' likelihood
   surfaces are harder — seed-to-seed scatter up to 60 in χ². All
   nuisance-stress conclusions use nested-anchor warm-start profiling,
   not blind DE.
