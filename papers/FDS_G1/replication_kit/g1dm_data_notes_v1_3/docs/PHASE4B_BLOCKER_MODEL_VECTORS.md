# Phase 4b Blocker: KiDS-1000 Model-Vector Dependency

**Status:** BLOCKED. Full Phase 4b SRO template fitting cannot proceed until
Planck-like and KiDS-best-fit theory prediction vectors are generated.

---

## 1. Why full Phase 4b is blocked

The SRO template-level residual fit requires:

$$
r = d - m_0
$$

where $d$ is the KiDS BandPower data vector (200 elements: 80 PneE + 120 PeeE),
$m_0$ is a fiducial model vector, and $r$ is the residual that SRO masks are
tested against.  The standard SRO amplitude fit is:

$$
\hat a = (T^T C^{-1} T)^{-1} T^T C^{-1} (d - m_0).
$$

The KiDS-1000 FITS release provides $d$ (`PneE`, `PeeE` extensions) and $C$
(`COVMAT` extension), but does **not** include $m_0$ vectors.  Without $m_0$,
the residual $d - m_0$ is undefined, and no SRO mask comparison is meaningful.

The Phase 4b-lite covariance readiness check confirmed that $C$ is positive
definite (Cholesky OK, $\kappa \approx 4.6\times 10^5$, shear-null S/N = 39.4),
but this is a shear-signal detection statistic, not an SRO residual test.

---

## 2. Required model vectors

| Vector | Parameters | Source |
|--------|-----------|--------|
| $m_{\rm Planck}$ | Planck 2018 best-fit $\Lambda$CDM | External: $\Omega_c h^2 = 0.120$, $\Omega_b h^2 = 0.0224$, $h = 0.674$, $n_s = 0.965$, $\sigma_8 = 0.811$ (Planck 2018, Table~2). Nuisance parameters: NLA IA $A = 1.0$, photo-$z$ biases $= 0$, HMCode $A = 2.6$. Neutrinos: $m_\nu = 0.06$ eV (one massive). CosmoSIS config matches the KiDS `values.ini` defaults for fixed parameters. |
| $m_{\rm KiDS}$ | KiDS-1000 MAP | `chains_and_config_files/main_chains_iterative_covariance/bp/chain/maxpost_multinest_start_C.txt` — first data row gives the MAP parameter set (31 columns). |

**Note on Planck parameters:** The numbers above are a Planck-like baseline,
consistent with the standard $\Lambda$CDM values used in the KiDS-Planck
tension literature.  Actual model-vector generation requires translating these
into KCAP/CosmoSIS-compatible inputs, including $A_s$ (or $S_8$), $\tau$,
nonlinear prescription (halofit mead2015), baryon feedback (HMCode $A$),
intrinsic alignment amplitude, and photo-$z$ bias defaults.

Both vectors must be generated in the same 200-element BandPower E-mode format
as the data, matching the 80 PneE (galaxy-shear BandPower) + 120 PeeE
(cosmic-shear E-mode BandPower) concatenation, with angular scale cuts
applied by the `scale_cuts` module.

---

## 3. Generator stack (from the KiDS pipeline.ini)

The KiDS-1000 CosmoSIS/KCAP pipeline module chain is:

```
sample_S8 → sigma8toAs → correlated_dz_priors → one_parameter_hmcode
→ camb → extrapolate_power → load_nz_fits → source_photoz_bias
→ linear_alignment → projection → bandpower_shear_e → scale_cuts
```

Key components with their roles:

| Module | Role |
|--------|------|
| `camb` | Boltzmann solver (mode=transfer, nonlinear=halofit mead2015, $k_{\rm max}=20$, $z_{\rm max}=6$, neutrino_hierarchy=normal) |
| `extrapolate_power` | Extrapolate P(k) to $k_{\rm max}=500$ for small-scale integration |
| `load_nz_fits` | Load $n_i(z)$ from the FITS file `NZ_SOURCE` / `NZ_LENS` extensions |
| `source_photoz_bias` | Additive photo-$z$ bias shifts (5 bins) |
| `linear_alignment` | NLA intrinsic alignment model (`bk_corrected` method, one amplitude) |
| `projection` | Project 3D P(k) to 2D shear power spectra $C^{ij}(\ell)$, $\ell \in [1, 10^4]$ |
| `bandpower_shear_e` | Convert $C^{ij}(\ell)$ to BandPower E-modes (8 log-spaced bands, $\ell \in [100, 1500]$, tophat response) |
| `scale_cuts` | Apply angular scale cuts to match the data vector |

**Key dependency:** CAMB (or CLASS) must be installed and callable by CosmoSIS.
The `pipeline.ini` references `pycamb`, which is available via `pip install camb`.

---

## 4. Required inputs for model generation

| Input | Location | Status |
|-------|----------|--------|
| `values.ini` | `bp/config/` — parameter definitions and default ranges | Available |
| `pipeline.ini` | `bp/config/` — module chain and settings | Available |
| `priors.ini` | `bp/config/` — prior distributions | Available |
| $n(z)$ distributions | `bp_KIDS1000_*.fits` — extensions `NZ_SOURCE` (5 bins), `NZ_LENS` (2 bins) | Available |
| Covariance $C$ | `bp_KIDS1000_*.fits` — extension `COVMAT` (200×200) | Available |
| KiDS MAP parameters | `bp/chain/maxpost_multinest_start_C.txt` — 31-column MAP | Available |
| Planck parameters | External (Planck 2018 Table 2) | Available |
| KCAP/CosmoSIS install | Not yet installed | **Required** |
| CAMB Python interface | Not yet installed | **Required** |

---

## 5. Validation criteria for model vectors

Before any SRO mask comparison, the generated model vectors must satisfy:

1. **Length match:** Output shape must be exactly 200.
2. **No invalid values:** No `NaN`, `Inf`, or `-Inf` in the output.
3. **Finite $\chi^2$:** $\chi^2(m_{\rm Planck}) = (d - m_{\rm Planck})^T C^{-1} (d - m_{\rm Planck})$ is finite.
4. **Consistency check:** $\chi^2(m_{\rm KiDS})$ reasonably close to the published best-fit $\chi^2$ from the KiDS-1000 analysis (consistency, not exact reproduction).
5. **Template slope check:** The residual vector $d - m_{\rm Planck}$ shows amplitude-like structure (not dominated by scale-dependent systematics).

**Failure modes to anticipate:**
- Unit mismatch between generated and data vectors (power spectrum conventions).
- Angular bin ordering differences between `bandpower_shear_e` output and FITS data vector layout.
- CAMB version / cosmology setting differences producing sub-percent offsets.
- Nuisance parameter defaults ($A_{\rm IA}$, photo-$z$ biases) not matching the implicit assumptions in the $S_8$ tension literature.

---

## 6. What NOT to claim before vectors exist

| Prohibited claim | Why |
|-----------------|-----|
| "v0.3 $S_8$ conclusion survives real covariance" | No residual $d - m_0$ computed; no SRO mask fit performed |
| "BandPower shear-null S/N = 39.4 confirms $S_8$ tension" | S/N measures overall shear signal strength, not Planck-vs-KiDS residual |
| "Source+optics is preferred under real covariance" | No template fit; no model comparison; no BIC ranking |
| "Optics channel independently selected" | Same as above |

The Phase 4b-lite readiness check **only** verifies that the data vector and
covariance can be loaded and that $C$ is positive definite.  It does not
constitute an SRO evidence result.

---

## 7. Version-control rule

Generated model vectors may be large (200 float64 × N_parameter_sets).
When generation begins:

- Place vectors under `data/generated/model_vectors/`
- Keep them **out of git** (add to `.gitignore`):
  ```
  data/generated/
  outputs/model_vectors/
  ```
- Small compressed summary artifacts (e.g., one-line $\chi^2$ tables) may be
  committed for reproducibility.

---

## 8. Next step after unblock

Once $m_{\rm Planck}$ and $m_{\rm KiDS}$ are generated:

1. Compute residuals: $r_{\rm Planck} = d - m_{\rm Planck}$, $r_{\rm KiDS} = d - m_{\rm KiDS}$.
2. Fit the three SRO templates ($t_{\rm src}$, $t_{\rm resp}$, $t_{\rm opt}$) against $r$.
3. Compare model masks (source-only, source+response, source+optics, source+resp+optics) via BIC/AIC.
4. Run the $r$-grid sensitivity test for the optics/response $S_8$ loading.
5. Compare the real-covariance conclusion against the v0.3 compressed-proxy result.
