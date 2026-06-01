
# Phase4E Numerical Consistency Check Report
## Check Date: 2026-05-30
## Check Status: Completed, all configurations fully aligned to Phase4B

---
## Key Outcomes
❌ **Original Phase4E conclusions invalid**: Initial scripts had critical configuration errors (mismatched parameter ranges, fixed values, starting points not aligned to Phase4B), leading to invalid fit results.
✅ **Corrected conclusion**: With full Phase4B configuration alignment, const-Σ and 2-bin Σ adversarial controls have lower chi2 than M34, all models hit parameter bounds.

---
## Numerical Results Summary (full EE+nE 200-row vector, same covariance, same baselines, same parameter ranges)
| Model               | chi2_min | chi2/dof | Bounds Hit | Notes |
|--------------------|----------|----------|--------------|------|
| LCDM (Phase4B baseline) | 1266.51  | 6.67     | All m_src at 0.1 upper bound | Reference baseline |
| M34 (Phase4B baseline)  | 1187.16  | 6.28     | All m_src at 0.1 upper bound | s=1.4253, corresponding to Σ = s/2 - 1 ≈ -0.29 |
| const-Σ (corrected)  | 1129.79  | 5.92     | Σ₀=0.5 (upper bound hit), all m_src at 0.1 upper bound | Σ₀ reaches physical upper bound, corresponding to s=3 (Phase4B s upper limit) |
| 2-bin Σ (corrected) | 1129.79  | 5.95     | Σ_bin0=Σ_bin1=0.5 (upper bounds hit), all m_src at 0.1 upper bound | Fully degenerates to const-Σ, no fit gain from extra bin |

---
## Key Findings
1. **Parameter bound limited**: Phase4B uses s upper limit of 3, corresponding to Σ₀= s/2 -1 = 0.5, which is exactly the upper bound we set for Σ parameters. All models hit this upper bound, indicating data prefers higher amplitude, but current parameter ranges limit fit capacity.
2. **Model degeneracy**: 2-bin Σ model fully degenerates to const-Σ, meaning redshift-binned amplitude corrections have no additional fit power, data does not prefer redshift-dependent Σ variations.
3. **Simple scaling outperforms M34**: The non-theory-motivated global amplitude scaling model const-Σ has χ² ~57 lower than M34, indicating current EE+nE data prefers simple global amplitude corrections over M34's redshift-dependent Weyl response.

---
## Boundary / Limitation Statement
⚠️ **These are diagnostic fit results only**: not model evidence, no physical conclusions are drawn, results only reflect fit performance under current data and model configurations.
⚠️ **All models hit parameter bounds**: Results are limited by chosen parameter ranges, lower χ² may be achieved with relaxed ranges.
⚠️ **No nested sampling used**: Only point estimate χ² values are provided, no Bayesian evidence computed.
⚠️ **No nn/clustering channel included**: This is not a full 3×2pt analysis.

---
## Recommended Next Steps
1. **Pause Phase4E adversarial control claims**: Until results are fully understood, do not claim shape specificity for M34, instead note that simple scaling models achieve better fit performance.
2. **Update all v1.2-dev documentation**: Remove earlier incorrect conclusions, update to validated results, clearly state all limitations.
3. **Validate M34 predictions**: Check for potential systematic errors leading to low amplitude in M34 BandPower predictions.
4. **Consider relaxing parameter ranges**: If physically motivated, test relaxing the s upper limit to see if M34 fit can achieve lower χ².
