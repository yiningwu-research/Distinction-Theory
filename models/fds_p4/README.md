# FDS-P4: Coarse-Grained Anti-Recurrence and Informational Hysteresis

## Contents

- `generate_results.py` — deterministic synthetic normal-form model
- `fig1_preimage_recovery_bound.pdf` / `.png` — Bayes-optimal recovery bound
- `fig2_capacity_hysteresis.pdf` / `.png` — capacity-recovery asymmetry
- `fig3_externalization_breakeven.pdf` / `.png` — externalization break-even
- `fig4_mori_zwanzig_kernel.pdf` / `.png` — Mori-Zwanzig memory kernel
- `fig5_js_markov_closure.pdf` / `.png` — JS Markov closure error
- `fig6_benign_malignant_hysteresis.pdf` / `.png` — benign vs malignant hysteresis
- `fig7_phase_b_selection.pdf` / `.png` — Phase-B survivor selection
- `fig8_p7_bridge.pdf` / `.png` — P4-to-P7 bridge
- `tables/*.csv` — generated output data

## Usage

```bash
pip install numpy pandas matplotlib scipy
python generate_results.py
```

All figures and data are synthetic normal-form illustrations, not empirical evidence.
