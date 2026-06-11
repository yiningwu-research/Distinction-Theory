# CMB-lensing Precheck - Integration Validation

Date: 2026
Commit: c574bbb (integrate/cmb-lensing-precheck)

## Test Environment

| Item | Value |
|------|-------|
| Platform | macOS darwin |
| Python | 3.9.6 |
| NumPy | 2.0.2 |
| SciPy | 1.13.1 |
| Matplotlib | 3.9.4 |
| PyYAML | 6.0.3 |
| pytest | 8.4.2 |

## Test Results

```
8 passed, 14 warnings in 32.28s
```

All warnings are matplotlib/pyparsing deprecation notices.
No test failures, no skipped tests.

## Benchmark Reproducibility

Verified 2026 on the same platform:

| Quantity | Value | Match (diff) |
|----------|-------|-------------|
| D_G1/D_LCDM today | 0.955089979178 | ✅ exact |
| CL mean ratio L=8-40 | 0.569455763021 | ✅ exact |
| CL mean ratio L=40-400 | 0.713580523272 | ✅ exact |
| CL mean ratio L=400-1000 | 0.774685315003 | ✅ exact |
| CL mean ratio L=1000-2998 | 0.796458171443 | ✅ exact |

Reproduction was achieved with rtol=1e-8, atol=1e-12.
Actual differences were < 1e-15 for all quantities.

## Reproduction Command

```bash
python scripts/check_benchmark.py \
  benchmarks/g1_m34_fiducial/summary.json \
  outputs/g1_m34_fiducial/summary.json
```
