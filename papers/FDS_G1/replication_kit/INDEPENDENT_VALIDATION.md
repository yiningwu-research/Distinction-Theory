# Independent Validation Protocol
# FDS-G1 Complete Series v1.1-rc1

The specification (spec/) is the validation target, not the author's code.
Independent reimplementations are encouraged and are the strongest form of
confirmation.

## Level 0: Model identity check

Verify that for each model, the response functions match the specification:

  - M_{3/4}: mu(a) = 1, Sigma(a) - 1 = -3/4 * (3-s) * Xhat(a)
  - M_kappa: mu(a) = 1, Sigma(a) - 1 = -kappa * (3-s) * Xhat(a)
  - const-Sigma: mu(a) = 1, Sigma(a) = 1 + Sigma_c
  - G1DE-2: mu(a) = 1 + mu0 * Xhat(a), Sigma(a) = 1 + Sigma0 * Xhat(a)
  - No model includes a free A(a,k) amplitude parameter.

## Level 1: Best-fit check

Reproduce chi2_min for each model within ±0.2.

  Expected range: [1767.1, 1767.3] for all G1DE models.

## Level 2: Evidence check

Using the same prior ranges, data vectors, covariance matrices, and
likelihood definitions, reproduce the evidence ranking and approximate
ΔlogZ:

  Expected ranking: M_{3/4} > M_kappa > const-Sigma > G1DE-2 > CPL > LCDM
  Tolerance: ΔlogZ within ±0.5, ranking must hold.
  Absolute logZ may vary with sampler and settings.

## Level 3: Stress test

  - Vary sampler (dynesty, PolyChord, MultiNest)
  - Vary seeds
  - Try wide prior bounds
  Check that M_{3/4} > M_kappa > const-Sigma is stable.

## Level 4: Adversarial reimplementation

  - Do not use the author's Python code at all
  - Use only spec/*.yaml and benchmark/*.csv
  - Use any sampler, any language
  - Reproduce the evidence ranking and approximate evidence differences

Passing Level 4 is the strongest form of independent confirmation.

## Level 5: KiDS diagnostic reproduction (new in v1.1-rc1)

  - Reproduce the CLASS backend P(k) sanity check
  - Reproduce the scale-cut covariance shape (135 x 135)
  - Reproduce the sign and approximate magnitude of delta-chi2(M3/4 - LCDM) = -39 to -44 under (m_i + dz_i + A_IA) nuisance
  - Reproduce the deterministic mock-injection confusion matrix:
    - LCDM mock -> LCDM lowest BIC (M3/4 must NOT win)
    - M3/4 mock -> M3/4 or Mkappa recovers (kappa ~ 0.75)
    - const-Sigma mock -> const-Sigma or binned-Sigma beats M3/4
    - binned-Sigma mock -> binned-Sigma beats M3/4

  Passing Level 5 confirms the v1.1 KiDS shear-only diagnostic stress-test results.

## Acceptance criteria

| Check | Tolerance | Must hold |
|-------|-----------|-----------|
| chi2_min | ±0.2 | Yes |
| Ranking | M34 > Mκ > constΣ | Yes |
| ΔlogZ(Mκ - M34) | 0.97 ± 0.5 | Approximate |
| ΔlogZ(constΣ - M34) | 1.92 ± 0.5 | Approximate |
| Wide-prior ranking | same | Yes |
| M34 > LCDM | ΔlogZ >> 5 | Yes |
| KiDS Δχ² sign | negative for M34 vs LCDM | Yes |
| KiDS mock LCDM→LCDM | BIC lowest for LCDM | Yes |
| KiDS mock M34→M34 | BIC lowest for M34 or Mκ | Yes |
| KiDS mock constΣ→constΣ or binΣ | M34 not lowest | Yes |
| KiDS mock binΣ→binΣ | M34 not lowest | Yes |
