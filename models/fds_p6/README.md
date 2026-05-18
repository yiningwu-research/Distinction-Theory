# FDS-P6: Speed, Precision, and Dissipation Bounds for Boundary Maintenance

## Contents

- `generate_results.py` — deterministic synthetic normal-form model
- `fig1_speed_precision_load.pdf` / `.png` — speed-precision load surface
- `fig2_resource_ledger.pdf` / `.png` — resource ledger decomposition
- `fig3_error_floor.pdf` / `.png` — finite-resource precision floor
- `fig4_causal_horizon.pdf` / `.png` — effective causal reach
- `fig5_externalization_break_even.pdf` / `.png` — externalization break-even
- `fig6_invariant_compression.pdf` / `.png` — invariant compression relief
- `fig7_regime_diagram.pdf` / `.png` — finite-boundary regimes
- `fig8_physical_ai_normal_form.pdf` / `.png` — Physical AI normal form
- `data/*.csv` — generated output data including `simulation_parameters.csv`

## Usage

```bash
pip install numpy pandas matplotlib scipy
python generate_results.py
```

All figures are synthetic normal-form demonstrations, not empirical phase diagrams.
