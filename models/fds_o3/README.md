# FDS-O3: Boundary Maintenance and the Second Law under Finite Memory

**Title:** Boundary Maintenance and the Second Law under Finite Memory: Irreversible Record Reuse, Entropy Ledgers, and Operational Time Arrows

**Code:** FDS-O3 | **Version:** v1.0 | **DOI:** [10.5281/zenodo.20255129](https://doi.org/10.5281/zenodo.20255129)

Operational Trident III. Finite-memory operational Second-Law channel: when a physically realized active finite system maintains a boundary under bounded memory, sustained record turnover produces residual irreversibility that appears in a coupled entropy or resource ledger unless exit channels are used.

## Contents

- `generate_results.py` — deterministic synthetic model and figure generation
- `FDS-O3_v1.0.pdf` — published paper
- `fig1_*.pdf/png` — memory reuse and record-load crossing
- `fig2_*.pdf/png` — residual irreversibility: reversible logging, bounded cleanup, lossy overwrite
- `fig3_*.pdf/png` — O3 coupled entropy ledger
- `fig4_*.pdf/png` — externalization audit
- `fig5_*.pdf/png` — pruning ROI
- `fig6_*.pdf/png` — invariant compression optimum
- `fig7_*.pdf/png` — hysteresis after overload
- `fig8_*.pdf/png` — regime diagram

## Reproduce figures

```bash
python generate_results.py
```

Regenerates all figures and CSV outputs in a single pass.

## Scope

The simulations are deterministic synthetic demonstrations of the O3 normal form. They are not fits to physical devices, biological organisms, quantum experiments, or human-subject data.

## Key claims

1. Finite memory creates record-reuse pressure under sustained update.
2. Non-injective record reuse creates residual irreversibility.
3. Physical irreversible record reuse enters an entropy/resource ledger.
4. Stable finite records require housekeeping beyond logical erasure.
5. Externalization shifts the operational Second-Law channel.
6. Pruning and invariant compression can reduce future entropy pressure.
7. Sustained residual turnover, fixed tolerance, and zero ledger cost cannot persist indefinitely.
8. Topological persistence redirects entropy accounting rather than violating the Second Law.
