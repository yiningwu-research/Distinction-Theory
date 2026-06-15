# Phase Execution Status

**Last Updated**: 2026-06-14
**Current Active Phase**: Phase 3 (complete — posterior frozen, evidence computed)

---

## Version Gates

| Version | Requirement | Status | Completed |
|---------|-------------|--------|-----------|
| **v0.1.0** | Analytic benchmark fully verified | ✅ COMPLETE | 2026-06-11 |
| **v0.2.0** | CLASS transfer/power backend validated | ✅ COMPLETE | 2026-06-11 |
| **v0.3.0** | Official ACT/PR4 likelihood validated | ✅ COMPLETE | 2026-06-11 |
| **v4.0.0** | Phase 3 ACT-only posterior frozen | ✅ COMPLETE | 2026-06-13 |
| **v1.4** | Full D11 Boltzmann + primary CMB refit | ⏳ Pending | — |

**G1 main archive stays at v1.3 until Phase 5 completion.**

---

## Phase Status

### ✅ Phase 0: Baseline Tag — COMPLETE

- Git tag: `cmb-lensing-precheck-v0.1.0`
- Benchmark reproduced at < 1e-15 numerical precision
- All 8 tests passing

### ✅ Phase 1A: CLASS Backend Validation — COMPLETE

- CLASS/Limber agreement verified: Weighted RMS < 0.09%
- Script: `scripts/run_class_validation.py`
- Output: `outputs/class_validation/v0.2.0/`

### ✅ Phase 1B: ACT Forward-Operator Validation — COMPLETE

- ACT DR6 v1.2 data loaded and validated
- D_L bandpower convention confirmed
- χ² equivalence verified
- Script: `scripts/run_act_validation.py`

### ✅ Phase 2: Fiducial ACT/PR4 Run — COMPLETE

- Four-point model comparison completed
- Convention closure verified
- **Note**: Pre-routing-fix results superseded by Phase 3. See `PHASE3_FINAL_RESULTS.md` for authoritative results.

### ✅ Phase 3: Posterior Inference & Bayesian Evidence — COMPLETE

#### 3a. Emulator Development (v4 Structured)
- G_L = log(R_Weyl)/(qκ) decomposition with local RBF
- RMS = 0.012%, P95 = 0.024%
- Null enforcement by construction
- Artifact: `outputs/frozen/v4_act_only/`

#### 3b. ACT-only Posterior (Frozen)
- Original production diagnostics passed: R̂ < 1.01, ESS > 17,000
- Rank-normalized split-R̂ audit: initial mild folded-R̂ flags in g1_bg (Ω_m, h) and g1_mκ (q) cleared by targeted non-frozen +500-step extension audit
- Direct-engine closure: max|Δχ²| = 0.068 < 0.1
- Compensation hierarchy: q_bg > q_free > q_3/4
- κ = 0.75 tail-compatible, not central in the 68% interval
- Artifact: `outputs/frozen/v4_act_only/chains/`

#### 3c. ACT+PR4 Posterior
- Cross-dataset consistency confirmed: all T_q < 0.10
- Compensation hierarchy preserved

#### 3d. Bayesian Evidence (UltraNest, K=1000, 3 independent runs)
- ΛCDM ≈ g1_bg (BF = 1.2) — indistinguishable
- ACT-only audit: all four models have 3/3 complete runs
- g1_mκ < ΛCDM (BF = 2.3) — mildly disfavored
- g1_m34 < ΛCDM (BF = 4.0) — moderately disfavored
- ACT+PR4 preserves same ranking exactly
- Artifact: `outputs/nested_evidence/`

#### 3e. Routing Bug Discovery & Resolution
- `model.name` inherited `g1de_m34`, forcing κ=0.75 for all branches
- Fixed: `build_ratio_config()` requires explicit `model_name` parameter
- All bugged artifacts archived at `outputs/INVALID_ROUTING_2026-06-13/`

### ⏳ Phase 4: Joint Low-z + CMB Lensing — PENDING

### ⏳ Phase 5: Full D11 Boltzmann + Primary CMB — PENDING

---

## Key Artifacts

| Artifact | Path |
|----------|------|
| Frozen v4 emulator + chains | `outputs/frozen/v4_act_only/` |
| ACT-only production chains | `outputs/phase3_production_v4/` |
| ACT+PR4 production chains | `outputs/phase3_production_v4_pr4/` |
| Nested evidence results | `outputs/nested_evidence/act_only_production/` |
| Phase 3 consistency audit | `outputs/phase3_consistency_audit.json` |
| Phase 3 posterior diagnostics | `outputs/phase3_posterior_diagnostics.json` |
| Phase 3 extension R-hat audit | `outputs/phase3_extension_v4_rhat_audit/` |
| Phase 3 reproducibility manifest | `PHASE3_MANIFEST.json` |
| Bugged artifacts archive | `outputs/INVALID_ROUTING_2026-06-13/` |
| Final results | `PHASE3_FINAL_RESULTS.md` |
| Evidence summary | `PHASE3_EVIDENCE_SUMMARY.md` |
| Interpretation rules | `docs/PHASE3_INTERPRETATION_RULES.md` |
