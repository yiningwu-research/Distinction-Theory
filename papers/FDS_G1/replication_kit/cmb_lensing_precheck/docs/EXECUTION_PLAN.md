# FDS-G1 CMB-Lensing Precheck: Execution Plan

**Status**: Phase 0 complete (baseline tagged). Science execution initiated.

---

## 🏷️ Baseline Tag

```bash
git tag -a cmb-lensing-precheck-v0.1.0 \
  -m "Integrated pre-production CMB-lensing stress-test"
```

**Current**: v0.1.0 - Analytic pre-production benchmark (verified, reproducible)

---

## 📋 Version Gates

| Version | Requirement | Status |
|---------|-------------|--------|
| **v0.1.0** | Analytic benchmark fully verified | ✅ COMPLETE |
| **v0.2.0** | CLASS transfer/power backend validated | Phase 1 |
| **v0.3.0** | Official ACT/PR4 likelihood validated | Phase 2 |
| **v1.4** | Full D11 Boltzmann + primary CMB refit | Phase 5 |

**Note**: G1 main archive remains at v1.3 until Phase 5 completion.

---

## 🚀 Execution Phases

### Phase 0: Baseline Tag (✅ COMPLETE)

- Tag: `cmb-lensing-precheck-v0.1.0`
- Benchmark reproduced at < 1e-15 numerical precision
- All 8 tests passing

---

### Phase 1A: CLASS Transfer/Power Backend Validation

**Goal**: Quantify how much of the 0.57-0.80 suppression comes from analytic/BBKS vs true G1 structure.

#### Outputs to Save

```
outputs/class_validation/
├── clpp_lcdm_analytic.csv       # BBKS ΛCDM reference
├── clpp_lcdm_class.csv          # CLASS linear P(k) ΛCDM
├── clpp_g1_analytic.csv        # BBKS + G1 growth/Σ
├── clpp_g1_class.csv           # CLASS linear P(k) + G1 growth/Σ
├── ratio_RL_analytic.csv       # G1/ΛCDM (analytic)
├── ratio_RL_class.csv          # G1/ΛCDM (CLASS)
└── delta_RL_percent.csv        # (analytic - CLASS)/CLASS in %
```

#### Null Tests (Must Pass Before Proceeding)

1. **Exact ΛCDM null**: `s=3, Σ=1` → `R_L ≡ 1`
2. **Growth null**: `D_G1 = D_ΛCDM, Σ=1` → `R_L ≡ 1`
3. **Σ-only null**: `D_G1 = D_ΛCDM` → `R_L` only reflects `Σ² + distance differences`

#### Pre-registered Decision Criteria

Report three statistics for `40 ≤ L < 400` and `400 ≤ L ≤ 1000`:

| Statistic | Definition |
|-----------|------------|
| Weighted RMS | `δR_RMS = [Σ (2L+1) δR_L² / Σ (2L+1)]¹⸍²` |
| 95th percentile | `P₉₅(|δR_L|)` |
| Max deviation | `max_L |δR_L|` |

**Gates**:

| Outcome | Action |
|---------|--------|
| Weighted RMS < 3%, no qualitative change | Analytic warning robust; proceed to ACT with CLASS |
| Weighted RMS 3% - 10% | Qualitative warning retained; quantitative must use CLASS |
| Weighted RMS > 10% OR shape/sign changes | Stop; revise precheck model first |

#### Report Deliverable

```
reports/CLASS_BACKEND_VALIDATION_v0.2.0.md
```

---

### Phase 1B: ACT Forward-Operator Validation

**Goal**: Verify the likelihood adapter is numerically correct before running real data.

**Note**: This phase is parallelizable with Phase 1A.

#### Critical Tests

1. **Forward-operator consistency**:
   ```
   C_L^φφ → C_L^κκ → C_b^κκ via adapter
   ```
   must match manual matrix calculation:
   ```
   C_b^adapter = Σ_L B_bL · [L(L+1)]²/4 · C_L^φφ
   ```

2. **Row-space round-trip**:
   ```
   b → B⁺b → BB⁺b ≈ b
   ```
   Verifies bandpower vector can be recovered (not arbitrary C_L).

3. **χ² equivalence**:
   ```
   χ²_manual = χ²_adapter
   ```
   for unit spectrum, delta multipole, constant scaling, ΛCDM truth, and known-suppression truth.

#### Report Deliverable

```
reports/ACT_ADAPTER_VALIDATION_v0.3.0_rc1.md
```

---

### Phase 2: Official Four-Point ACT/PR4 Run

**Goal**: First real-data measurement of lensing tension for M₃/₄.

#### Four Points

| Model | s | κ | Type | Expectation |
|-------|---|---|------|-------------|
| **ΛCDM** | - | - | Reference | Baseline |
| **M₃/₄** | 2.555 | 0.75 | Fiducial strict branch | Target measurement |
| **Background-only** | 2.555 | 0.0 | Control | Not necessarily ΛCDM; only Weyl closed |
| **Exact null** | 3.0 | 0.75 | Zero test | Must recover ΛCDM within numerical tolerance |

**Important Classification**:
- ✅ `s=3` → **Full ΛCDM zero test** (must recover ΛCDM)
- ✅ `κ=0, s=2.555` → **Background-only control** (need NOT match ΛCDM)
- ✅ `κ=0` independently computed vs explicit `Σ=1` → **Weyl implementation null** (must match)

#### Required Outputs

Report separately:
```
Δχ²_ACT,   Δχ²_PR4,   Δχ²_ACT+PR4
```

**Do NOT manually sum `χ²_ACT + χ²_PR4`** — use official `actplanck_baseline` for combined result.

---

### Phase 3: 41×41 Coarse Stress Map

**Goal**: Map the full prior range.

#### Configuration

- **Range**: `s ∈ [2.2, 3.0]`, `κ ∈ [0, 1]`
- **Grid**: 41 × 41 points (Δs=0.02, Δκ=0.025)
- **Mandatory lines**: `s=3`, `κ=0`, `κ=0.75`, `s=2.555`
- **Outputs**: Δχ², R̄₄₀₋₄₀₀, R̄₄₀₀₋₁₀₀₀

#### Secondary Coordinate System

Define:
```
q ≡ κ (3 - s)
```

Use internally for interpolation and fine sampling. Final plots use `(s, κ)`.

---

### Phase 4: Adaptive 101×101 Refinement

**Goal**: Resolve survival region accurately.

Apply 101×101 local refinement in region:
```
Δχ² < 25
```

---

### Phase 5: Full D11 Boltzmann + Primary CMB (G1 v1.4 Gate)

**Goal**: Final kill-test. Must implement full D11 perturbation equations in CLASS/CAMB:
```
H(a), I_H, Γ, Φ, Ψ
```
with proper initial conditions.

Includes full primary TT/TE/EE likelihood and cosmological parameter refit.

---

## 📊 Likelihood Diagnostics

For every model run, save:

1. **Bandpower pulls**: `r_b = (Ĉ_b - C_bᵗʰ) / sqrt(Cov_bb)`
2. **Whitened residuals**: `r_white = L⁻¹ (Ĉ - Cᵗʰ)` with `Cov = LLᵀ`
3. **Covariance eigenmode projections**: `a_i = u_iᵀ (Ĉ - Cᵗʰ) / sqrt(λ_i)`
   - Report largest |a_i|, cumulative χ², check for single-mode dominance
4. **Amplitude/shape decomposition**:
   - Best-fit template amplitude: `Â = tᵀ Cov⁻¹ d / tᵀ Cov⁻¹ t`
   - Report `χ²_fixed (A=1)` and `χ²_shape` (amplitude marginalized)
5. **Multipole-range decomposition**:
   - Δχ²(L < 100), Δχ²(100 ≤ L < 400), Δχ²(400 ≤ L < 1000), full range
6. **L-cut stability**:
   - Baseline, remove lowest L, remove highest L, conservative cuts
   - Verifies conclusion doesn't rest on edge multipoles

---

## 📌 Statistical Discipline

### ACT/PR4

- Use official `actplanck_baseline` for combined result
- Individual ACT and PR4 results for consistency diagnosis only
- Do NOT manually combine as independent unless explicitly verified uncorrelated

### Planck 2018

- **Not first priority**: Run only after Phase 3 complete
- Use only for robustness check: "Does conclusion depend on Planck lensing release?"
- **Do not mix with primary TT/TE/EE** until Phase 5

---

## ✅ Phase 0 Complete

```
Engineering integration: DONE
Scientific falsification sequence: INITIATED
```

Next: Phase 1A (CLASS backend validation) and Phase 1B (ACT forward-operator validation) begin in parallel.