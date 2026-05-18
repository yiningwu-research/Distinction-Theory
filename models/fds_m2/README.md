# FDS-M2: Value and Goal as Boundary-Relevance Ranking

## Contents

- `generate_results.py` — deterministic synthetic normal-form model
- `fig1_value_funnel.pdf` / `.png` — value funnel pipeline
- `fig2_predictive_vs_causal.pdf` / `.png` — predictive-causal dissociation
- `fig3_risk_weighted_ranking.pdf` / `.png` — risk-dominant ranking
- `fig4_goal_stability.pdf` / `.png` — goal-stability trajectories
- `fig5_proxy_boundary_divergence.pdf` / `.png` — proxy reward hacking
- `fig6_evaluation_deficit.pdf` / `.png` — evaluation deficit effects
- `fig7_multi_goal_pareto.pdf` / `.png` — multi-goal Pareto conflict
- `fig8_goal_hysteresis.pdf` / `.png` — goal hysteresis and recovery lag
- `data/*.csv` — generated output files

## Usage

```bash
pip install numpy pandas matplotlib scipy
python generate_results.py
```

Figures and data are written to `figures/` and `data/` subdirectories.

## Notes

All figures are synthetic normal-form illustrations, not empirical evidence.
See the paper for definitions, protocols, and audit templates.
