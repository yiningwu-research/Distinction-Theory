# v0.4 External Runbook: KCAP/CosmoSIS Model-Vector Generation

**Purpose:** Reproducible procedure to generate KiDS BandPower model vectors
$m_{\rm KiDS}$ and $m_{\rm Planck}$ on a machine with Fortran/C toolchain,
unblocking Phase 4b full SRO template fitting.

**Status:** Toolchain implemented (`1f286f6`). Model vectors not yet generated.

---

## 1. System requirements

| Requirement | Version / Notes |
|-------------|----------------|
| OS | macOS (Apple Silicon or Intel) or Linux (x86_64) |
| Compilers | `gcc` + `gfortran` (CosmoSIS build dependency) |
| Python | 3.9+ |
| CAMB | `pip install camb` (already in `requirements.txt`) |
| CosmoSIS | Install from source or release binary; not available via `pip` |
| KCAP modules | Clone/copy KiDS Cosmology Analysis Pipeline |
| Cosmosis Standard Library (CSL) | Clone/copy CSL repository |
| COSEBIs library | `libbandpower.so` — compile from source if architecture mismatch |
| KiDS-1000 data | Tarball extracted at `data/raw/kids_1000/cosmic_shear/`; must be copied to external machine or re-downloaded per `docs/KIDS1000_DOWNLOAD_PLAN.md` |

---

## 2. Directory assumptions

The runbook assumes the following layout. Adjust paths to match the external machine.

| Variable | Default (relative to `g1dm_data_notes/`) | Must resolve |
|----------|------------------------------------------|-------------|
| `KIDS_DATA` | `data/raw/kids_1000/cosmic_shear/KiDS1000_cosmic_shear_data_release/` | Pipeline `pipeline.ini` references |
| `KCAP_PATH` | User-defined (e.g., `/path/to/kcap/`) | All KCAP module imports |
| `CSL_PATH` | User-defined (e.g., `/path/to/cosmosis-standard-library/`) | All CSL module imports |
| `COSMOSIS_BIN` | `cosmosis` in `$PATH` | Pipeline runner script uses this |
| `COSMOSIS_MODULE_PATH` | `$KCAP_PATH:$CSL_PATH` | CosmoSIS module discovery |
| `outputs/phase4c_prep/` | Created by scripts | Model vectors, configs, validation |
| Ignored | `data/raw/`, `data/generated/`, `outputs/` | Per `.gitignore` |

---

## 3. Install checklist

```
[ ] Create Python virtual environment
    python3 -m venv .venv && source .venv/bin/activate

[ ] Install Python dependencies
    pip install -r requirements.txt
    # includes: camb, numpy, scipy, pandas, matplotlib, pyyaml, astropy, getdist, pytest

[ ] Install CosmoSIS (source build)
    git clone https://github.com/joezuntz/cosmosis.git
    cd cosmosis && make && cd ..
    # or use a pre-built CosmoSIS release

[ ] Install/verify KCAP modules
    # KCAP repository: verify URL against KiDS-1000 release documentation
    # Place at KCAP_PATH; modules referenced in pipeline.ini include:
    #   sample_S8, sigma8toAs, correlated_dz_priors, one_parameter_hmcode,
    #   scale_cuts, mini_like

[ ] Install/verify CSL modules
    # Cosmosis Standard Library
    # Place at CSL_PATH; modules referenced in pipeline.ini include:
    #   camb_interface, extrapolate_power, load_nz_fits, photoz_bias,
    #   linear_alignment_interface, project_2d

[ ] Compile COSEBIs libbandpower.so
    # If architecture mismatch: compile from COSEBIs source
    # Verify: file libbandpower.so (should match system architecture)

[ ] Copy KiDS-1000 data
    # Copy tarball from source machine or re-download:
    curl -LO https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_cosmic_shear_data_release.tgz
    tar -xzf KiDS1000_cosmic_shear_data_release.tgz
    # Expected: data/raw/kids_1000/cosmic_shear/KiDS1000_cosmic_shear_data_release/

[ ] Verify environment
    python -c "import camb; print('CAMB', camb.__version__)"
    cosmosis --version
    ls data/raw/kids_1000/cosmic_shear/KiDS1000_cosmic_shear_data_release/

[ ] Verify pipeline.ini paths
    # Open bp/config/pipeline.ini
    # Update KCAP_PATH and CSL_PATH to local paths
    # Update INPUT_FOLDER to point to KIDS_DATA

[ ] Dry-run evaluate-only
    export COSMOSIS_MODULE_PATH="$KCAP_PATH:$CSL_PATH"
    cosmosis $KIDS_DATA/chains_and_config_files/main_chains_iterative_covariance/bp/config/pipeline.ini
    # Should load all modules and produce output without MCMC
```

---

## 4. Run sequence

Execute in order. Each step gates the next.

### Step 4.1: Extract MAP parameters

```bash
cd g1dm_data_notes
source .venv/bin/activate

MAPFILE="data/raw/kids_1000/cosmic_shear/KiDS1000_cosmic_shear_data_release/chains_and_config_files/main_chains_iterative_covariance/bp/chain/maxpost_multinest_start_C.txt"

PYTHONPATH=src python scripts/extract_kids_map_params.py \
  --map-file "$MAPFILE" \
  --out outputs/phase4c_prep
```

**Expected:** `outputs/phase4c_prep/values_kids.ini` and `values_planck.ini`.

### Step 4.2: Configure the pipeline

```bash
CONFIG_DIR="data/raw/kids_1000/cosmic_shear/KiDS1000_cosmic_shear_data_release/chains_and_config_files/main_chains_iterative_covariance/bp/config"

# Back up original values.ini
cp "$CONFIG_DIR/values.ini" "$CONFIG_DIR/values.original.ini"

# Copy KiDS MAP values as active config
cp outputs/phase4c_prep/values_kids.ini "$CONFIG_DIR/values.ini"
```

**Verify:** `pipeline.ini` `KCAP_PATH` and `CSL_PATH` point to local installs.

### Step 4.3: Run CosmoSIS evaluate-only

```bash
cd "$KIDS_DATA"
export COSMOSIS_MODULE_PATH="$KCAP_PATH:$CSL_PATH"
cosmosis "$CONFIG_DIR/pipeline.ini" 2>&1 | tee outputs/phase4c_prep/cosmosis_kids.log
```

**Expected:** CosmoSIS completes without MCMC errors. The BandPower prediction
vector is in the `scale_cuts_output` section of the CosmoSIS output.

### Step 4.4: Extract and save model vector

The exact extraction depends on how CosmoSIS writes its output (text file,
HDF5, or stdout).  Adapt the extraction to the CosmoSIS output format:

```bash
# Template: extract the BandPower E-mode prediction vector
# Save as:
python -c "import numpy as np; np.save('outputs/phase4c_prep/m_kids.npy', model_vector)"
```

**Expected:** `outputs/phase4c_prep/m_kids.npy` — shape `(200,)`.

### Step 4.5: Validate m_KiDS

```bash
PYTHONPATH=src python scripts/validate_model_vector.py \
  --model-vector outputs/phase4c_prep/m_kids.npy \
  --tag KiDS \
  --out outputs/phase4c_prep
```

**Expected:** `outputs/phase4c_prep/validate_kids.json`.

### Step 4.6: If Gate 4 passes — generate m_Planck

```bash
# Copy Planck baseline values
cp outputs/phase4c_prep/values_planck.ini "$CONFIG_DIR/values.ini"

# Run CosmoSIS evaluate-only
cosmosis "$CONFIG_DIR/pipeline.ini" 2>&1 | tee outputs/phase4c_prep/cosmosis_planck.log

# Extract and save
python -c "import numpy as np; np.save('outputs/phase4c_prep/m_planck.npy', model_vector)"

# Validate
PYTHONPATH=src python scripts/validate_model_vector.py \
  --model-vector outputs/phase4c_prep/m_planck.npy \
  --tag Planck \
  --out outputs/phase4c_prep
```

### Step 4.7: Restore original config

```bash
cp "$CONFIG_DIR/values.original.ini" "$CONFIG_DIR/values.ini"
```

---

## 5. Expected outputs

| File | Source | Phase |
|------|--------|-------|
| `outputs/phase4c_prep/values_kids.ini` | Step 4.1 — MAP extraction | 4c-prep |
| `outputs/phase4c_prep/values_planck.ini` | Step 4.1 — MAP extraction | 4c-prep |
| `outputs/phase4c_prep/m_kids.npy` | Step 4.4 — CosmoSIS output | 4c-prep |
| `outputs/phase4c_prep/m_planck.npy` | Step 4.6 — CosmoSIS output | 4c-prep |
| `outputs/phase4c_prep/validate_kids.json` | Step 4.5 — validation | 4c-prep |
| `outputs/phase4c_prep/validate_planck.json` | Step 4.6 — validation | 4c-prep |
| `outputs/phase4c_prep/cosmosis_kids.log` | Step 4.3 — CosmoSIS log | 4c-prep |
| `outputs/phase4c_prep/cosmosis_planck.log` | Step 4.6 — CosmoSIS log | 4c-prep |

---

## 6. Gate conditions

These gates are enforced programmatically by `scripts/validate_model_vector.py`.
No SRO inference is allowed until all gates pass.

| Gate | Check | Enforcement |
|------|-------|-------------|
| **1** | `m_KiDS.shape == (200,)` | Validation script — `len_ok` |
| **2** | All values in `m_KiDS` are finite | Validation script — `all_finite` |
| **3** | $\chi^2(d - m_{\rm KiDS})$ is finite | Validation script — `chi2_finite` |
| **4** | $\chi^2(d - m_{\rm KiDS})$ is plausibly close to the published KiDS BandPower best-fit behavior, or otherwise explicitly explained by a known configuration mismatch | Validation script — `chi2_per_dof`; human review required |
| **5** | Residual $|d - m_{\rm Planck}| / \sigma$ shows amplitude-like structure | Validation script — `n_outliers_3sigma`, `max_r_sigma` |
| **6** | **Only after Gates 1–4 pass:** generate $m_{\rm Planck}$ | Procedural |
| **7** | **Only after all gates pass:** resume Phase 4b SRO template fit | Procedural |

---

## 7. Failure modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError` in CosmoSIS log | `KCAP_PATH` or `CSL_PATH` incorrect | Update `pipeline.ini` paths or `COSMOSIS_MODULE_PATH` |
| CAMB import error | CAMB not installed in venv | `pip install camb` |
| `libbandpower.so` load error | Architecture mismatch (ARM vs x86) | Compile from COSEBIs source for target architecture |
| Output vector length ≠ 200 | Scale-cuts angular bin mismatch | Verify `scale_cuts` settings in `pipeline.ini` match data FITS |
| $\chi^2(m_{\rm KiDS})$ implausibly large | Parameter translation error or config mismatch | Verify all 12 MAP params match extracted `values_kids.ini`; check against shipped original `values.ini` |
| Vector ordering mismatch | PneE/PeeE concatenation order differs | Verify `bandpower_shear_e` → `scale_cuts` ordering matches FITS data vector layout |
| Cosmo params not recognized | `values.ini` format differs from shipped version | Compare against `values.original.ini`; check section headers and key names |
| CosmoSIS segfault | CAMB/GSL/Fortran library mismatch | Reinstall CAMB; check `libgfortran` version matches compilation |

---

## 8. No-claim rule

**Throughout this procedure, the v0.3 compressed-proxy claim remains the
only active scientific claim:**

> $T_{\mu\nu}^{D}\neq0$, $\mu_{\rm grav}\simeq1$, $\mathcal D_{\rm optics}^{S_8}\neq0$
> at compressed-proxy level.

The following are prohibited until Gate 4 passes and full Phase 4b SRO
template fitting is completed:

1. "Real-covariance SRO confirmed"
2. "Weyl/optics channel independently selected under real covariance"
3. "v0.3 conclusion survives production-data validation"
4. "KiDS shear-null S/N = 39.4 means S₈ tension confirmed"
5. Any update to Companion G scientific conclusions

The v0.4 branch provides production-path infrastructure.  It has not
modified the v0.3 scientific claim.
