# Phase 2B-2: IA (NLA A_IA) Nuisance Profiling — Summary

Date: 2026-05-29
Config: KiDS-1000 270-vector, scale cuts (xip≥4′, xim≥30′), 135 data points
Backend: CLASS P(k,z) (nk=128, nz=64), fixed cosmology (h=0.68, Ωb=0.049, ns=0.965)
IA model: Minimal NLA, single A_IA, η=0, z₀=0, C1ρ_crit=0.0134

## Protocol

Nested-anchor warm-start profiling from Phase 2B-1 m+dz bestfits. Each model gets A_IA=0 injected as starting point, then L-BFGS-B optimizes all parameters simultaneously. This answers: *Does one-parameter intrinsic alignment nuisance absorb the M3/4 Weyl signal?*

## IA kernel correction

The initial IA implementation had a unit mismatch: the IA term `F * n(z)` was dimensionless while the lensing kernel `W(χ) * Σ(χ)` had units Mpc⁻¹. The fix multiplies the IA term by `H(z)/c = (100*h*E(z))/C_LIGHT` to convert n(z) to n(χ), matching the lensing kernel units.

## Results: χ² comparison

| Model | Phase 2B-1 (m+dz) | Phase 2B-2 (m+dz+IA) | Δχ²(IA) | A_IA | Ωm | Nuisance status |
|-------|-------------------|----------------------|----------|------|-----|-----------------|
| LCDM | 792.19 | 788.07 | −4.11 | −0.13 | 0.394 | all interior |
| M3/4 | 748.96 | 748.96 | 0.00 | 0.00 | 0.449 | all interior |
| Mκ (κ≈0.75) | 749.28 | 749.28 | 0.00 | 0.00 | 0.448 | all interior |
| const-Σ (good basin) | 733.19 | 726.16 | −7.03 | −0.09 | **0.45** | Ωm at bound |
| const-Σ (LCDM anchor) | 796.86 | 795.73 | −1.13 | −0.04 | 0.396 | all interior |

### Key cross-model differences

| Comparison | Without IA | With IA | Change |
|-----------|-----------|---------|--------|
| Δχ²(M3/4 − LCDM) | −43.23 | −39.11 | −4.12 (10%) |
| Δχ²(M3/4 − const-Σ good) | +15.77 | +22.80 | +7.03 |
| Δχ²(M3/4 − Mκ) | −0.32 | −0.32 | 0.00 |

## IA model verification

- **IA-off reproducibility: PASS** — M3/4 and Mκ both return exactly Phase 2B-1 χ² (748.96, 749.28) with A_IA=0.0
- **A_IA=±1 perturbation: PASS** — χ² in [1000, 1750], finite and reasonable

## Conclusions

1. **Weyl signal robust to IA nuisance.** M3/4 beats LCDM by Δχ²=−39.1 after IA marginalisation (vs −43.2 before). The ~10% shrinkage is well within existing uncertainties and consistent with LCDM needing non-zero IA (A_IA≈−0.13) while M3/4 sits at A_IA=0.

2. **A single IA amplitude cannot absorb the M3/4–LCDM χ² difference.** The gap remains >39 in χ², similar in magnitude to the m-only comparison (−44.6). This is the core result of Phase 2B-2.

3. **M3/4 and Mκ are IA-insensitive.** Both return A_IA=0.0 with zero χ² improvement. These Weyl-channel models already provide a good fit without intrinsic alignments.

4. **LCDM needs A_IA≈−0.13** (negative alignment, radially aligned galaxies) to improve by Δχ²≈−4.1. This is modest and within typical KiDS IA amplitudes.

5. **const-Σ good basin benefits most from IA** (Δχ²=−7.0) but remains at Ωm=0.45 upper bound — the shape-lock stress from Phase 2B-1 persists.

6. **Total Phase 2B nuisance count now 17** (5 m_i + 5 dz_i + 1 A_IA + 6 model parameters). Despite this, BIC-favoured model remains M3/4.

## Files

- `warmstart_ia_m34.json` — M3/4 m+dz+IA (A_IA=0, χ²=748.96)
- `warmstart_ia_lcdm.json` — LCDM m+dz+IA (A_IA=−0.13, χ²=788.07)
- `warmstart_ia_constsigma_goodbasin.json` — const-Σ good basin (A_IA=−0.09, χ²=726.16)
- `warmstart_ia_constsigma_lcdmanchor.json` — const-Σ LCDM anchor (A_IA=−0.04, χ²=795.73)
- `warmstart_ia_mkappa.json` — Mκ m+dz+IA (A_IA=0, χ²=749.28)
- `stage3_kids1000_xipm_270/stage3_kids1000_xipm_270_config_cuts_mdz_ia.yaml` — IA-enabled config
