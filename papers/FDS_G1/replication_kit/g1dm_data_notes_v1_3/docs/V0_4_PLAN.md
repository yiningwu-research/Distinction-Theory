# G1DM v0.4 Development Plan: Covariance-Aware 3×2pt SRO Audit

**Status:** Roadmap for `g1dm-v0.4-full-3x2pt-audit` branch.
**Parent:** `g1dm-release-v0.3` (frozen compressed-diagnostic layer).

## Goal

Reproduce the v0.3 compressed-proxy SRO conclusion (source required, growth
leakage suppressed, optics selected by $S_8$ pressure) under **real data
vectors and non-diagonal covariance matrices** from KiDS-1000 and DES Y3.

## Phase roadmap

| Phase | Description | Gate condition |
|-------|-------------|---------------|
| **4a** | Ingest KiDS-1000 cosmic shear data vector + covariance; reproduce published $S_8$ constraint | $\Delta S_8$ matches published within $\sim0.5\sigma$ |
| **4b** | Build SRO design matrix on real data; compare sparse model masks under non-diagonal covariance | Model ranking under real covariance is understood |
| **4c** | Add DES Y3 3×2pt or compressed constraint as independent cross-check | Cross-probe consistency evaluated |
| **4d** | Nuisance parameter sensitivity sweep: IA amplitude, photo-$z$ shift, shear calibration | Nuisance-propagation understood |
| **4e** | Full $r$-grid under real covariance; compare to v0.3 compressed-proxy result | v0.3-v0.4 comparison documented |

---

## Phase 4a: KiDS-1000 S₈ Reproduction (first target)

### Scientific question

Can the G1DM toolkit ingest the public KiDS-1000 cosmic shear data vector
and covariance matrix, and reproduce the published $S_8$ constraint
($S_8 = 0.759^{+0.024}_{-0.021}$) within $\sim0.5\sigma$?

### Data source

KiDS-1000 fiducial COSEBIs analysis (Asgari et al. 2021).
Data products available from:
- `https://kids.strw.leidenuniv.nl/DR4/KiDS-1000_cosmicshear.php`
- Tarball includes: data vectors, covariance matrices, $n(z)$ distributions,
  CosmoSIS configuration files, Multinest chains.

### Required files

| File | Purpose |
|------|---------|
| COSEBIs data vector | $\xi_\pm$ compressed into $E_n$ modes |
| COSEBIs covariance matrix | Non-diagonal, includes shape noise + cosmic variance |
| $n(z)$ distributions | 5 tomographic bins, for theory prediction |
| Published chains | Cross-check reference: $S_8$ posterior |

### Compression approach

For Phase 4a, the simplest approach is to extract the published $S_8$ constraint
directly from the chains rather than re-running a full likelihood. This validates
the data pipeline without requiring a Boltzmann code.

If the chains provide $S_8$ posterior samples, Phase 4a is:
1. Download chains and data products
2. Verify $S_8$ posterior mean and $\sigma$ match published values
3. Store compressed $S_8$ constraint for Phase 4b

### Success criteria

- $S_8$ posterior from chain: $S_8 = 0.759^{+0.024}_{-0.021}$ ($<0.5\sigma$ deviation)
- Data vector and covariance load without errors
- Repository: no raw data committed; provenance documented
- Test: new smoke test validates data ingestion

### Code changes

| File | Change |
|------|--------|
| `notes/note4a_kids_s8_validation.py` | **New** — download plan, FITS/chain inspection, $S_8$ validation, covariance PD check |
| `tests/test_smoke.py` | Add `test_note4a_kids_validation` (smoke) |
| `docs/KIDS1000_DOWNLOAD_PLAN.md` | **New** — download URL, paths, tarball contents, references |

**Status: PASSED.** S₈ = 0.751 ± 0.022 from the COSEBIs chain; Δ = −0.008 from published (0.3σ). Data vectors and covariances load. BandPower cov is PD; COSEBIs and ξ± are rank-deficient.

---

## Phase 4b: SRO Template Fit Under Real Covariance

### Status: BLOCKED

**Blocker:** The KiDS-1000 FITS release provides data vectors (`PneE`, `PeeE`, `En`, `xiP`, `xiM`) and covariance matrices (`COVMAT`), but does **not** include model/theory prediction vectors.

$$
m_{\rm Planck},\ m_{\rm KiDS}\ \text{not available in the FITS release}
\Rightarrow
r = d - m_0\ \text{undefined}
\Rightarrow
\text{SRO template fit blocked}.
$$

To fit SRO amplitudes $\hat a = (T^T C^{-1} T)^{-1} T^T C^{-1} (d - m_0)$ under
real covariance, a fiducial model vector $m_0$ is required.  This must be
generated via KCAP/CosmoSIS using the `values.ini` and `pipeline.ini` config
files included in the release, together with a Boltzmann code (CAMB or CLASS).

### Unblock path

1. Install CAMB or CLASS + CosmoSIS/KCAP.
2. Generate $m_{\rm Planck}$ from Planck 2018 best-fit parameters.
3. Generate $m_{\rm KiDS}$ from KiDS-1000 best-fit (MAP) parameters
   (`maxpost_multinest_start_C.txt` in the COSEBIs/BP/ξ± chain directories).
4. Compute residuals $r_{\rm Planck} = d - m_{\rm Planck}$ and
   $r_{\rm KiDS} = d - m_{\rm KiDS}$.
5. Fit SRO templates against $C$; compare masks.

### Phase 4b-lite: Covariance Readiness Check (completed)

**Status: PASSED.**

| Metric | Value |
|--------|-------|
| Data vector | 200 (80 PneE + 120 PeeE) |
| Covariance | 200×200, **positive definite** |
| Cholesky | OK |
| Condition number | 4.6 × 10⁵ |
| λ_min | 2.8 × 10⁻¹¹ |
| λ_max | 1.3 × 10⁻⁵ |
| Shear-null S/N | 39.4 (detection against zero, NOT an S₈ residual) |
| Whitened |w|>5 | 18 of 200 components |

**Label:** Engineering readiness only — NOT an SRO evidence test, NOT an S₈
residual test, NOT a source-vs-optics model comparison.

Script: `notes/note4b_kids_bandpower_covariance_ready.py`

### Code changes

| File | Change |
|------|--------|
| `notes/note4b_kids_bandpower_covariance_ready.py` | **New** — loads BP, checks PD/condition/whitening/S/N |
| `tests/test_smoke.py` | Add smoke test |
| `docs/V0_4_PLAN.md` | This update |

---

## Phase 4b–4e (future)

Design details deferred until Phase 4a passes.

### Key questions for later phases

- **4b:** Does a sparse SRO mask still select source+optics under real
  non-diagonal covariance?
- **4c:** Is the DES Y3 3×2pt $S_8$ result consistent with KiDS-1000?
  If not, does the SRO audit distinguish the two?
- **4d:** How does the IA amplitude (common systematic tension between
  KiDS and DES) affect the optics-channel selection?
- **4e:** Is the v0.3 compressed-proxy conclusion ($r$-stable source+optics
  preference) robust under real covariance?

---

## Constraints

1. **No Boltzmann code required.** Phases 4a–4d should use compressed
   constraints, data vectors, and posterior chains — not re-running
   CAMB/CLASS/CosmoSIS likelihoods.
2. **No raw data in git.** All data products live in `data/raw/`, excluded
   by `.gitignore`.
3. **No completed-theory claims.** v0.4 remains a model-compression audit,
   not a cosmological discovery.
4. **$r$-stability discipline.** All optics-vs-response channel assignments
   must be tested across $r \in \{0, 0.25, 0.5, 0.75, 1.0\}$.

---

## Comparison to v0.3

| Dimension | v0.3 | v0.4 target |
|-----------|------|-------------|
| Data | Compressed $S_8$ z-score | KiDS-1000 data vector + covariance |
| Covariance | Diagonal (identity) | Non-diagonal (real) |
| Nuisance | None | IA, photo-$z$, shear calibration |
| S₈ proxy | Hardcoded values | Chain-derived posterior |
| SRO masks | 7 models | 7 models, same structure |
| $r$-grid | 5 points | 5 points, same design |

---

## Branch management

- **This branch:** `g1dm-v0.4-full-3x2pt-audit`
- **Base:** `g1dm-release-v0.3` tag
- **Merge target:** `main` (when v0.4 is complete and frozen)
- **Do NOT modify v0.3 artifacts.** v0.3 is frozen.
