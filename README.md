# Distinction Theory / Active Finite Distinction Systems

[![Official Website](https://img.shields.io/badge/Official_Website-distinctiontheory.org-blue)](https://www.distinctiontheory.org)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![GitHub](https://img.shields.io/badge/GitHub-yiningwu--research%2FDistinction--Theory-black)](https://github.com/yiningwu-research/Distinction-Theory)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20130174.svg)](https://doi.org/10.5281/zenodo.20130174)

The archival source, version-control, claim-ledger, and reproducibility layer for Distinction Theory (DT) and Active Finite Distinction Systems (FDS).

> **Official website:** [distinctiontheory.org](https://www.distinctiontheory.org) — public navigation layer  
> **Claim Ledger:** [CLAIM_LEDGER.md](CLAIM_LEDGER.md) — canonical claim index  
> **Timestamp Index:** [TIMESTAMPS.md](TIMESTAMPS.md) — public priority records  
> **YouTube:** [@DistinctionTheory](https://www.youtube.com/@DistinctionTheory)  
> **X:** [@FDSTheory](https://x.com/FDSTheory)

**Author:** Yining Wu  
**Affiliation:** Independent Researcher  
**Contact:** yining.wu@alumni.upenn.edu

---

## Status

This repository is the public research archive for **Distinction Theory (DT)** and **Active Finite Distinction Systems (FDS)**.

The programme studies how finite systems maintain operational identity under limited capacity, limited resources, residual load, update cost, perturbation, pruning, externalization, collapse, and invariant-supported persistence.

The **agency-semantics spine** is now complete: Core → M0 → M1 → M2 → M3. All released with DOIs and open-source code.

This repository contains:
- released papers and registries in `papers/`;
- source files in `source/`;
- [canonical claim ledger](CLAIM_LEDGER.md) (`CLAIM_LEDGER.md`);
- [public timestamp index](TIMESTAMPS.md) (`TIMESTAMPS.md`);
- [machine-readable claim records](claims/);
- [failure and demotion conditions](FAILURE_REGISTRY.md);
- [prior-art boundaries](PRIOR_ART_BOUNDARY.md);
- [reproducibility files](REPRODUCIBILITY.md);
- [release records](RELEASE_PROTOCOL.md);
- [citation metadata](CITATION.cff).

This repository is the archival source layer. The official navigation layer is the website: [distinctiontheory.org](https://www.distinctiontheory.org)

---

## Priority Infrastructure

The DT/FDS public archive is organized to make priority, dependency, and failure conditions auditable.

Priority records are maintained through:

- `CLAIM_LEDGER.md` — canonical claim IDs, statements, and failure conditions.
- `claims/claims.csv` / `claims/claims.yaml` — machine-readable claim records.
- `TIMESTAMPS.md` — public timestamp index per document.
- `VERSION_HISTORY.md` — version changes and claim evolution.
- Git tags and GitHub releases — repository-level version records.
- Zenodo DOIs — citable archived versions.
- OSF registrations — frozen public records where applicable.
- Official website — public navigation and claim map.

A claim appearing in the ledger is not automatically asserted as established. Claims are organized by layer, dependency, status, and failure condition.

---

## Public Architecture

The current DT/FDS public architecture, organized by layer:

### Core

- **DT-Archive** — broad claim-space archive. DOI: 10.5281/zenodo.20130174.
- **FDS-0** — formal finite-system core: capacity deficit, boundary maintenance, pruning, externalization, collapse, invariant-supported persistence. DOI: 10.5281/zenodo.20158923.
- **FDS-T1** — finite distinguishability budgets and maintenance bounds. DOI: 10.5281/zenodo.20234249.
- **FDS-O1** — observer as a finite distinction register. DOI: 10.5281/zenodo.20248792.
- **FDS-O2** — time as irreversible distinction update. DOI: 10.5281/zenodo.20249369.
- **FDS-O3** — boundary maintenance and the Second Law under finite memory. DOI: 10.5281/zenodo.20255129.
- **FDS-T3** — capacity overflow and effective stochasticity. DOI: 10.5281/zenodo.20250367.
- **FDS-M0** — agency-semantics spine. DOI: 10.5281/zenodo.20257939.
- **FDS-M1** — attention as distinction admission. DOI: 10.5281/zenodo.20258570.
- **FDS-M2** — value and goal as boundary-relevance ranking. DOI: 10.5281/zenodo.20262998.
- **FDS-M3** — meaning as actionable semantic quotient. DOI: 10.5281/zenodo.20263294.

### Physical Bridge Ladder

- **FDS-P0** — physical bridge claim registry. DOI: 10.5281/zenodo.20159995.
- **FDS-P1** — physical distinction carriers and erasure maps. DOI: 10.5281/zenodo.20251854.
- **FDS-P2** — bounded-memory reversible computation and housekeeping dissipation. DOI: 10.5281/zenodo.20252480.
- **FDS-P5** — capacity deficit and entropy production ledger. DOI: 10.5281/zenodo.20254259.

### Domain Bridges

- **FDS-N1** — boundary-maintaining self-organizing systems. DOI: 10.5281/zenodo.20253151.
- **FDS-E1** — finite-capacity prospect theory. DOI: 10.5281/zenodo.20237306.
- **FDS-L1** — active pruning and protocell-like systems. DOI pending.
- **FDS-LC0** — life and cognitive science bridge claim registry. DOI: 10.5281/zenodo.20183373.
- **FDS-C1** — reportable access under finite capacity. DOI: 10.5281/zenodo.20229509.
- **FDS-A1** — artificial agency criterion (frozen public AI line). DOI: 10.5281/zenodo.20184709.
- **FDS-X1** — horizon-maintenance dark energy (pre-Euclid bridge note). DOI: 10.5281/zenodo.20234391.

### Operational Trident

The Operational Trident translates finite distinguishability budgets into observer-level physical processes.

- **FDS-O1 — Observer as a Finite Distinction Register.** Measurement capacity, dynamic bottlenecks, record formation, buffering, housekeeping heat, and budget-crossing signatures. DOI: 10.5281/zenodo.20248792.
- **FDS-O2 — Time as Irreversible Distinction Update.** Register time as causally ordered irreversible finite-record update, with synchronization bottlenecks, non-injective update, dissipative projection, and register-time collapse. DOI: 10.5281/zenodo.20249369.
- **FDS-O3 — Boundary Maintenance and the Second Law under Finite Memory.** Finite-memory operational Second-Law channel, record-turnover entropy, irreversibility from bounded memory. DOI: 10.5281/zenodo.20255129.

### Agency-Semantics Spine

- **FDS-M0 — Agency-Semantics Spine.** Attention, value, goal, meaning, agency, under finite capacity. DOI: 10.5281/zenodo.20257939.
- **FDS-M1 — Attention as Distinction Admission.** Capacity-limited admission gating, salience-value dissociation, tunnel vision, hysteresis. DOI: 10.5281/zenodo.20258570.
- **FDS-M2 — Value and Goal as Boundary-Relevance Ranking.** Causal boundary gradients, goal stability, proxy-boundary divergence, collective synchronization. DOI: 10.5281/zenodo.20262998.
- **FDS-M3 — Meaning as Actionable Semantic Quotient.** Policy-preserving compression, semantic deficit, false compression, meaning recovery. DOI: 10.5281/zenodo.20263294.

---

## Public Academic Spine and AI Scope

The public academic spine currently prioritizes:

1. **FDS-0** — formal finite-system core.
2. **FDS-T1** — finite observers and distinguishability budgets.
3. **FDS-O1** — observer as a finite distinction register.
4. **FDS-O2** — time as irreversible distinction update.
5. **FDS-T3** — capacity overflow and effective stochasticity.
6. **FDS-O3** — boundary maintenance and the Second Law under finite memory.
7. **FDS-N1** — boundary-maintaining self-organizing systems under finite capacity.
8. **FDS-P1** — physical distinction carriers and erasure maps.
9. **FDS-P2** — bounded-memory reversible computation and housekeeping dissipation.
10. **FDS-P5** — capacity deficit and entropy-production ledger.
11. **FDS-M0** — agency-semantics spine.
12. **FDS-M1** — attention as distinction admission.
13. **FDS-M2** — value and goal as boundary-relevance ranking.
14. **FDS-M3** — meaning as actionable semantic quotient.
15. **FDS-L1** — active pruning and artificial-life persistence.
16. **FDS-C1** — reportable access under finite capacity.
17. **FDS-E1** — finite-capacity prospect theory and boundary-risk preferences.
18. **FDS-X1** — pre-Euclid horizon-maintenance dark-energy bridge note (released).

FDS-A1 is retained as a conceptual timestamp for artificial agency. Because the author may pursue commercial work in AI and robotics, this public repository does not develop proprietary AI architectures, AGI robotics systems, private benchmarks, or product-level implementation details. See [CONFLICTS_OF_INTEREST.md](CONFLICTS_OF_INTEREST.md).

---

## If You Are New

Use the official website first:

- [Start Guide](https://www.distinctiontheory.org/start)
- [Papers](https://www.distinctiontheory.org/papers)
- [Claim Ledger](https://www.distinctiontheory.org/ledger)
- [Timestamps](https://www.distinctiontheory.org/timestamps)
- [Claim Status](https://www.distinctiontheory.org/claims)
- [Failure Registry](https://www.distinctiontheory.org/failure-registry)
- [Prior-Art Boundary](https://www.distinctiontheory.org/prior-art)

Recommended reading path:

1. **FDS-0 Formal Core** — start here for the formal finite-system architecture.
2. **FDS-T1 Finite Observers and Distinguishability Budgets** — finite observers, accessible capacity, information bounds, maintenance-cost accounting.
3. **FDS-O1 Observer as a Finite Distinction Register** — measurement as finite record formation under dynamic bottlenecks, buffering, and budget-crossing signatures.
4. **FDS-O2 Time as Irreversible Distinction Update** — register time as causally ordered irreversible finite-record update.
5. **FDS-O3 Boundary Maintenance and the Second Law** — finite-memory operational Second-Law channel.
6. **FDS-T3 Capacity Overflow and Effective Stochasticity** — common mechanism: capacity overflow induces effective stochasticity.
7. **FDS-N1 Self-Organization Bridge** — complex-systems normal form: boundary-maintaining self-organization, Phase-C collapse, invariant selection.
8. **FDS-M0 Agency-Semantics Spine** — attention, value, goal, meaning, agency under finite capacity.
9. **FDS-M1 Attention as Distinction Admission** — capacity-limited admission gating.
10. **FDS-M2 Value and Goal as Boundary-Relevance Ranking** — causal boundary gradients, goal stability, proxy divergence.
11. **FDS-M3 Meaning as Actionable Semantic Quotient** — policy-preserving compression, semantic deficit, false meaning.
12. **FDS-P0 Physical Bridge Registry** — physical bridge claims, dependency structure.
13. **FDS-P1 Physical Distinction Carriers** — Physical Bridge Ladder I.
14. **FDS-P2 Bounded-Memory Reversible Computation** — Physical Bridge Ladder II.
15. **FDS-P5 Deficit-Driven Entropy Ledger** — Physical Bridge Ladder III.
16. **FDS-L1 Active Pruning** — artificial-life, protocell-like systems, persistence-collapse transitions.
17. **FDS-C1 Reportable Access under Finite Capacity** — cognitive reportability paper.
18. **FDS-LC0 Life/Cognitive Bridge Registry** — life and cognitive science bridge claims.
19. **FDS-E1 Finite-Capacity Prospect Theory** — state-dependent loss aversion, reference dependence, probability weighting.
20. **FDS-X1 Horizon-Maintenance Dark Energy** — pre-Euclid bridge note.
21. **DT-Archive** — broad claim-space archive and historical map.
22. **FDS-A1** — retained as conceptual timestamp for artificial agency.

---

## Key Documents

| Code | Document | Status | DOI / Link |
|---|---|---|---|
| **DT-Archive** | *Distinction Theory: A General Theory of Finite Systems* | Zenodo archive | [10.5281/zenodo.20130174](https://doi.org/10.5281/zenodo.20130174) |
| **FDS-0** | *Active Finite Distinction Systems: A Formal Core for Boundary Maintenance under Finite Capacity* | Zenodo preprint | [10.5281/zenodo.20158923](https://doi.org/10.5281/zenodo.20158923) |
| **FDS-P0** | *Physical Bridge Claim Registry for Active Finite Distinction Systems* | Zenodo preprint | [10.5281/zenodo.20159995](https://doi.org/10.5281/zenodo.20159995) |
| **FDS-T1** | *Finite Distinguishability Budgets and Maintenance Bounds for Physical Observers* | Released | [10.5281/zenodo.20234249](https://doi.org/10.5281/zenodo.20234249) |
| **FDS-O1** | *Observer as a Finite Distinction Register: Measurement Capacity, Dynamic Bottlenecks, and Budget-Crossing Signatures* | Released | [10.5281/zenodo.20248792](https://doi.org/10.5281/zenodo.20248792) |
| **FDS-O2** | *Time as Irreversible Distinction Update: Finite Records, Causal Ordering, and Register-Time Collapse* | Released | [10.5281/zenodo.20249369](https://doi.org/10.5281/zenodo.20249369) |
| **FDS-T3** | *Capacity Overflow and Effective Stochasticity: Non-Injective Projection, Critical Deficit, Phase-B Invariants, and the Information-Theoretic Origin of Coarse Dynamics* | Released | [10.5281/zenodo.20250367](https://doi.org/10.5281/zenodo.20250367) |
| **FDS-P1** | *Physical Distinction Carriers and Erasure Maps: Accounting Boundaries, Distinction-to-Noise Ratio, and Thermodynamic Implementation* | Released | [10.5281/zenodo.20251854](https://doi.org/10.5281/zenodo.20251854) |
| **FDS-P2** | *Bounded-Memory Reversible Computation and Housekeeping Dissipation: Garbage Entropy, Cleanup Scheduling, and the Cost of Delayed Erasure* | Released | [10.5281/zenodo.20252480](https://zenodo.org/records/20252480) |
| **FDS-L1** | *Life and Death as Boundary Maintenance* | Released | DOI pending |
| **FDS-LC0** | *Life and Cognitive Science Bridge Claim Registry for Active Finite Distinction Systems* | Zenodo registry | [10.5281/zenodo.20183373](https://doi.org/10.5281/zenodo.20183373) |
| **FDS-C1** | *Consciousness and Forgetting as Compression and Active Pruning* | Released | [10.5281/zenodo.20229509](https://zenodo.org/records/20229509) |
| **FDS-A1** | *Active Finite Distinction Systems as a Criterion for Artificial Agency* | Zenodo / frozen public AI line | [10.5281/zenodo.20184709](https://doi.org/10.5281/zenodo.20184709) |
| **FDS-X1** | *Horizon-Maintenance Dark Energy: A Pre-Euclid Bridge Note from Finite Distinguishability* | Released | [10.5281/zenodo.20234391](https://doi.org/10.5281/zenodo.20234391) |
| **FDS-E1** | *Finite-Capacity Prospect Theory: State-Dependent Risk Preferences under Resource, Attention, and Boundary-Risk Constraints* | Released | [10.5281/zenodo.20237306](https://doi.org/10.5281/zenodo.20237306) |
| **FDS-N1** | *Boundary-Maintaining Self-Organizing Systems under Finite Capacity: Maintenance Load, Phase-C Collapse, and Invariant Selection* | Released | [10.5281/zenodo.20253151](https://doi.org/10.5281/zenodo.20253151) |
| **FDS-P5** | *Capacity Deficit and Entropy Production in Active Finite Systems: A Generalized Dissipation Ledger for Boundary Maintenance* | Released | [10.5281/zenodo.20254259](https://doi.org/10.5281/zenodo.20254259) |
| **FDS-O3** | *Boundary Maintenance and the Second Law under Finite Memory: Irreversible Record Reuse, Entropy Ledgers, and Operational Time Arrows* | Released | [10.5281/zenodo.20255129](https://doi.org/10.5281/zenodo.20255129) |
| **FDS-M0** | *The Agency-Semantics Spine of Distinction Theory: Attention, Value, Goal, Meaning, and Action under Finite Capacity* | Released | [10.5281/zenodo.20257939](https://doi.org/10.5281/zenodo.20257939) |
| **FDS-M1** | *Attention as Distinction Admission in Finite Systems: Capacity-Limited Gating, Boundary Relevance, and Tunnel Vision* | Released | [10.5281/zenodo.20258570](https://doi.org/10.5281/zenodo.20258570) |
| **FDS-M2** | *Value and Goal as Boundary-Relevance Ranking: Causal Boundary Gradients, Goal Stability, and Value Drift under Finite Capacity* | Released | [10.5281/zenodo.20262998](https://doi.org/10.5281/zenodo.20262998) |
| **FDS-M3** | *Meaning as Actionable Semantic Quotient: Policy-Preserving Compression, Semantic Deficit, and False Meaning under Finite Capacity* | Released | [10.5281/zenodo.20263294](https://doi.org/10.5281/zenodo.20263294) |
| **FDS-P4** | *Coarse-Grained Anti-Recurrence and Informational Hysteresis in Finite Memory Systems: Lost Preimages, Side Records, and Capacity-Recovery Asymmetry* | Released | [10.5281/zenodo.20265065](https://doi.org/10.5281/zenodo.20265065) |
| **FDS-P7** | *Topological Obstruction to Forgetting in Finite Distinction Systems: Quotient Invariants, Non-Hermitian Skin Effects, and Topological Side-Ledgers* | Released | [10.5281/zenodo.20265386](https://doi.org/10.5281/zenodo.20265386) |

---

## Falsifiability and Failure Propagation

A central design principle is that claims should specify how they can fail.

The framework uses:
- epistemic tiers;
- dependency maps;
- physical bridge assumptions;
- domain-specific mappings;
- falsification conditions;
- demotion rules;
- quarantine boundaries;
- downstream failure propagation.

Basic rule:

> Failure of a downstream bridge claim does not automatically falsify the formal FDS Core.

See [FAILURE_REGISTRY.md](FAILURE_REGISTRY.md) and [CLAIM_STATUS.md](CLAIM_STATUS.md) for current status.

---

## Core Idea

Distinction Theory begins from a primitive operation:

> **Distinction** — the operation by which "this" is separated from "not-this."

Once a system distinguishes itself from what it is not, it inherits a boundary.
Once it has a boundary, it faces finite representational capacity.
Once capacity is finite, it must approximate.
Approximation creates error.
Error correction creates complexity.
Complexity creates maintenance pressure.
Finite systems must eventually prune, externalize, relax the task, collapse, or persist through invariant-supported structure.

---

## Repository Contents

```text
Distinction-Theory/
├── README.md
├── CLAIM_LEDGER.md          # Canonical claim index
├── TIMESTAMPS.md            # Public timestamp records
├── VERSION_HISTORY.md       # Version evolution
├── CLAIM_STATUS.md
├── FAILURE_REGISTRY.md
├── EVALUATION_PROTOCOL.md
├── PRIOR_ART_BOUNDARY.md
├── CONFLICTS_OF_INTEREST.md # AI/robotics commercial scope
├── RELEASE_PROTOCOL.md      # Release workflow
├── REPRODUCIBILITY.md       # Reproducibility standards
├── CITATION.cff
├── OFFICIAL_LINKS.md
├── START_HERE.md
├── VIDEOS.md
├── claims/
│   ├── claim_schema.md
│   ├── claims.csv
│   └── claims.yaml
├── papers/
│   ├── archive/
│   ├── core/
│   ├── economics/
│   ├── physics/
│   ├── ai/
│   │   └── PUBLIC_SCOPE_NOTE.md
│   └── life_cognition/
├── source/
├── models/
└── registries/
```

---

## Citation

See [CITATION.cff](CITATION.cff) for full citation metadata.

---

## License

Unless otherwise stated, written materials in this repository are released for scholarly reading, citation, and discussion.

---

## Contact

Yining Wu  
Independent Researcher  
[yining.wu@alumni.upenn.edu](mailto:yining.wu@alumni.upenn.edu)
