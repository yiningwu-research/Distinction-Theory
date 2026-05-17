# FDS-P5: Capacity Deficit and Entropy Production in Active Finite Systems

**Title:** Capacity Deficit and Entropy Production in Active Finite Systems: A Generalized Dissipation Ledger for Boundary Maintenance

**Code:** FDS-P5 | **Version:** v1.0 | **DOI:** [10.5281/zenodo.20254259](https://doi.org/10.5281/zenodo.20254259)

Physical bridge between task-relative capacity deficit and entropy-production pressure in active finite distinction systems. Defines a generalized entropy-production audit ledger, correction-flow lower bounds, pruning ROI, externalization audit, and the deficit–maintenance–dissipation impossibility triangle.

## Contents

- `generate_results.py` — deterministic synthetic model and figure generation
- `FDS-P5_v1.0.pdf` — published paper
- `fig1_*.pdf/png` — deficit crossing and entropy-production pressure
- `fig2_*.pdf/png` — generalized entropy-production ledger decomposition
- `fig3_*.pdf/png` — pruning as dissipation ROI
- `fig4_*.pdf/png` — externalization audit (local vs coupled cost)
- `fig5_*.pdf/png` — invariant compression
- `fig6_*.pdf/png` — maintenance regime phase diagram
- `fig7_*.pdf/png` — entropy-production hysteresis

## Reproduce figures

```bash
python generate_results.py
```

Regenerates all figures and CSV outputs in a single pass.

## Scope

The simulations are deterministic synthetic demonstrations of the P5 normal form. They are not fits to physical memory devices, biological organisms, computers, or human-subject data.

## Key claims

1. Capacity deficit is task-relative information shortfall, not thermodynamic entropy.
2. Sustained deficit plus boundary maintenance requires correction, externalization, or failure.
3. Physical correction cycles induce audit channels through update, refresh, repair, synchronization, and transport.
4. Logical erasure contributes a Landauer-style entropy-production floor under bridge assumptions.
5. Housekeeping entropy persists even when logical erasure is zero.
6. Externalization shifts the entropy ledger across accounting boundaries.
7. Pruning and invariant compression can reduce future entropy-production pressure.
8. Deficit crossing predicts measurable signatures in heat, resource use, latency, resets, or error floor.
