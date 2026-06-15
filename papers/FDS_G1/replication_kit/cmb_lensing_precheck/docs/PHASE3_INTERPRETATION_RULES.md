# Phase 3 Interpretation Rules — Pre-Registered

**Status**: Frozen. All rules below must be applied before any production-chain result is labelled as a finding.

---

## 1. κ = 3/4 Membership

| Criterion | Verdict | Allowed statement |
|-----------|---------|-------------------|
| 0.75 ∈ 68% HPD of free-κ posterior | `central-compatible` | "0.75 lies within the central 68% highest posterior density interval of the free-κ posterior." |
| 0.75 ∈ 95% HPD but outside 68% | `tail-compatible` | "0.75 lies within the 95% HPD interval but outside the central 68% region." |
| 0.75 outside 95% HPD | `outside-95-HPD` | "0.75 is excluded at 95% HPD by the free-κ posterior → **trigger downgrade audit**." |

**Never claim**: "data measures κ = 3/4" or "data prefers κ = 3/4" from HPD membership alone.

**Current frozen v4 application**: κ = 0.75 is not in the central 68% interval of the
free-κ posterior. It should be reported as tail-compatible, not central-compatible.

---

## 2. Effective Lensing Response α = κq

### 2.1 α Compatibility Test

Compare the locked-α distribution `p(0.75 · q | M_{3/4})` against the free-α distribution `p(κq | M_κ)`.

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Locked median in free 68% HPD | True | `central-compatible` |
| Locked median in free 95% HPD only | True | `tail-compatible` |
| Locked median outside 95% HPD | — | `outside-95-HPD` → audit |
| Locked-α overlap with free 68% HPD | Report as diagnostic | No claim |
| Posterior shift T_α | < 2: normal; 2-2.5: monitor; >2.5: audit | No claim |

### 2.2 α as a Diagnostic Coordinate

α = κq is the most stable cross-seed Weyl diagnostic. Report its distribution in production, but never use it alone to claim Weyl detection or 3/4 preference.

---

## 3. Non-Zero Weyl Response

### 3.1 Point-Null Prohibition

**Never** use `P(κ > 0)` from a continuous posterior to claim Weyl detection. κ = 0 is a boundary point in the prior.

### 3.2 Allowed Test

Weyl preference is established exclusively by:

```
B(M_κ : M_bg)  with a pre-registered threshold
```

or a pre-registered non-zero effect threshold on a well-defined statistic.

### 3.3 Current Diagnostic Description

If `P(κ < 0.05)` is small and the posterior mass is concentrated away from the κ → 0 boundary, the allowed statement is:

> "The posterior mass of the free-κ model is concentrated at non-zero κ, with no evidence of boundary accumulation near κ = 0."

---

## 4. Evidence vs Likelihood Improvement

| Scenario | Allowed conclusion | Prohibited conclusion |
|----------|-------------------|----------------------|
| Z_{3/4} > Z_κ with no Δχ² improvement | "Fixing κ = 3/4 provides effective prediction compression." | "Data measures κ = 3/4." |
| Z_{3/4} > Z_ΛCDM with no Δχ² improvement | "The G1 locked model achieves comparable fit with τ + extended parameterisation, but does not out-predict ΛCDM." | "ACT data supports M_{3/4} over ΛCDM." |
| Z_{3/4} > Z_ΛCDM AND Δχ² improves | "The G1 locked model achieves both improved maximum likelihood and better predictive performance." | (allowed) |

---

## 5. Cross-Seed Tension Scale

For any parameter θ, let `T_θ = |median_seed1 − median_seed2| / pooled_half_width`.

| T_θ | Action |
|-----|--------|
| < 2 | Normal — no action |
| 2.0 – 2.5 | Monitor — flag in diagnostics, do not halt |
| 2.5 – 3.0 | Audit — investigate chain mixing, prior sensitivity |
| ≥ 3.0 | Downgrade hearing — parameter not suitable for constraint claims |

---

## 6. Near-Null q: Boundary Mass

q = 0 (s = 3) is a boundary point. Define `q_near = 0.02` (pre-registered).

| P(q < q_near) | Label |
|---------------|-------|
| ≥ 0.10 | Significant near-null support |
| 0.01 – 0.10 | Finite near-null support |
| < 0.01 | Posterior mass remote from near-null region |

**Never claim**: "q = 0 is excluded" or "q = 0 is supported" from boundary mass alone.

The dynamic-background verdict requires:

```
B(M_bg : ΛCDM)  or  B(M_{3/4} : ΛCDM)
```

---

## 7. Posterior Geometry Warnings

Before claiming any parameter constraint, verify:

| Check | Pass condition |
|-------|----------------|
| Boundary occupancy | < 5% for all parameters |
| Multi-modality | No well-separated peaks > 10% of total mass |
| q-κ degeneracy | Report 2D KDE; do not infer separable constraints from Pearson r alone |
| α stability | Cross-seed T_α < 2 |

---

## 8. Production Convergence Requirements

All production chains must satisfy:

- `R̂ < 1.01` between independent ensembles
- `N_prod > 50 τ_max`
- `bulk ESS > 1000` per parameter
- `tail ESS > 1000` per parameter
- `MC error on F_κ(0.75) < 0.02`

Evidence computation must use the same emulator, priors, and amplitude mode as production chains.

---

## 9. Emulator Spot-Check Gate

Before any production posteriors are used for inference:

```
max |Δχ²_direct − Δχ²_emu| < 0.1
```

on ≥ 50 posterior samples per model, drawn from maximum posterior, median, and 68% region boundary.

---

## 10. Frozen at

```
date: 2026-06-14
emulator: outputs/frozen/v4_act_only/ratio_emulator/  (v4 structured R_bg × R_Weyl)
cache: outputs/emulator_cache/ v3.0 (routing-fixed, model_name=g1de_mkappa)
production: outputs/phase3_production_v4/
evidence: outputs/nested_evidence/act_only_production/ (K=1000, 3 independent UltraNest runs)
closure: max|Δχ²| = 0.068 < 0.1 ✓
evidence correction: |ΔlogZ_corr| < 0.005 for all models
```

Any amendment to these rules must be committed with a dated rationale before being applied.
