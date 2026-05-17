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

## O1 — Observer as a Finite Distinction Register

FDS-O1 converts the finite-observer budget of FDS-T1 into an operational measurement model. It treats an observer as a finite distinction-register and measurement as stable record formation under sensor, channel, memory, buffer, update, and thermodynamic constraints.

### FDS-O1-001 — Observer as Finite Distinction-Register

**Statement.** An observer is a finite distinction-register rather than an ideal point of access to facts. It has finite record carriers, finite readout, finite stability, finite update, buffers, and finite task windows.

**Status.** Operational bridge.

**Dependencies.** FDS-T1-001.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** A complete physical account of registered observations requiring no finite carrier, boundary, stability condition, readout, or update capacity.

---

### FDS-O1-002 — Measurement as Stable Record Formation

**Statement.** A measurement is stable record formation over a finite retention and verification window, not merely an interaction.

**Status.** Operational definition.

**Dependencies.** FDS-O1-001.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** Operational measurement outcomes used without any stable record, reproducible trace, or accessible registration.

---

### FDS-O1-003 — Dynamically Bottlenecked Measurement Capacity

**Statement.** Measurement capacity is dynamically bottlenecked by sensor, channel, memory, record-stability, buffer, externalization, compression, and update constraints.

**Status.** Conditional theorem.

**Dependencies.** FDS-O1-002.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** Full-fidelity measurement bypasses all such constraints under bounded physical resources.

---

### FDS-O1-004 — Budget-Crossing Exits

**Statement.** When task-relevant demand crosses accessible capacity, observable exits should appear: coarse-graining, state merging, increased latency, buffering, externalization, reset, housekeeping heat, task relaxation, or failure.

**Status.** Testable prediction.

**Dependencies.** FDS-O1-003.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** No change in error, latency, coarse-graining, state merging, buffering, externalization, reset, heat, or failure under controlled crossing.

---

### FDS-O1-005 — Buffers Separate Transient from Sustained Crossing

**Statement.** Finite buffers allow transient demand spikes without sustained capacity violation. When buffer occupancy saturates, sustained crossing emerges.

**Status.** Engineering bridge.

**Dependencies.** FDS-O1-003.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** Finite buffers neither delay transient overload nor sharpen sustained overflow.

---

### FDS-O1-006 — Irreversible Record Reuse Carries Housekeeping Cost

**Statement.** Irreversible record reuse carries housekeeping cost under generalized Landauer accounting: fixed-memory overwrite produces higher immediate heat; expanding memory postpones erasure but accrues storage and garbage-collection costs.

**Status.** Physical bridge.

**Dependencies.** Landauer principle; FDS-O1-003.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** Repeated irreversible record reuse below generalized Landauer accounting after all reservoirs, correlations, and work sources are included.

---

### FDS-O1-007 — Active Inference Depends on Finite Record Formation

**Statement.** Active inference and robotic control presuppose finite record formation. If the observation register is saturated, delayed, compressed, or merged, inference operates on a lossy projection of the true observation.

**Status.** Interface claim.

**Dependencies.** Active inference; FDS-O1-001.

**First timestamp.** FDS-O1 v1.0, 2026-05-16.

**Failure condition.** Severe record compression, delay, merging, or unavailability has no measurable effect on inference or control under matched tasks.

---

## O2 — Time as Irreversible Distinction Update

FDS-O2 converts finite record formation into an operational model of register time. It treats usable temporal order for bounded observers as causally ordered irreversible distinction update under finite memory, finite clock precision, finite buffering, finite synchronization bandwidth, finite latency, and finite thermodynamic budgets.

### FDS-O2-001 — Register Time as Ordered Finite-Record Update

**Statement.** For a finite observer, usable temporal order is register time: causally ordered irreversible distinction update carried by finite records, clock labels, and dependency markers.

**Status.** Operational definition.

**Dependencies.** FDS-O1-001.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Finite observers use temporal order without any record ordering, update history, clock record, causal marker, dependency edge, or memory of change.

---

### FDS-O2-002 — Causal Dependency Precedes Temporal Labels

**Statement.** Causal dependency is prior to temporal labeling. Record $z_j$ is operationally after $z_i$ when the update that forms $z_j$ depends on $z_i$ through an accessible finite update chain.

**Status.** Structural proposition.

**Dependencies.** FDS-O2-001.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Stable temporal order is obtained solely from labels even when update dependencies and causal traces are removed or scrambled.

---

### FDS-O2-003 — Non-Injective Update Induces an Operational Arrow

**Statement.** When finite memory forces overwrite, compression, projection, or garbage collection, the update map is many-to-one. The non-injectivity loss $\Loss_U=H(X|Z)$ defines an arrow: erased distinctions cannot be reconstructed from the current finite record.

**Status.** Conditional theorem.

**Dependencies.** FDS-O2-001; Landauer/Bennett.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** A finite register repeatedly overwrites or compresses records yet reconstructs erased distinctions from the current finite record without external memory, hidden reservoirs, or additional records.

---

### FDS-O2-004 — Synchronization Is a Finite-Channel Record-Exchange Problem

**Statement.** Establishing cross-observer simultaneity requires finite signal exchange, finite channels, finite clock records, and finite latency bounds.

**Status.** Relativity-compatible bridge.

**Dependencies.** FDS-O2-001.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Bounded observers establish global simultaneity without signal exchange, finite bandwidth, latency, synchronization records, or propagation assumptions.

---

### FDS-O2-005 — Buffers and Latency Can Distort Recorded Order

**Statement.** Load-dependent latency and finite buffers can produce delayed records, order inversions, timestamp gaps, and apparent cause-effect reversal in the finite register's acquired order without violating physical causality.

**Status.** Testable prediction.

**Dependencies.** FDS-O2-001; FDS-O1-003.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Load-dependent latency and finite buffers never produce delayed records, order inversions, timestamp gaps, or apparent cause-effect reversal under controlled acquisition stress.

---

### FDS-O2-006 — Finite Clock Precision Coarsens Time

**Statement.** A bounded finite clock has finite tick width, drift, jitter, wraparound, and synchronization error, limiting the fineness of temporal ordering.

**Status.** Operational bridge.

**Dependencies.** FDS-O2-001.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Arbitrarily dense events are totally ordered by a bounded finite clock without tick collisions, synchronization error, or external ordering information.

---

### FDS-O2-007 — Dissipative Projection Carries Housekeeping Cost

**Statement.** When physically implemented through irreversible reset, overwrite, compression, or garbage collection, a many-to-one record update carries a Landauer-style lower bound on heat dissipation.

**Status.** Physical bridge.

**Dependencies.** Landauer/Bennett; FDS-O2-003.

**First timestamp.** FDS-O2 v1.0, 2026-05-16.

**Failure condition.** Repeated logically irreversible temporal record reuse violates generalized Landauer accounting after all reservoirs, correlations, feedback records, and work sources are included.

---

## T3 — Capacity Overflow / Effective Stochasticity Claims

FDS-T3 abstracts the common mechanism of O1 and O2: capacity overflow. When task-relevant distinction demand exceeds accessible capacity, missing distinctions re-enter the accessible description as effective stochasticity, coarse-graining, hysteresis, false invariants, externalization demand, or failure.

### FDS-T3-001 — Capacity Overflow

**Statement.** Capacity overflow occurs when task-relevant distinction demand exceeds accessible capacity, forcing the system to coarse-grain, project, or externalize.

**Status.** Operational bridge.

**Dependencies.** FDS-T1-002; FDS-O1-003.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Finite systems maintain full tracking fidelity when demand exceeds accessible capacity, with no measurable degradation, coarse-graining, or externalization.

---

### FDS-T3-002 — Projection-Induced Effective Stochasticity

**Statement.** Even when dynamics on a larger state space is deterministic, non-injective projection onto the accessible record space can induce stochastic accessible kernels because multiple inaccessible states map to the same visible state while having different successors.

**Status.** Conditional theorem.

**Dependencies.** FDS-T3-001; FDS-O1-001.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Non-injective projections of deterministic dynamics never induce non-degenerate accessible transition kernels when hidden successors differ.

---

### FDS-T3-003 — Critical Deficit and Predictive Susceptibility

**Statement.** Overflow deficit $\Delta_{\mathrm{T3}} = \Rmin - \Cacc$ controls a transition. Predictive susceptibility $\chi = \partial E_P / \partial \Delta_{\mathrm{T3}}$ should show a peak, kink, or rapid increase near $\Delta_{\mathrm{T3}} \approx 0$ when discarded distinctions are dynamically relevant.

**Status.** Testable prediction.

**Dependencies.** FDS-T3-001; rate-distortion theory.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Predictive error and transition entropy show no response, kink, or susceptibility peak as demand crosses capacity under controlled conditions.

---

### FDS-T3-004 — Phase-B Invariants and Markov Closure

**Statement.** After overflow, some coarse variables remain predictive with low update cost, slow information decay, and approximate Markov closure. These Phase-B invariants are selected by maintenance cost, not by tracking fidelity alone.

**Status.** Conditional theorem.

**Dependencies.** FDS-T3-002; FDS-CORE-005.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** No coarse variable remains stable, predictive, or cheap after overflow, or all coarse variables are equally predictive regardless of update and maintenance cost.

---

### FDS-T3-005 — Informational Hysteresis

**Statement.** Overflow can produce irrecoverable loss: returning demand below capacity does not automatically restore the original accessible state. External records or re-initialization may be required.

**Status.** Testable prediction.

**Dependencies.** FDS-T3-001; FDS-T1-005.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** System states and prediction fidelity return to pre-overflow baseline immediately after demand drops below capacity, without hysteresis or externalization traces.

---

### FDS-T3-006 — Observer-Relative Stochasticity

**Statement.** Stochasticity is observer-relative: two observers with different accessible capacities may have different effective stochasticity for the same underlying dynamics.

**Status.** Operational bridge.

**Dependencies.** FDS-T3-002.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** All observers with different accessible capacities report identical effective transition uncertainty for the same process.

---

### FDS-T3-007 — Wrong Invariant Completion Under Context Overflow

**Statement.** In finite-context systems, overflow can produce not merely random error but systematic wrong invariant completion: the system maintains a locally coherent but incorrect coarse variable when the true preimage is not uniquely recoverable.

**Status.** Engineering bridge.

**Dependencies.** FDS-T3-004; FDS-O2-001.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Context overflow never produces false dependency or semantic drift; all overflow-induced outputs remain as accurate as full-context outputs.

---

### FDS-T3-008 — Capacity Externalization and Phase-A Recovery

**Statement.** Externalization (external records, retrieval-augmented generation, distributed memory) increases effective accessible capacity and can push a system from Phase-B back toward Phase-A.

**Status.** Operational bridge.

**Dependencies.** FDS-T3-001; FDS-CORE-005.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Externalized records never reduce overflow-induced error, stochasticity, or hysteresis under matched tasks.

---

## P1 — Physical Distinction Carriers and Erasure Maps

FDS-P1 defines the physical accounting interface between formal distinctions and thermodynamic implementation. It distinguishes mathematical projection from dissipative physical implementation and introduces accounting boundaries, side records, DNR, residual irreversibility, refresh cost, and boundary-relative erasure accounting.

### FDS-P1-001 — Carrier Criterion

**Statement.** Task-available physical distinctions require carriers, readout reliability, and retention windows.

**Status.** Operational definition.

**Dependencies.** FDS-0.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** A finite physical system uses a distinction for a task without any carrier state, readable trace, retention interval, or external record.

---

### FDS-P1-002 — Readout Reliability and Generalized Distinguishability

**Statement.** Readout reliability is controlled by physical distinguishability, with DNR as the Gaussian binary special case. The carrier criterion generalizes to any pre-registered distinguishability metric (TV, Chernoff, Helstrom, etc.).

**Status.** Testable bridge.

**Dependencies.** Shannon detection theory.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** Readout error remains invariant as state separation, noise variance, drift, bandwidth, or carrier overlap are varied under controlled measurement.

---

### FDS-P1-003 — Accounting Boundary Determines Erasure

**Statement.** The accounting boundary determines whether missing preimage information is erasure, side memory, externalization, or hidden-reservoir correlation.

**Status.** Accounting principle.

**Dependencies.** FDS-0; Landauer/Bennett.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** Full-boundary audits show no boundary-dependent difference between absent, stored, erased, externalized, or reservoir-carried preimage information.

---

### FDS-P1-004 — Residual Irreversibility

**Statement.** Boundary-relative residual irreversibility is $\mathcal L_{\calA}=H(X\mid Y,G_{\calA})$.

**Status.** Formal definition.

**Dependencies.** FDS-P1-003.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** A many-to-one update preserves all preimage information in the visible output alone under nontrivial priors.

---

### FDS-P1-005 — Mathematical Projection Is Not Heat

**Statement.** Mathematical projection is not heat; dissipative projection is a physical implementation claim. An abstract many-to-one map without physical reset, overwrite, compression, or garbage collection does not dissipate heat by itself.

**Status.** Boundary statement.

**Dependencies.** FDS-O2; FDS-T3.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** An abstract many-to-one map alone, without physical reset, overwrite, compression, garbage collection, or substrate implementation, is shown to dissipate heat.

---

### FDS-P1-006 — Refresh Cost vs Erasure Cost

**Statement.** Refresh cost and erasure cost are distinct ledger terms: refresh preserves existing distinctions; erasure discards and reuses record space.

**Status.** Testable accounting claim.

**Dependencies.** FDS-P1-001.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** Holding, refresh, clocking, isolation, and reset costs prove inseparable in every controlled implementation.

---

### FDS-P1-007 — Reversible Logging Delays Erasure

**Statement.** Reversible logging delays erasure by increasing memory-fill, synchronization, refresh, externalization, or later cleanup burden.

**Status.** Conditional physical bridge.

**Dependencies.** Bennett; Landauer.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** Bounded-memory reversible systems sustain unbounded updates indefinitely without memory growth, externalization, cleanup, compression, or failure.

---

### FDS-P1-008 — Time-Resolution Requires Turnover

**Statement.** Sharper register-time resolution requires higher physical turnover and, under irreversible reuse, higher erasure-rate floor.

**Status.** Operational bridge.

**Dependencies.** FDS-O2.

**First timestamp.** FDS-P1 v1.0, 2026-05-16.

**Failure condition.** Systems maintain arbitrarily fine register-time resolution without increased update throughput, refresh, clocking, or erasure burden.

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

**Status.** High-risk physical bridge claim (pre-Euclid, registered).

**Dependencies.** FDS-T1-001; FDS-T1-002; general relativity (as background).

**Not claimed.** This does not derive GR, quantum gravity, or a complete cosmological model.

**First timestamp.** FDS-X1 v1.0, 2026-05-16.

**Failure condition.** Robust demonstration that cosmological horizons impose no finite distinguishability constraint.

---

### FDS-X1-002 — Horizon-Maintenance Energy Scale

**Statement.** If cosmological horizons are finite distinguishability boundaries, horizon-maintenance cost has characteristic energy scale rho_HM ~ H^2 M_Pl^2, consistent with the observed dark-energy scale.

**Status.** High-risk physical bridge claim (pre-Euclid, registered).

**Dependencies.** FDS-X1-001.

**Not claimed.** This does not claim to derive the exact numerical value of the cosmological constant.

**First timestamp.** FDS-X1 v1.0, 2026-05-16.

**Failure condition.** High-precision confirmation that dark energy has no relation to horizon-scale maintenance physics.

---

### FDS-X1-003 — Non-Phantom Dynamical Dark Energy

**Statement.** If horizon-maintenance cost drives late-time acceleration, the effective equation of state tends toward w = -1 from above (non-phantom), with possible mild evolution.

**Status.** High-risk physical bridge prediction (pre-Euclid, registered).

**Dependencies.** FDS-X1-002.

**Not claimed.** This does not predict the exact w(z) or its time derivative.

**First timestamp.** FDS-X1 v1.0, 2026-05-16.

**Failure condition.** Robust high-precision detection of w < -1 (phantom) at any redshift rules out the strict non-phantom version. Measurement of w = -1 exactly with no evolution demotes the dynamical version.

---

### FDS-X1-004 — Falsification / Demotion Contract

**Statement.** The X1 claim family has explicit falsification, demotion, and quarantine conditions stated in advance. Failure of X1 does not affect upstream T1 or core claims.

**Status.** Governance commitment.

**Dependencies.** FDS-X1-001—003.

**First timestamp.** FDS-X1 v1.0, 2026-05-16.

---

## E1 — Boundary-Risk / Prospect Theory Claims

### FDS-E1-001 — Loss Aversion as Boundary-Risk Asymmetry

**Statement.** Near a resource threshold, the boundary-risk potential is convex and decreasing, so equal-magnitude losses and gains produce asymmetric risk impact. This generates local loss aversion $\lambda>1$ without invoking an exogenous utility curvature.

**Status.** Operational bridge claim (formal model, synthetic simulation).

**Dependencies.** Finite resource buffers; boundary-risk potential.

**First timestamp.** FDS-E1 v1.0, 2026-05-16.

**Failure condition.** Loss aversion $\lambda$ is invariant across resource-buffer depletion states after controlling for measurement noise.

---

### FDS-E1-002 — Reference Dependence as Finite Updating

**Statement.** A finite agent maintains a compressed prediction baseline $r_t$ updated at rate $\alpha_t$ that declines with effective resource buffer $F_t^{\mathrm{eff}}$ and available capacity $C_t$.

**Status.** Computational bridge claim (formal model, synthetic simulation).

**Dependencies.** FDS-E1-001; finite memory and update capacity.

**First timestamp.** FDS-E1 v1.0, 2026-05-16.

**Failure condition.** Reference-point adaptation rate invariant across stress, cognitive load, and resource-depletion states.

---

### FDS-E1-003 — Probability Weighting as Finite Precision Allocation

**Statement.** Probability weighting curvature $\gamma_{tE}$ arises from finite precision allocation over probability space, modulated by total decision capacity $C_t$ and event-class boundary relevance $B_E$.

**Status.** Testable bridge hypothesis (formal model, synthetic simulation).

**Dependencies.** FDS-E1-001; finite distinguishability budget.

**First timestamp.** FDS-E1 v1.0, 2026-05-16.

**Failure condition.** Probability-weighting curvature invariant across cognitive load, event class, and perceived consequence severity.

---

### FDS-E1-004 — Nudge Bandwidth and Buffer-First Principle

**Statement.** Choice architecture interventions consume decision bandwidth. When required nudge bandwidth exceeds available capacity, the intervention may fail or backfire. Policy should restore resource buffers before imposing complex choice architecture.

**Status.** Policy bridge claim (formal model, synthetic simulation).

**Dependencies.** FDS-E1-001—003.

**First timestamp.** FDS-E1 v1.0, 2026-05-16.

**Failure condition.** Nudge effectiveness independent of scarcity, fatigue, administrative burden, and cognitive load.

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
