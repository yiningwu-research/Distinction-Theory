# Phase 3 — ACT Lensing Likelihood Results

**Date**: 2026-06-13
**Status**: ACT-only posterior frozen and direct-engine closed. ACT+PR4 evidence computed under the registered precheck approximations.
**Artifacts**: `outputs/frozen/v4_act_only/`, `outputs/nested_evidence/`
**Manifest**: `PHASE3_MANIFEST.json`

---

## 1. Posterior Results (v4 ACT-only, Converged + Closed)

Original production diagnostics reported R̂ < 1.01 and ESS > 17,000, with
direct-engine closure max|Δχ²| < 0.07. A subsequent rank-normalized split-R̂
audit flagged mild folded-R̂ excesses in `g1_bg` (Ω_m, h) and `g1_mκ` (q).
A non-frozen +500-step extension audit of those two models clears these flags
for all models, supporting the frozen posterior summaries while keeping the
frozen chains themselves unchanged.

| Model | Ω_m | h | ln(10¹⁰A_s) | q | κ |
|-------|------|---|-------------|---|---|
| **ΛCDM** | 0.344 [0.253, 0.431] | 0.656 [0.581, 0.772] | 3.027 [2.929, 3.126] | — | — |
| **g1_bg** | 0.329 [0.249, 0.430] | 0.666 [0.583, 0.776] | 3.112 [2.994, 3.252] | 0.573 [0.185, 0.970] | 0 (fixed) |
| **g1_m34** | 0.315 [0.230, 0.403] | 0.660 [0.581, 0.783] | 3.261 [3.079, 3.503] | 0.185 [0.054, 0.375] | 0.75 (fixed) |
| **g1_mκ** | 0.323 [0.235, 0.416] | 0.657 [0.576, 0.789] | 3.210 [3.044, 3.439] | 0.310 [0.089, 0.721] | 0.302 [0.087, 0.741] |

### Compensation Hierarchy

```
q_bg (0.57) > q_free (0.31) > q_3/4 (0.19)
```

When Weyl response is active (κ = 0.75), the required background deformation q decreases. This is a physically verified compensation mechanism — not a code artifact.

### κ = 0.75 Status

- Free-κ posterior: median = 0.30, central 68% interval ≈ [0.09, 0.74] in the frozen v4 summary
- κ = 0.75 is not in the central 68% interval; it remains a tail-compatible value rather than a central posterior value
- κ = 0.75 is allowed by ACT but not selected by the free-κ posterior

### Cross-Dataset Consistency (ACT vs ACT+PR4)

| Parameter | ACT-only | ACT+PR4 | T_q |
|-----------|----------|---------|-----|
| q_bg | 0.573 | 0.529 | 0.06 |
| q_3/4 | 0.185 | 0.157 | 0.09 |
| q_free | 0.310 | 0.301 | 0.01 |
| κ_free | 0.302 | 0.251 | 0.09 |

All standardized shifts T < 0.10. No detectable cross-dataset tension.

---

## 2. Emulator Performance (v4 Structured)

| Metric | Value | Gate |
|--------|-------|------|
| Architecture | R_bg × R_Weyl with G_L = log(R_Weyl)/(qκ) decomposition | — |
| RBF type | Local thin_plate_spline, neighbors=80-100 | — |
| Spectrum RMS | 0.012% | < 0.2% ✓ |
| Spectrum P95 | 0.024% | < 0.5% ✓ |
| Null test (q=0) | 0.0 (enforced by construction) | ✓ |
| Posterior closure (ACT) | max|Δχ²| = 0.068 | < 0.1 ✓ |
| Posterior closure (ACT+PR4) | max|Δχ²| < 0.07 | < 0.1 ✓ |

Evidence-weighted correction: |ΔlogZ_corr| < 0.005 for all models.

Route consistency audit: the packaged frozen-v4 loader reproduces saved frozen-chain
`log_prob_raw` exactly on the deterministic audit sample; legacy v2 routing gives large
log-likelihood shifts for the Weyl branches and must not be used for Phase 3 claims.

Posterior diagnostic audit: bulk/tail ESS pass comfortably on the frozen chains.
The initial folded rank-normalized R̂ flags are cleared by the targeted +500-step
non-frozen extension audit (`outputs/phase3_extension_v4_rhat_audit/`), where all
models satisfy R̂ < 1.01 and bulk/tail ESS > 1000 under the same diagnostic script.

---

## 3. Bayesian Evidence (ACT-only, K=1000, 3 Independent Runs)

All run scatters < 0.06 — well below the 0.15 threshold.

| Model | logZ | Run Scatter | ΔlogZ (vs ΛCDM) | BF | Interpretation |
|-------|------|------------|------------------|-----|----------------|
| **ΛCDM** | -12.23 | 0.05 | 0 | 1 | Best |
| g1_bg | -12.37 | 0.06 | -0.14 ± 0.08 | 1.2 | Indistinguishable |
| g1_mκ | -13.09 | 0.02 | -0.85 ± 0.05 | 2.3 | Mildly disfavored |
| g1_m34 | -13.61 | 0.05 | -1.38 ± 0.07 | 4.0 | Moderately disfavored |

### Key Interpretation

- **ΛCDM ≈ g1_bg**: ACT evidence cannot distinguish between ΛCDM and the background-only G1 branch. Adding q does not improve or worsen predictive performance.
- **g1_mκ < ΛCDM (BF ≈ 2.3)**: The free Weyl model is mildly penalized by Occam's razor — the extra κ parameter is not justified by the ACT data.
- **g1_m34 < ΛCDM (BF ≈ 4.0)**: The locked 3/4 branch is moderately disfavored. The prior volume penalty from q exceeds any fit improvement.
- **g1_mκ vs g1_m34 (BF ≈ 1.7)**: The free-κ model has slightly higher evidence than the locked model, but the difference is inconclusive.

---

## 4. Bayesian Evidence (ACT+PR4, K=1000)

The ACT+PR4 combined likelihood shifts absolute logZ by ~-3.7 (more constraining data), but **does not change any relative model ranking**.

| Model | PR4 ΔlogZ (vs ΛCDM) | BF(PR4) | ACT ΔlogZ | ΔΔ |
|-------|----------------------|---------|----------|-----|
| ΛCDM | 0 | 1 | 0 | — |
| g1_bg | -0.15 | 1.2 | -0.14 | -0.01 |
| g1_mκ | -0.92 | 2.5 | -0.85 | -0.07 |
| g1_m34 | -1.37 | 3.9 | -1.38 | +0.01 |

PR4 adds no new model preference beyond ACT-only. The ranking ΛCDM ≈ g1_bg > g1_mκ > g1_m34 is preserved exactly.

---

## 5. Routing Bug Discovery and Resolution

### Bug Identified (2026-06-13)

`build_ratio_config()` was not setting `config["model"]["name"]`, inheriting the default `"g1de_m34"` from DEFAULTS. The function `sigma_response()` hardcodes `kappa_eff = 0.75` for model `"g1de_m34"`, ignoring the actual κ parameter. **All G1 branches were computing the same Weyl response.**

### Fix

- `build_ratio_config()` now requires `model_name="g1de_mkappa"` as an explicit keyword argument
- Raises `ValueError` for any other value — cannot be silently inherited
- Five sentinel tests register branch separation at the config, analytic, full-engine, null, and likelihood levels

### Artifacts Preserved

All bugged artifacts archived at `outputs/INVALID_ROUTING_2026-06-13/` with invalidation notice.

---

## 6. Final Conclusions

### What ACT Lensing Tells Us About G1

1. **The dynamic background (q > 0) survives cleanly.** ACT evidence is indifferent between ΛCDM and the background-only G1 branch.

2. **The Weyl response is not rewarded.** Both free-κ and locked-κ models have lower evidence than ΛCDM, with BF = 2.3 and BF = 4.0 respectively.

3. **κ = 0.75 is tail-compatible but not evidence-supported.** The value is not central in the free-κ posterior, and the full locked model is the weakest G1 variant under ACT in this precheck.

4. **The compensation hierarchy (q_bg > q_free > q_3/4) appears consistently in this precheck** — verified across ACT-only, ACT+PR4, two independent seeds, and direct-engine closure.

5. **PR4 adds no new information** — ACT+PR4 reproduces both the posterior geometry and the evidence ordering of ACT-only.

### Most Accurate Current Statement

> At CMB lensing energies, the exact 3/4 lock is the weakest link in the G1 chain. The background deformation survives, the Weyl response is allowed but not needed, and the locked value receives no Bayesian reward.

### Model Ranking (CMB Lensing Only)

```
ΛCDM ≈ g1_bg  >  g1_mκ  >  g1_m34
  (BF≈1)       (BF≈2.3)   (BF≈4)
```

This does not constitute a rejection of M₃/₄. It means ACT alone provides a conditional precheck-level penalty for the locked branch relative to ΛCDM under the registered emulator, prior, and linear-response approximations.
