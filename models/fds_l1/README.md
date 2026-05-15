# Supplementary Code README

## FDS-L1: Active Pruning Protocell Model

This supplementary file describes the simulation code associated with the manuscript:

**Yining Wu, "Active Pruning Controls Boundary Persistence in Protocell-like Systems: Saddle-Node Attractor Loss, Stochastic Early Warnings, Multiscale Simulations, and Wet-Lab Benchmark Predictions."**

Source code, parameter files, generated figures, and CSV tables for the simulations are available at:

https://github.com/yiningwu-research/Distinction-Theory/tree/main/models/fds_l1

The repository contains scripts for the well-mixed model, SDE early-warning simulations, 2D reaction-diffusion clogging, reduced boundary model, rescue-window heatmap, robustness sweep, and radial-shell size-scaling analysis. A machine-readable parameter table specifying baseline values, sweep ranges, random seeds, and figure-generation scripts is included with the released code.

## Contents

```text
src/generate_figures.py   -> generates all 9 figures (PDF + PNG)
data/                     -> CSV tables with numerical results
figures/                  -> pre-generated figure files
````

## Dependencies

* Python 3
* numpy
* matplotlib

## Usage

```bash
python src/generate_figures.py
```

All figures, data tables, and random seeds are fixed for reproducibility. Each figure maps to a section in the manuscript:

| Figure | Content                                                            |
| ------ | ------------------------------------------------------------------ |
| 1      | Saddle-node bifurcation with potential landscape                   |
| 2      | SDE early-warning scaling                                          |
| 3      | 2D reaction-diffusion clogging snapshots                           |
| 4      | Dynamic-boundary snapshots                                         |
| 5      | Dynamic-boundary time series                                       |
| 6      | Radial size scaling with diffusion-delay correction                |
| 7      | Rescue-window heatmap                                              |
| 8      | Robustness sweep across production and diffusion-arrest parameters |
| 9      | Benchmark map / universality-class diagram                         |

## Parameter overview

Model parameters are documented in Table III of the manuscript. Baseline values and sweep ranges are set inside `src/generate_figures.py` and recorded in the released code.

## Citation

If you use this code, please cite:

Wu, Y. (2026). *Active Pruning Controls Boundary Persistence in Protocell-like Systems: Saddle-Node Attractor Loss, Stochastic Early Warnings, Multiscale Simulations, and Wet-Lab Benchmark Predictions*. Manuscript submitted.

