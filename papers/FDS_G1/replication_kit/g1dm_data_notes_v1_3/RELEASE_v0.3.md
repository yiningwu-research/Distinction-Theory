# G1DM Data Notes Toolkit — v0.3 Release Notes (Internal Checkpoint)

## Central diagnostic

The v0.3 compressed public-data diagnostics support a source--response--optics
separation:

$$ T_{\mu\nu}^{D}\neq0,\qquad \mu_{\rm grav}\simeq1,\qquad \mathcal D_{\rm optics}^{S_8}\neq0 \quad \text{at compressed-proxy level}. $$

- **Source / carrier floor:** Planck~2018 chains strongly exclude $\Omega_c h^2=0$
  ($>\!100\sigma$). A nonzero CDM-like carrier floor is required.
- **Response / growth leakage:** DESI DR1 `_mu_sigma` chains do not require
  $\mu_0\neq0$. Growth-only is disfavored in all dataset combinations.
- **Optics / low-$z$ lensing-structure:** Independent $S_8$ compressed proxies
  from KiDS-1000 and DES Y3 select a source+optics mask over source-only, with
  $r$-stable results. The optics component is motivated at compressed-proxy level.

This is not production multi-probe evidence. The optics component is motivated by
compressed $S_8$ proxies and remains pending full $3\times2$pt covariance, nuisance
profiling, cross-probe consistency checks, and independent pipeline replication.

---

## Version history

| Version | Date | Scientific increment |
|---------|------|---------------------|
| v0.2 | — | Smoke tests (13/13). Note 3 chain covariance (`summarize_samples`, `load_chain_columns`). |
| v0.2.1 | — | DESI DR1 Note 3 real-chain diagnostics: FS/BAO+Planck and +DESY3joint. DEMOTION_PATH_MAP with 4-row diagnostic. `.gitignore` data/raw and outputs. Note 1+3 technical note. Companion G v0.2.1. |
| v0.2.2 | — | Note 4 Phase 1a SRO sanity check: Scenario A (FS/BAO+Planck) and Scenario B (+DESY3joint). Capped-source robustness. Validates pipeline logic. |
| **v0.3** | **2026-06-03** | **Note 4 Phase 2: independent S₈ compressed-proxy audit.** KiDS-1000 and DES Y3 S₈ tension proxies. Five-point r-grid sensitivity. Source+optics consistently selected ($r$-stable). Capped-source checks confirm rankings not dominated by $100\sigma$ carrier-floor row. v0.3 S₈ addendum. Companion G updated. |

---

## Artifact list

### Papers and technical notes

| File | Description | Pages |
|------|-------------|-------|
| `Companion G v0.2` (in DT-Research) | Companion G public-data summary with v0.3 results | — |
| `docs/G1DM_Note_1_3_Carrier_Floor_Growth_Leakage.{tex,pdf}` | Note 1+3 technical note: carrier floor + growth leakage | 4 |
| `docs/G1DM_Note_v0.3_S8_Proxy_Addendum.{tex,pdf}` | v0.3 addendum: independent S₈ proxy audit | 2 |

### Toolkit

| Path | Description |
|------|-------------|
| `src/g1dm/` | Core I/O, stats, plotting utilities |
| `notes/` | 5 executable data-note scripts (Note 1–5) |
| `tests/` | 14 smoke tests (14/14 pass) |
| `config/data_registry.yml` | Official data landing pages and expected local paths |
| `data/compressed_constraints/` | Demo compressed constraints for Notes 2–3 |
| `data/templates/` | SRO YAML templates and v0.3 S₈ proxy scenario files |
| `requirements.txt` | Python dependencies |
| `Makefile` | `make test`, `make demo` targets |

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Quick-start guide |
| `docs/DATA_DOWNLOAD_PLAN.md` | Dataset-by-dataset acquisition plan |
| `docs/DEMOTION_PATH_MAP.md` | Note-to-demotion-path mapping with real-chain results |
| `docs/NOTE4_SRO_PROTOCOL.md` | Phase 1a and Phase 2 SRO audit protocol and results |
| `docs/G1DM_Note_1_3_Carrier_Floor_Growth_Leakage.{tex,pdf}` | Technical note |
| `docs/G1DM_Note_v0.3_S8_Proxy_Addendum.{tex,pdf}` | v0.3 addendum |

### Excluded (`.gitignore`)

- `data/raw/` — Real chain files and large data products
- `outputs/` — Generated outputs, tables, and figures
- `.venv/` — Python virtual environment

---

## Reproducibility

```bash
cd /Users/next/G_production_code/g1dm_data_notes

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run all tests (14/14)
PYTHONPATH=src python -m pytest tests/ -v

# Run demo notes (no external data needed)
make demo

# Run Note 3 with downloaded DESI DR1 chains
PYTHONPATH=src python notes/note3_lensing_growth_split.py \
  --chain-dir data/raw/desi_dr1/.../fs_bao_planck \
  --mu-col mu0 --sigma-col Sigma0 \
  --out outputs/note3_fsbao_planck

# Run Note 4 Phase 2 S8 proxy audit
PYTHONPATH=src python notes/note4_sro_sparse_audit.py \
  --observables data/templates/sro_v0.3_S8proxy_kids.yml \
  --r-value 0 --scenario-label kids_r0 --out outputs/note4_v03_kids_r0
```

### Required manual data

- Planck 2018 chains: Planck Legacy Archive (`https://pla.esac.esa.int/`)
- DESI DR1 chains: `https://data.desi.lbl.gov/doc/releases/dr1/vac/full-shape-cosmo-params/`
- See `docs/DATA_DOWNLOAD_PLAN.md` for full acquisition instructions.

---

## Tags

| Tag | Description |
|-----|-------------|
| `g1dm-notes-v0.2` | Smoke tests + Note 3 chain covariance |
| `g1dm-notes-v0.2.1` | DESI DR1 Note 3 real-chain diagnostics |
| `g1dm-toolkit-v0.2.1` | Same as v0.2.1 |
| `g1dm-note-1-3-v0.2.1` | Note 1+3 technical note |
| `g1dm-toolkit-v0.2.2` | Note 4 Phase 1a SRO sanity check |
| `g1dm-toolkit-v0.3` | Note 4 Phase 2 S8 compressed-proxy audit |
| **`g1dm-release-v0.3`** | **v0.3 frozen compressed-diagnostic layer** |

---

## What changed in v0.3

- **Note 4 script:** Added `--r-value` and `--scenario-label` flags, `resolve_design_value()` for r-dependent design matrices, Phase labeling, r-value interpretation notes.
- **New YAMLs:** `sro_v0.3_S8proxy_kids.yml`, `sro_v0.3_S8proxy_desy3.yml` — 3-row z-score vectors with S₈ tension proxies and r-grid metadata.
- **S8 proxy values:**
  - Planck 2018: $S_8 = 0.831 \pm 0.013$
  - KiDS-1000: $S_8 = 0.759^{+0.024}_{-0.021}$, $z = 2.77\sigma$
  - DES Y3: $S_8 = 0.776 \pm 0.017$, $z = 2.57\sigma$
- **r-grid:** $r \in \{0, 0.25, 0.5, 0.75, 1.0\}$ for response-loading fraction in $[0, r, 1-r]$ design row.
- **Key result:** Source+optics is consistently preferred across the full r-grid for both KiDS and DES Y3. Capped-source ($z=10$) checks preserve rankings.
- **Addendum:** 2-page LaTeX technical note documenting Phase 2.
- **Companion G:** Updated public-data summary with v0.3 S₈ proxy result.
- **Tests:** 13 → 14 (added `test_note4_r_value_option`).

---

## Caveats

1. **Not production evidence.** This is a compressed Gaussian SRO audit, not a
   production multi-probe likelihood. Full $3\times2$pt covariance, pipeline
   cross-correlation, and systematic nuisance profiling are required for a
   production-level result.

2. **S₈ proxy is a tension diagnostic.** The $S_8$ tension proxy does not directly
   measure a Weyl/lensing residual in the G1DM sense. Channel assignment to optics
   is a model choice tested for $r$-stability.

3. **$r=1$ behavior.**
   At $r=1$, the full $S_8$ tension is assigned to the response channel,
   creating artificial response pressure not supported by DESI $\mu_0$.
   Source+optics selection at $r=1$ should be interpreted as a consequence of
   the proxy design, not a growth-leakage detection.

4. **No combined cosmological evidence claim.**
   This audit tests model compression within the compressed SRO framework.
   It does not constitute combined cosmological parameter estimation.
