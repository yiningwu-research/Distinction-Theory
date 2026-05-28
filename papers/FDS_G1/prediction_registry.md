# FDS-G1 — Prediction Lock and Falsification Registry

**Purpose:** Public commitment to the G1DE-M<sub>3/4</sub> prediction lock, its control hierarchy, forward test channels, and explicit demotion conditions.

A prediction lock is not a claim of certainty. It is a public commitment to a model identity, its dependencies, and its demotion criteria. Pre-registered predictions are recorded before specific outcomes are known.

## Prediction G1-A — Background Deviation (s < 3)

**Statement.** The screen-index parameter satisfies s < 3, producing a late-time background deviation from ΛCDM with fewer dark-energy parameters and no free equation-of-state function.

**Locked form.** The G1DE background expansion is:
E(z)<sup>2</sup> = Ω<sub>m</sub>(1+z)<sup>3</sup> + (1−Ω<sub>m</sub>)(1+z)<sup>3−s</sup>.

**Dependencies.** FDS-G1-001 (finite causal-screen entropy response); FDS-X1-001 (horizon as distinguishability boundary).

**Not claimed.** This does not derive the exact value of s or predict Ω<sub>m</sub> from first principles.

**Forward test.** Future BAO/SN data should continue favoring s < 3 over the s = 3 ΛCDM-like limit.

**Failure condition.** Production evidence returns to s = 3 (ΛCDM-like) dominance.

---

## Prediction G1-B — Weyl/Projection Lock (κ = 3/4)

**Statement.** The optical projection coefficient is locked at κ = 3/4, corresponding to the isotropic finite-access fixed point. The Weyl-active unimodular sector (three of four optical ports) gives the trace ratio κ = 3/4.

**Locked form.** Σ(a,k) − 1 = −κ R<sub>H</sub>(a) with κ = 3/4, where R<sub>H</sub>(a) is the horizon response.

**Dependencies.** FDS-G1-002 (3/4 projection lock); FDS-T2-001 (effective geometry as horizon boundary accounting).

**Not claimed.** This does not derive optical isotropy or prove that every physical screen is unbiased. It identifies the isotropic fixed point.

**Forward test.** Free κ should not decisively beat κ = 3/4 in future evidence comparisons.

**Failure condition.** Free-κ decisively beats M<sub>3/4</sub> under production evidence.

---

## Prediction G1-C — Growth/Ward Suppression (μ ≃ 1)

**Statement.** The growth response μ(a,k) is locked to 1 (Ward-suppressed Ricci leakage). The Ricci port is entropy-stiff, suppressing density-like response while preserving the Weyl channel.

**Locked form.** μ(a,k) = 1; μ<sub>0</sub> = 0.

**Dependencies.** FDS-G1-003 (background–Weyl residual fingerprint); FDS-G1-001; Ward/Bianchi closure.

**Not claimed.** This does not claim that all modified-gravity μ ≈ 1 separations are FDS-G1 realizations.

**Forward test.** Growth data should continue requiring μ near 1. Large |μ−1| comparable to |Σ−1| would weaken the Ward-suppressed Ricci-leakage branch.

**Failure condition.** Data require |μ−1| ∼ |Σ−1|, indicating unsuppressed Ricci leakage.

---

## Prediction G1-D — Output-Response Shape Resolution

**Statement.** The normalized horizon-response output shape ŝ<sub>H</sub>(a) (redshift-kernel shape) beats or remains competitive with constant-Σ in nested-evidence comparisons.

**Locked form.** Σ(a,k) − 1 = −(3/4)(3−s) ŝ<sub>H</sub>(a), with ŝ<sub>H</sub>(1) = 1.

**Dependencies.** G1-B, G1-A.

**Not claimed.** ŝ<sub>H</sub>(a) is the normalized output-response shape, NOT a uniquely identified microscopic source–kernel factorization.

**Forward test.** Expanded lensing and E<sub>G</sub>/3×2pt likelihoods should resolve the ŝ<sub>H</sub>(a) shape beyond constant-Σ.

**Failure condition (partial).** Constant-Σ decisively beats the output-response-shape model: the ŝ<sub>H</sub>(a) shape is demoted while the κ = 3/4 amplitude lock may survive.

---

## Prediction G1-E — Evidence Hierarchy Stability

**Statement.** The completed homogeneous seven-model medium-prior evidence ranking is:
M<sub>3/4</sub> > M<sub>κ</sub> > const-Σ > G1DE-2 > G1DE-1 > CPL > ΛCDM.

**Dependencies.** G1-A, G1-B, G1-C, G1-D.

**Not claimed.** Homogeneous audit evidence is not final production evidence; production caveat applies.

**Forward test.** Production evidence refinement and expanded lensing/3×2pt likelihoods should preserve the ranking or at minimum the M<sub>3/4</sub> > ΛCDM direction.

**Failure condition.** Production evidence reverses the ranking or returns to CPL or ΛCDM dominance.

---

## Prediction G1-F — Model Identity (No Free Amplitude)

**Statement.** No independently sampled free A(a,k) function enters the G1DE parameter set. The Weyl normalization is fixed by the projection lock; no dark-stress normalization freedom remains.

**Dependencies.** G1-B, G1-D.

**Not claimed.** This does not claim that all finite-screen models lack a free amplitude. It is a specific identity statement about the G1DE class.

**Forward test.** Future data should not require an independent A(a,k) amplitude beyond the locked amplitude–shape structure.

**Failure condition.** Free A(a,k) is required: the model leaves the G1DE class and becomes a generic dark-stress source.

---

## Demotion Protocol

All six demotion paths are pre-specified:

| # | Condition | Demotion |
|---|-----------|----------|
| 1 | Free-κ decisively beats M<sub>3/4</sub> | Exact 3/4 projection lock demoted |
| 2 | Constant-Σ decisively beats output-shape model | ŝ<sub>H</sub>(a) shape demoted; κ = 3/4 amplitude may survive |
| 3 | Data require |μ−1| ∼ |Σ−1| | Ward-suppressed Ricci-leakage branch fails |
| 4 | Free A(a,k) required | Model leaves G1DE class → generic dark-stress |
| 5 | CPL or ΛCDM wins under production evidence | G1DE observational branch demoted |
| 6 | Expanded lensing does not support Weyl signal | Current dark-sector interpretation fails or is downgraded |

Failure of a downstream bridge claim does not automatically falsify upstream Core or T-series claims. The FDS formal core, finite observer budget, and effective-geometry bridges are not locked to the G1DE-M<sub>3/4</sub> branch.
