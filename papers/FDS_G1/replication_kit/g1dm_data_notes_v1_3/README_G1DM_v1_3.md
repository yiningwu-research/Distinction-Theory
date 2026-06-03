# G1DM Data Notes v1.3 — Replication Layer

This directory provides the G1DM compressed diagnostic layer supporting the
FDS--G1 v1.3 Companion G / matter-sector strengthening.  It contains the
executable toolkit, summary outputs, technical notes, and production-path
documentation.

## Central diagnostic

```
T_D != 0,  mu_grav ~= 1,  D_optics_S8 != 0  at compressed-proxy level.
```

- **Carrier floor (Note 1):** Planck 2018 Omega_c h^2 = 0.1200 +/- 0.0012.
  Omega_c h^2 = 0 excluded at >100 sigma. Pure Weyl-DM cannot replace full CDM.
- **Growth leakage suppressed (Note 3):** DESI DR1 base_mu_sigma chains.
  mu0 consistent with 0 in both FS/BAO+Planck and FS/BAO+Planck+DESY3joint.
- **Optics pressure (Note 4 Phase 2):** Independent S8 compressed proxies from
  KiDS-1000 (2.77 sigma) and DES Y3 (2.57 sigma) select source+optics over
  source-only at r-stable compressed level.

## Claim boundary

This is a compressed public-chain diagnostic layer, NOT production
multi-probe confirmation.  The full 3x2pt covariance-aware SRO audit is
blocked pending KCAP/CosmoSIS model-vector generation (see v0.4 docs).

## Directory structure

```
g1dm_data_notes_v1_3/
  README_G1DM_v1_3.md        This file
  requirements.txt            Python dependencies
  Makefile                    make test, make demo targets
  .gitignore                  Excludes data/raw/, outputs/, .venv/
  src/g1dm/                   Core I/O, stats, plotting utilities
  notes/                      Note 1-5 executable scripts
  tests/                      Smoke test suite (17/17 pass)
  config/                     data_registry.yml — official data landing pages
  data/compressed_constraints/ Compressed DESI mu_sigma constraints (demo)
  data/templates/              SRO YAML templates (Phase 1a, Phase 2 S8 proxies)
  scripts/                    MAP extraction, model-vector validation, pipeline runner
  docs/                       Technical notes, protocols, external runbook
  outputs_summary/            Compressed output JSONs and CSVs
  RELEASE_v0.3.md             v0.3 release notes
```

## Quick start

```bash
cd g1dm_data_notes_v1_3
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m pytest tests/ -v   # 17/17 pass
make demo                                     # Run all demo notes
```

## Key technical notes (in docs/)

| File | Description |
|------|-------------|
| `G1DM_Note_1_3_Carrier_Floor_Growth_Leakage.pdf` | Note 1+3: carrier floor and growth-leakage suppression |
| `G1DM_Note_v0.3_S8_Proxy_Addendum.pdf` | v0.3 addendum: independent S8 compressed-proxy audit |
| `DEMOTION_PATH_MAP.md` | Five-row note-to-demotion-path mapping |
| `NOTE4_SRO_PROTOCOL.md` | Phase 1a and Phase 2 SRO protocol and results |
| `V0_4_PLAN.md` | v0.4 development plan: covariance-aware 3x2pt SRO audit |
| `V0_4_EXTERNAL_RUNBOOK.md` | External-machine runbook for KCAP/CosmoSIS model vectors |
| `PHASE4B_BLOCKER_MODEL_VECTORS.md` | Why full Phase 4b SRO is blocked |
| `KCAP_COSMOSIS_MODEL_VECTOR_PLAN.md` | Model-vector generation plan |
| `KIDS1000_DOWNLOAD_PLAN.md` | KiDS-1000 data download instructions |
| `DATA_DOWNLOAD_PLAN.md` | Dataset-by-dataset acquisition plan |

## Excluded from this kit

- Raw Planck, DESI, KiDS, or DES Y3 chains
- Large FITS data files
- Generated model vectors
- KCAP/CosmoSIS installation and compiled libraries

See `docs/DATA_DOWNLOAD_PLAN.md` and `docs/KIDS1000_DOWNLOAD_PLAN.md` for
download instructions.  The summary outputs under `outputs_summary/` contain
the compressed diagnostic numbers that support the v1.3 G1DM-C0 claim.
