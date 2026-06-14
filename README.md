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
- **FDS-T2** — effective geometry as horizon boundary accounting / horizon-ledger bridge. DOI: 10.5281/zenodo.20284911.
- **FDS-O1** — observer as a finite distinction register. DOI: 10.5281/zenodo.20248792.
- **FDS-O2** — time as irreversible distinction update. DOI: 10.5281/zenodo.20249369.
- **FDS-O3** — boundary maintenance and the Second Law under finite memory. DOI: 10.5281/zenodo.20255129.
- **FDS-T3** — capacity overflow and effective stochasticity. DOI: 10.5281/zenodo.20250367.
- **FDS-Q1** — finite record boundaries in Wigner's friend scenarios. DOI: 10.5281/zenodo.20289215.
- **FDS-Q2** — finite distinction maintenance in fault-tolerant quantum computation / logical distinction ledgers. DOI: 10.5281/zenodo.20302569. [Video](https://www.youtube.com/watch?v=kIS-Ij6x1Ls).

### Physics → G1

- **FDS-G1** — *Finite Screen Spacetime: Entropy-Response Geometry from Causal-Screen Ledgers.* Complete Series v1.3. Preserves the v1.2 production-refined M<sub>3/4</sub> evidence and adds Companion G as the matter-sector / dark-matter ontology companion with G1DM compressed diagnostic layer (\(T^D\neq0\), \(\mu_{\rm grav}\simeq1\), \(\mathcal D_{\rm optics}^{S_8}\neq0\) at compressed-proxy level). G1DE-M<sub>3/4</sub> projection-locked branch selected by production-refined 8-seed 7-model homogeneous nested-evidence audit (\(d\log Z=0.1\)). KiDS-1000 shear-only diagnostics support the Weyl channel; full \(3\times2\)pt, CMB/BBN, nonlinear validation pending. **Production-refined evidence-selected, not production-confirmed.** Open limitations: D0 calibration lemmas, source–kernel factorization not unique, nn/clustering channel missing. [Paper DOI: 10.5281/zenodo.20521142](https://doi.org/10.5281/zenodo.20521142). [Video](https://www.youtube.com/watch?v=lJQYHDL5KY0). [Replication Kit](papers/FDS_G1/replication_kit).

- **FDS-H1** — *Finite Causal-Screen Holography: Boundary Capacity, Bulk Recovery, and Gluing Obstruction.* First H-series bridge paper. Formulates holography as finite boundary recovery; defines finite screen ledgers, recovery nets, exact (nerve-graph) and tolerant (Lipschitz) gluing theorems, and a matched-entropy/split-recovery proposition. Supplies candidate screen variables and recovery-obstruction structures for H2/H3. Does not derive G1 or M3/4. [Paper DOI: 10.5281/zenodo.20541234](https://doi.org/10.5281/zenodo.20541234).

- **FDS-H2** — *Recoverable-Support Geometry and Response Visibility.* Second H-series bridge paper. Constructs a formal recoverable-support bridge architecture from H1 finite recovery to G1 premetric response. Defines non-Abelian \v{C}ech--de Rham recovery descent, registered chamberwise connection rules, relative Kato recoverable-support geometry with support-equivalent channel blindness, regular physical quotient bundle, and two independent bridge branches: an operational-covector bridge with flat coefficients ($\dd\omega_{\rm th}=\ell(F_{\rm phys})$) tested by Stokes residuals and closed-cycle periods, and a response-bundle bridge with holonomy-intertwiner existence criterion. Separates holonomy-relative parallel readouts from character-based full-group Abelianization. Does not derive G1, GR, or $M_{3/4}$. [Paper DOI: 10.5281/zenodo.20567788](https://doi.org/10.5281/zenodo.20567788).

- **FDS-Q0** — *Boundary-Access Holonomy and the Quantum Reversible Quotient.* Upstream quantum-access layer. Formulates standard QM as the zero-record-holonomy quotient of asymmetric finite boundary access. Restricted quotient-consistency theorem, three-holonomy separation (coherent/record/leakage), Mach-Zehnder stable-record and QEC directed-leakage operational models. Born-rule program is a companion target. Does not derive CP^{N-1}, the Born rule, or full Hilbert reconstruction. [Paper DOI: 10.5281/zenodo.20542105](https://doi.org/10.5281/zenodo.20542105). [Video](https://www.youtube.com/watch?v=aZf9aw-5enw).

### Physical Bridge Ladder

- **FDS-P0** — physical bridge claim registry. DOI: 10.5281/zenodo.20159995.
- **FDS-P1** — physical distinction carriers and erasure maps. DOI: 10.5281/zenodo.20251854.
- **FDS-P2** — bounded-memory reversible computation and housekeeping dissipation. DOI: 10.5281/zenodo.20252480.
- **FDS-P3** — finite-bath memory, Markovianization, and environmental forgetting. DOI: 10.5281/zenodo.20272541.
- **FDS-P4** — coarse-grained anti-recurrence and informational hysteresis. DOI: 10.5281/zenodo.20265065.
- **FDS-P5** — capacity deficit and entropy production ledger. DOI: 10.5281/zenodo.20254259.
- **FDS-P6** — speed, precision, and dissipation bounds for boundary maintenance. DOI: 10.5281/zenodo.20269733.
- **FDS-P7** — topological obstruction to forgetting / invariant side-ledgers / NHSE bridge. DOI: 10.5281/zenodo.20265386.
- **FDS-P8** — residue spectral dynamics, coupled residue channels, memory kernels, Markov closure. DOI: 10.5281/zenodo.20611696.

### Domain Bridges

- **FDS-N1** — boundary-maintaining self-organizing systems. DOI: 10.5281/zenodo.20253151.
- **FDS-E1** — finite-capacity prospect theory. DOI: 10.5281/zenodo.20237306. Also available at SocArXiv: 10.31235/osf.io/pj43k_v1.
- **FDS-B0** — biomedical bridge registry / non-clinical framework / safety firewall. DOI: 10.5281/zenodo.20312983.
- **FDS-B1** — immunity as boundary verification / normal-form dynamics / adversarial classification / distributed topology / non-clinical proxy maps. DOI: 10.5281/zenodo.20327539. [Video](https://www.youtube.com/watch?v=crvO77ytI6A).
- **FDS-LC0** — life and cognitive science bridge claim registry. DOI: 10.5281/zenodo.20183373.
- **FDS-A1** — artificial agency criterion (frozen public AI line). DOI: 10.5281/zenodo.20184709.

### Frontier Physical Consequences

- **FDS-X1** — horizon-maintenance dark energy (pre-Euclid bridge note). DOI: 10.5281/zenodo.20290215.
- **FDS-X2** — three fermion generations as CP/T-asymmetric identity transformation. DOI: 10.5281/zenodo.20289955.
- **FDS-X3** — functional decomposition of the four fundamental interactions. DOI: 10.5281/zenodo.20388356. [Video](https://www.youtube.com/watch?v=5kdst0aEcC4).
- **FDS-X4** — Pauli exclusion as finite address protection. DOI: 10.5281/zenodo.20278029.
- **FDS-X5** — mathematical form of physical law as invariant-form compression. DOI: 10.5281/zenodo.20278236.

### Operational Trident

The Operational Trident translates finite distinguishability budgets into observer-level physical processes.

- **FDS-O1 — Observer as a Finite Distinction Register.** Measurement capacity, dynamic bottlenecks, record formation, buffering, housekeeping heat, and budget-crossing signatures. DOI: 10.5281/zenodo.20248792.
- **FDS-O2 — Time as Irreversible Distinction Update.** Register time as causally ordered irreversible finite-record update, with synchronization bottlenecks, non-injective update, dissipative projection, and register-time collapse. DOI: 10.5281/zenodo.20249369.
- **FDS-O3 — Boundary Maintenance and the Second Law under Finite Memory.** Finite-memory operational Second-Law channel, record-turnover entropy, irreversibility from bounded memory. DOI: 10.5281/zenodo.20255129.

---

## Public Academic Spine and AI Scope

The public academic spine currently prioritizes:

1. **FDS-0** — formal finite-system core.
2. **FDS-G1** — finite-screen entropy-response geometry (physics flagship).
3. **FDS-T1** — finite observers and distinguishability budgets.
4. **FDS-T2** — effective geometry as horizon boundary accounting / horizon-ledger bridge.
5. **FDS-O1** — observer as a finite distinction register.
6. **FDS-O2** — time as irreversible distinction update.
7. **FDS-T3** — capacity overflow and effective stochasticity.
8. **FDS-O3** — boundary maintenance and the Second Law under finite memory.
9. **FDS-N1** — boundary-maintaining self-organizing systems under finite capacity.
10. **FDS-P1** — physical distinction carriers and erasure maps.
11. **FDS-P2** — bounded-memory reversible computation and housekeeping dissipation.
12. **FDS-P5** — capacity deficit and entropy-production ledger.
13. **FDS-LC0** — life and cognitive science bridge claim registry.
14. **FDS-B0** — biomedical bridge registry / non-clinical framework / safety firewall.
15. **FDS-B1** — immunity as boundary verification / normal-form dynamics / adversarial classification / distributed topology / non-clinical proxy maps.
16. **FDS-E1** — finite-capacity prospect theory and boundary-risk preferences. SocArXiv preprint: 10.31235/osf.io/pj43k_v1.
17. **FDS-X1** — pre-Euclid horizon-maintenance dark-energy bridge note (released).
18. **FDS-X2** — three fermion generations as CP/T-asymmetric identity transformation (released).
19. **FDS-X3** — functional decomposition of the four fundamental interactions (released).
20. **FDS-X4** — Pauli exclusion as finite address protection (released).
21. **FDS-X5** — mathematical form of physical law as invariant-form compression (released).
22. **FDS-Q1** — finite record boundaries in Wigner's friend scenarios (released).
23. **FDS-Q2** — finite distinction maintenance in fault-tolerant quantum computation (released).
24. **FDS-Q0 Boundary-Access Holonomy** — zero-record-holonomy quotient, three-holonomy separation, stable-record and QEC leakage operational models.
25. **FDS-H2 Recoverable-Support Geometry and Response Visibility** — non-Abelian recovery descent, Kato support geometry, two independent bridge branches, holonomy-relative visibility.

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
2. **FDS-G1 Finite Screen Spacetime** — physics flagship: finite-screen entropy-response geometry, G1DE-M₃/₄ evidence-selected.
3. **FDS-T1 Finite Observers and Distinguishability Budgets** — finite observers, accessible capacity, information bounds, maintenance-cost accounting.
4. **FDS-T2 Effective Geometry as Horizon Boundary Accounting** — horizon-ledger bridge: effective geometry from finite distinguishability, non-equilibrium residuals, Phase-B geometry selection.
5. **FDS-O1 Observer as a Finite Distinction Register** — measurement as finite record formation under dynamic bottlenecks, buffering, and budget-crossing signatures.
6. **FDS-O2 Time as Irreversible Distinction Update** — register time as causally ordered irreversible finite-record update.
7. **FDS-O3 Boundary Maintenance and the Second Law** — finite-memory operational Second-Law channel.
8. **FDS-T3 Capacity Overflow and Effective Stochasticity** — common mechanism: capacity overflow induces effective stochasticity.
9. **FDS-N1 Self-Organization Bridge** — complex-systems normal form: boundary-maintaining self-organization, Phase-C collapse, invariant selection.
10. **FDS-P0 Physical Bridge Registry** — physical bridge claims, dependency structure.
11. **FDS-P1 Physical Distinction Carriers** — Physical Bridge Ladder I.
12. **FDS-P2 Bounded-Memory Reversible Computation** — Physical Bridge Ladder II.
13. **FDS-P5 Deficit-Driven Entropy Ledger** — Physical Bridge Ladder III.
14. **FDS-B0 Biomedical Bridge Registry** — non-clinical framework, safety firewall, maintenance debt.
15. **FDS-B1: Immunity as Boundary Verification** — normal-form dynamics, adversarial classification, distributed topology, non-clinical proxy maps, dimensionless control numbers, crucial divergent predictions.
16. **FDS-LC0 Life/Cognitive Bridge Registry** — life and cognitive science bridge claims.
17. **FDS-E1 Finite-Capacity Prospect Theory** — state-dependent loss aversion, reference dependence, probability weighting. SocArXiv: 10.31235/osf.io/pj43k_v1.
18. **FDS-X1 Horizon-Maintenance Dark Energy** — pre-Euclid bridge note.
19. **FDS-X2 Three Fermion Generations** — CP/T-asymmetric identity transformation.
20. **FDS-X3 Functional Decomposition of Four Interactions** — operation closure.
21. **FDS-X4 Pauli Exclusion as Finite Address Protection** — collision-free occupancy.
22. **FDS-X5 Mathematical Form as Invariant Compression** — Wigner puzzle.
23. **FDS-Q1 Finite Record Boundaries in Wigner's Friend** — observer-relative record algebras, false promotion risk, record-availability horizon for quantum-device diagnostics.
24. **FDS-Q2 Finite Distinction Maintenance in Fault-Tolerant QC** — logical distinction ledgers, vector ledger audit, scaling-wall diagnostics, latency tax.
25. **FDS-Q0 Boundary-Access Holonomy** — zero-holonomy quotient, restricted quotient-consistency theorem, coherent/record/leakage holonomy separation, stable-record and QEC leakage models.
26. **FDS-H2 Recoverable-Support Geometry and Response Visibility** — non-Abelian recovery descent, Kato support geometry, two bridge branches, holonomy-relative visibility.
27. **DT-Archive** — broad claim-space archive and historical map.
28. **FDS-A1** — retained as conceptual timestamp for artificial agency.

---

## Key Documents

| Code | Document | Status | DOI / Link |
|---|---|---|---|
| **DT-Archive** | *Distinction Theory: A General Theory of Finite Systems* | Zenodo archive | [10.5281/zenodo.20130174](https://doi.org/10.5281/zenodo.20130174) |
| **FDS-0** | *Active Finite Distinction Systems: A Formal Core for Boundary Maintenance under Finite Capacity* | Zenodo preprint | [10.5281/zenodo.20158923](https://doi.org/10.5281/zenodo.20158923) |
| **FDS-G1** | *Finite Screen Spacetime: Entropy-Response Geometry from Causal-Screen Ledgers* | Released | [10.5281/zenodo.20521142](https://doi.org/10.5281/zenodo.20521142) | [Video](https://www.youtube.com/watch?v=lJQYHDL5KY0) | [Code](papers/FDS_G1/replication_kit) |
| **FDS-H1** | *Finite Causal-Screen Holography: Boundary Capacity, Bulk Recovery, and Gluing Obstruction* | Released | [10.5281/zenodo.20541234](https://doi.org/10.5281/zenodo.20541234) | — | [Code](papers/FDS_H1) |
| **FDS-H2** | *Recoverable-Support Geometry and Response Visibility* | Released | [10.5281/zenodo.20567788](https://doi.org/10.5281/zenodo.20567788) | — | — |
| **FDS-Q0** | *Boundary-Access Holonomy and the Quantum Reversible Quotient* | Released | [10.5281/zenodo.20542105](https://doi.org/10.5281/zenodo.20542105) | [Video](https://www.youtube.com/watch?v=aZf9aw-5enw) | — |
| **FDS-P0** | *Physical Bridge Claim Registry for Active Finite Distinction Systems* | Zenodo preprint | [10.5281/zenodo.20159995](https://doi.org/10.5281/zenodo.20159995) |
| **FDS-T1** | *Finite Distinguishability Budgets and Maintenance Bounds for Physical Observers* | Released | [10.5281/zenodo.20234249](https://doi.org/10.5281/zenodo.20234249) |
| **FDS-O1** | *Observer as a Finite Distinction Register: Measurement Capacity, Dynamic Bottlenecks, and Budget-Crossing Signatures* | Released | [10.5281/zenodo.20248792](https://doi.org/10.5281/zenodo.20248792) |
| **FDS-O2** | *Time as Irreversible Distinction Update: Finite Records, Causal Ordering, and Register-Time Collapse* | Released | [10.5281/zenodo.20249369](https://doi.org/10.5281/zenodo.20249369) |
| **FDS-T3** | *Capacity Overflow and Effective Stochasticity: Non-Injective Projection, Critical Deficit, Phase-B Invariants, and the Information-Theoretic Origin of Coarse Dynamics* | Released | [10.5281/zenodo.20250367](https://doi.org/10.5281/zenodo.20250367) |
| **FDS-P1** | *Physical Distinction Carriers and Erasure Maps: Accounting Boundaries, Distinction-to-Noise Ratio, and Thermodynamic Implementation* | Released | [10.5281/zenodo.20251854](https://doi.org/10.5281/zenodo.20251854) |
| **FDS-P2** | *Bounded-Memory Reversible Computation and Housekeeping Dissipation: Garbage Entropy, Cleanup Scheduling, and the Cost of Delayed Erasure* | Released | [10.5281/zenodo.20252480](https://zenodo.org/records/20252480) |
| **FDS-B0** | *FDS-B0: Biomedical Bridge Registry — A Non-Clinical Framework for Boundary Maintenance, Disease-Model Translation, and Safety Firewalls in Finite Distinction Systems* | Released | [10.5281/zenodo.20312983](https://doi.org/10.5281/zenodo.20312983) |
| **FDS-B1** | *Immunity as Boundary Verification: Normal-Form Dynamics, Adversarial Classification, Distributed Verification, and Non-Clinical Proxy Maps in Active Biological Systems* | Released | [10.5281/zenodo.20327539](https://doi.org/10.5281/zenodo.20327539) | [Video](https://www.youtube.com/watch?v=crvO77ytI6A) |
| **FDS-LC0** | *Life and Cognitive Science Bridge Claim Registry for Active Finite Distinction Systems* | Zenodo registry | [10.5281/zenodo.20183373](https://doi.org/10.5281/zenodo.20183373) |
| **FDS-A1** | *Active Finite Distinction Systems as a Criterion for Artificial Agency* | Zenodo / frozen public AI line | [10.5281/zenodo.20184709](https://doi.org/10.5281/zenodo.20184709) |
| **FDS-X1** | *Horizon-Maintenance Dark Energy: A Pre-Euclid Bridge Note from Finite Distinguishability* | Released | [10.5281/zenodo.20290215](https://doi.org/10.5281/zenodo.20290215) |
| **FDS-X2** | *Three Fermion Generations as CP/T-Asymmetric Identity Transformation: The CKM Lower Bound, Irreversible Pruning, and the Minimal Flavor Architecture of Finite Distinction Systems* | Released | [10.5281/zenodo.20289955](https://doi.org/10.5281/zenodo.20289955) |
| **FDS-X3** | *Functional Decomposition of the Four Fundamental Interactions: A Minimal Physical Distinction-Operation Closure for Finite Distinction Systems* | Released | [10.5281/zenodo.20388356](https://doi.org/10.5281/zenodo.20388356) | [Video](https://www.youtube.com/watch?v=5kdst0aEcC4) |
| **FDS-X4** | *Pauli Exclusion as Finite Address Protection: Collision-Free Fermionic Occupancy, Structural Diversity, and Stable Matter in Finite Distinction Systems* | Released | [10.5281/zenodo.20278029](https://doi.org/10.5281/zenodo.20278029) |
| **FDS-X5** | *Mathematical Form of Physical Law as Invariant-Form Compression: Invariant, Equivariant, and Covariant Law Forms in Finite Distinction Systems* | Released | [10.5281/zenodo.20278236](https://doi.org/10.5281/zenodo.20278236) |
| **FDS-E1** | *Finite-Capacity Prospect Theory: State-Dependent Risk Preferences under Resource, Attention, and Boundary-Risk Constraints* | Released | [10.5281/zenodo.20237306](https://doi.org/10.5281/zenodo.20237306) / [SocArXiv: 10.31235/osf.io/pj43k_v1](https://doi.org/10.31235/osf.io/pj43k_v1) |
| **FDS-Q1** | *Finite Record Boundaries in Wigner's Friend Scenarios: Observer-Relative Distinguishability and Quantum Record Availability in Finite Distinction Systems* | Released | [10.5281/zenodo.20289215](https://doi.org/10.5281/zenodo.20289215) |
| **FDS-Q2** | *FDS-Q2: Finite Distinction Maintenance in Fault-Tolerant Quantum Computation — Logical Distinction Ledgers, Error-Correction Infrastructure, and Architecture-Specific Resource Bounds* | Released | [10.5281/zenodo.20302569](https://doi.org/10.5281/zenodo.20302569) | [Video](https://www.youtube.com/watch?v=kIS-Ij6x1Ls) |
| **FDS-N1** | *Boundary-Maintaining Self-Organizing Systems under Finite Capacity: Maintenance Load, Phase-C Collapse, and Invariant Selection* | Released | [10.5281/zenodo.20253151](https://doi.org/10.5281/zenodo.20253151) |
| **FDS-P5** | *Capacity Deficit and Entropy Production in Active Finite Systems: A Generalized Dissipation Ledger for Boundary Maintenance* | Released | [10.5281/zenodo.20254259](https://doi.org/10.5281/zenodo.20254259) |
| **FDS-O3** | *Boundary Maintenance and the Second Law under Finite Memory: Irreversible Record Reuse, Entropy Ledgers, and Operational Time Arrows* | Released | [10.5281/zenodo.20255129](https://doi.org/10.5281/zenodo.20255129) |
| **FDS-P4** | *Coarse-Grained Anti-Recurrence and Informational Hysteresis in Finite Memory Systems: Lost Preimages, Side Records, and Capacity-Recovery Asymmetry* | Released | [10.5281/zenodo.20265065](https://doi.org/10.5281/zenodo.20265065) |
| **FDS-P7** | *Topological Obstruction to Forgetting in Finite Distinction Systems: Quotient Invariants, Non-Hermitian Skin Effects, and Topological Side-Ledgers* | Released | [10.5281/zenodo.20265386](https://doi.org/10.5281/zenodo.20265386) |
| **FDS-P8** | *Residue Spectral Dynamics and Markov Closure in Finite Distinction Systems: Coupled Residue Channels, Memory Kernels, and Operational Closure Bounds* | Released | [10.5281/zenodo.20611696](https://doi.org/10.5281/zenodo.20611696) |
| **FDS-P6** | *Speed, Precision, and Dissipation Bounds for Boundary Maintenance in Finite Distinction Systems: Finite Update Windows, Bottleneck Throughput, and Resource-Ledger Exit Theorems* | Released | [10.5281/zenodo.20269733](https://doi.org/10.5281/zenodo.20269733) |
| **FDS-P3** | *Finite-Bath Memory, Markovianization, and Environmental Forgetting in Finite Distinction Systems: Side Records, Memory Kernels, and the Loss of Recoverable Distinctions* | Released | [10.5281/zenodo.20272541](https://doi.org/10.5281/zenodo.20272541) |

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

- **Papers and documentation:** CC BY 4.0 — see [`LICENSE`](LICENSE).
- **Code:** MIT — see `papers/FDS_G1/replication_kit/LICENSE`.
- **External datasets:** governed by upstream licenses.
- **Figures/tables:** CC BY 4.0 unless generated from restricted data.

---

## Contact

Yining Wu  
Independent Researcher  
[yining.wu@alumni.upenn.edu](mailto:yining.wu@alumni.upenn.edu)
