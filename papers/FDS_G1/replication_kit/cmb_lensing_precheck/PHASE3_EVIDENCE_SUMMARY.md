# G1 Lensing Precheck — Phase 3 Evidence Summary

**Date**: 2026-06-13
**Data**: ACT DR6 lensing only (`act_baseline`)
**Sampler**: UltraNest ReactiveNestedSampler, K=1000 live points, 3 independent runs
**Correction gate**: All models |ΔlogZ_corr| < 0.005 (threshold: 0.05)

---

## Evidence Table

| Model | Parameters | logZ | Scatter | ΔlogZ (vs ΛCDM) | Bayes Factor | Verdict |
|-------|-----------|------|---------|-----------------|---------------|---------|
| ΛCDM | Ω_m, h, lnAs | -12.23 | 0.05 | 0 | 1 | Best |
| g1_bg | +q | -12.37 | 0.06 | -0.14 | 1.2 | Indistinguishable |
| g1_mκ | +q, κ | -13.09 | 0.04 | -0.86 | 2.4 | Mildly disfavored |
| g1_m34 | +q (κ=3/4) | -13.61 | 0.05 | -1.38 | 4.0 | Moderately disfavored |

---

## Interpretation

### Bayes Factor Scale

| |ΔlogZ| | BF | Interpretation |
|---------|-----|----------------|
| < 0.5 | 1.0 – 1.6 | Inconclusive |
| 0.5 – 1.0 | 1.6 – 2.7 | Mild preference |
| 1.0 – 2.3 | 2.7 – 10 | Moderate preference |
| > 2.3 | > 10 | Strong preference |

### Model-by-Model

**ΛCDM vs g1_bg (BF = 1.2)**: Inconclusive. ACT evidence cannot distinguish between ΛCDM and a G1 model with background deformation only. The extra q parameter carries essentially zero Occam penalty because the ACT likelihood is broad enough in the q-direction that the prior volume loss is negligible.

**ΛCDM vs g1_mκ (BF = 2.4)**: Mild preference for ΛCDM. Adding both q and κ as free parameters is penalized. The ACT data does not require Weyl freedom.

**ΛCDM vs g1_m34 (BF = 4.0)**: Moderate preference for ΛCDM. Fixing κ = 3/4 restricts the model to a region that, while posterior-compatible, does not achieve sufficient average predictive performance to offset the prior volume cost of the extra q parameter.

**g1_mκ vs g1_m34 (BF = 1.7)**: Inconclusive. The free-κ model has slightly higher evidence than the locked branch, but the difference is too small to constitute a firm ranking. This means the locked model does not gain from "parameter compression" — the fixed value 3/4 is not an efficient summary of the free posterior.

---

## Stability

- **Run-to-run scatter**: All < 0.06 (threshold: 0.15) ✓
- **Evidence-weighted correction**: All |ΔlogZ_corr| < 0.005 ✓
- **ACT+PR4 cross-check**: Relative rankings preserved exactly (ΔΔ < 0.06) ✓

---

## Bottom Line

**ACT lensing alone provides a stable, moderate (BF ≈ 4) Bayesian penalty for the exact 3/4 lock.** This is not a rejection — the locked model remains viable — but it is a clear signal that CMB lensing does not reward the Weyl prediction. The background deformation alone fits as well as ΛCDM, but neither Weyl form (free or locked) improves upon it.
