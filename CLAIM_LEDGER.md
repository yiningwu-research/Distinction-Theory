

## FDS Core Claims

### FDS-CORE-001 — Distinction Primitive

**Statement.** A distinction is an operation or relation that separates at least two alternatives within a possibility space.

**Status.** Formal definition.

**Dependencies.** None specified.

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Not falsified in usual sense; usefulness can fail.

---

### FDS-CORE-002 — Boundary Inheritance

**Statement.** Once a system distinguishes itself from what it is not, it inherits a boundary.

**Status.** Formal definition.

**Dependencies.** FDS-CORE-001

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Bounded system with zero maintenance cost under sustained load.

---

### FDS-CORE-003 — Finite Capacity

**Statement.** A finite system with a boundary has finite representational and operational capacity.

**Status.** Formal/operational claim.

**Dependencies.** FDS-CORE-002

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Physically instantiated bounded system with infinite operational capacity.

---

### FDS-CORE-004 — Capacity Deficit

**Statement.** When task-relevant distinction demand exceeds accessible capacity, the system operates under a capacity deficit.

**Status.** Formal definition.

**Dependencies.** FDS-CORE-003

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-CORE-005 — Budget Exits

**Statement.** A finite system under persistent positive capacity deficit must prune, externalize, relax the task, compress, or collapse.

**Status.** Conditional theorem.

**Dependencies.** FDS-CORE-004

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-CORE-006 — Invariant-Supported Persistence

**Statement.** Systems that persist under finite capacity do so by maintaining invariants that reduce effective distinction load.

**Status.** Conditional theorem.

**Dependencies.** FDS-CORE-005

**First timestamp.** FDS-0 v1.0, 2026-05-12.

**Failure condition.** Persistent system under sustained deficit with no invariant-supported load reduction.

---

## Finite Observer and Distinguishability Budget Claims

### FDS-T1-001 — Finite Observer Projection

**Statement.** A finite physical observer O can operationally use only a finite image Im(pi_O) of a physical possibility space.

**Status.** Operational/physical bridge claim.

**Dependencies.** None specified.

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Observer with unbounded distinctions under finite resources.

---

### FDS-T1-002 — Distinguishability Budget

**Statement.** Operational distinguishability is bounded by minimum of internal record capacity and accessible boundary/channel capacity.

**Status.** Conditional theorem.

**Dependencies.** FDS-T1-001

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-003 — Stock vs Throughput

**Statement.** Accessible capacity separates into stock capacity and update throughput; effective task capacity is their minimum.

**Status.** Formal definition/Conditional theorem.

**Dependencies.** FDS-T1-002

**First timestamp.** FDS-T1 v1.1, 2026-05-16.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-004 — Boundary-Relative Capacity Deficit

**Statement.** Delta_FDS = R_min - C_acc where R_min is task demand and C_acc is accessible capacity.

**Status.** Definition.

**Dependencies.** FDS-T1-003

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-005 — Budget-Exit Theorem

**Statement.** If Delta_FDS > 0 persists, observer must enter at least one exit class.

**Status.** Conditional theorem.

**Dependencies.** FDS-T1-004; FDS-CORE-005

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-006 — Maintenance Inequality

**Statement.** Positive deficit implies Landauer-style lower bound on thermodynamic maintenance cost for irreversible erasure.

**Status.** Conditional physical bridge.

**Dependencies.** FDS-T1-005

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-007 — Budget-Crossing Signature

**Statement.** As chi = R_min - C_acc crosses zero, observers should show measurable transitions.

**Status.** Testable prediction.

**Dependencies.** FDS-T1-005

**First timestamp.** FDS-T1 v1.1, 2026-05-16.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-T1-008 — Bottleneck-Switching Kink

**Statement.** Rate-distortion error floor shows slope discontinuities at bottleneck switches.

**Status.** Conditional theorem.

**Dependencies.** FDS-T1-003

**First timestamp.** FDS-T1 v0.1, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

## Boundary-Maintenance / Operational Second-Law Channel Claims

### FDS-O3-001 — Finite Memory Creates Record-Reuse Pressure

**Statement.** Finite memory creates record-reuse pressure under sustained update unless history is externalized, compressed, uncomputed, abandoned, or resources expand.

**Status.** Bridge claim.

**Dependencies.** Finite memory capacity; O2 register time

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Bounded-memory system maintains unbounded usable history internally without reuse, external memory, compression, or failure.

---

### FDS-O3-002 — Non-Injective Reuse Creates Residual Irreversibility

**Statement.** Non-injective record reuse creates residual irreversibility relative to an accounting boundary.

**Status.** Bridge claim.

**Dependencies.** O3-001; O1 finite record formation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Many-to-one update preserves full preimage information without side records or enlarged boundary.

---

### FDS-O3-003 — Physical Reuse Enters an Entropy Ledger

**Statement.** Physical irreversible record reuse enters an entropy/resource ledger under bridge assumptions.

**Status.** Bridge claim.

**Dependencies.** O3-002; P1 Landauer bridge

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Reliable physical erasure or overwrite violates Landauer-style accounting under stated assumptions.

---

### FDS-O3-004 — Stable Records Require Housekeeping

**Statement.** Stable finite records require housekeeping beyond logical erasure.

**Status.** Bridge claim.

**Dependencies.** O3-003; P2 garbage entropy rate

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Refresh, retention, clocking, synchronization, carrier repair, and verification cost-free in every implementation.

---

### FDS-O3-005 — Externalization Shifts Operational Second-Law Channel

**Statement.** Externalization shifts the operational Second-Law channel across accounting boundaries.

**Status.** Bridge claim.

**Dependencies.** O3-003; P1 accounting boundary

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** External records impose no write, verification, retrieval, latency, maintenance, or environmental cost.

---

### FDS-O3-006 — Pruning and Compression Reduce Future Pressure

**Statement.** Pruning and invariant compression can reduce future entropy pressure when task identity is preserved.

**Status.** Bridge claim.

**Dependencies.** O3-004; T3 Phase-B invariants

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** No task-preserving quotient, pruning, or compression ever reduces future record-maintenance cost.

---

### FDS-O3-007 — Sustained Turnover with Zero Cost Cannot Persist

**Statement.** Sustained residual record turnover, fixed boundary tolerance, and zero coupled entropy/resource cost cannot persist indefinitely.

**Status.** Bridge claim.

**Dependencies.** O3-001--006

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Finite active-boundary system maintains sustained residual turnover at fixed tolerance with no ledger cost and no exit channel.

---

### FDS-O3-008 — Topological Persistence Redirects Entropy Accounting

**Statement.** Topological or invariant persistence redirects entropy accounting rather than violating the Second Law.

**Status.** Bridge claim.

**Dependencies.** O3-003; Core invariant-supported persistence

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Protected invariant supplies perpetual work or global entropy-law violation rather than bounded persistence or entropy relocation.

---

## P4 — Coarse-Grained Anti-Recurrence and Informational Hysteresis Claims

### FDS-P4-001 — Non-Injective Truncation Creates Preimage Uncertainty

**Statement.** Non-injective truncation creates preimage uncertainty relative to the effective record.

**Status.** Formal information claim.

**Dependencies.** FDS-CORE-005

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A many-to-one map contains enough information, without side records or conventions, to distinguish all of its preimages.

---

### FDS-P4-002 — Bayes-Optimal Exact Recovery Bound

**Statement.** Bayes-optimal guaranteed exact preimage recovery is bounded by the largest conditional preimage mass.

**Status.** Decision-theoretic bound.

**Dependencies.** FDS-P4-001; Bayes decision theory

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A decoder using only Z exceeds the Bayes-optimal classifier bound for X|Z.

---

### FDS-P4-003 — Informational Hysteresis

**Statement.** Capacity recovery does not recover distinctions erased during a bottleneck.

**Status.** Informational hysteresis theorem.

**Dependencies.** FDS-P4-001; side-record criterion

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A finite system recovers exact task-relevant preimage distinctions after capacity restoration with no side record, no enlarged boundary, no external trace, and no hidden convention.

---

### FDS-P4-004 — Non-Lumpability Creates Hidden-State Memory

**Statement.** Non-lumpable coarse-graining creates hidden-state memory and effective stochasticity.

**Status.** Markov projection bridge.

**Dependencies.** FDS-P4-001; lumpability condition

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A non-lumpable projection closes exactly on Z_t alone without hidden state, history, or extra variables.

---

### FDS-P4-005 — Mori-Zwanzig Memory Burden

**Statement.** Projection-induced memory burden has a Mori-Zwanzig analogue.

**Status.** Relation to standard theory.

**Dependencies.** FDS-P4-004; Mori-Zwanzig formalism

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** Eliminated variables never reappear as memory, noise, or closure error in projected dynamics, even when lumpability fails.

---

### FDS-P4-006 — Externalization Restores Inverse Information Only by Moving It

**Statement.** Externalization restores inverse information only by moving it to a side ledger.

**Status.** Accounting-boundary bridge.

**Dependencies.** FDS-P4-001; external cost model

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** External logs restore exact recovery at no writing, retention, indexing, synchronization, retrieval, verification, or boundary-expansion cost.

---

### FDS-P4-007 — Finite-Memory Exit Theorem

**Statement.** Sustained truncation requires residual irrecoverability, side records, externalization, task relaxation, or failure.

**Status.** Finite-memory exit theorem.

**Dependencies.** FDS-P4-001; FDS-P4-003

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A finite system repeatedly applies non-injective truncation to task-relevant distinctions while preserving exact recovery with no residual uncertainty and no extra ledger.

---

## P3 — Finite-Bath Memory, Markovianization, and Environmental Forgetting Claims

### FDS-P3-001 — Environmental Side Records Have Finite Accessible Recovery Ca...

**Statement.** Environmental side records have finite accessible recovery capacity.

**Status.** Operational FDS bridge.

**Dependencies.** FDS-CORE-003; FDS-CORE-005

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** A finite system recovers unbounded inverse information from the environment through a finite observation channel with no latency, cost, degradation, or boundary expansion.

---

### FDS-P3-002 — Markovianization Is an Effective Forgetting Condition

**Statement.** Markovianization is an effective forgetting condition.

**Status.** Model-class bridge.

**Dependencies.** FDS-P3-001; lumpability condition

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** A projected process is treated as Markovian while accessible history measurably improves prediction or boundary maintenance under the same variables and accounting boundary.

---

### FDS-P3-003 — Memory Kernels Measure Unresolved Environmental Memory

**Statement.** Memory kernels measure unresolved environmental memory.

**Status.** Projection-form bridge.

**Dependencies.** FDS-P3-001; projection operator methods

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** Eliminated variables never reappear as memory, noise, or closure error in projected dynamics despite coupling and non-lumpable projection.

---

### FDS-P3-004 — Finite Baths Can Remember, Forget, and Recur

**Statement.** Finite baths can remember temporarily, forget operationally, and recur.

**Status.** Physical/model-class caveat.

**Dependencies.** FDS-P3-001; finite bath capacity

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** A finite bath is always exactly Markovian and never returns correlations under any admissible finite-bath model.

---

### FDS-P3-005 — Environmental Forgetting Complements P4 Internal Truncation

**Statement.** Environmental forgetting complements P4 internal truncation.

**Status.** FDS bridge.

**Dependencies.** FDS-P3-001; FDS-P4-001

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** Internal preimages are lost, yet environmental side records remain fully accessible indefinitely with bounded cost and no accounting-boundary change.

---

### FDS-P3-006 — Bath Saturation Forces Collisions or Loss of Recoverability

**Statement.** Bath saturation forces collisions, compression, externalization, verification cost, or loss of recoverability.

**Status.** Finite-record theorem.

**Dependencies.** FDS-P3-001; bath record capacity

**First timestamp.** FDS-P3 v1.0, 2026-05-18.

**Failure condition.** A finite accessible bath stores more distinguishable side records than its operational capacity without collision, compression, indexing, erasure, or hidden expansion.

---

## P6 — Speed, Precision, and Dissipation Bounds Claims

### FDS-P6-001 — Boundary Maintenance Requires Finite Update Throughput

**Statement.** Boundary maintenance requires finite update throughput.

**Status.** Formal FDS claim.

**Dependencies.** FDS-CORE-003; FDS-CORE-005

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** A time-varying boundary is maintained without updating, verifying, storing, externalizing, protecting, or acting on any task-relevant distinction.

---

### FDS-P6-002 — Speed and Precision Jointly Increase Maintenance Burden

**Statement.** Speed and precision jointly increase maintenance burden.

**Status.** Operational bridge.

**Dependencies.** FDS-P6-001; rate-distortion demand

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** Faster and more precise maintenance is sustained indefinitely at fixed representation and fixed resource input, with no extra dissipation, error, latency, externalization, invariant compression, or failure.

---

### FDS-P6-003 — Sustainable Internal Rate Is Bottlenecked

**Statement.** The sustainable internal rate is bottlenecked by sensing, updating, verification, correction, action, and resources.

**Status.** Bottleneck definition.

**Dependencies.** FDS-P6-001; FDS-P6-002

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** A system exceeds its slowest internal channel indefinitely without queueing, latency, loss, externalization, or resource expansion.

---

### FDS-P6-004 — Correction and Verification Belong in the Resource Ledger

**Statement.** Correction and verification belong in the resource ledger.

**Status.** O3-compatible physical bridge.

**Dependencies.** FDS-P6-001; FDS-P6-003; O3 ledger principle

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** Physical correction, refresh, verification, synchronization, overwrite, and recovery are cost-free under the stated implementation assumptions.

---

### FDS-P6-005 — Effective Causal Update Bandwidth Limits Real-Time Maintenance

**Statement.** Effective causal update bandwidth limits real-time maintenance.

**Status.** Physical/engineering bridge.

**Dependencies.** FDS-P6-001; finite causal reach

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** A finite observer integrates arbitrarily distant boundary-relevant information within a finite update window with no latency, no prediction burden, and no effective signal-speed limit.

---

### FDS-P6-006 — Externalization and Invariant Compression Are Relief Channels...

**Statement.** Externalization and invariant compression are relief channels, not free exits.

**Status.** P4/P7-compatible bridge.

**Dependencies.** FDS-P6-001; P4 side-record criterion; P7 invariant quotient

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** External ledgers or invariant quotients reduce internal demand with no write, synchronization, verification, protection, latency, or boundary-accounting cost.

---

### FDS-P6-007 — Throughput Deficit Exit Theorem

**Statement.** If rate-distortion demand exceeds sustainable internal throughput, the system must enter at least one exit channel: higher resource/dissipation cost, increased error, latency growth, task relaxation, externalization, invariant compression, resource expansion, or boundary-maintenance failure.

**Status.** Formal exit theorem.

**Dependencies.** FDS-P6-001-006

**First timestamp.** FDS-P6 v1.0, 2026-05-18.

**Failure condition.** Demand exceeds sustainable throughput with no exit channel and no boundary failure, given a valid implementation mapping.

---

## P7 — Topological Obstruction to Forgetting Claims

### FDS-P7-001 — Invariant Side-Ledgers Suppress Residual Uncertainty

**Statement.** Invariant side-ledgers can suppress P4 residual inverse uncertainty.

**Status.** Formal FDS bridge.

**Dependencies.** FDS-P4-001; invariant quotient map

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A task variable factors through an accessible invariant, but H(V|Z,Q_inv) remains high under the stated assumptions.

---

### FDS-P7-002 — Noisy Invariant Recovery Bound

**Statement.** Noisy invariant readout gives a bounded recovery penalty.

**Status.** Information bound.

**Dependencies.** FDS-P7-001; Fano-style bound

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A noisy invariant readout with error probability δ exceeds the Fano-style bound without hidden information or changed task labels.

---

### FDS-P7-003 — Local Perturbations Cannot Change Protected Invariant

**Statement.** Local perturbations cannot change a protected invariant without a protection-breaking event.

**Status.** Topological bridge.

**Dependencies.** FDS-P7-001; local perturbation family; protection margin

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A local perturbation changes the invariant while the protection gap, locality assumptions, and accounting boundary remain intact.

---

### FDS-P7-004 — NHSE as Model Class

**Statement.** NHSE supplies a model class for invariant-supported persistence.

**Status.** Physical bridge claim.

**Dependencies.** FDS-P7-003; point-gap winding; GBZ structure

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** NHSE is present, but it carries no stable recoverable distinction, no boundary-sensitive protection, and no robustness to local perturbation in the registered model class.

---

### FDS-P7-005 — Protection Relocates Entropy/Resource Accounting

**Statement.** Protection relocates entropy/resource accounting rather than deleting it.

**Status.** O3-compatible accounting claim.

**Dependencies.** FDS-P7-001; O3 ledger principle

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A protected invariant supplies indefinite maintenance with no drive, boundary, refresh, dissipation, verification, control, or external ledger.

---

### FDS-P7-006 — Dual-Channel Signature

**Statement.** Protected phases can generate a dual forgetting/ledger signature.

**Status.** Experimental bridge.

**Dependencies.** FDS-P7-004; FDS-P7-005; operational forgetting rate

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** Confirmed protection-breaking transition with no feature in operational forgetting and no corresponding resource/entropy signature under a well-powered registered protocol.

---

## P8 — Residue Spectral Dynamics and Markov Closure Claims

### FDS-P8-001 — Projection Yields Instantaneous-Memory-Forcing Decomposition

**Statement.** Projection yields an exact instantaneous-memory-forcing decomposition for linear dynamics.

**Status.** Imported exact identity, specialized in the exact-dynamics section.

**Dependencies.** Exact linear semigroup; registered projection; compatible domain.

**Not claimed.** Nonlinear state equations without a valid lifted observable representation.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** The declared generator, projection, domain, or semigroup assumptions fail, or a nonlinear state equation is used without a valid lifted observable representation.

---

### FDS-P8-002 — Only Controllable-and-Observable Residue Contributes to Visible Memory

**Statement.** Only controllable-and-observable residue contributes to visible round-trip memory.

**Status.** Restricted theorem in the active-residue section.

**Dependencies.** FDS-P4-001 non-injective truncation; exact linear realization; input-output factorization; silent-sector definition.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** Removing a declared silent sector changes the memory kernel, transfer function, or retained input-output behavior.

---

### FDS-P8-003 — Exponential Semigroup Stability Gives Finite Memory-Burden Bound

**Statement.** Exponential residue-semigroup stability gives a finite memory-burden bound.

**Status.** Conditional theorem in the closure section.

**Dependencies.** Exponential stability bound; bounded couplings; finite horizon; registered norm.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** Exponential stability does not hold, couplings are unbounded on the relevant domain, or the retained solution class violates the finite-horizon assumptions.

---

### FDS-P8-004 — Coupled Marginal Modes Obstruct Integrable Memory Closure

**Statement.** Coupled marginal modes obstruct integrable memory closure.

**Status.** Conditional theorem in the marginal-mode section.

**Dependencies.** Transfer function poles near imaginary axis; both input and output coupling; no exact cancellation.

**Not claimed.** The marginal mode is silent, canceled by the transfer channel, removed by symmetry, or absent from the registered active quotient.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** The marginal mode is silent, canceled by the transfer channel, removed by symmetry, or absent from the registered active quotient.

---

### FDS-P8-005 — Low-Frequency Transfer Weight Can Generate Algebraic Memory Tails

**Statement.** Low-frequency transfer spectral weight can generate algebraic memory tails under registered Tauberian conditions.

**Status.** Tauberian result for a restricted positive-measure class.

**Dependencies.** Scalar positive-kernel regularity assumptions; monotonicity or bounded variation.

**Not claimed.** Non-normal, sign-changing, matrix-canceling, time-dependent, or outside-regular-variation kernels.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** The kernel is non-normal, sign-changing, matrix-canceling, time dependent, or outside the registered regular-variation assumptions.

---

### FDS-P8-006 — Transfer Significance Bounds Reachable Round-Trip Recoverability

**Statement.** Transfer significance bounds reachable round-trip recoverability when the two observation channels are boundedly equivalent on reachable residue.

**Status.** P8 channel-registration bridge theorem.

**Dependencies.** Registered bounded interconnection between retained return channel and physical recovery channel; reachable residue sector; linear finite-dimensional; Gaussian.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** No bounded interconnection exists, the lower bound vanishes, or recovery uses side records outside the registered retained return channel.

---

### FDS-P8-007 — Recoverability Depends on Observation Channel, Not Just Lifetime

**Statement.** Operational recoverability depends on the observation channel, not on residue lifetime alone.

**Status.** Exact finite-dimensional linear-Gaussian model theorem.

**Dependencies.** P4 pre-image observability; P8 channel registration; decoder specification.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** The claimed recovery is obtained only by changing the accounting boundary, decoder resources, task labels, or observation channel.

---

### FDS-P8-008 — Strictly Proper Rational Memory Admits Finite Exact Markov Augmentation

**Statement.** Strictly proper rational memory admits finite exact Markov augmentation.

**Status.** Imported realization theorem, FDS interpretation.

**Dependencies.** Strictly proper rational transfer function; feedthrough term absorbed into instantaneous generator; minimal realization dimension.

**First timestamp.** FDS-P8 v1.0, 2026-06-09.

**Failure condition.** A non-rational kernel is asserted to have a finite exact realization, the feedthrough term is not absorbed into the instantaneous generator, or the proposed augmentation fails to reproduce the transfer function.

---

## Self-Organization Bridge Claims

### FDS-N1-001 — Active Self-Organization Requires Boundary-Relevant Update

**Statement.** Active self-organization requires boundary-maintenance-relevant internal update.

**Status.** Domain bridge claim.

**Dependencies.** Active boundary criterion; finite capacity

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** System classified active even when update ablation has no effect on future boundary loss.

---

### FDS-N1-002 — Task-Relative Organizational Capacity

**Statement.** Effective organizational capacity is task-relative and reduced by coordination, verification, latency, resource, and externalization costs.

**Status.** Domain bridge claim.

**Dependencies.** Finite capacity; bottleneck logic

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Boundary tasks maintained at full fidelity when all capacity factors fall below demand.

---

### FDS-N1-003 — Deficit-Driven Load Pressure

**Statement.** Capacity deficit creates maintenance-load pressure, not necessarily raw complexity growth alone.

**Status.** Domain bridge claim.

**Dependencies.** Capacity deficit; maintenance load equation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Increasing task demand never increases maintained load in any implementation.

---

### FDS-N1-004 — Bounded Growth Exit Theorem

**Statement.** Unbounded Phase-A growth is impossible under finite resource input without exit channels.

**Status.** Domain bridge claim.

**Dependencies.** Finite resource envelope; exit channel taxonomy

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Active finite systems grow maintained load forever under finite resources with no exit.

---

### FDS-N1-005 — Pruning Has a Viability Window

**Statement.** Pruning has a viability window and is resource-gated.

**Status.** Domain bridge claim.

**Dependencies.** Resource-gated pruning equation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Pruning strength has no systematic effect on overload or persistence across controlled cases.

---

### FDS-N1-006 — Externalization Shifts Burden

**Statement.** Externalization shifts rather than removes boundary-maintenance burden, and can clog the environment.

**Status.** Domain bridge claim.

**Dependencies.** Accounting boundary; externalization ROI equation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** External records impose no storage, verification, retrieval, or repair burden in any implementation.

---

### FDS-N1-007 — Phase-C Catastrophic Feedback

**Statement.** Phase-C catastrophic feedback couples boundary loss with resource depletion.

**Status.** Domain bridge claim.

**Dependencies.** Resource and loss dynamics; positive loop gain

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Resource depletion and boundary loss never couple positively in collapse-prone systems.

---

### FDS-N1-008 — Phase-B Residues Are Biased to Low-Maintenance Tasks

**Statement.** Phase-B residues are biased toward low-maintenance, task-relevant invariants.

**Status.** Domain bridge claim.

**Dependencies.** T3 Phase-B invariants; survival score function

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Residues after overload show no bias toward reduced maintenance cost or task relevance.

---

## Deficit-Driven Entropy-Production Ledger Claims

### FDS-P5-001 — Capacity Deficit Is Not Thermodynamic Entropy

**Statement.** Capacity deficit is task-relative information shortfall, not thermodynamic entropy.

**Status.** Bridge claim.

**Dependencies.** Rate-distortion demand; effective capacity

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Not empirical (boundary statement separating formal from physical).

---

### FDS-P5-002 — Sustained Deficit Requires Correction or Exit

**Statement.** Sustained deficit plus boundary maintenance requires correction, externalization, or failure.

**Status.** Bridge claim.

**Dependencies.** Budget exits; deficit definition

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Finite system maintains task at fixed tolerance despite deficit and no correction or exit.

---

### FDS-P5-003 — Correction Cycles Induce Audit Channels

**Statement.** Physical correction cycles induce audit channels through update, refresh, repair, synchronization, externalization, and transport.

**Status.** Bridge claim.

**Dependencies.** Carrier criterion; accounting boundary

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Sustained correction, refresh, repair, and sync at zero entropy or resource cost.

---

### FDS-P5-004 — Landauer Floor under Bridge Assumptions

**Statement.** Logical erasure contributes a Landauer-style entropy-production floor under bridge assumptions.

**Status.** Bridge claim.

**Dependencies.** Landauer bridge; correction channels

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Logically irreversible erature violates Landauer lower bound under stated assumptions.

---

### FDS-P5-005 — Housekeeping Persists beyond Erasure

**Statement.** Housekeeping entropy persists even when logical erasure is zero.

**Status.** Bridge claim.

**Dependencies.** Reversible embedding; carrier maintenance

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Boundary maintenance, refresh, clocking, sensing, and repair cost-free when erasure is zero.

---

### FDS-P5-006 — Externalization Shifts the Ledger

**Statement.** Externalization shifts rather than removes the entropy ledger.

**Status.** Bridge claim.

**Dependencies.** Accounting boundary; externalization audit

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** External records impose no write, verification, retrieval, sync, or maintenance cost.

---

### FDS-P5-007 — Pruning and Compression Reduce Future Pressure

**Statement.** Pruning and invariant compression can reduce future entropy-production pressure.

**Status.** Bridge claim.

**Dependencies.** T3 Phase-B invariants; pruning ROI model

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** No task-preserving simplification ever reduces refresh, repair, or verification cost.

---

### FDS-P5-008 — Deficit Crossing Predicts Measurable Signatures

**Statement.** Deficit crossing predicts measurable signatures in heat, resource use, latency, resets, or error floor.

**Status.** Bridge claim.

**Dependencies.** Deficit-crossing protocol; ledger decomposition

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Positive deficit sustained with no measurable change in any physical or task channel.

---

## Life and Cognitive Science Bridge Registry Claims

### FDS-LC0-001 — Registry Structure

**Statement.** FDS-LC0 registers life/cognitive bridge claims with dependencies, risks, and failure conditions.

**Status.** Registry governance.

**Dependencies.** None specified.

**First timestamp.** FDS-LC0 v1.0, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-LC0-002 — Downstream Failure Rule

**Statement.** Failure of life/cognitive bridge does not propagate to upstream physical bridges or core.

**Status.** Registry governance.

**Dependencies.** None specified.

**First timestamp.** FDS-LC0 v1.0, 2026-05-14.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

## Frontier Physical Consequences (X-Series) Claims

### FDS-X1-001 — Horizon as Boundary

**Statement.** Cosmological horizons act as finite distinguishability boundaries for observers.

**Status.** Frontier Physical Consequences (P3).

**Dependencies.** FDS-T1-001; FDS-T1-002

**First timestamp.** FDS-X1 v1.2, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-X1-002 — Horizon-Maintenance Scale

**Statement.** Horizon-maintenance cost has scale rho ~ H^2 M_Pl^2, consistent with dark energy.

**Status.** Frontier Physical Consequences (P3) — strong candidate (DE-1 B+/A−).

**Dependencies.** FDS-X1-001

**First timestamp.** FDS v1.0, 2026-05-18.

**Failure condition.** Dark-energy scale is shown to be unrelated to any horizon-area or causal-boundary scale.

---

### FDS-X1-003 — Non-Phantom Dark Energy

**Statement.** Equation of state tends toward w=-1 from above (non-phantom) with possible mild evolution.

**Status.** Frontier Physical Consequences (P3) — candidate (DE-3 B−/C+, pending data closure).

**Dependencies.** FDS-X1-002

**First timestamp.** FDS v1.0, 2026-05-18.

**Failure condition.** Robust unavoidable physical w<-1 not attributable to effective reconstruction, or model-independent reconstruction excludes physical non-phantom DE.

---

### FDS-X1-004 — Falsification Contract

**Statement.** X1 claims have explicit falsification conditions stated in advance.

**Status.** Governance.

**Dependencies.** FDS-X1-001; FDS-X1-002; FDS-X1-003

**First timestamp.** FDS v1.0, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

## Artificial Agency (Frozen) Claims

### FDS-A1-001 — AI Agency Criterion

**Statement.** An artificial agent is an active finite distinction system maintaining boundary through durable updates.

**Status.** Conceptual criterion.

**Dependencies.** FDS-CORE-002; FDS-CORE-003; FDS-CORE-004; FDS-CORE-005

**First timestamp.** FDS-A1 v1.0, 2026-05-12.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-A1-002 — AI Line Frozen

**Statement.** Public programme retains FDS-A1 as conceptual timestamp; no proprietary AI development in repo.

**Status.** Governance.

**Dependencies.** None specified.

**First timestamp.** CONFLICTS_OF_INTEREST v1.0, 2026-05-16.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-A1-D — Strong FDS-agency requires resource-governed persistence.

**Statement.** Strong FDS-agency requires resource-governed persistence.

**Status.** Operational.

**Dependencies.** FDS tuple + persistence test

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** System satisfies task output competence without durable update or boundary maintenance.

---

### FDS-A1-C — FDS-agency requires action-to-future-state causal influence.

**Statement.** FDS-agency requires action-to-future-state causal influence.

**Status.** Operational.

**Dependencies.** Intervention / transfer influence test

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Actions have no measurable influence on future boundary-relevant states.

---

### FDS-A1-E — Capacity-deficit estimation is required to distinguish scali...

**Statement.** Capacity-deficit estimation is required to distinguish scaling from agency.

**Status.** Operational.

**Dependencies.** Task demand + system capacity estimate

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Systems qualify as agents without measurable boundary-relevant capacity pressure.

---

## Physical Bridge / Core Bridge Claims

### FDS-B — Active boundary maintenance distinguishes active finite syst...

**Statement.** Active boundary maintenance distinguishes active finite systems from passive mappings.

**Status.** Core claim.

**Dependencies.** Boundary variable + update participation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Boundary update ablation has no effect on future maintenance loss.

---

### PB-FD — Physically instantiated identity maintenance requires finite...

**Statement.** Physically instantiated identity maintenance requires finite distinguishability budgets.

**Status.** Bridge claim.

**Dependencies.** Finite physical resources / bounded records

**First timestamp.** PB v1.0, 2026-05-18.

**Failure condition.** A physical system maintains unlimited usable distinguishability within finite resources.

---

### PB-L — Logically irreversible updates incur a thermodynamic cost un...

**Statement.** Logically irreversible updates incur a thermodynamic cost under Landauer bridge assumptions.

**Status.** Bridge claim.

**Dependencies.** Standard Landauer conditions

**First timestamp.** PB v1.0, 2026-05-18.

**Failure condition.** Reliable irreversible erasure below the thermodynamic floor under stated conditions.

---

## Boundary-Maintaining AI Agent Protocol Claims

### B1 — Boundary-maintaining artificial agents can be benchmarked by...

**Statement.** Boundary-maintaining artificial agents can be benchmarked by ablation, deficit, pruning, externalization, and persistence metrics.

**Status.** Operational.

**Dependencies.** Benchmark protocol

**First timestamp.** B1 v1.0, 2026-05-18.

**Failure condition.** Metrics fail to distinguish passive mappers from active boundary-maintaining systems.

---

## Organizations and Civilizations Claims

### S1 — Organizations and civilizations can be modeled as active fin...

**Statement.** Organizations and civilizations can be modeled as active finite distinction systems.

**Status.** Domain bridge claim.

**Dependencies.** Institutional boundary + memory + resource budget

**First timestamp.** S1 v1.0, 2026-05-18.

**Failure condition.** Persistent institutions avoid collapse under unlimited complexity growth without pruning, externalization, or reform.

---

## Core Claims

### FDS-0 — Active finite systems maintain boundaries under finite capac...

**Statement.** Active finite systems maintain boundaries under finite capacity.

**Status.** Core claim.

**Dependencies.** Formal definitions

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Mathematical counterexample under stated hypotheses.

---

### CC-1 — Capacity deficit arises under finite representation and inco...

**Statement.** Capacity deficit arises under finite representation and incompressible task demand.

**Status.** Core claim.

**Dependencies.** Finite capacity + task demand

**First timestamp.** CC v1.0, 2026-05-18.

**Failure condition.** Finite system maintains lossless model of incompressible environment under bounded capacity.

---

### CC-2 — Capacity deficit forces approximation under bounded represen...

**Statement.** Capacity deficit forces approximation under bounded representation.

**Status.** Core claim.

**Dependencies.** Finite capacity + nontrivial task demand

**First timestamp.** CC v1.0, 2026-05-18.

**Failure condition.** Bounded systems maintain exact task-relevant representation without compression, omission, or distortion.

---

### CC-3 — Approximation generates residual error requiring correction ...

**Statement.** Approximation generates residual error requiring correction or tolerance.

**Status.** Core claim.

**Dependencies.** Approximation + task loss

**First timestamp.** CC v1.0, 2026-05-18.

**Failure condition.** Approximation produces no residual burden under nontrivial task constraints.

---

### CC-5 — Persistent capacity deficit drives pruning, externalization,...

**Statement.** Persistent capacity deficit drives pruning, externalization, task relaxation, or collapse.

**Status.** Core claim.

**Dependencies.** Capacity deficit + finite resources

**First timestamp.** CC v1.0, 2026-05-18.

**Failure condition.** Persistent deficit produces none of the predicted response modes.

---

### CC-6 — Long-term persistence is favored by invariant-supported stru...

**Statement.** Long-term persistence is favored by invariant-supported structure.

**Status.** Core claim.

**Dependencies.** Perturbation family + identity predicate

**First timestamp.** CC v1.0, 2026-05-18.

**Failure condition.** Structures persist without invariant support under sustained perturbation.

---

## X2 — Three Fermion Generations as CP/T-Asymmetric Identity Transformation Claims

### FDS-X2-001 — CKM CP-Phase Lower Bound

**Statement.** For a CKM-type N×N unitary charged-current mixing matrix, an irreducible physical complex phase exists if and only if N≥3.

**Status.** Standard Model algebra / hard hook.

**Dependencies.** FDS core finite capacity; Kobayashi-Maskawa 1973

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

### FDS-X2-002 — Weak-Sector CP/T Orientation Bridge

**Statement.** Weak-sector identity transformation requires a rephasing-invariant CP/T orientation.

**Status.** FDS/DT physical bridge.

**Dependencies.** FDS-X2-001; CPT theorem

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

### FDS-X2-003 — Weak Charged Current as Identity-Transformation Carrier

**Statement.** The weak charged current is the Standard Model identity-transformation carrier.

**Status.** Interpretive bridge.

**Dependencies.** FDS-X2-002; Standard Model flavor physics

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

### FDS-X2-004 — NCKM≥3 Conditional Theorem

**Statement.** NCKM≥3 follows from the X2 chain: weak identity update → T/CP orientation → irreducible CKM phase → NCKM≥3.

**Status.** Conditional theorem.

**Dependencies.** FDS-X2-001; FDS-X2-002; FDS-X2-003

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

### FDS-X2-005 — Exactly Three Generations as Minimality Bridge

**Statement.** Exactly three sequential chiral generations follow from minimality.

**Status.** Higher-risk upper-bound bridge.

**Dependencies.** FDS-X2-004; flavor-cost functional

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

### FDS-X2-006 — Nonzero Leptonic Dirac CP Phase

**Statement.** If the lepton sector participates in the same CP/T-oriented identity-transformation requirement, and if the relevant observable channel is the Dirac PMNS phase, then X2 motivates a nonzero leptonic Dirac CP phase.

**Status.** Optional PMNS extension.

**Dependencies.** FDS-X2-002; PMNS phenomenology

**First timestamp.** FDS-X2 v2.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20289955

---

## X3 — Functional Decomposition of the Four Fundamental Interactions Claims

### FDS-X3-001 — Token Stabilization Requirement

**Statement.** Finite distinction systems require token stabilization.

**Status.** Operational / structural.

**Dependencies.** FDS core; distinction persistence requirement

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-002 — Strong Interaction as Encapsulation

**Statement.** The strong interaction realizes hadronic/baryonic encapsulation.

**Status.** Physical mapping.

**Dependencies.** FDS-X3-001; QCD

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-003 — Remote Detectability Requirement

**Statement.** Finite distinction systems require remote detectability and compositional connection.

**Status.** Operational / structural.

**Dependencies.** FDS core; FDS-X3-001

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-004 — Electromagnetism as Connection

**Statement.** Electromagnetism realizes connection and communication among charged sectors.

**Status.** Physical mapping.

**Dependencies.** FDS-X3-003; QED

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-005 — Identity Transformation Requirement

**Statement.** Finite distinction systems require identity transformation and selective update.

**Status.** Operational / structural.

**Dependencies.** FDS core; FDS-X3-001; FDS-X3-003

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-006 — Weak Interaction as Identity Transformation

**Statement.** The weak interaction realizes identity transformation, flavor change, and unstable-state pruning.

**Status.** Physical mapping.

**Dependencies.** FDS-X3-005; electroweak theory; FDS-X2

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-007 — Gravity as Global Boundary Accounting

**Statement.** Gravity realizes global boundary / causal geometry / stress-energy accounting.

**Status.** Physical bridge.

**Dependencies.** FDS-X3-001; general relativity

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

### FDS-X3-008 — Minimal Distinction-Operation Closure

**Statement.** The four interactions form a minimal distinction-operation closure.

**Status.** Main X3 thesis.

**Dependencies.** FDS-X3-001–007

**First timestamp.** FDS-X3 v2.0, 2026-05-26.

**Failure condition.** 10.5281/zenodo.20388356

---

## X4 — Pauli Exclusion as Finite Address Protection Claims

### FDS-X4-001 — Nilpotent Fermionic Algebra

**Statement.** Fermionic creation operators obey nilpotency $(a_i^\dagger)^2=0$, enforcing single-occupancy fermionic mode addresses.

**Status.** Standard quantum algebra.

**Dependencies.** FDS core; canonical anticommutation relations

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-002 — Pauli Exclusion as Address Protection

**Statement.** Pauli exclusion protects single-fermion mode-address occupancy: a second identical fermionic occupancy event cannot be written into an already occupied address.

**Status.** FDS interpretation.

**Dependencies.** FDS-X4-001

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-003 — Exclusion Forces Structural Diversity

**Statement.** Pauli exclusion forces structural diversity in fermionic matter by distributing occupancy events across distinct addresses.

**Status.** Physical / operational.

**Dependencies.** FDS-X4-002

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-004 — Matter Stability from Antisymmetry

**Statement.** Stability of bulk ordinary matter depends on fermionic antisymmetry, as established by Dyson-Lenard and Lieb-Thirring bounds.

**Status.** Standard mathematical physics.

**Dependencies.** FDS-X4-003; Dyson-Lenard; Lieb-Thirring

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-005 — Bosons Are Not a Violation

**Statement.** Bosonic multiple occupation is not an X4 violation because bosonic mode occupation increases field amplitude, not independently address-protected fermionic occupancy events.

**Status.** Conceptual caveat.

**Dependencies.** FDS-X4-001; Bose-Einstein condensation

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-006 — Minimal Address-Protection Rule

**Statement.** The Pauli rule $n_i\in\{0,1\}$ is the minimal address-protection rule among finite occupancy cutoffs for identical fermionic matter in ordinary $3+1$-dimensional relativistic QFT.

**Status.** Minimality bridge.

**Dependencies.** FDS-X4-002; generalized statistics

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-007 — Degeneracy Pressure as Address Protection

**Statement.** Fermionic degeneracy pressure is the macroscopic expression of finite address protection.

**Status.** Physical bridge.

**Dependencies.** FDS-X4-002; Chandrasekhar; TOV

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

### FDS-X4-008 — Address Scarcity from Causal Reachability

**Statement.** Address scarcity follows from the finite causal reachability boundary: within a finite causal horizon the number of distinguishable modes any system can resolve is bounded, making exclusive single-address occupancy the optimal strategy for maximizing structural diversity.

**Status.** Physical bridge (P6 connection).

**Dependencies.** FDS-X4-002; FDS-P6

**First timestamp.** FDS-X4 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278029

---

## X5 — Mathematical Form of Physical Law as Invariant-Form Compression Claims

### FDS-X5-001 — Finite Systems Cannot Represent All Detail

**Statement.** Finite systems cannot internally represent all microstate detail. Exceeding finite capacity forces compression, approximation, externalization, or task relaxation.

**Status.** Formal FDS core.

**Dependencies.** FDS core; finite capacity theorem

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-002 — Stable Law-Like Regularities Require Invariant Compression

**Statement.** Stable law-like regularities require invariant-form compression: a portable relation must factor through a strict-invariant, equivariant, or covariant sector.

**Status.** FDS structural claim.

**Dependencies.** FDS-X5-001

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-003 — Equations Are Compressed Invariant Relations

**Statement.** Mathematical equations are compressed representations of invariant-form relations that remain valid across an equivalence class of states, frames, scales, gauges, or perturbations.

**Status.** Interpretive bridge.

**Dependencies.** FDS-X5-002

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-004 — Symmetries Reduce Rule-Maintenance Cost

**Statement.** Symmetries and covariance structures reduce rule-maintenance cost by replacing many case-specific rules with one orbit-level or representation-level rule.

**Status.** Physical / information bridge.

**Dependencies.** FDS-X5-002; group theory

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-005 — Wigner Puzzle Reframed

**Statement.** Wigner's puzzle is reframed by invariant-form compression: mathematics is effective because the portable part of physics is the part compressible into invariant-form structures.

**Status.** Philosophical bridge.

**Dependencies.** FDS-X5-002; FDS-X5-003

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-006 — Constants as Model-Class Signatures

**Statement.** Constants such as e, i, and related constants are model-class signatures that appear because of semigroup structure, coherent phase bookkeeping, geometry, or unit conventions, not numerological cosmic design.

**Status.** Optional bridge.

**Dependencies.** FDS-X5-002; semigroup theory; quantum theory

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-007 — Open Math Problems May Have Physical Analogues

**Statement.** Some open mathematical problems (Riemann hypothesis, P vs NP, finite simple groups) may acquire physical analogues as spectra, partition functions, complexity gaps, or symmetry classifications.

**Status.** Speculative appendix.

**Dependencies.** FDS-X5-002

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

### FDS-X5-008 — RG Fixed Points as Invariant Compression

**Statement.** Renormalization-group fixed points are a model-class example of invariant-form compression: a relation whose form survives coarse-graining becomes law-like for finite observers.

**Status.** Physical bridge.

**Dependencies.** FDS-X5-002; Wilson RG

**First timestamp.** FDS-X5 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20278236

---

## T2 — Effective Geometry as Horizon Boundary Accounting Claims

### FDS-T2-001 — Bounded Distinguishability Budgets

**Statement.** Finite observers have bounded distinguishability budgets.

**Status.** FDS / T1 bridge.

**Dependencies.** FDS-T1

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

### FDS-T2-002 — Horizons as Causal-Access Boundaries

**Statement.** Horizons act as causal-access boundaries.

**Status.** GR / QFTCS bridge.

**Dependencies.** General relativity

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

### FDS-T2-003 — Horizon Entropy as Area Accounting

**Statement.** Horizon entropy gives boundary area accounting.

**Status.** Physical bridge.

**Dependencies.** Bekenstein-Hawking entropy

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

### FDS-T2-004 — Clausius-Type Horizon Closure

**Statement.** Clausius-type local horizon closure links heat flow and entropy variation.

**Status.** Model-class bridge.

**Dependencies.** Jacobson 1995

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

### FDS-T2-005 — Effective Geometry as Boundary Accounting

**Statement.** Effective geometry can be read as boundary thermodynamic accounting for finite observers.

**Status.** Main T2 thesis.

**Dependencies.** T2-001–004

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

### FDS-T2-006 — Non-Equilibrium Residual Terms

**Statement.** Non-equilibrium horizon accounting may require residual terms.

**Status.** Optional extension.

**Dependencies.** T2-005

**First timestamp.** FDS-T2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20284911

---

## T3 — Capacity Overflow and Effective Stochasticity Claims

### FDS-T3-001 — Capacity Overflow

**Statement.** Capacity overflow occurs when task-relevant distinction demand exceeds accessible capacity.

**Status.** Operational criterion.

**Dependencies.** FDS-CORE-004 capacity deficit; task-relevant demand measure; accessible capacity measure.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Full-fidelity tracking persists under bounded resources after independently estimated demand exceeds all accessible capacity.

---

### FDS-T3-002 — Non-Injective Projection Induces Effective Stochasticity

**Statement.** Non-injective projection induces effective stochasticity.

**Status.** Conditional theorem.

**Dependencies.** FDS-P4-001 non-injective truncation; deterministic or stochastic underlying dynamics; hidden successor variation within pre-image classes.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** A many-to-one accessible projection always induces deterministic accessible transitions despite hidden successors varying within the same visible record class.

---

### FDS-T3-003 — Critical-Deficit Signature

**Statement.** Overflow has a critical-deficit signature: predictive error and transition entropy show rapid increase near the capacity crossing.

**Status.** Testable prediction.

**Dependencies.** FDS-T3-001 overflow definition; predictive error measure; transition entropy measure; controlled capacity crossing.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Predictive error, transition entropy, and exit signatures vary smoothly through controlled capacity crossing with no susceptibility peak, kink, or rapid regime change.

---

### FDS-T3-004 — Phase-B Variable Selection

**Statement.** Phase-B variables are selected by low update cost, slow information decay, and approximate Markov closure.

**Status.** Selection principle.

**Dependencies.** FDS-T3-002 effective stochasticity; mutual information decay measure; Markov closure error measure; maintenance cost function.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** All coarse variables lose predictive information at the same rate under projection, regardless of update cost, closure error, or persistence utility.

---

### FDS-T3-005 — Informational Hysteresis

**Statement.** Capacity recovery need not reverse overflow: discarded distinctions are not automatically recovered.

**Status.** Conditional prediction.

**Dependencies.** FDS-P4-003 informational hysteresis; finite record capacity; no external recovery side-record.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Discarded distinctions are perfectly reconstructed after capacity recovery without external logs, hidden reservoirs, or additional records.

---

### FDS-T3-006 — Capacity-Relative Stochasticity

**Statement.** Stochastic descriptions are capacity-relative unless supported by capacity-independent noise sources.

**Status.** Scope claim.

**Dependencies.** FDS-T3-002 effective stochasticity; accounting boundary registration; capacity-independent noise source definition.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** The same process yields the same stochastic description independent of observer capacity, projection, measurement boundary, and retained memory.

---

### FDS-T3-007 — Long-Context Drift as Wrong Invariant Completion

**Statement.** Long-context drift is a domain projection of wrong invariant completion under overflow.

**Status.** Engineering projection.

**Dependencies.** FDS-T3-004 Phase-B invariants; context window capacity; false invariant completion mechanism.

**First timestamp.** FDS-T3 v1.0, 2026-05-16.

**Failure condition.** Context overflow in finite-window systems never increases false dependency, semantic drift, wrong task-state completion, or external-memory demand under matched tasks.

---

## T4 — Macroscopic State and Law Selection from Coupled Residue Channels Claims

### FDS-T4-001 — Joint Forced-and-Preparation Closure Response

**Statement.** Joint closure response includes both forced-history and preparation-coordinate input families.

**Status.** Definition / typed response structure.

**Dependencies.** FDS-P8 coupled residue channel; P3/P4 preparation/initial-data structure; registered preparation injection map.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Preparation-forced residue has no measurable effect on closure quality or error budget.

---

### FDS-T4-002 — Four-Way Residue Treatment Taxonomy

**Statement.** Active residue admits four admissible treatments: promote, localize, truncate, or reject.

**Status.** Classification principle.

**Dependencies.** FDS-P8 residue qualification hierarchy; finite task tolerance; closure error budget.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Four-way taxonomy systematically misclassifies residue treatment decisions in controlled test cases.

---

### FDS-T4-003 — Noncommuting Closure Pipeline Order

**Statement.** Closure operations do not commute: active quotient → persistent isolation → promotion → stable reduction → localization.

**Status.** Operational principle.

**Dependencies.** Ordered pipeline hypothesis; persistent-mode isolation before localization.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Localization before persistent isolation yields identical or superior closure quality without divergence.

---

### FDS-T4-004 — Four-Level State Firewall Distinction

**Statement.** Four-level state firewall distinguishes realization coordinates, physical closure states, macroscopic variables, and conserved quantities.

**Status.** Classification principle.

**Dependencies.** FDS-P7 side-ledger distinction; P3/P4 accessible/observer boundary; carrier registration.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** No measurable information-theoretic or physical difference between state categories under valid closure mapping.

---

### FDS-T4-005 — Persistent-Channel Degree Obligation

**Statement.** Persistent joint-response poles impose a minimum additional closure degree: additional closure degree ≥ McMillan degree of persistent block.

**Status.** Restricted realization theorem.

**Dependencies.** Minimal realization theory; rational transfer function McMillan degree; isolated persistent spectrum; joint forced-and-preparation response.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** An exact causal closure with fewer degrees than the persistent-block McMillan degree reproduces all registered joint responses.

---

### FDS-T4-006 — Representation Invariance of Additional Closure Degree

**Statement.** Additional closure degree is representation-invariant across internal state, higher-order derivatives, and registered side-ledgers.

**Status.** Corollary / invariant property.

**Dependencies.** FDS-T4-005 persistent-channel theorem; minimal linearization; full initial-data manifold.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Equivalent joint responses with different representations have measurably different minimal linearized degrees.

---

### FDS-T4-007 — Operational Promotion Rank Monotonicity

**Statement.** Operational promotion rank is monotonic in task window length, error tolerance strictness, and law-class restrictiveness.

**Status.** Conditional proposition.

**Dependencies.** Nested closure classes; contractive time-norm restriction; compatible input-window registration; finite-window Hankel operator.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Promotion rank systematically decreases with longer task window, stricter tolerance, or smaller law class under valid registration.

---

### FDS-T4-008 — Startup-Qualified Temporal Localization

**Statement.** Fast-residue memory admits a startup-qualified Taylor expansion in derivatives of the retained state with controlled remainder.

**Status.** Conditional theorem.

**Dependencies.** Exponential semigroup bound; incomplete moment tail estimate; initial fast-residue forcing bound; retained-state regularity.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Temporal localization with declared order violates error bound or diverges for valid stable memory kernels within stated assumptions.

---

### FDS-T4-009 — Stability Firewall for Local-Truncation Laws

**Statement.** Local-truncation laws require separate stability audit: constitutive series convergence does not guarantee autonomous-law well-posedness.

**Status.** Admissibility criterion.

**Dependencies.** Stable auxiliary-state reference; operator-pencil well-posedness criterion.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** All convergent Taylor expansions of stable memory kernels yield well-posed autonomous evolution laws.

---

### FDS-T4-010 — Phase-B Pareto Closure Frontier

**Statement.** Phase-B closure frontier selects Pareto-minimal closures trading error, additional degree, law order, maintenance cost, and side-ledger access.

**Status.** Definition / selection framework.

**Dependencies.** Multi-objective Pareto order; registered resource costs; certified error budgets.

**First timestamp.** FDS-T4 v1.0, 2026-06-15.

**Failure condition.** Pareto-optimal frontier does not correlate with actual closure quality or maintainability in controlled synthetic or experimental benchmarks.

---

## Q1 — Finite Record Boundaries in Wigner's Friend Claims

### FDS-Q1-001 — Finite Distinction-Registers

**Statement.** Observers are finite distinction-registers.

**Status.** O1 operational bridge.

**Dependencies.** FDS-O1

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-002 — Facts Indexed by Record Boundaries

**Statement.** Operationally assertable quantum facts are indexed by accessible record boundaries.

**Status.** Q1 bridge.

**Dependencies.** Q1-001

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-003 — Wigner-Friend as Boundary-Promotion Problem

**Statement.** Wigner-friend tension is a boundary-promotion problem.

**Status.** Main Q1 thesis.

**Dependencies.** Q1-001; Q1-002

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-004 — Mutual Information Required for Promotion

**Statement.** Friend-relative records require mutual information before promotion into Wigner's algebra.

**Status.** Information-theoretic bridge.

**Dependencies.** Q1-003

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-005 — Ignorance Is Not Coherence

**Statement.** Wigner's ignorance is not physical coherence.

**Status.** Scope firewall.

**Dependencies.** Q1-001

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-006 — Objective Availability Requires Redundancy

**Statement.** Objective availability requires redundancy, access, and record stability.

**Status.** Testable bridge hypothesis.

**Dependencies.** Q1-003; quantum Darwinism

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

### FDS-Q1-007 — Not a Born-Rule Derivation

**Statement.** Q1 does not derive Born probabilities.

**Status.** Scope firewall.

**Dependencies.** Q1-001

**First timestamp.** FDS-Q1 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20289215

---

## Q2 — Finite Distinction Maintenance in Fault-Tolerant Quantum Computation Claims

### FDS-Q2-001 — Logical Qubits as Protected Quantum Distinctions

**Statement.** Logical qubits are protected quantum distinctions.

**Status.** FDS/QI bridge.

**Dependencies.** FDS core; QEC theory

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-002 — QEC as Active Finite-Distinction Maintenance

**Statement.** QEC is active finite-distinction maintenance.

**Status.** Main Q2 interpretation.

**Dependencies.** Q2-001

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-003 — Threshold Theorem as Conditional Baseline

**Statement.** Threshold theorem is accepted as conditional baseline.

**Status.** Scope firewall.

**Dependencies.** Threshold theorem

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-004 — Correction Demand as Vector Ledger

**Statement.** Correction demand is a vector ledger.

**Status.** Engineering bridge.

**Dependencies.** Q2-002

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-005 — Landauer Lower Bound on Irreversible Reset

**Statement.** Irreversible reset has a Landauer lower bound.

**Status.** Physical bridge.

**Dependencies.** Landauer 1961

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-006 — Cold-Stage Ledger Constraints

**Statement.** Cryogenic solid-state systems face cold-stage ledger constraints.

**Status.** Architecture-specific claim.

**Dependencies.** Q2-004; Q2-005

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-007 — Passive Protection Reduces Active Load

**Statement.** Topological/passive protection can reduce active load.

**Status.** Escape-channel bridge.

**Dependencies.** Q2-002

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

### FDS-Q2-008 — Failure Propagation Rule

**Statement.** Q2 failure does not falsify FDS Core or Q1.

**Status.** Failure propagation rule.

**Dependencies.** Q2-001; Q2-002

**First timestamp.** FDS-Q2 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20302569

---

## B0 — Biomedical Bridge Registry Claims

### FDS-B0-001 — Finite Observer Bound

**Statement.** Finite observer bound applies to biomedical knowledge.

**Status.** Formal bridge.

**Dependencies.** FDS Core

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-002 — Modeling Not Diagnosis

**Statement.** Biomedical FDS mapping is modeling, not diagnosis.

**Status.** Governance firewall.

**Dependencies.** B0-001

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-003 — Domain Bridge Status

**Statement.** B-series claims are domain bridges.

**Status.** Governance firewall.

**Dependencies.** B0-002

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-004 — Claim-Level Hierarchy

**Statement.** Claim-level hierarchy (B-L0 to B-L5) governs interpretation.

**Status.** Registry governance.

**Dependencies.** B0-003

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-005 — Translation Barrier

**Statement.** Translation barrier prevents clinical overreach.

**Status.** Safety firewall.

**Dependencies.** B0-004

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-006 — Mechanism Non-Replacement Rule

**Statement.** Mechanism non-replacement rule.

**Status.** Governance rule.

**Dependencies.** B0-001

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-007 — Maintenance Debt Concept

**Statement.** Maintenance debt as accumulated repair-verification mismatch.

**Status.** Non-clinical concept.

**Dependencies.** B0-001

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B0-008 — Failure Propagation Rule

**Statement.** B0 failure does not falsify FDS Core.

**Status.** Propagation rule.

**Dependencies.** B0-001

**First timestamp.** FDS-B0 v1.0, 2026-05-19.

**Failure condition.** 10.5281/zenodo.20312983

---

### FDS-B1-001 — Immunity as Boundary Verification

**Statement.** Immune systems can be modeled as finite-capacity boundary-verification architectures.

**Status.** Domain bridge (B-L2).

**Dependencies.** B0 biomedical bridge governance; FDS core capacity definitions.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Immune response can be fully organized without finite classification, memory, resource, boundary, or verification roles.

---

### FDS-B1-002 — Admission Before Action

**Statement.** Immune action requires admission and classification of candidate distinctions before downstream response.

**Status.** Domain bridge (B-L2/B-L3).

**Dependencies.** B1-001; recognition-admission-verification-action pipeline.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Action is empirically independent of admission, classification, memory, or context in the specified model.

---

### FDS-B1-003 — Multiaxis Classifier

**Statement.** Immune classification is better modeled as a boundary-state vector than as a single self/non-self label.

**Status.** Domain bridge (B-L2).

**Dependencies.** B1-001; multiaxis classification.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** A one-dimensional label captures all relevant verification behavior in the declared system.

---

### FDS-B1-004 — Verification Saturation

**Statement.** High candidate-distinction load should produce delay, broad default action, reduced specificity, false positives/negatives, or FDS-resolution failure.

**Status.** Domain bridge (B-L3).

**Dependencies.** B1-001; verification saturation; VLR control number.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Increasing verification burden produces no change in accuracy, delay, alarm load, resource use, or resolution.

---

### FDS-B1-005 — Memory-Tolerance Tradeoff

**Statement.** Immune memory reduces future verification cost but can produce drift, overgeneralization, or tolerance risk.

**Status.** Domain bridge (B-L3).

**Dependencies.** B1-001; memory-tolerance tradeoff.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Memory has no measurable cost, drift, or threshold effect in the declared system.

---

### FDS-B1-006 — Adversarial Sabotage

**Statement.** Some perturbations actively consume verification capacity or modify classification.

**Status.** Domain bridge (B-L3).

**Dependencies.** B1-001; adversarial distinction injection model.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Evasion-like processes never alter Y, pi, M, Phi, or C_verify in declared models.

---

### FDS-B1-007 — Distributed Spatial Latency

**Statement.** Immune verification is constrained by routing, migration, amplification, and return times.

**Status.** Domain bridge (B-L3).

**Dependencies.** B1-001; spatial latency graph model; SLR control number.

**First timestamp.** FDS-B1 v1.0, 2026-05-21.

**Failure condition.** Spatial latency has no measurable effect in systems where local damage timescale is shorter than verification time.

---

## FDS-G1 Finite Screen Spacetime Claims

### FDS-G1-001 — Finite Causal-Screen Entropy Response
**Statement.** Finite causal-screen capacity defines an entropy-response substrate for local gravitational coupling. The area response component controls the local coupling (stiffness) through an entropy Hessian formalism, with Onsager-type stochastic screen dynamics producing Raychaudhuri-like capacity-flow normal forms.
**Status.** Production-refined evidence-selected (pilot grade); D0 microscopic calibration lemmas remain open.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-T1-001, FDS-T2-001.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** Finite-screen entropy response produces no distinguishable gravitational coupling signature beyond standard GR+\(\Lambda\)CDM under production evidence.

### FDS-G1-002 — 3/4 Projection Lock
**Statement.** Under optical port isotropy, the Weyl-active unimodular sector \(S_1\oplus S_2\oplus T\) occupies three of four optical port dimensions, giving a projection coefficient \(\kappa=3/4\). This is the isotropic MaxEnt/Fisher-compliance fixed point of the finite-access optical ledger.
**Status.** Exact-pilot evidence-selected; survives top-control wide-prior sensitivity.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-001, FDS-T2-001.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** Free-\(\kappa\) decisively beats \(M_{3/4}\) under production evidence.

### FDS-G1-003 — Background–Weyl Residual Fingerprint
**Statement.** The G1DE-M\(_{3/4}\) branch predicts a locked background–Weyl residual:
\[
s<3,\qquad \mu(a,k)=1,\qquad \Sigma(a,k)-1=-\frac34(3-s)\widehat R_H(a),\quad \widehat R_H(1)=1.
\]
The background deviation and Weyl response are tied to the same output-response shape \(\widehat R_H(a)\), with near-GR growth (\(\mu\simeq1\)). This is a sparse residual, not a flexible dark-energy or modified-growth fit.
**Status.** Production-refined evidence-selected (pilot grade); ranked first in completed homogeneous seven-model medium-prior nested-evidence hierarchy. KiDS-1000 shear-only diagnostics support the Weyl channel; full \(3\times2\)pt, CMB, and nonlinear validation pending.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-002, FDS-X1-001, FDS-X1-002.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** Any of: (1) Free-\(\kappa\) beats M\(_{3/4}\); (2) Constant-\(\Sigma\) beats output-shape model; (3) \(|\mu-1|\sim|\Sigma-1|\); (4) Free \(A(a,k)\) required; (5) CPL or \(\Lambda\)CDM wins; (6) Expanded lensing does not support Weyl signal.

### FDS-G1-004 — Completed Homogeneous Seven-Model Medium-Prior Nested-Evidence Hierarchy
**Statement.** Completed homogeneous seven-model medium-prior nested-evidence audit over matched exact likelihoods selects:
\[
M_{3/4} > M_\kappa > \text{const-}\Sigma > \text{G1DE-2} > \text{G1DE-1} > \text{CPL} > \Lambda\text{CDM},
\]
with margins \(\Delta\log Z\simeq0.856, 1.775, 6.523, 7.402, 9.603, 11.884\) against the six controls. G1DE-1 serves as growth-only negative control. Top-control wide-prior sensitivity confirms ranking stability.
**Status.** Production-refined medium-prior 8-seed audit (\(d\log Z=0.1\)); diagnostic-only KiDS support; nn/clustering channel missing; full \(3\times2\)pt pending.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-003, FDS-X1-004.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** Ranking fails under production evidence refinement, expanded lensing likelihoods, full baseline wide-prior sensitivity, or independent replication. Production evidence returns to CPL or \(\Lambda\)CDM dominance.

### FDS-G1-005 — Finite Markov-Screen Realization
**Statement.** The G1DE-M\(_{3/4}\) normal form is realizable by a finite detailed-balance Markov screen with optical symmetry (\(\kappa=3/4\)), slow horizon mode (\(\Gamma_H=2\epsilon r_H\)), and Ward-stiff Ricci leakage. This is a constructive existence prototype, not a unique microscopic derivation of physical finite-screen states.
**Status.** Realizability claim — existence prototype constructed; physical microphysics not uniquely identified.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-002, FDS-G1-003.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** The finite Markov-screen class cannot realize the optical projection, rank-one horizon output, or Ward-stiff Ricci leakage simultaneously under any admissible parameter choice.

### FDS-G1-006 — Falsification Contract
**Statement.** The G1 dark-sector branch carries ten pre-specified demotion paths with severity tiers (Critical/High/Medium), documented in the kill-test table of the main paper. No free macroscopic drift of gravitational coupling without conservation closure is claimed. Every residual must either close a conservation law, correlate observables through a common ledger variable, or be demoted by information criteria. The G1DE class contains no free \(A(a,k)\) amplitude parameter.
**Status.** Governance — claim; demotion table published in main paper.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-004.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** G1DE class collapses to generic dark-stress model (free amplitude required).

### FDS-G1-007 — Amplitude Lock vs Shape Lock Distinction
**Statement.** The current empirical support separates into two levels: the amplitude lock (\(s<3\), \(\mu\simeq1\), \(\Sigma_0=-\frac34(3-s)\)) and the more demanding redshift-shape lock (\(\Sigma(a)-1\propto \widehat R_H(a)\)). The amplitude lock is supported by production-refined evidence and KiDS free-\(\kappa\) relaxation; the shape lock remains preliminary and nuisance-entangled. The amplitude lock can survive even if the redshift-kernel shape is demoted.
**Status.** Operational distinction — documented in main paper §Amplitude Lock vs Shape Lock.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-002, FDS-G1-003.
**First timestamp.** FDS-G1 Complete Series v1.2, 2026-06-02.
**DOI.** 10.5281/zenodo.20521142.
**Failure condition.** Distinction fails to organize future data outcomes: amplitude and shape locks always co-succeed or co-fail in production.

---

### FDS-H1-001 — Finite Causal-Screen Holography
**Statement.** Holography is finite boundary distinction recovery under screen-capacity constraints.
**Status.** Released (v0.21, H-series bridge paper).
**Layer.** Physics — Gravity 1, H-series.
**Dependencies.** Standard AdS/CFT, RT/FLM, holographic QEC, causal-diamond thermodynamics, Bousso covariant entropy bound.
**First timestamp.** FDS-H1, 2026-06-04.
**DOI.** 10.5281/zenodo.20541234.
**Failure condition.** Finite boundary recovery cannot be captured by screen capacity, recovery nets, or gluing obstruction diagnostics.

### FDS-H1-002 — Finite Recovery-Net Theorem (Exact Nerve-Graph)
**Statement.** On each connected component of the nerve graph of a finite cover, path-independent recovery holds if and only if all cycle holonomies vanish.
**Status.** Restricted theorem — exact nerve-graph case.
**Layer.** Physics — Gravity 1, H-series.
**Dependencies.** FDS-H1-001.
**First timestamp.** FDS-H1, 2026-06-04.
**DOI.** 10.5281/zenodo.20541234.
**Failure condition.** Recovery consistency cannot be captured by loop holonomy or gluing obstruction in finite models.

### FDS-H1-003 — Finite Recovery-Net Theorem (Lipschitz Tolerant)
**Statement.** Under Lipschitz transition maps, recovery error accumulates as product-weighted sum; 1-Lipschitz corollary gives simple triangular error bound.
**Status.** Restricted theorem — tolerant case with Lipschitz condition.
**Layer.** Physics — Gravity 1, H-series.
**Dependencies.** FDS-H1-002.
**First timestamp.** FDS-H1, 2026-06-04.
**DOI.** 10.5281/zenodo.20541234.
**Failure condition.** Finite recovery error bounds cannot be established under Lipschitz or non-expansive transition maps.

### FDS-H1-004 — Matched Local Entropy, Split Recovery
**Statement.** There exist finite boundary ledgers with identical local marginal boundary entropy \(H(B_i)\) but different recovery errors \(\epsilon_{B_i}(Q)\) for the same bulk distinction.
**Status.** Proposition — constructive proof via redundancy code and parity code.
**Layer.** Physics — Gravity 1, H-series.
**Dependencies.** FDS-H1-001.
**First timestamp.** FDS-H1, 2026-06-04.
**DOI.** 10.5281/zenodo.20541234.
**Failure condition.** Recovery error is entirely determined by local marginal boundary entropy in all controlled finite models.

---

### FDS-Q0-001 — Physical Distinguishability as Directed Boundary Access
**Statement.** Physical distinguishability is first directed boundary access.
**Status.** FDS primitive / definition.
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS core; standard quantum distinguishability theory.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** All operational record production, erasure, and recovery are symmetric without boundary cost or accessibility structure.

### FDS-Q0-002 — Zero-Holonomy Quotient-Consistency Theorem
**Statement.** Zero record holonomy makes the reversible quotient well-defined; in the restricted quantum-access category the induced kernel is symmetric.
**Status.** Restricted quotient-consistency theorem.
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS-Q0-001.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** A closed, record-neutral, zero-holonomy sector fails to admit any well-defined symmetric quotient kernel.

### FDS-Q0-003 — Hilbert QM as Zero-Holonomy Sector
**Statement.** Hilbert quantum mechanics is the finite-capacity zero-holonomy sector.
**Status.** Conditional theorem target (not yet proved in Q0).
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS-Q0-002.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** A non-Hilbert reciprocal finite-capacity quotient satisfies reversible dynamics, composition stability, and no hidden record asymmetry.

### FDS-Q0-004 — Born Rule as No-Arbitrage Rule
**Statement.** Born weights are the no-record-capacity-arbitrage rule.
**Status.** Open theorem target (companion target — Q0B).
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS-Q0-003.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** A non-Born rule satisfies basis neutrality, coarse-graining, composition, and finite record-capacity no-arbitrage.

### FDS-Q0-005 — Decoherence Irreversibility Tracks Stable Records
**Statement.** Decoherence irreversibility tracks stable records, not mere entanglement alone.
**Status.** Operational prediction.
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS-Q0-001.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** Stable record accessibility has no independent predictive role for recovery once ordinary overlap and noise metrics are controlled.

### FDS-Q0-006 — QEC Overhead Tracks Directed Leakage Holonomy
**Statement.** QEC overhead tracks directed leakage holonomy.
**Status.** Q0/Q2 bridge prediction.
**Layer.** Physics — Quantum upstream.
**Dependencies.** FDS-Q0-001; FDS-Q2.
**First timestamp.** FDS-Q0, 2026-06-04.
**DOI.** 10.5281/zenodo.20542105.
**Failure condition.** Directed leakage has no independent predictive value for logical failure after matched-fidelity and matched-syndrome controls.

---

### FDS-H2-001 — Recovery Descent Hierarchy
**Statement.** Raw exact descent, quotient descent, and strict liftability are distinct.
**Status.** Restricted formal propositions.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H1; non-Abelian Čech–de Rham descent; bundle theory.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** A $G_0$-valued defect guarantees quotient descent only; a strict lift requires triviality of the associated twisted lifting obstruction.

### FDS-H2-002 — Registered Connection Rule and Kato Support Geometry
**Statement.** A connection must be generated by a pre-registered gauge-covariant rule; the relative Kato construction defines recoverable-support transport.
**Status.** Admissibility rule; relative Kato theorem.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-001.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** If curvature changes under equivalent presentations or response-dependent ambient geometry, it is not an identifiable support invariant.

### FDS-H2-003 — Kato Transport Scope and Full-Channel Blindness
**Statement.** Kato transport is a recoverable-support geometry, not a full-channel geometry.
**Status.** Scope theorem and blindness proposition.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-002.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** Equal support projectors imply equal Kato connections and curvatures even when channel spectra, weights, fidelity, or action differ.

### FDS-H2-004 — Regular Physical Recovery Quotient
**Statement.** The physical recovery quotient is a regular principal-bundle quotient.
**Status.** Restricted quotient theorem.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-002.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** Outside the closed-normal, regular branch the quotient must be treated as stratified, orbifold, groupoid, or stack-like.

### FDS-H2-005 — Operational-Covector Bridge
**Statement.** The operational-covector bridge is $\dd\omega_{\rm th}=\ell(F_{\rm phys})$ for a pre-registered parallel flat-coefficient readout.
**Status.** Conditional functional bridge and Stokes protocol.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-004.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** A global bridge requires $[\ell(F_{\rm phys})]_{\rm dR}=0$; failure demotes the functional, scale calibration, or global covector realization.

### FDS-H2-006 — Response-Bundle Bridge
**Statement.** A parallel bundle bridge exists exactly when a base-point map intertwines all holonomies.
**Status.** Bundle-branch theorem; standard holonomy principle specialized to registered bundles.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-004.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** Held-out loops support only the sampled subgroup unless generators are proved; does not apply to the direct covector branch.

### FDS-H2-007 — Holonomy-Relative Visibility and Character-Based Abelianization
**Statement.** Parallel Branch-A readouts are holonomy-relative; character-based one-dimensional responses see only the full Lie-algebra Abelianization of the identity component.
**Status.** Holonomy-invariance proposition and character no-go theorem.
**Layer.** Physics — H-series, recovery bridge.
**Dependencies.** FDS-H2-005.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** A general parallel readout annihilates $[\mathfrak{hol}_{X_0},\mathfrak g_{\rm phys}]$, not necessarily $[\mathfrak g_{\rm phys},\mathfrak g_{\rm phys}]$; full Abelianization requires full-group invariance, a character differential, or equality of these commutator subspaces.

### FDS-H2-008 — H2 Does Not Derive G1, GR, or $M_{3/4}$
**Statement.** H2 derives G1, GR, or $M_{3/4}$.
**Status.** Explicitly not claimed.
**Layer.** Physics — H-series.
**Dependencies.** FDS-H2-001.
**First timestamp.** FDS-H2, 2026-06-06.
**DOI.** 10.5281/zenodo.20567788.
**Failure condition.** H2 ends at a support-level premetric response-obstruction criterion; full-channel geometry, Ward closure, optical selection, and cosmology remain downstream.


*End of ledger. New claims added as documents are released or revised.*