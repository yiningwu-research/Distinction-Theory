# FDS-L1: Active Pruning Protocell Model

Simulation code for the paper **"Active Pruning Controls Boundary Persistence in Protocell-like Systems"**.

## Contents

```
src/generate_figures.py   → generates all 9 figures (PDF + PNG)
data/                     → 9 CSV tables with numerical results
figures/                  → 18 pre-generated figure files
```

## Dependencies

- Python 3 with `numpy` and `matplotlib`

## Usage

```bash
python src/generate_figures.py
```

All figures, data tables, and random seeds are fixed for reproducibility. Each figure maps to a section in the paper:

| Figure | Content |
|--------|---------|
| 1 | Saddle-node bifurcation with potential landscape |
| 2 | SDE early-warning scaling |
| 3 | 2D reaction-diffusion clogging snapshots |
| 4 | Dynamic-boundary snapshots |
| 5 | Dynamic-boundary time series |
| 6 | Radial size scaling with diffusion-delay correction |
| 7 | Rescue-window heatmap |
| 8 | Robustness sweep across production and diffusion-arrest parameters |
| 9 | Benchmark map / universality-class diagram |

## Parameter overview

Model parameters are documented in Table IV of the paper. Baseline values and sweep ranges are set inside `generate_figures.py` and recorded in each figure's generation code.

## Citation

If you use this code, cite:

Y. Wu, Active Pruning Controls Boundary Persistence in Protocell-like Systems, submitted (2026).
