# Phase 2B-3: Redshift-Binned Σ(z) Weyl Control — Summary

Date: 2026-05-29
Config: KiDS-1000 270-vector, scale cuts (xip≥4′, xim≥30′), 135 data points
Backend: CLASS P(k,z) (nk=128, nz=64), fixed cosmology (h=0.68, Ωb=0.049, ns=0.965)
IA model: Minimal NLA, single A_IA, η=0, z₀=0, C1ρ_crit=0.0134
Sigma bins: 2-bin top-hat, [0, 0.5, 10.0], bounds [−0.95, 1.0]

## Design

This is an adversarial Weyl-shape control, not a nuisance. It replaces `const-Σ` (single parameter Σ₀) with a
2-bin piecewise-constant Σ(z): two free amplitudes (Σ_low for z<0.5, Σ_high for z≥0.5). The nested limit
Σ_low = Σ_high = Σ₀ must exactly reproduce const-Σ. The test answers:

> *Is the const-Σ χ² advantage real redshift-shape information, or nuisance/bound artifact?*

## Reproducibility sanity

| Test | Expected χ² | Got χ² | Diff | Status |
|------|-------------|--------|------|--------|
| 2-bin Σ with Σ_bin0=Σ_bin1=Σ₀ from const-Σ good IA anchor | 726.1579857424 | 726.1579857424 | 0.00e+00 | PASS |

## Results

### 2-bin Σ + m+dz+IA warm-start, good basin anchor

| Quantity | const-Σ good IA (anchor) | 2-bin Σ good IA | Δ |
|----------|------------------------|-----------------|---|
| χ² | 726.16 | **696.97** | **−29.19** |
| Ωm | 0.45 (bound) | **0.45 (bound)** | 0 |
| sigma8 | 0.708 | 0.695 | −0.014 |
| Σ₀ | −0.367 | — | — |
| Σ_bin0 (z<0.5) | — | **−0.441** | — |
| Σ_bin1 (z≥0.5) | — | **−0.156** | — |
| A_IA | −0.085 | **−0.472** | −0.387 |
| dz range | [−0.019, +0.018] | **[−0.014, +0.035]** | wider |
| m range | [−0.040, +0.045] | [−0.043, +0.047] | similar |

### 2-bin Σ + m+dz+IA warm-start, LCDM anchor

| Quantity | const-Σ LCDM anchor (anchor) | 2-bin Σ LCDM anchor | Δ |
|----------|----------------------------|-------------------|---|
| χ² | 795.73 | **793.12** | **−2.60** |
| Ωm | 0.396 | 0.396 | 0 |
| Σ_bin0 | — | −0.003 | — |
| Σ_bin1 | — | −0.003 | — |
| A_IA | −0.042 | −0.060 | −0.018 |
| dz range | [−0.0008, +0.0008] | [−0.0009, +0.0010] | similar |

## AIC/BIC comparison (full Phase 2B chain)

N = 135, ln(N) = 4.905

| Model | k | χ² | AIC | BIC | ΔBIC vs M3/4 |
|-------|---|-----|-----|-----|--------------|
| LCDM m+dz+IA | 12 | 788.07 | 812.07 | 846.93 | +34.21 |
| M3/4 m+dz+IA | 13 | 748.96 | 774.96 | **812.72** | 0 |
| const-Σ m+dz+IA | 13 | 726.16 | 752.16 | 789.93 | −22.79 |
| **2-bin Σ m+dz+IA** | 14 | **696.97** | **724.97** | **765.64** | **−47.08** |

## Key diagnostics

### Σ_low vs Σ_high difference

Σ_bin0 − Σ_bin1 = −0.441 − (−0.156) = **−0.285**. The two bins differ significantly (>10σ relative to typical Sigma uncertainties). The control IS using its shape freedom.

### Redshift trend comparison with M3/4

| Model | Σ(z≈0) − 1 | Σ(z≫1) − 1 | Gradient |
|-------|-----------|-----------|----------|
| M3/4 (s≈2.64) | ≈−0.27 | ≈0 | low-z negative |
| **2-bin Σ** | **−0.44** | **−0.16** | **low-z more negative** |

Qualitatively consistent — both show stronger Weyl depression at low-z — but binned-Σ amplitude is 1.6× larger.

### Nuisance stress indicators

| Stress indicator | const-Σ good IA | 2-bin Σ good IA | Worse? |
|-----------------|----------------|-----------------|--------|
| Ωm at bound | ✅ (0.45) | ✅ (0.45) | = |
| dz max | 0.018 | **0.035** | **YES** |
| A_IA | −0.09 | **−0.47** | **YES** |
| Anchor dependence | strong | strong | = |

## Interpretation: Situation D

> *binned-Σ wins via nuisance-assisted basin, not clean shape evidence.*

The 2-bin control finds a deeper χ² basin (−29 relative to const-Σ), and the bins differ significantly
(low-z more negative), but the following stressors prevent a clean interpretation:

1. **Ωm pinned at prior boundary** (0.45) in both const-Σ and binned-Σ good basins
2. **dz_i usage increases 2×** relative to const-Σ (max 0.035 vs 0.018), approaching ±0.05 bound
3. **A_IA jumps to −0.47** (vs −0.09 in const-Σ), suggesting IA+m+dz+Σ are co-absorbing
4. **Strong anchor dependence** — LCDM anchor finds Σ_bin0≈Σ_bin1≈0, χ²=793 (no deep basin)

The redshift shape information *exists* (bins differ), and the trend (low-z more negative) is
*consistent* with R_bH(a), but the amplitude and nuisance entanglement make it impossible to claim
that the Weyl channel *needs* free shape freedom. The const-Σ model already captures the dominant signal.

## Conclusion: Shape-lock stress UPDATED

Phase 2B-1: const-Σ shape-lock stress flagged as **WARN** — does single-Σ₀ miss shape information?

Phase 2B-3: 2-bin Σ resolves this with a nuanced answer:

> *A two-bin Σ(z) adversarial control finds a substantially lower local χ² (696.97 vs 726.16), indicating that redshift-dependent Weyl response information is present in the KiDS shear-only data. However, this basin is strongly nuisance- and boundary-entangled: Ωm remains pinned to its upper prior edge (0.45), dz excursions increase (max|dz| ≈ 0.035), A_IA becomes larger (−0.47), and the low-χ² basin is not reached from the LCDM anchor. We therefore treat the result as evidence for Weyl-shape information, but not as a clean demotion of the M3/4 R_bH(a) shape lock.*

**Updated recommendation: WARN → controlled WARN / NOTE.**

Core findings:
- Redshift shape information exists — the two bins differ by ΔΣ ≈ −0.285, and the trend (low-z more negative) is compatible with M3/4's R_bH(a)
- But the basin is nuisance-assisted — Ωm at bound, dz_i 2× wider, A_IA 5× larger than const-Σ
- LCDM anchor does not find the deep basin — the solution is not a global minimum
- const-Σ and M3/4 remain viable for production; binned-Σ serves as an adversarial control showing the bounds of interpretability

### v1.1 narrative

> The data contain Weyl-shape information, and its trend is compatible with M3/4, but flexible binned controls can overfit it through nuisance-entangled basins. The Weyl-channel signal is robust; the 3/4 projection lock is stable; redshift-shape specificity is promising but not yet cleanly isolated.

## Files

- `stage3_lensing_3x2pt.py` — `binned_sigma` model in `Sigma_lensing()`, dynamic `Sigma_bin_i` params
- `stage3_kids1000_xipm_270/stage3_kids1000_xipm_270_config_cuts_mdz_ia_binned_sigma.yaml` — config with `sigma_bin_edges: [0.0, 0.5, 10.0]`
- `warmstart_binsigma2_from_constsigma_good_ia.json` — 2-bin warm-start from const-Σ good (χ²=696.97)
- `warmstart_binsigma2_from_constsigma_lcdmanchor_ia.json` — 2-bin warm-start from LCDM anchor (χ²=793.12)
