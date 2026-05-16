# DT/FDS Canonical Claim Ledger

This file records the canonical public claim IDs of the Distinction Theory / Active Finite Distinction Systems research programme.

**Purpose:** priority, auditability, dependency tracking, and falsification management.

A claim appearing here is not automatically asserted as established. Each claim is assigned:
- a claim ID;
- a statement;
- epistemic status;
- dependencies;
- first public timestamp;
- source document;
- what is not claimed;
- falsification or demotion condition;
- downstream consequences.

**Last updated:** 2026-05-16

---

## Core Claims

### FDS-CORE-001 — Distinction Primitive

**Statement.** A distinction is an operation or relation that separates at least two alternatives within a possibility space.

**Status.** Formal definition.

**Dependencies.** None (primitive).

**Not claimed.** This is not a claim about physics, consciousness, or computation. It is an operational starting point.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** The primitive is not falsified in the usual sense; its usefulness can fail.

**Downstream.** FDS-CORE-002, FDS-CORE-003.

---

### FDS-CORE-002 — Boundary Inheritance

**Statement.** Once a system distinguishes itself from what it is not, it inherits a boundary. A boundary separates internal from external and incurs maintenance cost.

**Status.** Formal definition.

**Dependencies.** FDS-CORE-001.

**Not claimed.** This does not imply a specific physical membrane. Boundaries may be operational, functional, or formal.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Counterexample of a bounded system with zero maintenance cost under sustained distinction load.

**Downstream.** FDS-CORE-003.

---

### FDS-CORE-003 — Finite Capacity

**Statement.** A finite system with a boundary has finite representational and operational capacity.

**Status.** Formal / operational claim.

**Dependencies.** FDS-CORE-002.

**Not claimed.** This does not derive the specific numerical value of any capacity bound. It states finiteness in principle.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** A physically instantiated bounded system with demonstrably infinite operational capacity.

**Downstream.** FDS-CORE-004.

---

### FDS-CORE-004 — Capacity Deficit

**Statement.** When task-relevant distinction demand exceeds accessible capacity, the system operates under a capacity deficit.

**Status.** Formal definition.

**Dependencies.** FDS-CORE-003.

**Not claimed.** Deficit alone does not imply collapse. It may be managed through exits.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Not directly falsifiable; usefulness of the framing can fail.

**Downstream.** FDS-CORE-005.

---

### FDS-CORE-005 — Budget Exits: Prune / Externalize / Collapse

**Statement.** A finite system under persistent positive capacity deficit must prune, externalize, relax the task, compress, or collapse.

**Status.** Conditional theorem.

**Dependencies.** FDS-CORE-004.

**Not claimed.** This does not prescribe which exit occurs; it states that at least one is compulsory under sustained deficit.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** A finite system under sustained capacity deficit with none of the listed exits and no equivalent alternative.

**Downstream.** FDS-CORE-006, FDS-T1-005.

---

### FDS-CORE-006 — Invariant-Supported Persistence

**Statement.** Systems that persist under finite capacity do so by maintaining invariants that reduce effective distinction load.

**Status.** Conditional theorem.

**Dependencies.** FDS-CORE-005.

**Not claimed.** This does not identify which invariants are used in any specific system.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** A persistent finite system under sustained capacity deficit with no invariant-supported load reduction and no exit class.

---

## T1 — Finite Observer / Distinguishability Budget Claims

### FDS-T1-001 — Finite Observer Projection

**Statement.** A finite physical observer O can operationally use only a finite image Im(pi_O) of a physical possibility space, giving N_O = |Im(pi_O)| and C_O = log2 N_O.

**Status.** Operational / physical bridge claim.

**Dependencies.** Finite record-bearing system; finite memory or finite error tolerance; finite operational timescale; finite update resources.

**Not claimed.** This does not imply consciousness. It does not solve quantum measurement. It does not claim all information in the universe is available to any observer.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** A physically finite observer reliably registering, preserving, updating, and operationally using unbounded distinctions under finite resources.

**Downstream.** FDS-T1-002, FDS-T1-003, FDS-T1-004.

---

### FDS-T1-002 — Distinguishability Budget

**Statement.** The operational distinguishability of a finite observer is bounded by the minimum of its internal record capacity and the information capacity of its accessible boundary or channel.

**Status.** Conditional theorem.

**Dependencies.** FDS-T1-001; Bekenstein and holographic bridges (physical assumptions).

**Not claimed.** This does not specify which bound dominates in every regime.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** An observer reliably using more distinctions than any accessible capacity bound allows.

**Downstream.** FDS-T1-003.

---

### FDS-T1-003 — Stock Capacity vs Update Throughput

**Statement.** Accessible capacity separates into stock capacity (storage / boundary / channel / externalization) and update throughput (Landauer-limited irreversible operations). The effective task capacity is the minimum of the two.

**Status.** Formal definition / conditional theorem.

**Dependencies.** FDS-T1-002; Landauer bridge assumption.

**Not claimed.** This does not claim every operation is Landauer-charged. Stable storage and reversible operations are excluded.

**First timestamp.** FDS-T1 v1.1, 2026-05-16.

**Failure condition.** A finite observer reliably performing tasks that exceed both stock and throughput bounds simultaneously.

**Downstream.** FDS-T1-004, FDS-T1-005.

---

### FDS-T1-004 — Boundary-Relative Capacity Deficit

**Statement.** The FDS-T1 capacity deficit is Delta_FDS = R_min^(tau)(epsilon; Psi) - C_acc, where R_min is the task-relevant rate-distortion demand and C_acc is the accessible capacity bottleneck.

**Status.** Definition.

**Dependencies.** FDS-T1-003.

**Not claimed.** Positive deficit is not automatically failure; it may trigger exits.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not falsified directly; only usefulness of the framing can fail.

**Downstream.** FDS-T1-005.

---

### FDS-T1-005 — Budget-Exit Theorem

**Statement.** If Delta_FDS > 0 persists, a finite observer cannot maintain full-fidelity task performance using internal accessible capacity alone. It must enter at least one exit class: coarse-graining or compression, externalization, pruning, task relaxation, or failure.

**Status.** Conditional theorem.

**Dependencies.** FDS-T1-004; FDS-CORE-005.

**Not claimed.** The theorem does not predict which exit occurs.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Full-fidelity task performance under sustained positive deficit with no exit observed.

**Downstream.** FDS-T1-006, FDS-T1-007.

---

### FDS-T1-006 — Maintenance Inequality

**Statement.** Positive capacity deficit implies a Landauer-style lower bound on thermodynamic maintenance cost when the surplus distinctions are irreversibly erased.

**Status.** Conditional physical bridge.

**Dependencies.** FDS-T1-005; Landauer bridge; finite available free energy.

**Not claimed.** This is a lower bound, not a full thermodynamic model. Physical overhead dominates in most regimes.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Reliable irreversible erasure below Landauer cost under stated conditions.

---

### FDS-T1-007 — Budget-Crossing Signature

**Statement.** As chi = R_min - C_acc crosses zero from negative to positive, finite observers should exhibit measurable transitions in error, latency, compression, externalization, pruning, heat, or failure.

**Status.** Testable prediction.

**Dependencies.** FDS-T1-005.

**Not claimed.** The magnitude and sharpness of the transition depend on system class.

**First timestamp.** FDS-T1 v1.1, 2026-05-16.

**Failure condition.** No measurable transition in any relevant observable under controlled budget crossing.

---

### FDS-T1-008 — Bottleneck-Switching Kink

**Statement.** When accessible capacity switches between bottleneck regimes (memory, boundary, channel, update), the rate-distortion error floor shows slope discontinuities (kinks) at each transition.

**Status.** Conditional theorem (model-supported).

**Dependencies.** FDS-T1-003; rate-distortion theory.

**Not claimed.** The kink magnitude is model-dependent.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Smooth error floor under controlled bottleneck switching with no measurable slope change.

---

## L1 — Active Pruning / Protocell Claims

### FDS-L1-001 — Residue-Pruning-Boundary Loop

**Statement.** In protocell-like finite systems, sustained flux generates residue; residue impairs boundary and access function; active pruning controls residue and maintains persistence.

**Status.** Conditional claim (model + simulation supported).

**Dependencies.** Finite boundary system; sustained input flux; measurable residue.

**Not claimed.** This does not claim all biological persistence follows this loop.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

**Failure condition.** A protocell-like system with sustained flux and no pruning mechanism that maintains indefinite persistence.

---

### FDS-L1-002 — Active Pruning Threshold

**Statement.** There exists a critical pruning rate S_c below which residue cannot be bounded and the system approaches collapse.

**Status.** Conditional theorem (model-supported).

**Dependencies.** FDS-L1-001.

**Not claimed.** S_c is system-dependent.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

**Failure condition.** Persistent system under sustained flux with pruning rate below S_c and no equivalent maintenance mechanism.

---

### FDS-L1-003 — Maintenance-Attractor Loss

**Statement.** When pruning falls below threshold, the system crosses a saddle-node fold and loses the stable maintenance attractor.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-002.

**Not claimed.** The saddle-node normal form is a local approximation; other transition types are possible.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

**Failure condition.** Collapse without fold-like slowing or critical slowing-down signatures under quasi-static parameter drift.

---

### FDS-L1-004 — Rescue-Window Closure

**Statement.** Restoring pruning after interruption rescues the system only within a finite delay window; after the window closes, rescue requires stronger pruning or fails.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-002.

**Not claimed.** Window duration is system-dependent.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

**Failure condition.** Pruning restoration always rescues the system independent of delay or state.

---

### FDS-L1-005 — Spatial Clogging / Boundary Deformation

**Statement.** In spatial models, residue accumulation causes local clogging and boundary deformation, increasing local pruning demand.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-001.

**Not claimed.** Not all systems exhibit spatial clogging.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

---

### FDS-L1-006 — Radius-Dependent Pruning Demand

**Statement.** In spatially extended protocell models, required pruning increases with system radius due to surface-to-volume scaling of residue influx.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-005.

**First timestamp.** FDS-L1 submitted manuscript, 2026.

---

## C1 — Reportable Access Claims

### FDS-C1-001 — Reportability as Finite-Capacity Maintenance

**Statement.** Conscious reportability can be modeled as a maintained finite-capacity regime: a system must maintain task-relevant distinctions under bounded capacity, sustained input, residue accumulation, and active pruning.

**Status.** Theoretical framework claim.

**Dependencies.** FDS-CORE-003, FDS-CORE-004.

**Not claimed.** This does not solve the hard problem of phenomenal consciousness.

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

**Failure condition.** Sustained reportable access under positive capacity deficit with no pruning, no externalization, no compression, and no task relaxation.

---

### FDS-C1-002 — Representational Residue

**Statement.** Unresolved rate-distortion surplus accumulates as representational residue, which damages access-network coherence and reportability.

**Status.** Conditional claim.

**Dependencies.** FDS-C1-001.

**Not claimed.** Not all cognitive load produces residue in this specific sense.

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

---

### FDS-C1-003 — Active Cognitive Pruning Threshold

**Statement.** There exists a critical cognitive pruning rate S_c for maintaining reportable access under sustained cognitive load.

**Status.** Conditional claim.

**Dependencies.** FDS-C1-002; FDS-L1-002.

**Not claimed.** S_c depends on task, capacity, and individual differences.

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

---

### FDS-C1-004 — Access-Network Collapse / Early Warning

**Statement.** Near reportability collapse, leading covariance eigenvalues of the access network rise, providing an early-warning signal.

**Status.** Model-supported prediction.

**Dependencies.** FDS-C1-001.

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

---

## LC0 — Life/Cognitive Registry Claims

### FDS-LC0-001 — Registry Structure

**Statement.** FDS-LC0 registers life-science and cognitive-science bridge claims with dependency labels, risk levels, failure conditions, and downstream propagation rules.

**Status.** Registry governance claim.

**Dependencies.** LC0 registry document.

**First timestamp.** FDS-LC0 v1.0, 2026-05-14.

---

### FDS-LC0-002 — Downstream Failure Propagation Rule

**Statement.** Failure of a life/cognitive domain bridge does not automatically propagate to upstream physical bridges or the formal core.

**Status.** Registry governance rule.

**Dependencies.** LC0 registry structure.

**First timestamp.** FDS-LC0 v1.0, 2026-05-14.

---

## X1 — Horizon-Maintenance Dark Energy Claims

### FDS-X1-001 — Cosmological Horizon as Finite Distinguishability Boundary

**Statement.** Cosmological horizons act as finite distinguishability boundaries for finite observers, constraining accessible distinction capacity.

**Status.** High-risk physical bridge claim (pre-registration planned).

**Dependencies.** FDS-T1-001; FDS-T1-002; general relativity (as background).

**Not claimed.** This does not derive GR, quantum gravity, or a complete cosmological model.

**First timestamp.** Planned pre-Euclid note.

**Failure condition.** Robust demonstration that cosmological horizons impose no finite distinguishability constraint.

---

### FDS-X1-002 — Horizon-Maintenance Energy Scale

**Statement.** If cosmological horizons are finite distinguishability boundaries, horizon-maintenance cost has characteristic energy scale rho_HM ~ H^2 M_Pl^2, consistent with the observed dark-energy scale.

**Status.** High-risk physical bridge claim (pre-registration planned).

**Dependencies.** FDS-X1-001.

**Not claimed.** This does not claim to derive the exact numerical value of the cosmological constant.

**First timestamp.** Planned pre-Euclid note.

**Failure condition.** High-precision confirmation that dark energy has no relation to horizon-scale maintenance physics.

---

### FDS-X1-003 — Non-Phantom Dynamical Dark Energy

**Statement.** If horizon-maintenance cost drives late-time acceleration, the effective equation of state tends toward w = -1 from above (non-phantom), with possible mild evolution.

**Status.** High-risk physical bridge prediction (pre-registration planned).

**Dependencies.** FDS-X1-002.

**Not claimed.** This does not predict the exact w(z) or its time derivative.

**First timestamp.** Planned pre-Euclid note.

**Failure condition.** Robust high-precision detection of w < -1 (phantom) at any redshift rules out the strict non-phantom version. Measurement of w = -1 exactly with no evolution demotes the dynamical version.

---

### FDS-X1-004 — Falsification / Demotion Contract

**Statement.** The X1 claim family has explicit falsification, demotion, and quarantine conditions stated in advance. Failure of X1 does not affect upstream T1 or core claims.

**Status.** Governance commitment.

**Dependencies.** FDS-X1-001—003.

**First timestamp.** Planned pre-Euclid note.

---

## A1 — AI Agency Frozen Line Claims

### FDS-A1-001 — Artificial Agency as Active Finite Distinction System

**Statement.** An artificial agent is an active finite distinction system that maintains an operational boundary through durable updates, causal loop closure, capacity-deficit management, and resource-governed persistence.

**Status.** Conceptual criterion (frozen public AI line).

**Dependencies.** FDS-CORE-002—005.

**Not claimed.** This does not claim that any specific architecture is or is not an agent. It provides an operational criterion.

**First timestamp.** FDS-A1 v1.0, 2026-05-12.

**Failure condition.** A non-FDS system satisfying all listed criteria, or an FDS-satisfying system that is clearly not an agent by all reasonable definitions.

---

### FDS-A1-002 — AI Public Line Frozen Due to Commercial Scope

**Statement.** The public DT/FDS programme retains FDS-A1 as a conceptual timestamp but does not develop proprietary AI/robotics architectures, private benchmarks, product designs, or commercial implementation details in this repository.

**Status.** Governance statement.

**Dependencies.** None (scope decision).

**First timestamp.** CONFLICTS_OF_INTEREST.md, 2026-05-16.

---

*End of ledger. New claims added as documents are released or revised.*
