# Phase Execution Status

## Version Gates

| Version | Requirement | Status | Completed |
|---------|-------------|--------|-----------|
| **v0.1.0** | Analytic benchmark fully verified | ✅ COMPLETE | 2026-06-11 |
| **v0.2.0** | CLASS transfer/power backend validated | 🔄 Running | - |
| **v0.3.0** | Official ACT/PR4 likelihood validated | ⏳ Pending | - |
| **v1.4** | Full D11 Boltzmann + primary CMB refit | ⏳ Pending | - |

**G1 main archive stays at v1.3 until Phase 5 completion.**

---

## Phase Status

### ✅ Phase 0: Baseline Tag - COMPLETE

- Git tag: `cmb-lensing-precheck-v0.1.0`
- Benchmark reproduced at < 1e-15 numerical precision
- All 8 tests passing
- Execution plan documented

---

### 🔄 Phase 1A: CLASS Transfer/Power Backend Validation - IN PROGRESS

**Goal**: Quantify how much of the 0.57-0.80 suppression comes from analytic/BBKS vs true G1 structure.

**Runner**: `scripts/run_class_validation.py`

**Output directory**: `outputs/class_validation/v0.2.0/`

#### Pre-registered Null Tests

1. **Exact ΛCDM null**: `s=3, Σ=1 → R_L ≡ 1`
2. **Growth null**: `D_G1 = D_ΛCDM, Σ=1 → R_L ≡ 1`
3. **Σ-only null**: `D_G1 = D_ΛCDM → R_L reflects only Σ² and geometry`

#### Pre-registered Decision Gates

Report statistics for `40 ≤ L < 400` and `400 ≤ L ≤ 1000`:

| Statistic | Definition |
|-----------|------------|
| Weighted RMS | `δR_RMS = [Σ (2L+1) δR_L² / Σ (2L+1)]¹⸍²` |
| 95th percentile | `P₉₅(|δR_L|)` |
| Max deviation | `max_L |δR_L|` |

**Decision criteria** (using low multipole range):

| Outcome | Action |
|---------|--------|
| Weighted RMS < 3%, no qualitative change | ✅ Analytic warning robust; proceed to Phase 2 with CLASS |
| Weighted RMS 3% - 10% | ⚠️  Qualitative warning retained; quantitative must use CLASS |
| Weighted RMS > 10% OR shape/sign changes | ❌ Stop; revise precheck model before data interpretation |

---

### 🔄 Phase 1B: ACT Forward-Operator Validation - IN PROGRESS

**Goal**: Verify likelihood adapter is numerically correct before running real data.

**Runner**: `scripts/run_act_validation.py`

**Output directory**: `outputs/act_validation/v0.3.0-rc1/`

#### Test Sequence

1. **φφ → κκ conversion** correctness
2. **Binning matrix direction** and multipole indexing
3. **Synthetic bandpower** recovery
4. **Manual χ² ≡ adapter χ²** equality
5. **Covariance whitening** verification
6. **Row-space pseudoinverse** round-trip

#### Required Outputs for Each Test

```
max |C_b^manual - C_b^adapter|
max |χ²_manual - χ²_adapter|
max absolute and relative errors per test vector
```

---

### ⏳ Phase 2: Four-Point ACT/PR4 Run - PENDING

**Prerequisite**: Phase 1A gate passed, Phase 1B complete.

**Output directory**: `outputs/four_point_run/`

#### Four Points

| Model | s | κ | Type | Expectation |
|-------|---|---|------|-------------|
| ΛCDM | - | - | Reference | Baseline |
| M₃/₄ | 2.555 | 0.75 | Fiducial strict branch | Target measurement |
| Background-only | 2.555 | 0.0 | Control | NOT necessarily ΛCDM |
| Exact null | 3.0 | 0.75 | Zero test | MUST recover ΛCDM |

**Important**: `κ=0, s=2.555` is a background-only control, NOT a ΛCDM null test.
The only exact null is `s=3`, which must return ΛCDM within numerical tolerance.

#### Must Report Separately

```
Δχ²_ACT,   Δχ²_PR4,   Δχ²_ACT+PR4
```

**Do NOT manually sum** — use official `actplanck_baseline` for combined result.

---

### ⏳ Phase 3: 41×41 Coarse Stress Map - PENDING

- **Range**: `s ∈ [2.2, 3.0]`, `κ ∈ [0, 1]`
- **Grid**: 41 × 41 points
- **Mandatory lines**: `s=3`, `κ=0`, `κ=0.75`, `s=2.555`
- **Outputs per point**: Δχ², R̄₄₀₋₄₀₀, R̄₄₀₀₋₁₀₀₀

#### Secondary Coordinate

Define: `q ≡ κ (3 - s)`
Use internally for interpolation; final plots use `(s, κ)`.

---

### ⏳ Phase 4: Adaptive 101×101 Refinement - PENDING

Apply locally in region: `Δχ² < 25`

---

### ⏳ Phase 5: Full D11 Boltzmann + Primary CMB - G1 v1.4 GATE - PENDING

This is the only phase whose completion enables formal exclusion statements.
Must implement full D11 perturbation equations in CLASS/CAMB:
```
H(a), I_H, Γ, Φ, Ψ
```
with proper initial conditions.

Includes full primary TT/TE/EE likelihood and cosmological parameter refit.

---

## Likelihood Diagnostics

Saved for every model run:

1. **Bandpower pulls**: `r_b = (Ĉ_b - C_bᵗʰ) / sqrt(Cov_bb)`
2. **Whitened residuals**: `r_white = L⁻¹ (Ĉ - Cᵗʰ)` with `Cov = LLᵀ`
3. **Eigenmode projections**: Report largest |a_i|, cumulative χ², check for single-mode dominance
4. **Amplitude/shape decomposition**:
   - Best-fit template amplitude: `Â = tᵀ Cov⁻¹ d / tᵀ Cov⁻¹ t`
   - Report `χ²_fixed (A=1)` and `χ²_shape` (amplitude marginalized)
5. **Multipole-range decomposition**: Δχ²(L<100), Δχ²(100≤L<400), Δχ²(400≤L<1000), full range
6. **L-cut stability**: Baseline, remove lowest L, remove highest L, conservative cuts

---

## Statistical Discipline

### ACT/PR4
- Use official `actplanck_baseline` for combined result
- Individual ACT and PR4 results for consistency diagnosis only
- **Do NOT manually combine as independent** unless uncorrelated is explicitly verified

### Planck 2018
- **Not first priority**: Run only after Phase 3 complete
- Purpose only: "Does conclusion depend on Planck lensing release?"
- **Do not mix with primary TT/TE/EE until Phase 5**

---

## Running the Phases

```bash
# Phase 1 (A and B in sequence; parallelize manually if desired)
./start_phase1.sh

# Phase 2: After gate passes (see Phase 2 docs when ready)

# Phase 3: After Phase 2 complete
```

---

## Audit Trail Requirements

EVERY scientific run must record:

```
git commit
git tag
config hash
data hash
dependency lock
random seed
backend name
normalization convention
amplitude mode
```

NEVER overwrite the v0.1.0 analytic benchmark.
All new results go into version-numbered directories.
