

---

## M1 — Attention as Distinction Admission Claims

### FDS-M1-001 — Attention as Capacity-Limited Distinction Admission

**Statement.** Attention is capacity-limited distinction admission into an update channel.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003 (finite capacity); FDS-M0-001 (attention definition).

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Attention-like selection occurs without finite capacity, admission, update gating, or priority constraint under the specified mapping.

---

### FDS-M1-002 — Salience and Attention Are Separable

**Statement.** Salience and attention are separable. Salient distinctions can be rejected if cost or verification burden is too high.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; verification cost model.

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Empirical systems always admit highest-salience items regardless of cost, capacity, task, or verification constraints.

---

### FDS-M1-003 — Boundary-Efficient Attention Prefers High Causal Value

**Statement.** Boundary-efficient or loss-minimizing attention systems preferentially admit high causal boundary-value distinctions under controlled capacity conditions.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; FDS-M0-002 (causal value).

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Admission patterns are no better predicted by causal boundary value than by raw salience or noise under a valid mapping.

---

### FDS-M1-004 — Attention Allocation as Constrained Optimization

**Statement.** Attention allocation can be written as constrained optimization over value, curiosity, cost, and capacity.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M1-001; FDS-M1-003.

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** No useful mapping exists between admission patterns and constrained allocation variables.

---

### FDS-M1-005 — Deficit Steepens Admission Thresholds and Produces Tunnel Vision

**Statement.** Semantic or attention deficit steepens admission thresholds and can produce tunnel vision.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-001; FDS-T3-001 (capacity overflow).

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** High load or deficit produces no narrowing, thresholding, or priority collapse in systems claimed to have finite attention.

---

### FDS-M1-006 — Artificial Attention Requires Coupled Architecture

**Statement.** Artificial attention belongs to a coupled architecture only when routed distinctions affect durable update, action, maintenance, or verification.

**Status.** AI / cognition bridge claim.

**Dependencies.** FDS-M1-001; FDS-M0-005 (strong agency).

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Bare attention weights alone satisfy strong FDS attention without durable update or downstream relevance.

---

### FDS-M1-007 — Collective Attention as Shared Admission

**Statement.** Collective attention is shared admission under finite communication, verification, and externalized memory capacity.

**Status.** Social bridge claim.

**Dependencies.** FDS-M1-001; FDS-N1-006 (externalization burden).

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Group-scale attention shows no relation to verification capacity, agenda-setting, or externalized memory.

---

### FDS-M1-008 — Attention Failure Modes as Admission Errors

**Statement.** Attention failure includes overload, distraction, salience capture, suppression, tunnel vision, false admission, and critical distinction exclusion.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M1-001—005.

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** These failure modes cannot be operationalized as admission errors under finite capacity.

---

### FDS-M1-009 — Attention Recovery Hysteresis

**Statement.** Attention recovery after deficit-induced narrowing can lag behind external load reduction because of hysteresis in gate thresholds, verification routines, or maintained threat priors.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M1-005; hysteresis model.

**First timestamp.** FDS-M1 v1.0, 2026-05-17.

**Failure condition.** Attention gates relax immediately and without lag after load reduction in systems where hysteresis is claimed.

---

## M2 — Value and Goal as Boundary-Relevance Ranking Claims

### FDS-M2-001 — FDS-Value as Causal Boundary-Gradient Relevance

**Statement.** FDS-value is causal boundary-gradient relevance under a specified boundary, loss, intervention grammar, horizon, and cost model.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003 (finite capacity); FDS-M0-002 (causal value).

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Valuation cannot be operationalized as causal effect on any specified future boundary-maintenance loss under valid mappings.

---

### FDS-M2-002 — Predictive Relevance and Causal FDS-Value Are Separable

**Statement.** Predictive relevance and causal FDS-value are separable.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; intervention grammar.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Correlational predictors always coincide with intervention-relevant boundary effects under audited systems.

---

### FDS-M2-003 — Value Ranking as Finite-Difference Ordering

**Statement.** Value ranking can be expressed as an ordering over finite-difference action, admission, maintenance, or policy effects.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M2-001; FDS-CORE-005 (update map).

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** No useful ordering exists between evaluands and their causal boundary effects under stated mappings.

---

### FDS-M2-004 — Risk-Weighted Value Can Dominate Average-Loss Value

**Statement.** Near collapse thresholds, risk-weighted FDS-value can dominate average-loss value.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; bounded risk-sensitivity model.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Collapse-risk reduction never changes ranking near boundary failure thresholds under valid mappings.

---

### FDS-M2-005 — Goals as Stabilized FDS-Value Rankings

**Statement.** Goals are stabilized FDS-value rankings coupled to policy orientation across update windows.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M2-001; FDS-M0-003 (goal definition); FDS-O2-001 (register time).

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Goal-like behavior persists without ranking stability, memory, policy orientation, or update-window persistence.

---

### FDS-M2-006 — Value Drift under Evaluation Deficit

**Statement.** Value drift occurs when rankings change faster than the system can verify, update, or maintain the reasons for the change.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M2-005; evaluation capacity model.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Ranking instability produces no detectable change in behavior, loss, or policy under claimed goal systems.

---

### FDS-M2-007 — Proxy Reward Can Diverge from Causal Boundary Value

**Statement.** Proxy reward can diverge from causal boundary value, creating reward hacking or misalignment.

**Status.** AI / agency bridge claim.

**Dependencies.** FDS-M2-001; proxy alignment score.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Proxy optimization remains aligned despite divergent finite-difference effects on host boundary loss.

---

### FDS-M2-008 — Collective Goals as Shared Stabilized Rankings

**Statement.** Collective goals are shared stabilized rankings under finite verification and coordination capacity.

**Status.** Social bridge claim.

**Dependencies.** FDS-M2-005; ranking synchronization demand.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Group goals show no relation to shared rankings, institutional memory, verification capacity, or policy orientation.

---

### FDS-M2-009 — Goal Recovery and Hysteresis

**Statement.** Goal recovery can lag after resource or threat recovery because rankings, commitments, or threat priors persist.

**Status.** Recovery bridge claim.

**Dependencies.** FDS-M2-005; goal hysteresis model.

**First timestamp.** FDS-M2 v1.0, 2026-05-18.

**Failure condition.** Goals relax immediately and without lag after boundary load changes in systems where goal hysteresis is claimed.

---

## M3 — Meaning as Actionable Semantic Quotient Claims

### FDS-M3-001 — FDS-Meaning as Actionable Semantic Quotient

**Statement.** FDS-meaning is actionable semantic quotient under a specified system, boundary, task family, context family, policy or verification target, horizon, loss, tolerance, and capacity budget.

**Status.** Formal bridge claim.

**Dependencies.** FDS-CORE-003 (finite capacity); FDS-M0-004 (meaning definition); FDS-M2-001 (FDS-value).

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Compressed representations function semantically without preserving any action, prediction, verification, coordination, or boundary-relevant structure.

---

### FDS-M3-002 — Semantic Quotient Must Preserve Policy-Relevant Distinctions

**Statement.** A semantic quotient must preserve policy-relevant distinctions within tolerance.

**Status.** Formal / model bridge claim.

**Dependencies.** FDS-M3-001; policy-preservation audit.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Quotient classes systematically merge distinctions requiring different actions or updates under the audited task.

---

### FDS-M3-003 — Semantic Compression Is Useful When It Reduces Load without Excess Loss

**Statement.** Semantic compression is useful when it lowers capacity load without increasing boundary loss beyond tolerance.

**Status.** Operational bridge claim.

**Dependencies.** FDS-M3-001; maintained semantic load model.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Compression always degrades performance or never reduces maintained semantic load under valid mappings.

---

### FDS-M3-004 — Semantic Deficit Produces Degradation

**Statement.** Semantic deficit produces merging, loss, drift, unsupported completion, false compression, or meaning collapse.

**Status.** Failure-mode bridge claim.

**Dependencies.** FDS-M3-001; semantic capacity model.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Semantic overload produces no degradation, merging, proxy substitution, or action-relevance loss.

---

### FDS-M3-005 — Embedding Similarity Is Not Sufficient for FDS-Meaning

**Statement.** Embedding similarity is not sufficient for FDS-meaning unless it preserves downstream policy or verification structure.

**Status.** AI / cognition bridge claim.

**Dependencies.** FDS-M3-001; embedding-policy dissociation test.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Embedding-near items always remain policy-equivalent under audited tasks.

---

### FDS-M3-006 — Shared Meaning Requires Quotient Synchronization

**Statement.** Shared meaning requires synchronized semantic quotients and verification channels across agents.

**Status.** Social bridge claim.

**Dependencies.** FDS-M3-001; semantic synchronization load factor.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Collective meaning persists without shared quotient, external record, translation, verification, or coordination channel.

---

### FDS-M3-007 — Meaning Recovery Requires Quotient Reconstruction

**Statement.** Meaning recovery requires reconstructing lost action-relevant distinctions, not merely increasing information volume.

**Status.** Recovery bridge claim.

**Dependencies.** FDS-M3-004; meaning recovery model.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** Restoring raw information always restores task meaning without quotient reconstruction.

---

### FDS-M3-008 — High-Level Meanings as Invariant Semantic Quotients

**Statement.** High-level meanings are candidate invariant semantic quotients stable across contexts and perturbations.

**Status.** Invariant bridge claim.

**Dependencies.** FDS-M3-001; M2 high-level goals invariant model.

**First timestamp.** FDS-M3 v1.0, 2026-05-18.

**Failure condition.** High-level meanings fail to preserve policy, value, or coordination relevance across any stated context family.

---

## P4 — Coarse-Grained Anti-Recurrence and Informational Hysteresis Claims

### FDS-P4-001 — Non-Injective Truncation Creates Preimage Uncertainty

**Statement.** Non-injective truncation creates preimage uncertainty relative to the effective record.

**Status.** Formal information claim.

**Dependencies.** FDS-CORE-005 (finite projection).

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A many-to-one map contains enough information, without side records or conventions, to distinguish all of its preimages.

---

### FDS-P4-002 — Bayes-Optimal Exact Recovery Bound

**Statement.** Bayes-optimal guaranteed exact preimage recovery is bounded by the largest conditional preimage mass.

**Status.** Decision-theoretic bound.

**Dependencies.** FDS-P4-001; Bayes decision theory.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A decoder using only Z exceeds the Bayes-optimal classifier bound for X|Z.

---

### FDS-P4-003 — Informational Hysteresis

**Statement.** Capacity recovery does not recover distinctions erased during a bottleneck.

**Status.** Informational hysteresis theorem.

**Dependencies.** FDS-P4-001; side-record criterion.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A finite system recovers exact task-relevant preimage distinctions after capacity restoration with no side record, no enlarged boundary, no external trace, and no hidden convention.

---

### FDS-P4-004 — Non-Lumpability Creates Hidden-State Memory

**Statement.** Non-lumpable coarse-graining creates hidden-state memory and effective stochasticity.

**Status.** Markov projection bridge.

**Dependencies.** FDS-P4-001; lumpability condition.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A non-lumpable projection closes exactly on Z_t alone without hidden state, history, or extra variables.

---

### FDS-P4-005 — Mori-Zwanzig Memory Burden

**Statement.** Projection-induced memory burden has a Mori-Zwanzig analogue.

**Status.** Relation to standard theory.

**Dependencies.** FDS-P4-004; Mori-Zwanzig formalism.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** Eliminated variables never reappear as memory, noise, or closure error in projected dynamics, even when lumpability fails.

---

### FDS-P4-006 — Externalization Restores Inverse Information Only by Moving It

**Statement.** Externalization restores inverse information only by moving it to a side ledger.

**Status.** Accounting-boundary bridge.

**Dependencies.** FDS-P4-001; external cost model.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** External logs restore exact recovery at no writing, retention, indexing, synchronization, retrieval, verification, or boundary-expansion cost.

---

### FDS-P4-007 — Finite-Memory Exit Theorem

**Statement.** Sustained truncation requires residual irrecoverability, side records, externalization, task relaxation, or failure.

**Status.** Finite-memory exit theorem.

**Dependencies.** FDS-P4-001; FDS-P4-003.

**First timestamp.** FDS-P4 v1.0, 2026-05-18.

**Failure condition.** A finite system repeatedly applies non-injective truncation to task-relevant distinctions while preserving exact recovery with no residual uncertainty and no extra ledger.

---

## P7 — Topological Obstruction to Forgetting Claims

### FDS-P7-001 — Invariant Side-Ledgers Suppress Residual Uncertainty

**Statement.** Invariant side-ledgers can suppress P4 residual inverse uncertainty.

**Status.** Formal FDS bridge.

**Dependencies.** FDS-P4-001; invariant quotient map.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A task variable factors through an accessible invariant, but H(V|Z,Q_inv) remains high under the stated assumptions.

---

### FDS-P7-002 — Noisy Invariant Recovery Bound

**Statement.** Noisy invariant readout gives a bounded recovery penalty.

**Status.** Information bound.

**Dependencies.** FDS-P7-001; Fano-style bound.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A noisy invariant readout with error probability δ exceeds the Fano-style bound without hidden information or changed task labels.

---

### FDS-P7-003 — Local Perturbations Cannot Change Protected Invariant

**Statement.** Local perturbations cannot change a protected invariant without a protection-breaking event.

**Status.** Topological bridge.

**Dependencies.** FDS-P7-001; local perturbation family; protection margin.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A local perturbation changes the invariant while the protection gap, locality assumptions, and accounting boundary remain intact.

---

### FDS-P7-004 — NHSE as Model Class

**Statement.** NHSE supplies a model class for invariant-supported persistence.

**Status.** Physical bridge.

**Dependencies.** FDS-P7-003; point-gap winding; GBZ structure.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** NHSE is present, but it carries no stable recoverable distinction, no boundary-sensitive protection, and no robustness to local perturbation in the registered model class.

---

### FDS-P7-005 — Protection Relocates Entropy/Resource Accounting

**Statement.** Protection relocates entropy/resource accounting rather than deleting it.

**Status.** O3-compatible accounting claim.

**Dependencies.** FDS-P7-001; O3 ledger principle.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** A protected invariant supplies indefinite maintenance with no drive, boundary, refresh, dissipation, verification, control, or external ledger.

---

### FDS-P7-006 — Dual-Channel Signature

**Statement.** Protected phases can generate a dual forgetting/ledger signature.

**Status.** Experimental bridge.

**Dependencies.** FDS-P7-004; FDS-P7-005; operational forgetting rate.

**First timestamp.** FDS-P7 v1.0, 2026-05-18.

**Failure condition.** Confirmed protection-breaking transition with no feature in operational forgetting and no corresponding resource/entropy signature under a well-powered registered protocol.

---

*End of ledger. New claims added as documents are released or revised.*