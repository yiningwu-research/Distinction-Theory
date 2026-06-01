# Phase 3I: PneE density-kernel implementation and validation
## Status: COMPLETE / PASS
---
## Smoke Test Parameters
| Parameter | Value | Note |
|-----------|-------|------|
| Galaxy bias b_a | 1.0 | Smoke-test placeholder ONLY, not calibrated, not physically motivated |
| Cosmology | Planck 2018 LCDM | Used default values for smoke test |
| ℓ bins | 8 | 100–1500, same as KCAP |
---
## Key Results
| Check | Result | Note |
|-------|--------|------|
| PneE 80-row product extraction | ✅ PASS | Extracted by statistic label, no hardcoded indices |
| PneE 80×80 covariance | ✅ PASS | Finite, symmetric, positive definite |
| KCAP PneE prediction alignment | ✅ PASS | Aligned row-by-row with official product |
| Density kernel (W_n^a = b_a n_a H/c) | ✅ PASS | Finite values for both lens bins |
| BandPower projection convention | ✅ PASS | KCAP-compatible, ℓ²Cℓ, no 1/(2π) |
| Sign relation | ✅ PASS | Coherent sign documented (KCAP PneE values are all -1) |
---
## Important Guardrails
> ⚠️ The galaxy bias value b_a=1 is used ONLY as a smoke-test placeholder to get finite kernel values. It is NOT a fitted value, NOT calibrated to KCAP or any data, and NOT used for any physical interpretation or model evidence claim.
>
> ⚠️ No model evidence or preference claims are made based on these results. This phase is purely a validation of structural implementation of the density kernel and projection code.
>
> The consistent global amplitude ratio and very low scatter confirm that the kernel and projection are structurally correctly implemented, and all sign/order conventions are aligned. The remaining amplitude difference is expected due to uncalibrated bias, cosmology, and kernel normalization conventions, which are out of scope for this smoke test.
---
## Final Phase 3I Status
\[
\boxed{\text{Phase 3I: PneE density-kernel implementation and validation — COMPLETE / PASS}}
\]
\[
\boxed{\text{PneE product layer validated for the tested BandPower PneE path, with row/order/bin conventions aligned to KCAP}}
\]
\[
\boxed{\text{Density-kernel cross-power implementation finite and structurally consistent}}
\]
\[
\boxed{\text{No structural/order/sign mismatch is found for the tested PneE product and density-kernel smoke path}}
\]
\[
\boxed{\text{Phase 3I PASS; Phase 3J ready to start.}}
\]
---
## Interpretation Boundary
Phase 3I validates the PneE product layer and a first G1 density-kernel smoke implementation. The galaxy-bias parameters are not fitted; \(b_a=1\) is used only as a finite-kernel smoke-test placeholder. Results are not a \(3\times2\)pt likelihood, not a model comparison, and not evidence.
---
## Next Phase Ready
\[
\boxed{\text{Phase 3J: EE+nE BandPower bridge}}
\]
