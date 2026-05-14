# Dependency Map

DT/FDS claims form a directed dependency graph. Downstream claims depend on upstream claims without the reverse holding.

## Dependency Direction

```
formal core (FDS-0)
  ├── capacity deficit (CC-1)
  │     ├── physical bridge claims (PB-L, O1, O2)
  │     ├── AI agency criteria (A1, A1-D)
  │     └── domain bridges (L1, L1-D)
  ├── high-risk physical bridges (P3, X1)
  └── downstream applications
```

## Rules

1. Failure of a downstream claim does not automatically falsify upstream claims.
2. Failure of an upstream claim requires revision or demotion of all dependent downstream claims.
3. High-risk claims (P3, X1) are quarantined: their failure does not propagate to the formal core.

## File References

- Full claim table: `CLAIM_STATUS.md`
- Full failure table: `FAILURE_REGISTRY.md`
- CSV versions: `claim_status.csv`, `failure_registry.csv`
