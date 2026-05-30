# KiDS-1000 Shear-Only Diagnostic Stress Test Layer

## Status

This directory contains the **KiDS-1000 shear-only diagnostic stress tests** used in
FDS-G1 Complete Series **v1.1-rc1**. It is a **diagnostic layer**, not production 3x2pt
evidence.

The full 3x2pt likelihood (galaxy-galaxy lensing + angular clustering + cosmic shear)
and noisy mock ensembles remain pending.

## What this tests

The KiDS-1000 cosmic-shear xi_pm 270-element data vector (scale-cut to 135 points) is
used to stress-test the G1DE-M_{3/4} branch through:

| Layer | Description | Result |
|-------|-------------|--------|
| Baseline | LCDM cosmology + BBKS P(k) + CLASS comparison | CLASS backend verified |
| (m_i) | Shear calibration nuisance | M3/4 survives |
| (m_i + dz_i) | Shear cal + photo-z shift nuisance | M3/4 favored Δχ²≈−44 |
| (m_i + dz_i + A_IA) | + minimal NLA intrinsic alignments | M3/4 favored Δχ²≈−39 |
| M_kappa | Free projection coefficient | κ≈0.746 (consistent with 3/4 lock) |
| const-Sigma | Constant Weyl-amplitude control | Ranks below M3/4 |
| binned-Sigma(z) | Adversarial Weyl-shape control | M3/4 R_bH shape survives |
| Deterministic mock injection | False-positive audit | No misclassification of LCDM/const-/binned- as M3/4 |

## Dependencies

CLASS backend requires `classy` (see `requirements_kids.txt` in parent directory).
The exact-pilot evidence kit (SN+BAO+RSD+EG) does not require CLASS.

```bash
pip install -r ../requirements_kids.txt
```

## Contents

```
src/           Core likelihood, warm-start profiler, mock injection, plotting
configs/       YAML configs for each nuisance/adversarial layer
data/          Data manifest and download instructions (KiDS data not redistributed)
scripts/       Step-by-step reproduction shell scripts
outputs/       Summary tables, confusion matrix, selected best-fit JSONs
figures/       Paper Figure 6 and mock confusion matrix
validation/    Unit/integration tests for covariance, units, reproducibility
```

## Quick start

```bash
# 1. Check environment
./scripts/00_check_environment.sh

# 2. Prepare data (download KiDS if needed)
./scripts/00_prepare_kids_data.sh

# 3. CLASS backend sanity
./scripts/01_class_pk_sanity.sh

# 4. Reproduce Phase 2B summary (m-only through binned-Sigma)
./scripts/02_reproduce_phase2b_summary.sh

# 5. Deterministic mock injection audit
./scripts/03_mock_injection_deterministic.sh

# 6. Collect results and make figures
./scripts/04_collect_results.sh
./scripts/05_make_figures.sh
```

## Historical note

The core likelihood module is named `stage3_lensing_3x2pt.py` for historical reasons.
In this v1.1 release it is used **for shear-only xi_pm**.
Full 3x2pt (galaxy-galaxy lensing + clustering + shear) is not yet included.

## References

- KiDS-1000 cosmic shear: Asgari et al. 2021, A&A 645, A104
- KiDS-1000 catalogue: Giblin et al. 2021, Open J. Astrophys. 4, 3
- KiDS-1000 cosmology: Heymans et al. 2021, A&A 646, A140
- CLASS: Blas, Lesgourgues, Tram 2011, JCAP 07, 034
- FDS-G1 Complete Series v1.1-rc1: Wu 2026
