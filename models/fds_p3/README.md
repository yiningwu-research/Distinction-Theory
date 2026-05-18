# FDS-P3: Finite-Bath Memory, Markovianization, and Environmental Forgetting

## Contents

- `generate_results.py` — deterministic synthetic normal-form model
- `fig1_finite_bath_memory_decay.pdf` / `.png` — finite-bath memory decay
- `fig2_markov_closure_error.pdf` / `.png` — Markov closure error
- `fig3_memory_kernel_burden.pdf` / `.png` — memory-kernel burden
- `fig4_side_record_recovery.pdf` / `.png` — side-record recovery
- `fig5_finite_bath_saturation.pdf` / `.png` — finite-bath saturation
- `fig6_markovianization_regimes.pdf` / `.png` — Markovianization regimes
- `fig7_environmental_ledger.pdf` / `.png` — environmental ledger
- `fig8_p3_p4_p7_regimes.pdf` / `.png` — P3/P4/P7 regimes
- `data/*.csv`, `data/simulation_parameters.json` — generated output data

## Usage

```bash
pip install numpy pandas matplotlib scipy
python code/generate_results.py
```

All figures are synthetic normal-form demonstrations, not empirical phase diagrams.
