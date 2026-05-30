# FDS-G1 Replication Kit v1.1-rc1

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20453246.svg)](https://doi.org/10.5281/zenodo.20453246)

## Which code produced the paper evidence tables?

The paper's exact-pilot and medium-prior nested-evidence tables were produced with the scripts archived in:

    paper_original_code/

The most important entry points are:

- `stage2d_exact_likelihood.py` — exact Stage-2d likelihood:
  Pantheon+ full-covariance SN, DESI DR2 BAO covariance, curated RSD f\sigma_8, and compressed E_G.
- `run_nested_extended.py` — dynesty nested evidence for \Lambda CDM, CPL, G1DE-1/2, and extended G1DE controls including M_{3/4}, M_\kappa, and constant-\Sigma.
- `collect_nested_evidence.py` — aggregation of per-seed nested evidence JSON files.
- `run_extended_mcmc.py` — extended-model MCMC diagnostics and model definitions.

The `reference_impl/` directory is a cleaned specification-facing implementation. It is not claimed to be byte-for-byte identical to the scripts used for the paper tables.

For transparency, the original scripts are archived verbatim. Known post-archive reproducibility notes and recommended fixes are listed in `reproducibility_patch/README_PATCH_NOTES.md`.

**The code in `paper_original_code/` is the archived analysis code used for the evidence tables reported in the paper. The code in `reference_impl/` is a cleaned specification-facing implementation. The code in `reproducibility_patch/` contains recommended fixes for third-party reruns and prior-stress production checks.**

## Claim Boundary

The archived original code supports the paper's exact-pilot evidence claim. It is not advertised as final survey-grade production evidence.

The current benchmark hierarchy is a pilot-level result under the stated processed datasets, priors, samplers, and stopping tolerances.

## Homogeneous Medium-Prior Audit (v1.0-rc3 data update)

**This rc3 supersedes earlier mixed-provenance seven-model audits with a completed homogeneous seven-model medium-prior nested-evidence audit.** All seven models (G1DE-M_{3/4}, G1DE-M_kappa, G1DE-constSigma, G1DE-2, G1DE-1, CPL, LambdaCDM) were run with 3 independent seeds under the same medium-prior configuration (`nested_priors_medium.json`), `n_live=800`, `dlogz=0.5`.

The canonical evidence hierarchy is:

| Model | logZ_mean | ΔlogZ | B(M_{3/4},i) |
|-------|-----------|-------|---------------|
| G1DE-M_{3/4} | -894.34 ± 0.03 | 0.00 | 1 |
| G1DE-M_kappa | -895.06 ± 0.11 | 0.72 | 2.1 |
| G1DE-constSigma | -896.13 ± 0.12 | 1.79 | 6.0 |
| G1DE-2 | -900.95 ± 0.19 | 6.61 | 7.4×10^2 |
| G1DE-1 | -901.75 ± 0.04 | 7.41 | 1.65×10^3 |
| CPL | -903.85 ± 0.09 | 9.51 | 1.35×10^4 |
| LambdaCDM | -906.22 ± 0.07 | 11.88 | 1.44×10^5 |

All per-seed JSONs and the canonical summary CSV are in `outputs_medium_audit/`.
The earlier mixed-provenance raw audit (`raw_audit_table.csv`) is retained for provenance only and has been superseded for model ranking.

This is a medium-prior audit, not the final production evidence pass. Production refinement with `dlogz≤0.1` and ≥8 seeds remains pending.

The following remain future or independent-validation tasks:

- stricter production nested evidence with smaller dlogz and more seeds;
- full prior stress across all six baseline/control models;
- full 3\times2pt lensing likelihoods including galaxy-galaxy lensing and clustering;
- noisy mock ensembles;
- independent reimplementation from `spec/` only.

## v1.1 KiDS shear-only diagnostic layer

This release adds a **KiDS-1000 shear-only diagnostic stress-test layer** in
`kids_shear_only/`. It is a diagnostic layer, not production 3x2pt evidence.
It reproduces the CLASS-based KiDS-1000 xi_pm analysis supporting the
G1DE-M_{3/4} branch under (m_i + dz_i + A_IA) nuisance, free-kappa, constant-Sigma,
binned-Sigma(z), and deterministic mock injection.

See `kids_shear_only/README.md` for the full description and reproduction
instructions.  KiDS dependencies (`classy`, etc.) are in `requirements_kids.txt`.

**Note on naming**: The core likelihood module is `kids_shear_only/src/stage3_lensing_3x2pt.py`
for historical reasons.  In v1.1 it is used for shear-only xi_pm.
Full 3x2pt is not included.

## Specification

The specification (spec/), benchmark outputs (benchmark/), and validation tests
(validation_tests/) are the authoritative validation targets. The Python code
in reference_impl/ is provided only as a reference implementation.

**Independent reimplementation is encouraged.** Third parties should use the
machine-readable model cards, prior definitions, likelihood conventions, and
benchmark tables as the specification against which validation is performed.

## Contents

```
spec/                   Machine-readable model and likelihood specification
  model_cards/          YAML files defining all 6 models
  priors/               Medium and wide prior ranges
  likelihood_conventions/ Chi2 definitions and prediction formulas per dataset
  normalization/        R̂_H(1)=1 rule, no-free-A guard

benchmark/              Expected outputs for validation
  medium_evidence_table.csv   Six-model nested evidence comparison
  wide_topcontrol_table.csv   Top-3 wide-prior sensitivity

kids_shear_only/        v1.1 KiDS-1000 shear-only diagnostic stress tests (new)
  src/                  Core likelihood, warm-start profiler, mock injection
  configs/              YAML configs for all nuisance/adversarial layers
  outputs/              Summary tables, confusion matrix, selected best-fits
  figures/              Paper Figure 6 and mock confusion matrix
  scripts/              Step-by-step reproduction shell scripts
  validation/           Unit/integration tests for covariance, units, reproducibility

outputs_medium_audit/    Homogeneous 7-model medium-prior evidence outputs (rc3 data)
  *_medium_nested_evidence.json   Per-seed nested-evidence JSONs (15 files, 7 models × 3 seeds, minus lcdm/g1de2 unchanged)
  homogeneous_medium_summary.csv  Canonical homogeneous evidence table (supersedes raw audit)
  raw_audit_table.csv             Mixed-provenance raw audit (retained for provenance only)

paper_original_code/     Frozen analysis code used for paper evidence tables
  outputs_frozen/        Frozen per-seed outputs and SHA256 hashes
  reproducibility_patch/ Patch notes and fixed runners for third-party reproduction

processed_data/         Stage-1 processed data with SHA256 hashes

reference_impl/         Minimal reference Python implementation
  models.py             All 6 models as standalone functions
  distances.py          Comoving distance + E(z) functions
  likelihoods.py        Chi2 functions per dataset
  run_bestfit.py        Fast best-fit optimizer skeleton
  d7_markov_toy.py      D7 two-state Markov-screen spectrum + checks

validation_tests/       Unit tests for model identities and D7 toy
companion_d_demo/       Companion D falsification demo notebook + script
```

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# For KiDS shear-only tests, also install CLASS dependencies:
pip install -r requirements_kids.txt

# Run model identity checks
python reference_impl/models.py

# Run D7 Markov-screen toy verification
python reference_impl/d7_markov_toy.py

# Run KiDS shear-only smoke test (requires classy + downloaded data)
cd kids_shear_only && python src/run_stage3_smoke_tests.py && cd ..

# Run all tests
pytest validation_tests/ -v
```

## Validation protocol

Five levels of independent validation are defined in `INDEPENDENT_VALIDATION.md`:

0. **Model identity** — verify mu=1, Sigma=-3/4*(3-s)*R̂_H, no free A
1. **Best-fit** — reproduce chi2_min within ±0.2
2. **Evidence** — reproduce ranking and ΔlogZ within ±0.5
3. **Stress test** — ranking survives sampler/seed/prior changes
4. **Adversarial** — full reimplementation from specification only
5. **KiDS diagnostic** (new in v1.1) — reproduce CLASS backend sanity, scale-cut covariance shape,
   Δχ² signs for M3/4 vs LCDM under nuisance, and deterministic mock-injection confusion matrix

## Data

Post-stage-1 processed data files with reference SHA256 hashes are in
`processed_data/`. Covariance matrices are included. See `DATA_MANIFEST.md`
for provenance and URLs.

KiDS-1000 data for the shear-only diagnostic layer is **not redistributed**.
See `kids_shear_only/data/README_DATA.md` for download instructions and
expected SHA256 hashes.

## License

MIT — see LICENSE file.

## Citation

See CITATION.cff. If you use this replication kit, please cite the
FDS-G1 Complete Series.
