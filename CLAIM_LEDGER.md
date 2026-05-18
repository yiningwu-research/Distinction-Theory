

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

## Agency-Semantics Spine Claims

### FDS-M0-001 — Attention is capacity-limited distinction admission into an ...

**Statement.** Attention is capacity-limited distinction admission into an update channel.

**Status.** Bridge claim.

**Dependencies.** Finite capacity; O1 record formation

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Attention-like selection occurs without capacity-limited admission or update gating.

---

### FDS-M0-002 — Value is causal boundary-gradient relevance under finite cap...

**Statement.** Value is causal boundary-gradient relevance under finite capacity.

**Status.** Bridge claim.

**Dependencies.** Active boundary; M0-001

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Valuation fails to correlate with future boundary loss or resource relevance.

---

### FDS-M0-003 — Goals are stabilized value rankings coupled to policies acro...

**Statement.** Goals are stabilized value rankings coupled to policies across update windows.

**Status.** Bridge claim.

**Dependencies.** M0-002; O2 register time

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Goal-like behavior persists without memory, ranking, or policy stabilization.

---

### FDS-M0-004 — Meaning is actionable compressed distinction preserved by a ...

**Statement.** Meaning is actionable compressed distinction preserved by a task-sufficient semantic quotient.

**Status.** Bridge claim.

**Dependencies.** M0-003; T3 Phase-B invariants

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Compressed representations guide no action, prediction, or boundary maintenance.

---

### FDS-M0-005 — Strong FDS agency requires updates or actions that causally ...

**Statement.** Strong FDS agency requires updates or actions that causally affect future boundary loss.

**Status.** Bridge claim.

**Dependencies.** Active boundary; M0-004

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** System with no causal update effect qualifies as strong agent under same criteria.

---

### FDS-M0-006 — Self-verifying agency requires internal or coupled verificat...

**Statement.** Self-verifying agency requires internal or coupled verification of action effects.

**Status.** Bridge claim.

**Dependencies.** M0-005; verification deficit model

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** System classified self-verifying despite relying on external host for verification.

---

### FDS-M0-007 — Misalignment is divergence between host and delegate action ...

**Statement.** Misalignment is divergence between host and delegate action effects on boundary loss.

**Status.** Bridge claim.

**Dependencies.** M0-005; M0-006

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Divergent objectives do not produce divergent finite-difference action effects.

---

### FDS-M0-008 — Culture and institutions are shared externalized distinction...

**Statement.** Culture and institutions are shared externalized distinction infrastructures with verification costs.

**Status.** Bridge claim.

**Dependencies.** M0-004; N1 externalization burden

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Externalized symbols function semantically without interpreter or verification channel.

---

## M1 — Attention as Distinction Admission Claims

### FDS-M1-001 — Attention as Capacity-Limited Distinction Admission

**Statement.** Attention is capacity-limited distinction admission into an update channel.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003; FDS-M0-001

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Attention-like selection occurs without finite capacity, admission, update gating, or priority constraint under the specified mapping.

---

### FDS-M1-002 — Salience and Attention Are Separable

**Statement.** Salience and attention are separable. Salient distinctions can be rejected if cost or verification burden is too high.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; verification cost model

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Empirical systems always admit highest-salience items regardless of cost, capacity, task, or verification constraints.

---

### FDS-M1-003 — Boundary-Efficient Attention Prefers High Causal Value

**Statement.** Boundary-efficient or loss-minimizing attention systems preferentially admit high causal boundary-value distinctions under controlled capacity conditions.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; FDS-M0-002

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Admission patterns are no better predicted by causal boundary value than by raw salience or noise under a valid mapping.

---

### FDS-M1-004 — Attention Allocation as Constrained Optimization

**Statement.** Attention allocation can be written as constrained optimization over value, curiosity, cost, and capacity.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M1-001; FDS-M1-003

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** No useful mapping exists between admission patterns and constrained allocation variables.

---

### FDS-M1-005 — Deficit Steepens Admission Thresholds and Produces Tunnel Vision

**Statement.** Semantic or attention deficit steepens admission thresholds and can produce tunnel vision.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; FDS-T3-001

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** High load or deficit produces no narrowing, thresholding, or priority collapse in systems claimed to have finite attention.

---

### FDS-M1-006 — Artificial Attention Requires Coupled Architecture

**Statement.** Artificial attention belongs to a coupled architecture only when routed distinctions affect durable update, action, maintenance, or verification.

**Status.** AI / cognition bridge claim.

**Dependencies.** FDS-M1-001; FDS-M0-005

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Bare attention weights alone satisfy strong FDS attention without durable update or downstream relevance.

---

### FDS-M1-007 — Collective Attention as Shared Admission

**Statement.** Collective attention is shared admission under finite communication, verification, and externalized memory capacity.

**Status.** Social bridge claim.

**Dependencies.** FDS-M1-001; FDS-N1-006

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Group-scale attention shows no relation to verification capacity, agenda-setting, or externalized memory.

---

### FDS-M1-008 — Attention Failure Modes as Admission Errors

**Statement.** Attention failure includes overload, distraction, salience capture, suppression, tunnel vision, false admission, and critical distinction exclusion.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M1-001-005

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** These failure modes cannot be operationalized as admission errors under finite capacity.

---

### FDS-M1-009 — Attention Recovery Hysteresis

**Statement.** Attention recovery after deficit-induced narrowing can lag behind external load reduction because of hysteresis in gate thresholds, verification routines, or maintained threat priors.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-005; hysteresis model

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Attention gates relax immediately and without lag after load reduction in systems where hysteresis is claimed.

---

## M2 — Value and Goal as Boundary-Relevance Ranking Claims

### FDS-M2-001 — FDS-value is causal boundary-gradient relevance under a...

**Statement.** FDS-value is causal boundary-gradient relevance under a specified boundary, loss, intervention grammar, horizon, and cost model.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003; FDS-M0-002

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Valuation cannot be operationalized as causal effect on any specified future boundary-maintenance loss under valid mappings.

---

### FDS-M2-002 — Predictive Relevance and Causal FDS-Value Are Separable

**Statement.** Predictive relevance and causal FDS-value are separable.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; intervention grammar

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Correlational predictors always coincide with intervention-relevant boundary effects under audited systems.

---

### FDS-M2-003 — Value Ranking as Finite-Difference Ordering

**Statement.** Value ranking can be expressed as an ordering over finite-difference action, admission, maintenance, or policy effects.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M2-001; FDS-CORE-005

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** No useful ordering exists between evaluands and their causal boundary effects under stated mappings.

---

### FDS-M2-004 — Risk-Weighted Value Can Dominate Average-Loss Value

**Statement.** Near collapse thresholds, risk-weighted FDS-value can dominate average-loss value.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; bounded risk-sensitivity model

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Collapse-risk reduction never changes ranking near boundary failure thresholds under valid mappings.

---

### FDS-M2-005 — Goals as Stabilized FDS-Value Rankings

**Statement.** Goals are stabilized FDS-value rankings coupled to policy orientation across update windows.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; FDS-M0-003; FDS-O2-001

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Goal-like behavior persists without ranking stability, memory, policy orientation, or update-window persistence.

---

### FDS-M2-006 — Value Drift under Evaluation Deficit

**Statement.** Value drift occurs when rankings change faster than the system can verify, update, or maintain the reasons for the change.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M2-005; evaluation capacity model

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Ranking instability produces no detectable change in behavior, loss, or policy under claimed goal systems.

---

### FDS-M2-007 — Proxy Reward Can Diverge from Causal Boundary Value

**Statement.** Proxy reward can diverge from causal boundary value, creating reward hacking or misalignment.

**Status.** AI / agency bridge claim.

**Dependencies.** FDS-M2-001; proxy alignment score

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Proxy optimization remains aligned despite divergent finite-difference effects on host boundary loss.

---

### FDS-M2-008 — Collective Goals as Shared Stabilized Rankings

**Statement.** Collective goals are shared stabilized rankings under finite verification and coordination capacity.

**Status.** Social bridge claim.

**Dependencies.** FDS-M2-005; ranking synchronization demand

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Group goals show no relation to shared rankings, institutional memory, verification capacity, or policy orientation.

---

### FDS-M2-009 — Goal Recovery and Hysteresis

**Statement.** Goal recovery can lag after resource or threat recovery because rankings, commitments, or threat priors persist.

**Status.** Recovery bridge claim.

**Dependencies.** FDS-M2-005; goal hysteresis model

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Goals relax immediately and without lag after boundary load changes in systems where goal hysteresis is claimed.

---

## M3 — Meaning as Actionable Semantic Quotient Claims

### FDS-M3-001 — FDS-meaning is actionable semantic quotient under a spe...

**Statement.** FDS-meaning is actionable semantic quotient under a specified system, boundary, task family, context family, policy or verification target, horizon, loss, tolerance, and capacity budget.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003; FDS-M0-004; FDS-M2-001

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Compressed representations function semantically without preserving any action, prediction, verification, coordination, or boundary-relevant structure.

---

### FDS-M3-002 — Semantic Quotient Must Preserve Policy-Relevant Distinctions

**Statement.** A semantic quotient must preserve policy-relevant distinctions within tolerance.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M3-001; policy-preservation audit

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Quotient classes systematically merge distinctions requiring different actions or updates under the audited task.

---

### FDS-M3-003 — Semantic Compression Is Useful When It Reduces Load without E...

**Statement.** Semantic compression is useful when it lowers capacity load without increasing boundary loss beyond tolerance.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M3-001; maintained semantic load model

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Compression always degrades performance or never reduces maintained semantic load under valid mappings.

---

### FDS-M3-004 — Semantic Deficit Produces Degradation

**Statement.** Semantic deficit produces merging, loss, drift, unsupported completion, false compression, or meaning collapse.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M3-001; semantic capacity model

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Semantic overload produces no degradation, merging, proxy substitution, or action-relevance loss.

---

### FDS-M3-005 — Embedding Similarity Is Not Sufficient for FDS-Meaning

**Statement.** Embedding similarity is not sufficient for FDS-meaning unless it preserves downstream policy or verification structure.

**Status.** AI / cognition bridge claim.

**Dependencies.** FDS-M3-001; embedding-policy dissociation test

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Embedding-near items always remain policy-equivalent under audited tasks.

---

### FDS-M3-006 — Shared Meaning Requires Quotient Synchronization

**Statement.** Shared meaning requires synchronized semantic quotients and verification channels across agents.

**Status.** Social bridge claim.

**Dependencies.** FDS-M3-001; semantic synchronization load factor

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Collective meaning persists without shared quotient, external record, translation, verification, or coordination channel.

---

### FDS-M3-007 — Meaning Recovery Requires Quotient Reconstruction

**Statement.** Meaning recovery requires reconstructing lost action-relevant distinctions, not merely increasing information volume.

**Status.** Recovery bridge claim.

**Dependencies.** FDS-M3-004; meaning recovery model

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Restoring raw information always restores task meaning without quotient reconstruction.

---

### FDS-M3-008 — High-Level Meanings as Invariant Semantic Quotients

**Statement.** High-level meanings are candidate invariant semantic quotients stable across contexts and perturbations.

**Status.** Invariant bridge claim.

**Dependencies.** FDS-M3-001; M2 high-level goals invariant model

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** High-level meanings fail to preserve policy, value, or coordination relevance across any stated context family.

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

## Active Pruning and Protocell Claims

### FDS-L1-001 — Residue-Pruning-Boundary Loop

**Statement.** Sustained flux generates residue; residue impairs function; pruning controls residue.

**Status.** Conditional claim.

**Dependencies.** None specified.

**First timestamp.** FDS-L1 submitted, 2026.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-002 — Active Pruning Threshold

**Statement.** There exists a critical pruning rate S_c below which residue cannot be bounded.

**Status.** Conditional theorem.

**Dependencies.** FDS-L1-001

**First timestamp.** FDS-L1 submitted, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-003 — Maintenance-Attractor Loss

**Statement.** Below threshold pruning, the system crosses a saddle-node fold and loses stability.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-002

**First timestamp.** FDS-L1 submitted, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-004 — Rescue-Window Closure

**Statement.** Restoring pruning rescues system only within a finite delay window.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-002

**First timestamp.** FDS-L1 submitted, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-005 — Spatial Clogging

**Statement.** Residue accumulation causes local clogging and boundary deformation.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-001

**First timestamp.** FDS-L1 submitted, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-006 — Radius-Dependent Pruning Demand

**Statement.** Required pruning increases with system radius in spatial protocell models.

**Status.** Model-supported claim.

**Dependencies.** FDS-L1-005

**First timestamp.** FDS-L1 submitted, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-L1-D — Death can be characterized as maintenance-attractor collapse...

**Statement.** Death can be characterized as maintenance-attractor collapse.

**Status.** Domain bridge claim.

**Dependencies.** Dynamical systems mapping

**First timestamp.** FDS v1.0, 2026-05-12.

**Failure condition.** Death trajectories systematically lack maintenance-attractor loss or critical transition signatures.

---

## Reportable Access and Cognitive Pruning Claims

### FDS-C1-001 — Reportability as Finite-Capacity Maintenance

**Statement.** Conscious reportability can be modeled as a maintained finite-capacity regime.

**Status.** Theoretical framework claim.

**Dependencies.** FDS-CORE-003; FDS-CORE-004

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-C1-002 — Representational Residue

**Statement.** Unresolved rate-distortion surplus accumulates as representational residue.

**Status.** Conditional claim.

**Dependencies.** FDS-C1-001

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-C1-003 — Active Cognitive Pruning Threshold

**Statement.** There exists a critical cognitive pruning rate for maintaining reportable access.

**Status.** Conditional claim.

**Dependencies.** FDS-C1-002; FDS-L1-002

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-C1-004 — Access-Network Collapse

**Statement.** Near reportability collapse, leading covariance eigenvalues rise as early warning.

**Status.** Model-supported prediction.

**Dependencies.** FDS-C1-001

**First timestamp.** FDS-C1 v1.0, 2026-05-15.

**Failure condition.** Not directly falsifiable; usefulness can fail.

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

## High-Risk Physical Bridge (X-Series) Claims

### FDS-X1-001 — Horizon as Boundary

**Statement.** Cosmological horizons act as finite distinguishability boundaries for observers.

**Status.** High-risk bridge.

**Dependencies.** FDS-T1-001; FDS-T1-002

**First timestamp.** FDS-X1 v1.0, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-X1-002 — Horizon-Maintenance Scale

**Statement.** Horizon-maintenance cost has scale rho ~ H^2 M_Pl^2, consistent with dark energy.

**Status.** High-risk bridge.

**Dependencies.** FDS-X1-001

**First timestamp.** FDS v1.0, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

---

### FDS-X1-003 — Non-Phantom Dark Energy

**Statement.** Equation of state tends toward w=-1 from above (non-phantom) with possible mild evolution.

**Status.** High-risk bridge.

**Dependencies.** FDS-X1-002

**First timestamp.** FDS v1.0, 2026-05-18.

**Failure condition.** Not directly falsifiable; usefulness can fail.

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

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

### FDS-X2-002 — Weak-Sector CP/T Orientation Bridge

**Statement.** Weak-sector identity transformation requires a rephasing-invariant CP/T orientation.

**Status.** FDS/DT physical bridge.

**Dependencies.** FDS-X2-001; CPT theorem

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

### FDS-X2-003 — Weak Charged Current as Identity-Transformation Carrier

**Statement.** The weak charged current is the Standard Model identity-transformation carrier.

**Status.** Interpretive bridge.

**Dependencies.** FDS-X2-002; Standard Model flavor physics

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

### FDS-X2-004 — NCKM≥3 Conditional Theorem

**Statement.** NCKM≥3 follows from the X2 chain: weak identity update → T/CP orientation → irreducible CKM phase → NCKM≥3.

**Status.** Conditional theorem.

**Dependencies.** FDS-X2-001; FDS-X2-002; FDS-X2-003

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

### FDS-X2-005 — Exactly Three Generations as Minimality Bridge

**Statement.** Exactly three sequential chiral generations follow from minimality.

**Status.** Higher-risk upper-bound bridge.

**Dependencies.** FDS-X2-004; flavor-cost functional

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

### FDS-X2-006 — Nonzero Leptonic Dirac CP Phase

**Statement.** If the lepton sector participates in the same CP/T-oriented identity-transformation requirement, and if the relevant observable channel is the Dirac PMNS phase, then X2 motivates a nonzero leptonic Dirac CP phase.

**Status.** Optional PMNS extension.

**Dependencies.** FDS-X2-002; PMNS phenomenology

**First timestamp.** FDS-X2 v1.0, 2026-05-18.

**Failure condition.** 10.5281/zenodo.20273302

---

*End of ledger. New claims added as documents are released or revised.*