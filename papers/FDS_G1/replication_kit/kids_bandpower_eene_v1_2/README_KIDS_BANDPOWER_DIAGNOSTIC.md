# KiDS BandPower EE+nE Diagnostic Bridge (v1.2)

This directory contains the **KiDS BandPower EE+nE diagnostic bridge**
infrastructure for the FDS-G1 v1.2 paper.

## Claim Boundary

**This is an infrastructure/diagnostic validation layer, NOT an optimized
likelihood, NOT model evidence, and NOT a completed full 3×2pt analysis.**

What it provides:
- Product/covariance/order audit (Phase 3A)
- PeeE projector and PneE density kernel smoke tests (Phase 3E–3I)
- 200-row EE+nE bandpower bridge (Phase 3J)
- Local refit, mock recovery, noisy mock ensemble (Phase 4B–4C)
- Nuisance robustness: bias prior stress, shear m prior stress,
  IA prior stress (Phase 4D)
- Prior-regularized refit (Phase 4G)
- Toy nn closure diagnostic (Phase 4H)

What it does NOT provide:
- Optimized stage-3d lensing likelihood
- Production model evidence
- Full 3×2pt cosmological constraints
- Usable real Pnn / w(theta) clustering vector

## Contents

```
src/                  Phase 3 and Phase 4 diagnostic scripts (76 total)
configs/              YAML/JSON configs for all diagnostic layers
outputs_summary/      20 summary Markdown reports (PHASE3*, PHASE4*)
data_manifest/        Row-order conventions, covariance shapes, data policy
README_KIDS_BANDPOWER_DIAGNOSTIC.md  This file
```

## Script Status

The Python scripts in `src/` are from the internal diagnostic pipeline.
They are provided as-is for transparency. Some may have dependencies on
internal data paths or not-yet-packaged utilities.

**KiDS BandPower scripts are being packaged from the internal diagnostic
pipeline. The current release provides diagnostic summaries, manifests,
row-order conventions, and boundary statements; raw KiDS products are not
redistributed.**

## Data

Raw KiDS-1000 data is **not redistributed**. See `data_manifest/` for
download instructions, expected SHA256 hashes, row-order conventions,
and covariance shape documentation.

## Dependencies

- `classy` (CLASS) for theoretical predictions
- `numpy`, `scipy`, `pandas`
- Additional dependencies in the kit's `requirements_kids.txt`

## References

See the individual PHASE*.md summaries in `outputs_summary/` for detailed
methodology, results, and validation status.
