# Reproducibility Patch Notes

The original code in `paper_original_code/` is preserved verbatim for provenance.

The patched scripts in this directory make the following reproducibility-facing changes:

## P1. Prior Override Consistency

**File:** `run_nested_extended.py` (lines 115, 58)

The archived runner loads prior overrides from `--config`, but the original standard-model branch resets `bounds` to built-in defaults (`BOUNDS[args.model]`), and the extended-model branch checks `in_ext_prior()` against built-in `EXT_BOUNDS`.

The patched runner `run_nested_extended_fixed.py` uses runtime config-overridden bounds consistently for all models.

## N1. Xhat Normalization Convention

**File:** `stage2d_exact_likelihood.py` (line 257)

The archived exact-pilot code uses the unnormalized shape `X(a) = 4\chi_H(a)(1-\chi_H(a))`. The manuscript notation uses the normalized convention `\widehat R_H(1)=1`.

Therefore the archived `Sigma0` coefficient should be interpreted in the code convention unless the normalized patch is used. The benchmark evidence tables correspond to the archived code convention.

The patched runner exposes an optional `--normalize-RbH` flag that transforms to the manuscript-normalized convention.

## B1. Bayes Factor Column Naming

**File:** `collect_nested_evidence.py` (line 66)

The archived collector computes `Delta_logZ = best - model` (correct) and `Bayes_factor = exp(max(Delta_logZ) - Delta_logZ)`. This column name is potentially confusing because the value is not "best over model" in all cases.

The patched collector `collect_nested_evidence_fixed.py` produces two explicit columns:
- `BF_best_over_model = exp(Delta_logZ)`
- `BF_model_over_best = exp(-Delta_logZ)`

The paper table reports `B_{best,i} = \exp(\log Z_best - \log Z_i)`.

## R1. Emergency Recovery Exclusion

**File:** `recover_nested_evidence.py`

The archived recovery script uses saved `logwt` to recover logZ via `logsumexp` and sets `logZ_err = 0`, marking `recovered_from_chains=True`. This is an emergency archival recovery mechanism.

Recovered evidence JSON files are excluded from the main benchmark tables unless `--include-recovered` is explicitly passed.

## E1. Default E_G Data Creation Disabled

**File:** `stage2d_exact_likelihood.py` (line 592)

The archived code calls `create_eg_default()` when the E_G data file is missing. This is disabled in the patched runner by default; use `--allow-default-eg` to re-enable.

## S1. Seed Handling

The patched runner treats `seed=0` as a valid seed in output filenames for production prior-stress runs.

## Recommended Production Commands

For third-party prior-stress reproduction:

```bash
python reproducibility_patch/run_nested_extended_fixed.py \
  --config paper_original_code/configs/nested_priors_medium.json \
  --model g1dem34 --seed 0 --nlive 3000 --dlogz 0.05 \
  --outdir outputs_production

python reproducibility_patch/collect_nested_evidence_fixed.py \
  --tables-dir outputs_production/tables \
  --out-dir outputs_production/tables \
  --prior-label medium
```
