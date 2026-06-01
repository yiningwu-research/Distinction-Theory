# Phase 3E-2: G1 PeeE BandPower Model-Smoke

## Status
\boxed{\text{Phase 3E-2: PASS}}

## Summary
Phase 3E-2 computes finite diagnostic PeeE-only BandPower χ² values for G1 model predictions. The calculation validates model/projector integration but is not an optimized likelihood result and is not used as model evidence.

## Results
- **lcdm**: χ² = 519.23 (χ²/n = 4.33) for 120 data points, finite = True
- **m34**: χ² = 517.32 (χ²/n = 4.31) for 120 data points, finite = True
- **mkappa**: χ² = 517.43 (χ²/n = 4.31) for 120 data points, finite = True

## Implementation Details
- **Nuisance status**: smoke diagnostic; no optimized BandPower nuisance refit
  - m_i: applied_by_script (checked that pipeline returns raw C_l)
  - dz_i: applied_by_pipeline
  - A_IA: applied_by_pipeline
- **BandPower configuration**: 8 log bins from ℓ=100 to ℓ=1500, projection uses ⟨ℓ² C_ℓ / 2π⟩ averaging
- **Input data**: Verified KiDS-1000 PeeE 120-element vector with 120×120 covariance

## Output Files
All outputs stored in: /Users/next/G_production_code/phase3a_kids_3x2pt_audit/outputs/bandpower_peeE_model_smoke
- Predictions: lcdm_peeE_prediction.csv, m34_peeE_prediction.csv, mkappa_peeE_prediction.csv
- Summary: peeE_model_smoke_summary.md
- Manifest: bandpower_peeE_model_smoke_manifest.json

## Interpretation Boundary
These χ² values are PeeE-only BandPower diagnostic smoke values. They are not optimized BandPower likelihood results and are not used as model evidence.
