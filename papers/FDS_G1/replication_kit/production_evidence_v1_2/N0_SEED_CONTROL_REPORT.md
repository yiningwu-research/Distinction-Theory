# N0 Seed Control Report (v1.2 Production Audit)

## Summary

The N0 phase applied critical fixes to the nested-sampling pipeline before
launching the v1.2 production run. These ensure reproducibility, provenance
tracking, and consistent seed control across all 7 models.

## Fixes Applied

### 1. dynesty 3.0.0 Compatibility

- `dynesty==3.0.0` installed (was 2.x).
- `rstate=rng` passed to `NestedSampler` (accepts `np.random.default_rng(seed)`).
- Old-style `nlive`/`bound`/`sample` keyword API preserved.

### 2. `run_nested_extended.py` (canonical runner)

Changes:
- Extended models now read nlive from config file (not hardcoded 800).
- `rstate=rng` passed to `NestedSampler`.
- `--run-type {smoke,production}` argument added.
- Hierarchical output paths: `chains/{prior_label}/{model}/seed_{N}/`.
- Full provenance in JSON output:
  - `dynesty_version`, `python_version`, `git_commit`
  - `run_type`, `prior_config`, `prior_label`

### 3. `run_exact_nested.py` (legacy-compatible fallback)

Changes:
- `--seed`, `--prior-config`, `--run-type` arguments added.
- Output naming matches hierarchical convention.

### 4. `collect_nested_evidence.py`

Changes:
- `--include-smoke` flag added (default: exclude smoke runs).
- Recursive glob support.
- Legacy-safe `run_type` handling.

### 5. N0 Smoke Tests (N0c)

Smoke tests passed for:
- Same-seed LCDM and g1dem34: bitwise identical trajectories.
- Different-seed: independent trajectories verified.
- Prior override: correctly changes sampling domain.
- Collector: correctly filters smoke when `--include-smoke` not passed.

## Seed Assignment

| Category | Seeds | Models |
|---|---|---|
| N1 (seed 101, production) | 101 | All 7 |
| N2A (seeds 202-808, production) | 202, 303, 404, 505, 606, 707, 808 | All 7 |
| Top-up (not needed) | — | — |

N1 seed=101 was run with `run_type=production`, so it directly reuses as
N2 seed 101 — no rerun required.

Total: 8 seeds per model, 56 jobs.

## Queue Order

Fastest-first (based on model dimensionality and likelihood evaluation cost):

1. lcdm (3 params)
2. g1dem34 (4 params)
3. g1demk (4 params)
4. g1deconstsig (4 params)
5. cpl (4 params)
6. g1de1 (5 params)
7. g1de2 (5 params)

Throttled at 8 concurrent jobs on Apple M5 (10 cores).

## Convergence Verification

All 56 jobs converged to dlogZ <= 0.1. Per-model seed scatter:

| Model | Scatter | Within 2σ? |
|---|---|---|
| g1dem34 | 0.130 | Yes |
| g1demk | 0.129 | Yes |
| g1deconstsig | 0.069 | Yes |
| g1de2 | 0.191 | No (see note) |
| g1de1 | 0.180 | No (see note) |
| cpl | 0.105 | Yes |
| lcdm | 0.100 | Yes |

**Note on G1DE-1 and G1DE-2 scatter:** Both models have seed scatter
slightly above the 0.15 target (0.180 and 0.191 respectively). Top-up
seeds were considered but not required, because:

1. The evidence gaps from the reference model (M3/4) are large:
   ΔlogZ(M3/4, G1DE-2) ≈ 6.5, ΔlogZ(M3/4, G1DE-1) ≈ 7.4.
2. The model ranking is unaffected by the elevated scatter.
3. The hierarchy is stable: M3/4 > Mκ > const-Σ > G1DE-2 > G1DE-1 > CPL > ΛCDM.

See CLAIM_STATUS.md for the full discussion.
