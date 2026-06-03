# G1DM / M₃/₄ Demotion Path Map

This table maps each data note to the specific G1DM/M₃/₄ demotion path it tests.
It is intended to feed directly into the Companion G paper as an evidence summary.

| Data note | Tests | Supports | Demotes if failed |
|-----------|-------|----------|-------------------|
### Note 1 — carrier floor (compressed Planck posterior)

| Parameter | Mean | σ | Q₁₆ | Q₅₀ | Q₈₄ | $z$(Ω_c h²=0) | Status |
|-----------|------|---|-----|-----|-----|----------------|--------|
| Ω_c h² | 0.1200 | 0.0012 | 0.1188 | 0.1200 | 0.1212 | 100.0σ | **PASSED** |

**Result:** Planck 2018 TT,TE,EE+lowE chains strongly exclude Ω_c h² = 0 at ~100σ. A nonzero CDM-like source component is required by CMB data. Pure Weyl/optical residuals cannot replace the full CDM sector. This establishes G1DM-C0's carrier floor: dark matter is a source/carrier problem, not primarily a modified-growth problem.

**Data source:** Planck 2018 published posterior (Planck Collaboration VI, 2020, Table~2), using the base_plikHM_TTTEEE_lowl_lowE constraint Ω_c h² = 0.1200 ± 0.0012. Real-chain confirmation is straightforward (requires Planck Legacy Archive access) but the synthetic result is robust given the enormous significance.

### Note 3 — lensing-growth split (real-chain results)

First real-chain diagnostics using DESI DR1 `base_mu_sigma` public chains.

#### Summary table

| Combination | μ₀ | σ_μ₀ | Σ₀ | σ_Σ₀ | Weyl z | Growth z | Best model (BIC) |
|------------|-----|-------|-----|------|--------|---------|-----------------|
| FS/BAO+Planck (197K) | +0.223 | 0.236 | +0.389 | 0.101 | 3.86σ | 0.94σ | Weyl-only |
| +DESY3joint (111K) | +0.038 | 0.226 | +0.045 | 0.047 | 0.96σ | 0.17σ | GR |
| +DESY5SN | — | — | — | — | — | — | — | _chain not yet available in DESI DR1 VAC for `base_mu_sigma`_ |

#### Formal diagnostic status

| Diagnostic | Status | Interpretation |
|---|---|---|
| Ricci/growth leakage | **Passed** | μ₀ consistent with 0 in both combinations ran |
| Growth-only explanation | **Disfavored** | Growth-only is not the preferred channel in any combination |
| Weyl-channel residual | **Planck-linked / not robust** | Strong in FS/BAO+Planck (3.86σ), disappears with DESY3joint (0.96σ) |
| M₃/₄ sign-lock | **Pending / under pressure** | DESI Σ₀ > 0 is opposite current M₃/₄ sign convention for s < 3 |

**Scientific conclusion:** Ricci/growth leakage is not required in any combination; a Planck-linked Weyl residual appears in FS/BAO+Planck but is not robust after DES Y3 3×2pt is added. The strong Weyl signal in the FS/BAO+Planck chain is consistent with the known Planck PR3 lensing anomaly and the official DESI MG paper's finding of GR-consistent results in combined datasets. DESI DR1 `_mu_sigma` chains do not yet provide robust external confirmation of the M₃/₄ Weyl sign/amplitude lock, but they do support suppressed growth leakage — a required condition for the G1DE/M₃/₄ channel hierarchy. Companion G's source–response–optics decomposition is strongly justified as a robustness discipline.

## Demotion chain (simplified)

```
carrier floor failed → G1DM-C0 rejected → full ΛCDM with CDM preferred
μ=1 consistency failed → Ricci leakage unsuppressed → M₃/₄ locked branch stressed
lensing-growth split → Weyl residual absent → M₃/₄ Weyl branch demoted
SRO audit → arbitrary absorption wins → Companion G sparse structure invalidated
```

## Integration with FDS-G1 paper

This table should be reproduced in the Companion G paper as a summary of
public-data diagnostics. Each row maps to a specific demotion condition in the
M₃/₄ and G1DM-C0 frameworks. The notes are designed to be run independently;
the table above shows which demotion paths are triggered by which failure.
