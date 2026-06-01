# Provenance Directory

This directory contains pointers to legacy audit outputs retained for
provenance. No files in the v1.1 `replication_kit/` have been moved or
modified.

## v1.1 Homogeneous 3-Seed Audit

- **Location**: `../outputs_medium_audit/` (unchanged, in v1.1 kit root)
- **Status**: **SUPERSEDED** for v1.2 model ranking
- **Superseded by**: `../production_evidence_v1_2/outputs_medium_8seed/`

The v1.1 three-seed homogeneous medium-prior audit (`dlogZ=0.5`) was the
canonical evidence table for v1.0-rc3 and v1.1-rc1. The v1.2
production-refined audit (8 seeds, `dlogZ=0.1`) supersedes it for all
model-ranking claims.

## Mixed-Provenance Raw Audit

- **Location**: `../outputs_medium_audit/raw_audit_table.csv` (unchanged)
- **Status**: Retained for provenance only; superseded by both the v1.1
  3-seed audit and the v1.2 production-refined audit.

## Why Not Move?

The v1.1 `replication_kit/` is frozen. All v1.2 additions are new files
within the same `replication_kit/` directory. No existing files are moved
or modified.
