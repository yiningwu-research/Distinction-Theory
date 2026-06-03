# KCAP/CosmoSIS Model-Vector Generation Plan

**Goal:** Generate $m_{\rm KiDS}$ and $m_{\rm Planck}$ BandPower prediction vectors
(200 elements each: 80 PneE + 120 PeeE) using KCAP/CosmoSIS + CAMB, to unblock
Phase 4b full SRO template fitting.  See `PHASE4B_BLOCKER_MODEL_VECTORS.md` for
context.

---

## 1. Environment / install plan

### Required components

| Component | Role | Install |
|-----------|------|---------|
| CAMB | Boltzmann solver (CMB + matter power spectra) | `pip install camb` |
| CosmoSIS framework | Pipeline runner, parameter manager, likelihood evaluation | Install from official source |
| KCAP | KiDS Cosmology Analysis Pipeline modules | Verify repository URL against KiDS-1000 release documentation before installation. The modules referenced in `pipeline.ini` include: `sample_S8`, `sigma8toAs`, `correlated_dz_priors`, `one_parameter_hmcode`, `scale_cuts`, `mini_like` |
| Cosmosis Standard Library (CSL) | Generic cosmology modules: `camb_interface`, `extrapolate_power`, `load_nz_fits`, `photoz_bias`, `linear_alignment_interface`, `project_2d` | Same as above |
| COSEBIs library | BandPower computation (`libbandpower.so`) | Same as above; compiled from source if needed for architecture |

### Configuration

The `pipeline.ini` file references paths via the `KCAP_PATH` and `CSL_PATH`
variables.  These must be updated to point to the local installation:

```ini
[DEFAULT]
KCAP_PATH = /path/to/local/kcap/
CSL_PATH  = /path/to/local/cosmosis-standard-library/
```

### Validation step

Before generating model vectors, verify the pipeline can run in non-sampling mode:
```bash
cosmosis pipeline.ini
```
This should load all modules, evaluate the model at the default parameter values
defined in `values.ini`, and produce output without MCMC.

---

## 2. Input inventory

All inputs are located relative to the KiDS-1000 tarball extraction at:
`data/raw/kids_1000/cosmic_shear/KiDS1000_cosmis_shear_data_release/`

### Config files (for BandPower)

| File | Path | Purpose |
|------|------|---------|
| `values.ini` | `chains_and_config_files/main_chains_iterative_covariance/bp/config/values.ini` | Parameter definitions, start points, ranges |
| `pipeline.ini` | `chains_and_config_files/main_chains_iterative_covariance/bp/config/pipeline.ini` | Module chain, runtime settings |
| `priors.ini` | `chains_and_config_files/main_chains_iterative_covariance/bp/config/priors.ini` | Prior distributions |

### Data files

| File | Path | Purpose |
|------|------|---------|
| BandPower FITS | `data_fits/bp_KIDS1000_*.fits` | $n(z)$ (`NZ_SOURCE`, `NZ_LENS`), data vector (`PneE`, `PeeE`), covariance (`COVMAT`) |

### Parameter sets

| Set | Source | Format |
|-----|--------|--------|
| KiDS MAP | `bp/chain/maxpost_multinest_start_C.txt` | 31 columns, first data row |
| Planck baseline | External (Planck 2018, Table 2) | $\Lambda$CDM best-fit parameters |

---

## 3. KiDS MAP parameter extraction

The MAP file has 31 columns.  The first row after the header contains the
maximum-posterior parameter values.  Column mapping:

| Index | Parameter | Role |
|-------|-----------|------|
| 0 | `cosmological_parameters--omch2` | $\Omega_c h^2$ |
| 1 | `cosmological_parameters--ombh2` | $\Omega_b h^2$ |
| 2 | `cosmological_parameters--h0` | $H_0$ |
| 3 | `cosmological_parameters--n_s` | $n_s$ |
| 4 | `cosmological_parameters--s_8_input` | $S_8$ input |
| 5 | `halo_model_parameters--a` | HMCode amplitude |
| 6 | `intrinsic_alignment_parameters--a` | NLA IA amplitude |
| 7–11 | `nofz_shifts--uncorr_bias_1` through `_5` | Uncorrelated photo-$z$ shifts |
| 12–30 | Derived parameters (not used as input) | $S_8$, $\sigma_8$, $A_s$, $\Omega_m$, etc. |

Only columns 0–11 are needed as input to re-generate the prediction vector.
Values are read directly from the first data line of the MAP file.

---

## 4. Planck baseline translation

**Source:** Planck 2018 TT,TE,EE+lowE, Table 2 — base $\Lambda$CDM best-fit.

| Cosmological parameter | Planck value | `values.ini` key |
|------------------------|-------------|------------------|
| $\Omega_c h^2$ | 0.1200 | `omch2` |
| $\Omega_b h^2$ | 0.0224 | `ombh2` |
| $H_0$ | 67.4 | `h0` |
| $n_s$ | 0.965 | `n_s` |
| $\sigma_8$ | 0.811 | `s_8_input` (via $S_8 = \sigma_8 \sqrt{\Omega_m/0.3}$, with $\Omega_m$ computed from $\Omega_c h^2$, $\Omega_b h^2$, $H_0$) |

**Nuisance parameters** (initial placeholders for evaluate-once run):

| Parameter | Placeholder value | Rationale |
|-----------|------------------|-----------|
| HMCode $A$ | 2.6 | Fiducial KiDS `values.ini` default |
| NLA IA $A$ | 1.0 | Common NLA amplitude baseline |
| Photo-$z$ biases (×5) | 0.0 | No-shift baseline |

These are initial evaluate-once defaults, not final nuisance choices.
A production analysis would marginalize or profile them.

---

## 5. Validation protocol

### Success gate

Before any $m_{\rm Planck} - m_{\rm KiDS}$ comparison or SRO residual fit, the
KiDS vector must pass its own validation:

$$
\chi^2(m_{\rm KiDS}) = (d - m_{\rm KiDS})^T C^{-1} (d - m_{\rm KiDS})
$$

must be plausibly close to the published KiDS-1000 best-fit behavior.  If
$\chi^2(m_{\rm KiDS})$ is wildly inconsistent (e.g., orders of magnitude
larger than the published best-fit $\chi^2$), the generated vector is suspect
and full SRO inference must be deferred until the discrepancy is resolved.

### Five validation criteria (from PHASE4B_BLOCKER_MODEL_VECTORS.md)

| # | Criterion | Check |
|---|-----------|-------|
| 1 | Length = 200 | Assert dimension match |
| 2 | No invalid values | `np.isfinite(m).all()` |
| 3 | $\chi^2(m_{\rm Planck})$ finite | `np.isfinite(chi2_planck)` |
| 4 | $\chi^2(m_{\rm KiDS}) \approx$ published | Within $\sim 2\sigma$ of published best-fit $\chi^2$ |
| 5 | Residual structure check | $d - m_{\rm Planck}$ dominated by amplitude-like components, not scale-dependent systematics |

---

## 6. Version-control rule

Generated model vectors are excluded from git:

```
data/generated/
outputs/model_vectors/
```

(This rule is already in `.gitignore`.)

Small summary artifacts (e.g., single-line $\chi^2$ comparison tables) may be
committed for reproducibility.  Full prediction vectors are reconstructed
from config files + parameter sets on demand.

---

## 7. Post-generation steps

Once $m_{\rm KiDS}$ and $m_{\rm Planck}$ pass validation:

1. Compute residuals: $r_{\rm Planck} = d - m_{\rm Planck}$, $r_{\rm KiDS} = d - m_{\rm KiDS}$.
2. Fit the three SRO templates ($t_{\rm src}$, $t_{\rm resp}$, $t_{\rm opt}$) against $r$.
3. Compare model masks (source-only, source+response, source+optics, source+resp+optics) via BIC/AIC under real covariance $C$.
4. Run the $r$-grid sensitivity test for the optics/response $S_8$ loading.
5. Compare the real-covariance conclusion against the v0.3 compressed-proxy result.

See `PHASE4B_BLOCKER_MODEL_VECTORS.md` §8 for the full post-unblock sequence.

---

## 8. Failure modes to anticipate

| Failure | Likely cause | Remedy |
|---------|-------------|--------|
| CAMB import error | `pycamb` not installed or CAMB version mismatch | `pip install camb`; check CAMB version |
| Module not found | `KCAP_PATH` / `CSL_PATH` incorrect | Update `pipeline.ini` paths |
| `libbandpower.so` load error | Architecture mismatch or missing compilation | Compile from COSEBIs source; check OS/arch |
| $\chi^2(m_{\rm KiDS})$ wildly off | Parameter translation error or config mismatch | Verify MAP parameter extraction; check all 12 parameters match `values.ini` keys |
| Output vector wrong shape | Scale-cuts or binning mismatch | Verify `scale_cuts` settings match FITS data vector layout |
| Nuisance defaults produce systematic offset | IA, photo-$z$, or HMCode defaults not matching KiDS assumptions | Profile nuisances at KiDS best-fit values from the chain |