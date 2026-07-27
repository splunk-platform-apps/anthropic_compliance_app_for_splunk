## [1.2.4] - 2026-07-24

### Fixed
- Money correctness: Anthropic API amounts are cents as decimal strings and
  are now always divided by 100; the previous heuristic inflated USD 100x.
- Usage/cost report buckets wrapping rows in a results[] array are flattened
  into one event per row, making product/model/amount flat fields.
- group_by is now sent using the API's array-parameter convention
  (group_by[]), so product and model dimensions populate; 400 responses
  fall back to ungrouped collection.
- Analytics client authenticates with x-api-key first (scope-based
  enterprise keys) with bearer fallback.
- Directory sync falls back to the Admin API (users, organization,
  workspaces) when Compliance directory endpoints are unavailable.
- Dashboards recompute USD from raw cents fields at search time, correcting
  previously indexed values; spend-limit, top-user, and tokenomics panels
  verified against production data.

### Changed
- All dashboards default to Last 24 hours and include a user filter.
- Security Audit rebuilt around the real Compliance API event taxonomy
  (access failures, admin/org changes, artifact exposure, compliance-API
  access auditing).

## [1.2.1] - 2026-07-23

### Changed
- Updated app package to address automated quality check findings