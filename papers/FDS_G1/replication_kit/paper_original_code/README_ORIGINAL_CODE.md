# Original Code Used for FDS-G1 Exact-Pilot Evidence Tables

This directory archives the original scripts used to generate the exact-pilot MCMC and nested-evidence outputs reported in the FDS-G1 complete series.

## Status

These scripts are archived for provenance. They are not a polished public API.

The cleaned, specification-facing implementation is in `../reference_impl/`.
The recommended reproducibility patches are in `../reproducibility_patch/`.

## Main likelihood

`stage2d_exact_likelihood.py` implements the exact Stage-2d likelihood used in the paper:

- Pantheon+ full-covariance SN block
- DESI DR2 BAO covariance block
- curated non-overlapping RSD f\sigma_8 block
- compressed E_G block

## Main evidence runner

`run_nested_extended.py` runs dynesty nested sampling for:

- LCDM
- CPL
- G1DE-1
- G1DE-2
- G1DE-M_{3/4}
- G1DE-M_\kappa
- G1DE-const\Sigma
- additional diagnostic controls

## Main table collector

`collect_nested_evidence.py` collects per-seed evidence JSON files and produces comparison tables.

## Exact-pilot claim boundary

The archived outputs support the exact-pilot / medium-prior evidence claim in the paper. They do not by themselves constitute final production-level cosmological evidence.

Production-level evidence requires stricter stopping tolerance, more seeds, full prior stress across all baselines, independent pipeline replication, and expanded lensing/3\times2pt likelihoods.

## How to use

```bash
# Install dependencies
pip install -r ../../requirements.txt dynesty

# Run medium-prior nested evidence (one model, one seed)
python run_nested_extended.py \
  --config configs/nested_priors_medium.json \
  --model g1dem34 \
  --seed 101 \
  --nlive 800 \
  --dlogz 0.5 \
  --outdir /tmp/g1_output

# Collect evidence comparison tables
python collect_nested_evidence.py \
  --tables-dir /tmp/g1_output/tables \
  --out-dir /tmp/g1_output/tables \
  --prior-label medium
```

For full prior-stress reproducibility, use the patched runner in `../reproducibility_patch/`.
