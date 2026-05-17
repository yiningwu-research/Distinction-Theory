# FDS-N1: Boundary-Maintaining Self-Organizing Systems under Finite Capacity

**Title:** Boundary-Maintaining Self-Organizing Systems under Finite Capacity: Maintenance Load, Phase-C Collapse, and Invariant Selection

**Code:** FDS-N1 | **Version:** v1.0 | **DOI:** [10.5281/zenodo.20253151](https://doi.org/10.5281/zenodo.20253151)

Complex-systems bridge for Active Finite Distinction Systems. Translates the FDS formal core into a normal-form account of boundary-maintaining self-organization.

## Contents

- `generate_results.py` — deterministic synthetic model and figure generation
- `FDS-N1_v1.0.pdf` — published paper
- `fig1_*.pdf/png` — Phase-A/B/C time series
- `fig2_*.pdf/png` — effective organizational capacity $C_{\rm org}$
- `fig3_*.pdf/png` — pruning viability window
- `fig4_*.pdf/png` — externalization clogging and ROI
- `fig5_*.pdf/png` — regime phase diagram
- `fig6_*.pdf/png` — invariant selection score
- `fig7_*.pdf/png` — active-boundary ablation
- `fig8_*.pdf/png` — domain bridge flow diagram

## Reproduce figures

```bash
python generate_results.py
```

Regenerates all figures and CSV outputs in a single pass.

## Scope

The simulations are deterministic synthetic demonstrations of the N1 normal form. They are not fits to biological systems, robots, organizations, ecosystems, physical devices, or human-subject data.

## Key claims

1. Active self-organization requires boundary-maintenance-relevant internal update.
2. Effective organizational capacity is task-relative and reduced by coordination, verification, latency, resource, and externalization costs.
3. Deficit creates maintenance-load pressure.
4. Unbounded Phase-A growth is impossible under finite resource input without exit channels.
5. Pruning has a viability window and is resource-gated.
6. Externalization shifts rather than removes boundary-maintenance burden.
7. Phase-C catastrophic feedback couples boundary loss with resource depletion.
8. Phase-B residues are biased toward low-maintenance, task-relevant invariants.
