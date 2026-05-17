## O3 — Boundary-Maintenance Second-Law Channel Claims

### FDS-O3-001 — Finite Memory Creates Record-Reuse Pressure

**Statement.** Finite memory creates record-reuse pressure under sustained update unless history is externalized, compressed, uncomputed, abandoned, or resources expand.

**Status.** Operational theorem.

**Dependencies.** FDS-CORE-003 (finite capacity); FDS-O2-001 (register time).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** A bounded-memory system maintains unbounded usable update history internally without record reuse, external memory, compression, task relaxation, or failure.

---

### FDS-O3-002 — Non-Injective Record Reuse Creates Residual Irreversibility

**Statement.** Non-injective record reuse creates residual irreversibility relative to an accounting boundary.

**Status.** Formal information claim.

**Dependencies.** FDS-O3-001; FDS-O1-001 (finite record formation).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** A many-to-one update preserves full preimage information without side records or an enlarged boundary.

---

### FDS-O3-003 — Physical Irreversible Record Reuse Enters an Entropy Ledger

**Statement.** Physical irreversible record reuse enters an entropy/resource ledger under bridge assumptions.

**Status.** Physical bridge claim.

**Dependencies.** FDS-O3-002; FDS-P1-003 (Landauer bridge).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** Reliable physical erasure or overwrite violates Landauer-style accounting under the stated assumptions.

---

### FDS-O3-004 — Stable Finite Records Require Housekeeping Beyond Logical Erasure

**Statement.** Stable finite records require housekeeping (refresh, retention, clocking, synchronization, carrier repair, verification) beyond logical erasure.

**Status.** Accounting claim.

**Dependencies.** FDS-O3-003; FDS-P2-002 (garbage entropy rate).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** Refresh, retention, clocking, synchronization, carrier repair, and verification are cost-free in every controlled finite-record implementation.

---

### FDS-O3-005 — Externalization Shifts the Operational Second-Law Channel

**Statement.** Externalization shifts the operational Second-Law channel across accounting boundaries rather than eliminating it.

**Status.** Accounting bridge claim.

**Dependencies.** FDS-O3-003; FDS-P1-002 (accounting boundary).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** External records impose no write, verification, retrieval, latency, maintenance, or environmental cost.

---

### FDS-O3-006 — Pruning and Invariant Compression Reduce Future Entropy Pressure

**Statement.** Pruning and invariant compression can reduce future entropy pressure when task identity is preserved.

**Status.** Conditional bridge claim.

**Dependencies.** FDS-O3-004; FDS-T3-004 (Phase-B invariants).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** No task-preserving quotient, pruning, or compression ever reduces future record-maintenance cost.

---

### FDS-O3-007 — Sustained Record Turnover, Fixed Tolerance, Zero Cost Cannot Persist

**Statement.** Sustained residual record turnover, fixed boundary tolerance, and zero coupled entropy/resource cost cannot persist indefinitely.

**Status.** O3 theorem claim.

**Dependencies.** FDS-O3-001—006.

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** A finite active-boundary system maintains sustained residual record turnover at fixed tolerance with no ledger cost and no exit channel.

---

### FDS-O3-008 — Topological Persistence Redirects Entropy Accounting

**Statement.** Topological or invariant persistence, if present, redirects entropy accounting rather than violating the Second Law.

**Status.** Quarantined projection claim.

**Dependencies.** FDS-O3-003; FDS-CORE-006 (invariant-supported persistence).

**First timestamp.** FDS-O3 v1.0, 2026-05-17.

**Failure condition.** A protected invariant supplies perpetual work or global entropy-law violation rather than bounded persistence or entropy relocation.

---

*End of ledger. New claims added as documents are released or revised.*