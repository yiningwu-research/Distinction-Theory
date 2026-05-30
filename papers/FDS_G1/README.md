# FDS-G1 Complete Series

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20453246.svg)](https://doi.org/10.5281/zenodo.20453246)

**Finite Screen Spacetime: Entropy-Response Geometry from Causal-Screen Ledgers**
The physics flagship of Active Finite Distinction Systems (FDS).

## Files

| File | Description |
|------|-------------|
| `FDS_G1_Complete.pdf` | Complete Series (19 papers, 290 pages) — including Core, Companions A–F, G1fit-real, D0–D10 |
| `FDS_G1_Core_Entropy_Response_Geometry.pdf` | Core paper only (19 pages) |
| `prediction_registry.md` | Prediction lock and falsification registry (6 predictions G1-A through G1-F) |
| `replication_kit/` | Machine-readable specification, benchmark outputs, processed data, reference Python implementation, validation tests, and D7 Markov-screen toy model |

## DOI

`10.5281/zenodo.20453246` — [View on Zenodo](https://doi.org/10.5281/zenodo.20453246)

## Citation

```bibtex
@misc{wu2026fdscoptet,
  author       = {Wu, Yining},
  title        = {Finite Screen Spacetime: Entropy-Response Geometry from Causal-Screen Ledgers},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20453246},
  note         = {FDS-G1 Complete Series v1.1-rc1},
}
```

## Replication Kit

The `replication_kit/` directory contains everything needed for independent validation:

- `spec/` — machine-readable model cards, priors, likelihood conventions, normalization rules
- `benchmark/` — expected evidence tables (medium + wide)
- `processed_data/` — stage-1 processed data with SHA256 hashes
- `reference_impl/` — minimal Python reference implementation (all 6 models, D7 Markov-screen toy)
- `validation_tests/` — 20 unit tests verifying model identities and D7 toy
- `d7_markov_screen/` — standalone D7 package with CLI and test suite
- `companion_d_demo/` — falsification demo notebook and script

**The specification (`spec/`) is the validation target, not the author's code. Independent reimplementation is encouraged.**

```bash
cd replication_kit
pip install -r requirements.txt
python reference_impl/models.py        # model identity checks
python reference_impl/d7_markov_toy.py # D7 Markov-screen toy
bash test_all.sh                        # full test suite (25 tests)
```
