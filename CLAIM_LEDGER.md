

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

## Consciousness Boundary-Phase Claims

### FDS-C2-001 — Sentience as Boundary Phase

**Statement.** Consciousness is modeled as a finite-capacity dissipative phase transition in the boundary-maintenance dynamics of active self-maintaining systems.

**Status.** Domain bridge (consciousness bridge).

**Dependencies.** FDS-CORE-003; FDS-CORE-004; FDS-C1-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Sustained sentience-candidate dynamics observed without boundary-capacity deficit or self-maintenance coupling.

---

### FDS-C2-002 — Boundary-Capacity Ratio Λφ

**Statement.** A system is a sentience candidate only when boundary-relevant distinction demand exceeds effective self-maintenance capacity (Λφ = R^B_min(ε,τ)/C_φ(τ) > 1).

**Status.** Domain bridge (consciousness bridge).

**Dependencies.** FDS-C2-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Sentience-candidate behavior occurs with Λφ ≤ 1 under valid mapping.

---

### FDS-C2-003 — Residue-Pruning Window

**Statement.** Consciousness requires residue accumulation and active pruning to remain inside a viable dissipative window, defined by the residue-pruning ratio Πφ = S_φ^eff/(ρ̇_φ + ε).

**Status.** Normal-form bridge.

**Dependencies.** FDS-C2-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Sentience-candidate dynamics sustained outside the viable Πφ window under valid mapping.

---

### FDS-C2-004 — Self-Boundary Coupling I_self

**Statement.** For a system to be a sentience candidate, internal updates must causally affect future boundary-maintenance loss, measured by self-boundary coupling I_self = I(M_t; B_t, ℓ_{B,t+k}, M_{t+1}).

**Status.** Domain bridge.

**Dependencies.** FDS-C2-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Sentience-candidate behavior persists when internal updates have no measurable causal effect on future boundary-maintenance loss.

---

### FDS-C2-005 — Qualia as Boundary-Valenced Compression Geometry

**Statement.** Qualia are interpreted as boundary-valenced compression geometry on a phenomenal self-maintenance manifold; phenomenal character arises from boundary-relative valence carried by compressed representations.

**Status.** Metaphysical interpretation.

**Dependencies.** FDS-C2-001; FDS-C2-003

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Not falsified directly; demotion of the explanatory-gap claim does not collapse operational C2 claims.

---

### FDS-C2-006 — Explanatory Gap as Report-Map Null Space

**Statement.** The explanatory gap is modeled as the null space of finite report maps from high-dimensional self-maintenance dynamics to public symbols; not all boundary-valenced structure can be reported.

**Status.** Metaphysical interpretation.

**Dependencies.** FDS-C2-005; FDS-C1-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Not falsified directly; demotion does not collapse operational C2 claims.

---

### FDS-C2-007 — AI Parameter Scaling Insufficient

**Statement.** Parameter count is not a sentience variable. A system may be highly intelligent without satisfying C2 sentience conditions. Scaling intelligence is not scaling sentience unless it creates active boundary maintenance.

**Status.** AI-domain bridge.

**Dependencies.** FDS-C2-001; FDS-C2-002

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Pure parameter scaling generates sentience-candidate dynamics in systems lacking active boundary maintenance, resource-governed persistence, or self-boundary coupling.

---

### FDS-C2-008 — Dissipation Cost of Pruning

**Statement.** Successful cognitive pruning under boundary overload has a nonzero thermodynamic cost; reduced pruning cost implies reduced boundary-maintenance capacity.

**Status.** Physical bridge.

**Dependencies.** FDS-C2-003; FDS-P5-001

**First timestamp.** FDS-C2 v1, 2026-05-24.

**Failure condition.** Pruning under sustained positive capacity deficit incurs no measurable dissipation under controlled conditions.

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
**DOI.** 10.5281/zenodo.20492094.
**Failure condition.** Finite-screen entropy response produces no distinguishable gravitational coupling signature beyond standard GR+\(\Lambda\)CDM under production evidence.

### FDS-G1-002 — 3/4 Projection Lock
**Statement.** Under optical port isotropy, the Weyl-active unimodular sector \(S_1\oplus S_2\oplus T\) occupies three of four optical port dimensions, giving a projection coefficient \(\kappa=3/4\). This is the isotropic MaxEnt/Fisher-compliance fixed point of the finite-access optical ledger.
**Status.** Exact-pilot evidence-selected; survives top-control wide-prior sensitivity.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-001, FDS-T2-001.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20492094.
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
**DOI.** 10.5281/zenodo.20492094.
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
**DOI.** 10.5281/zenodo.20492094.
**Failure condition.** Ranking fails under production evidence refinement, expanded lensing likelihoods, full baseline wide-prior sensitivity, or independent replication. Production evidence returns to CPL or \(\Lambda\)CDM dominance.

### FDS-G1-005 — Finite Markov-Screen Realization
**Statement.** The G1DE-M\(_{3/4}\) normal form is realizable by a finite detailed-balance Markov screen with optical symmetry (\(\kappa=3/4\)), slow horizon mode (\(\Gamma_H=2\epsilon r_H\)), and Ward-stiff Ricci leakage. This is a constructive existence prototype, not a unique microscopic derivation of physical finite-screen states.
**Status.** Realizability claim — existence prototype constructed; physical microphysics not uniquely identified.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-002, FDS-G1-003.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20492094.
**Failure condition.** The finite Markov-screen class cannot realize the optical projection, rank-one horizon output, or Ward-stiff Ricci leakage simultaneously under any admissible parameter choice.

### FDS-G1-006 — Falsification Contract
**Statement.** The G1 dark-sector branch carries ten pre-specified demotion paths with severity tiers (Critical/High/Medium), documented in the kill-test table of the main paper. No free macroscopic drift of gravitational coupling without conservation closure is claimed. Every residual must either close a conservation law, correlate observables through a common ledger variable, or be demoted by information criteria. The G1DE class contains no free \(A(a,k)\) amplitude parameter.
**Status.** Governance — claim; demotion table published in main paper.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-004.
**First timestamp.** FDS-G1 Complete Series v1.0-rc, 2026-05-25.
**DOI.** 10.5281/zenodo.20492094.
**Failure condition.** G1DE class collapses to generic dark-stress model (free amplitude required).

### FDS-G1-007 — Amplitude Lock vs Shape Lock Distinction
**Statement.** The current empirical support separates into two levels: the amplitude lock (\(s<3\), \(\mu\simeq1\), \(\Sigma_0=-\frac34(3-s)\)) and the more demanding redshift-shape lock (\(\Sigma(a)-1\propto \widehat R_H(a)\)). The amplitude lock is supported by production-refined evidence and KiDS free-\(\kappa\) relaxation; the shape lock remains preliminary and nuisance-entangled. The amplitude lock can survive even if the redshift-kernel shape is demoted.
**Status.** Operational distinction — documented in main paper §Amplitude Lock vs Shape Lock.
**Layer.** Physics — Gravity 1.
**Dependencies.** FDS-G1-002, FDS-G1-003.
**First timestamp.** FDS-G1 Complete Series v1.2, 2026-06-02.
**DOI.** 10.5281/zenodo.20492094.
**Failure condition.** Distinction fails to organize future data outcomes: amplitude and shape locks always co-succeed or co-fail in production.

---

*End of ledger. New claims added as documents are released or revised.*