# FDS-G1 Replication Kit v1.0-rc

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20382013.svg)](https://doi.org/10.5281/zenodo.20382013)

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

# Run model identity checks
python reference_impl/models.py

# Run D7 Markov-screen toy verification
python reference_impl/d7_markov_toy.py

# Run all tests
pytest validation_tests/ -v
```

## Validation protocol

Four levels of independent validation are defined in `INDEPENDENT_VALIDATION.md`:

0. **Model identity** — verify mu=1, Sigma=-3/4*(3-s)*R̂_H, no free A
1. **Best-fit** — reproduce chi2_min within ±0.2
2. **Evidence** — reproduce ranking and ΔlogZ within ±0.5
3. **Stress test** — ranking survives sampler/seed/prior changes
4. **Adversarial** — full reimplementation from specification only

## Data

Post-stage-1 processed data files with reference SHA256 hashes are in
`processed_data/`. Covariance matrices are included. See `DATA_MANIFEST.md`
for provenance and URLs.

## License

MIT — see LICENSE file.

## Citation

See CITATION.cff. If you use this replication kit, please cite the
FDS-G1 Complete Series.
