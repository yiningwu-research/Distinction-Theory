# FDS-M1: Attention as Distinction Admission in Finite Systems

**Title:** Attention as Distinction Admission in Finite Systems: Capacity-Limited Gating, Boundary Relevance, and Tunnel Vision

**Code:** FDS-M1 | **Version:** v1.0 | **DOI:** [10.5281/zenodo.20258570](https://doi.org/10.5281/zenodo.20258570)

Attention paper in the agency-semantics spine of Distinction Theory. Treats attention as capacity-limited admission of candidate distinctions into an update channel. Separates attention from salience, introduces verification status classes, background scanning, tunnel vision, attention hysteresis, and collective attention.

## Contents

- `generate_results.py` — deterministic synthetic normal-form model
- `FDS-M1_v1.0.pdf` — published paper
- `fig1_*.pdf/png` — attention flow and admission gate
- `fig2_*.pdf/png` — salience-value dissociation quadrants
- `fig3_*.pdf/png` — capacity-limited admission sweep
- `fig4_*.pdf/png` — verification-limited attention
- `fig5_*.pdf/png` — tunnel vision gate steepening
- `fig6_*.pdf/png` — attention failure modes
- `fig7_*.pdf/png` — hysteretic attention recovery
- `fig8_*.pdf/png` — collective attention and epistemic pollution

## Reproduce figures

```bash
python generate_results.py
```

Regenerates all figures and CSV outputs in a single pass.

## Scope

The simulations are deterministic synthetic normal-form illustrations. They are not fits to biological, cognitive, artificial, or social attention systems.

## Key claims

1. Attention is capacity-limited distinction admission into an update channel.
2. Salience and attention are separable: salient distinctions can be rejected if cost or verification burden is too high.
3. Boundary-efficient attention systems preferentially admit high causal boundary-value distinctions.
4. Attention allocation can be written as constrained optimization over value, curiosity, cost, and capacity.
5. Semantic or attention deficit steepens admission thresholds and can produce tunnel vision.
6. Artificial attention belongs to a coupled architecture only when routed distinctions affect durable update or verification.
7. Collective attention is shared admission under finite communication, verification, and externalized memory capacity.
8. Attention failure includes overload, distraction, salience capture, suppression, tunnel vision, false admission, and critical distinction exclusion.
9. Attention recovery after deficit-induced narrowing can lag behind external load reduction because of hysteresis in gate thresholds.
