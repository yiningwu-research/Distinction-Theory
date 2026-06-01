# FDS-G1 Replication Kit — Reproducibility Status

| Evidence Layer | Status | Reproducible? | Location | Notes |
|---|---|---|---|---|
| Exact-pilot (v1.0-rc3) | Superseded | Yes | `paper_original_code/` | 3 seeds, dlogZ=0.5; retained for provenance |
| Medium-prior 3-seed (v1.1) | Superseded | Yes | `outputs_medium_audit/` | 3 seeds, dlogZ=0.5; homogeneous seven-model audit |
| **Medium-prior 8-seed production-refined (v1.2)** | **Canonical** | **Yes** | `production_evidence_v1_2/` | **8 seeds, dlogZ=0.1; see configs + runner scripts** |
| KiDS shear-only diagnostic (v1.1) | Diagnostic | Yes | `kids_shear_only/` | Requires CLASS (`classy`) dependency; external KiDS data |
| KiDS BandPower EE+nE bridge (v1.2) | Diagnostic | Yes | `kids_bandpower_eene_v1_2/` | Validated compressed-space bridge; no nn clustering |
| Full 3x2pt | **Blocked** | No | `phase5_nn_sourcing/` | Pending real nn clustering vector or catalog-level recomputation |

## Notes

- **Production-refined audit (v1.2, canonical):** Fully scripted in `production_evidence_v1_2/src/`. Run `bash production_evidence_v1_2/README_RUN_PRODUCTION.md` for the full 56-job sequence. Per-seed JSON outputs, summary CSV, and generated Table 3 are committed.
- **KiDS diagnostics:** Both shear-only and BandPower layers require external KiDS data (not redistributed). See respective READMEs for download instructions and expected SHA256 hashes.
- **Full 3x2pt:** Phase 5 sourcing audits confirmed a 300x300 BandPower covariance exists and its first 200x200 block matches the validated EE+nE covariance, but no usable real Pnn/clustering data vector is locally available in BandPower format. Blocked until external sourcing or catalog-level recomputation.
- **Independent reimplementation:** The `spec/` directory is the authoritative validation target. Third-party reimplementations from `spec/` alone are the strongest form of reproducibility.
