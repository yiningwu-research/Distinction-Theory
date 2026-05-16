# DT/FDS Claim Schema

Each claim in `claims.csv` and `claims.yaml` follows this schema:

| Field | Type | Description |
|---|---|---|
| claim_id | string | Unique claim identifier (e.g., FDS-T1-001). |
| title | string | Short claim title. |
| statement | text | Exact claim statement. |
| status | string | Formal definition / Conditional theorem / Physical bridge / Testable prediction / Registry governance / High-risk bridge / Frozen line. |
| layer | string | Core, Physical Bridge, Operational, Domain Bridge, High-Risk, Frozen. |
| dependencies | list | Claim IDs or external assumptions this depends on. |
| not_claimed | list | What this claim does NOT assert. |
| first_document | string | Source document code (e.g., FDS-T1). |
| first_version | string | Document version at first claim appearance. |
| first_date | string | ISO date of first claim appearance. |
| doi | string or null | DOI of source document. |
| github_tag | string or null | Git tag for this version. |
| commit_hash | string or null | Commit hash for this version. |
| website_url | string or null | Website page URL. |
| failure_condition | text | What would falsify or demote this claim. |
| downstream_claims | list | Claim IDs that depend on this one. |
