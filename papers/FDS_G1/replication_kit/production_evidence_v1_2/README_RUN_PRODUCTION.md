# Production Nested-Evidence Run (v1.2)

This directory contains the production-refined nested-evidence audit for the
FDS-G1 v1.2 paper: seven models, medium prior, 8 independent seeds each,
dlogZ=0.1, run_type=production.

## Contents

```
src/                              N0-fixed analysis scripts
configs/                          Medium and wide prior configs + runner config
outputs_medium_8seed/
  per_seed_json/                  56 per-seed nested-evidence JSON files
  production_8seed_summary.csv    Aggregated statistics per model
  production_8seed_table3.csv     Table 3 formatted output
  production_8seed_manifest.json  Full provenance manifest
logs_summary/                     Per-job metadata (runtime, final dlogz, etc.)
```

## How to reproduce the full run

The canonical runner is `src/run_nested_extended.py`:

```bash
python src/run_nested_extended.py \
  --model g1dem34 \
  --seed 101 \
  --config configs/nested_priors_medium.json \
  --run-type production
```

All 56 jobs (7 models x 8 seeds) used:
- **Sampler**: dynesty 3.0.0 (NestedSampler, `rstate=rng`)
- **Stopping**: dlogZ_target=0.1
- **Likelihood**: `stage2d_exact_likelihood.py` (SN + DESI DR2 BAO + RSD fσ₈ + E_G)
- **Prior**: `nested_priors_medium.json`
- **Parallelism**: 8-way on Apple M5 (10 cores)

The queue was ordered fastest-first (lcdm → g1dem34 → g1demk → g1deconstsig
→ cpl → g1de1 → g1de2) for earlier validation signal.

N1 seed=101 runs directly reused as N2 seed 101 (no rerun needed).

To aggregate results:

```bash
python src/collect_nested_evidence.py \
  --input outputs_medium_8seed/per_seed_json \
  --include-production
  # --include-smoke flag available but unused in production
```

To reproduce Table 3:

```bash
python src/generate_evidence_tables.py \
  --input-dir outputs_medium_8seed/per_seed_json \
  --output-dir outputs_medium_8seed \
  --reference-model g1dem34
```

## Differences from v1.1

| Aspect | v1.1 (3-seed) | v1.2 (production) |
|---|---|---|
| Seeds per model | 3 | 8 |
| dlogZ target | 0.5 | 0.1 |
| Run type | mixed-pilot | production |
| N0 fixes applied | No | Yes (rstate, provenance, hierarchical paths) |

The v1.2 audit supersedes the v1.1 3-seed audit for model ranking.

## Provenance Note on Per-Seed JSON Files

The per-seed JSON files in `outputs_medium_8seed/per_seed_json/` preserve the
original runtime provenance from the production machine, including the
absolute `prior_config` path (e.g., `/Users/next/G_production_code/configs/...`)
and `git_commit`. These paths are **not required** for replication. The
release configs in `configs/` provide the same prior and runner settings
using relative paths and environment-variable templates.

If you are replicating the analysis, use the configs from `configs/`
rather than the paths recorded in the per-seed JSONs.
