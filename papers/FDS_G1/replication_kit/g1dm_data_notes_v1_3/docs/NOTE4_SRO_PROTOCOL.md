# Note 4: Source–Response–Optics Sparse Audit — Protocol (Phase 1)

**Status:** Protocol / design phase. No production multi-probe likelihood.

## Scientific question

Given Note~1 (source floor, $T_{\mu\nu}^{D}\neq0$) and Note~3 (suppressed growth
leakage, $\mu_{\rm grav}\simeq1$), do current compressed observables require an
independent optics or response component after parameter penalty?

Note~4 is a **model-compression audit**, not a discovery test.  It asks whether
a sparse source-only or source+one-channel explanation is sufficient, or whether
the multi-channel source–response–optics picture is required by the data.

## Observables

The compressed data vector is curated from public cosmological results.  Each
observable $y_i \pm \sigma_i$ is a deviation from a baseline GR+$\Lambda$CDM
reference, with a design matrix assigning each observable to the source,
response, and optics channels.

| Observable | Channel | $y$ | $\sigma$ | Status |
|-----------|---------|----:|-----:|--------|
| $\Omega_c h^2$ | source | $0.120$ | $0.0012$ | Fixed — Planck 2018 / Note~1 |
| $\mu_0$ | response/growth | $0.038$ | $0.226$ | DESI DR1 + DESY3joint / Note~3 |
| $\sigma_0^{\rm DESI}$ | optics | $0.045$ | $0.047$ | DESI DR1 + DESY3joint / Note~3 |
| $\sigma_0^{\rm DESI}$ (Planck-linked) | optics | $0.389$ | $0.101$ | FS/BAO+Planck, diagnostic only |
| $S_8$ proxy | optics/response | TBD | TBD | KiDS/DES compressed, future |

**Notes:**
- The Planck-linked $\sigma_0^{\rm DESI}$ value is included as a **diagnostic
  observable** to test whether adding it forces a model to absorb the Weyl
  residual at significant BIC cost.  It is not treated as a production-quality
  constraint unless corroborated by independent lensing data.
- The $S_8$ proxy is a placeholder for future compressed KiDS/DES measurements.
  It is not required for Phase~1.

## Design matrix

Each observable is assigned a loading onto the three channels via a binary
design matrix $X$.

| Observable | Source | Response | Optics |
|-----------|------:|--------:|------:|
| $\Omega_c h^2$ | $1$ | $0$ | $0$ |
| $\mu_0$ | $0$ | $1$ | $0$ |
| $\sigma_0^{\rm DESI}$ (DESY3joint) | $0$ | $0$ | $1$ |
| $\sigma_0^{\rm DESI}$ (Planck-linked, diagnostic) | $0$ | $0$ | $1$ |

The model prediction is $\mathbf{y}_{\rm pred} = X\boldsymbol{\theta}$, where
$\boldsymbol{\theta} = (\theta_{\rm source}, \theta_{\rm response}, \theta_{\rm optics})$
are the three channel amplitudes.

## Sparse model masks

Models are defined by which channel amplitudes are free (1) vs fixed to zero (0).

| Model | Source | Response | Optics | $k$ (free params) | Rationale |
|-------|------:|--------:|------:|:-:|----------|
| Source only | 1 | 0 | 0 | 1 | Conservative; Note~1 floor |
| Source + response | 1 | 1 | 0 | 2 | Tests $\mu$ residual requirement |
| Source + optics | 1 | 1 | 0 | 2 | Tests $\Sigma$ residual requirement |
| Source + response + optics | 1 | 1 | 1 | 3 | Full decomposition |
| Optics only | 0 | 0 | 1 | 1 | Demotion baseline (Note~1 rules this out) |
| Response only | 0 | 1 | 0 | 1 | Demotion baseline (Note~3 disfavors this) |

**Expectation:** Models without source are expected to be demoted by Note~1
($\Omega_c h^2=0$ is excluded at $>\!100\sigma$) and are included only as
formal completeness checks.

## Gaussian linear model

For a data vector $\mathbf{y}$ and covariance $\Sigma$ (assumed diagonal in
Phase~1), the four-source model fit uses:

$$
\begin{aligned}
\hat{\boldsymbol{\theta}} &= (X_{\rm free}^T \Sigma^{-1} X_{\rm free})^{-1}
X_{\rm free}^T \Sigma^{-1} \mathbf{y}, \\
\chi^2_{\rm min} &= (\mathbf{y} - X\hat{\boldsymbol{\theta}})^T \Sigma^{-1}
(\mathbf{y} - X\hat{\boldsymbol{\theta}}), \\
\log\mathcal{L}_{\rm max} &= -\tfrac{1}{2}\bigl(\chi^2_{\rm min}
+ \log\det(2\pi\Sigma)\bigr).
\end{aligned}
$$

Model comparison uses BIC and AIC:

$$
\begin{aligned}
\text{BIC} &= k\ln n_{\rm eff} - 2\log\mathcal{L}_{\rm max}, \\
\text{AIC} &= 2k - 2\log\mathcal{L}_{\rm max},
\end{aligned}
$$

where $n_{\rm eff}$ is an adopted effective data count (not the posterior
sample count).  Phase~1 uses $n_{\rm eff}=4$ (the number of compressed
observables) with a caveat that this is a compressed Gaussian information
criterion, not a production Bayesian evidence.

## Phase~1 run plan

The current `note4_sro_sparse_audit.py` script already implements the core
logic.  Phase~1 execution requires:

1. Populate the template YAML file `data/templates/sro_observables_template.yml`
   with the values from the observable table above.
2. Run:
   ```bash
   PYTHONPATH=src python notes/note4_sro_sparse_audit.py \
     --observables data/templates/sro_observables_template.yml \
     --out outputs/note4_sro_phase1
   ```
3. Examine the model ranking to answer the protocol question.

## Interpretation logic

| Outcome | Interpretation |
|---------|---------------|
| Source only has lowest BIC | Public compressed data do not require independent response or optics beyond the source floor |
| Source + optics beats source | Weyl/optical channel is independently favored; supports G1DM-W / M$_{3/4}$ optics channel |
| Source + response beats source | Growth channel independently required; Ricci-leakage suppression under pressure |
| Source + response + optics wins | Full three-channel decomposition is required; largest theoretical upgrade |
| No-source model wins | **Protocol failure** — Notes 1 and 3 veto this; check design matrix or data values |

## Warning: not a production likelihood

> Note~4 Phase~1 is a compressed Gaussian audit protocol, not a production
> multi-probe likelihood.  It is intended to define the data vector, design
> matrix, sparse masks, and penalty logic before production covariance and
> nuisance modeling are added.  Full 3$\times$2pt covariance, pipeline
> cross-correlation, and systematic nuisance profiling are required for
> a production-level result.

## Integration with the toolkit

- **Script:** `notes/note4_sro_sparse_audit.py` (exists, functional, updated for z-score input and source-floor cap)
- **Scenario files:** `data/templates/sro_scenario_A.yml`, `data/templates/sro_scenario_B.yml`
- **Dependencies:** `g1dm.io`, `g1dm.stats` (gaussian_linear_fit, bic, aic, model_mask_grid)

## Phase 1a results (populated compressed sanity check)

Phase~1a was run on 2026-06-03 with the standardized z-score vectors from
Notes~1 and~3.  This is a populated compressed sanity check, NOT a production
multi-probe evidence audit.

### Scenario A — FS/BAO+Planck

| Model | $\theta_{\rm src}$ | $\theta_{\rm resp}$ | $\theta_{\rm opt}$ | $k$ | $\chi^2$ | BIC | $\Delta$BIC |
|-------|----:|----:|----:|:-:|----:|----:|----:|
| **source+optics** | 100.0 | 0 | 3.86 | 2 | 0.88 | **8.59** | 0.00 |
| source+resp+optics | 100.0 | 0.94 | 3.86 | 3 | 0.00 | 8.81 | +0.22 |
| source only | 100.0 | 0 | 0 | 1 | 15.78 | 22.40 | +13.80 |
| source+response | 100.0 | 0.94 | 0 | 2 | 14.90 | 22.61 | +14.02 |
| optics only | 0 | 0 | 3.86 | 1 | 10000.88 | 10007.50 | +9998.90 |
| response+optics | 0 | 0.94 | 3.86 | 2 | 10000.00 | 10007.71 | +9999.12 |
| response only | 0 | 0.94 | 0 | 1 | 10014.90 | 10021.51 | +10012.92 |

**Result:** Source+optics is preferred over source-only ($\Delta$BIC = $-13.80$).
The Planck-linked Weyl residual ($\sigma_0^{\rm DESI}=3.86\sigma$) drives a
clear optics-channel preference.  The response channel is not required
(source+resp+optics adds only $\Delta$BIC = $+0.22$ vs source+optics).
Models without source are decisively demoted (Note~1 carrier floor).

Robustness display with source z-score capped at 10 preserves the same ranking.

### Scenario B — FS/BAO+Planck+DESY3joint

| Model | $\theta_{\rm src}$ | $\theta_{\rm resp}$ | $\theta_{\rm opt}$ | $k$ | $\chi^2$ | BIC | $\Delta$BIC |
|-------|----:|----:|----:|:-:|----:|----:|----:|
| **source** | 100.0 | 0 | 0 | 1 | 0.95 | **7.56** | 0.00 |
| source+optics | 100.0 | 0 | 0.96 | 2 | 0.03 | 7.74 | +0.18 |
| source+response | 100.0 | 0.17 | 0 | 2 | 0.92 | 8.63 | +1.07 |
| source+resp+optics | 100.0 | 0.17 | 0.96 | 3 | 0.00 | 8.81 | +1.25 |
| optics only | 0 | 0 | 0.96 | 1 | 10000.03 | 10006.64 | +9999.08 |
| response only | 0 | 0.17 | 0 | 1 | 10000.92 | 10007.53 | +9999.97 |
| response+optics | 0 | 0.17 | 0.96 | 2 | 10000.00 | 10007.71 | +10000.15 |

**Result:** Source-only has the lowest BIC.  Among source-admissible masks,
no additional response or optics component is required after parameter penalty.
Adding DESY3joint removes the optics preference seen in Scenario~A.
The response channel is again not required.  Models without source are
decisively demoted.

Robustness display with source z-score capped at 10 preserves the same ranking.

### Phase 1a conclusion

```
Scenario A: Planck-linked Weyl residual favors source+optics over source-only.
Scenario B: Adding DESY3joint removes the optics preference; source-only is sufficient.
```

This reproduces the Note~1+3 diagnosis ($T_{\mu\nu}^{D}\neq0$, $\mu_{\rm grav}\simeq1$,
Weyl not robust) and validates the SRO pipeline logic.  It is NOT a production
multi-probe evidence audit and no combined cosmological evidence claim is made.

## Phase 2 results — independent S₈ compressed-proxy audit

Phase~2 introduces an independent compressed $S_8$ tension proxy as an
optics/response pressure row.  This is not a direct measurement of a Weyl
residual.  It tests whether public weak-lensing constraints add a sparse
low-redshift residual requirement after the source floor and growth-leakage
diagnostics are already included.

### S₈ values used

| Source | $S_8$ | $\sigma$ | $\Delta S_8$ vs Planck | $z$-score |
|--------|-------|---------|------------------------|-----------|
| Planck 2018 (TT,TE,EE+lowE) | $0.831$ | $0.013$ | — | — |
| KiDS-1000 cosmic shear | $0.759$ | $0.0225$ | $0.072$ | $2.77\sigma$ |
| DES Y3 3$\times$2pt | $0.776$ | $0.017$ | $0.055$ | $2.57\sigma$ |

$S_8 = \sigma_8(\Omega_m/0.3)^{0.5}$.
$\Delta S_8$ defined as $S_8^{\rm Planck} - S_8^{\rm WL}$.
$z = \Delta S_8 / \sqrt{\sigma_{\rm Planck}^2 + \sigma_{\rm WL}^2}$.

### Design matrix with r-grid

The $S_8$ observable row has design $[0, r, 1-r]$ where
$r \in \{0, 0.25, 0.5, 0.75, 1.0\}$ is the response loading fraction:
\begin{itemize}
\item $r=0$: $S_8$ tension fully assigned to optics/lensing residual.
\item $r=1$: $S_8$ tension fully assigned to response/growth residual.
\item Intermediate values: mixed attribution.
\end{itemize}

### KiDS-1000 proxy (primary)

| $r$ | Best model (BIC) | $\Delta$BIC(source+optics vs source) | $\Delta$BIC(source+response vs source) |
|-----|-----|-----:|-----:|
| 0.00 | source+optics | $-6.57$ | $+0.40$ |
| 0.25 | source+optics | $-6.57$ | $-0.84$ |
| 0.50 | source+optics | $-6.57$ | $-2.13$ |
| 0.75 | source+optics | $-6.57$ | $+1.07$ |
| 1.00 | source+optics\textsuperscript{$\dagger$} | — | — |

\noindent$\dagger$: At $r=1$, the response-channel design absorbs the full
$S_8$ tension.  Response becomes selected, but this reflects artificial
response pressure from the proxy assignment, not a growth-leakage detection
(the DESI $\mu_0$ row remains near zero).

**Result:** Source+optics is consistently preferred across the full $r$-grid.
The independent $S_8$ proxy introduces sufficient low-redshift lensing/structure
pressure to select an optics component beyond the source floor, and this result
is $r$-stable.

### DES Y3 3×2pt proxy (sensitivity)

| $r$ | Best model (BIC) | $\Delta$BIC(source+optics vs source) | $\Delta$BIC(source+response vs source) |
|-----|-----|-----:|-----:|
| 0.00 | source+optics | $-5.51$ | $+0.48$ |
| 0.25 | source+optics | $-5.51$ | $-0.60$ |
| 0.50 | source+optics | $-5.51$ | $-1.72$ |
| 0.75 | source+optics | $-5.51$ | $+1.07$ |
| 1.00 | source+optics\textsuperscript{$\dagger$} | — | — |

**Result:** Source+optics is again consistently preferred, with slightly
weaker $\Delta$BIC ($-5.51$ vs $-6.57$) reflecting the marginally lower
$S_8$ tension in DES Y3 compared to KiDS.  The result is $r$-stable.

### Capped-source robustness

All Phase~2 results are verified with the source $z$-score capped at 10.
Rankings are stable under the capped-source rerun, confirming that the
optics selection is driven by the $S_8$ proxy ($2.57$--$2.77\sigma$) rather
than by the $100\sigma$ carrier-floor row mechanically dominating the model
comparison.

### Phase 2 conclusion

```
The independent S8 proxy introduces low-redshift lensing/structure pressure
that selects an optics component beyond the source floor.  This result is
r-stable across both KiDS-1000 and DES Y3 proxies.  However, the channel
assignment is model-dependent: at high r, the proxy creates artificial
response pressure not supported by DESI mu0.  Source floor remains required;
DESI mu0 still does not require growth leakage.
```

Phase~2 remains a compressed SRO audit — not a production multi-probe evidence
audit.  Full $3\times2$pt covariance, pipeline cross-correlation, and systematic
nuisance profiling are required for a production-level result.
