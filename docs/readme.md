# Anthropic Claude Enterprise Add-on for Splunk

The Anthropic Claude Enterprise Add-on ingests audit, usage, cost, and
spend-limit data from an Anthropic Claude Enterprise organization into
Splunk, and ships dashboards for **security auditing**, **governance**, and
**usage & spend analytics (tokenomics)**.

It is a UCC-based (Splunk Add-on UCC Framework 6.5) modular-input add-on
written in Python 3, using Splunk KV Store for checkpointing (search-head
cluster safe) and Splunk's encrypted credential store for API keys.


## Features

- Data collection from an Anthropic Claude Enterprise organization through 14 [sourcetypes](#sourcetypes) and 4 [inputs](#usage), *Compliance Activity Feed*, *Compliance Directory Sync*, *Analytics Reports* and *Compliance Content Export*.

- Set of dashboards to easily visualize and get clear insights on collected data:
  - **Security Audit** — access failures (e.g. `claude_chat_access_failed`),
  admin/org changes (API keys, roles, spend limits, integrations), data
  exports, file activity, artifact publishing/sharing exposure, user
  activity by IP with multi-IP anomaly detection, and auditing of who reads
  your compliance data via the API.
  - **Governance** — directory users/groups roster, invitations,
  project/conversation/artifact activity, agent lifecycle. Panels that
  depend on optional inputs hide themselves until data exists.
  - **Usage & Spend Analytics** — DAU/WAU/stickiness, adoption
  rate, token mix (output / uncached input / cache read / cache creation),
  prompt-cache hit rate, blended cost per 1M tokens, spend by product and
  model, top users by cost/tokens, spend-vs-limit utilization, pending
  limit requests, Claude Code tool acceptance, and connector usage.

- **CIM normalization** — the activity feed maps to the **Authentication** and
  **Change** data models (`user`, `src`, `action`, `object`, `change_type`,
  `vendor_product`, ...), with tagged eventtypes for both.

:point_right: Basically the add-on:
- polls Anthropic's enterprise APIs on a schedule you choose,
- indexes the results as JSON events under `anthropic:compliance:*` and `anthropic:analytics:*` sourcetypes, and
- visualizes them in three dashboards plus the UCC monitoring dashboard.

### Sourcetypes

| Sourcetype | Description |
|---|---|
| `anthropic:compliance:activity` | Audit/activity feed events |
| `anthropic:compliance:user` | Directory user snapshots |
| `anthropic:compliance:organization` | Directory organization snapshots |
| `anthropic:compliance:group` | Directory group/workspace snapshots |
| `anthropic:compliance:chat_content` | On-demand chat content export |
| `anthropic:compliance:file_metadata` | On-demand file metadata export |
| `anthropic:analytics:summary` | Daily adoption summaries |
| `anthropic:analytics:usage` | Token usage by product/model |
| `anthropic:analytics:cost` | Cost by product/model |
| `anthropic:analytics:user_usage` | Per-user token usage |
| `anthropic:analytics:user_cost` | Per-user cost |
| `anthropic:analytics:user_activity` | Per-user product activity metrics |
| `anthropic:analytics:spend_limit` | Effective spend-limit snapshots |
| `anthropic:analytics:spend_limit_request` | Spend-limit increase requests |

### API Endpoints

Data sources polled from `https://api.anthropic.com`:

| API | Data |
|---|---|
| Compliance API | Activity (audit) feed, directory (users, organizations, groups), on-demand chat/file content export |
| Enterprise Analytics API | Adoption summaries, token usage report, cost report, per-user usage/cost, per-user activity metrics |
| Admin API | Effective spend limits, pending spend-limit increase requests; directory fallback (users, organization, workspaces) |

## Getting Started
### Requirements

- **Splunk** Enterprise 9.x/10.x or Splunk Cloud Platform.
- **A Claude Enterprise organization.**
- **An enterprise API key** created by a Claude Enterprise **admin** in the
  Anthropic Console. Scopes are selected at key creation; grant the ones
  for the inputs you plan to use:

  | Scope | Used by |
  |---|---|
  | `read:compliance_activities` | Compliance Activity Feed input |
  | `read:compliance_user_data`, `read:compliance_org_data` | Compliance Directory Sync, Content Export inputs |
  | `read:analytics` | Analytics Reports input |
  | `read:spend_limits` | Spend-limit panels and reports |
  | `read:members`, `read:rbac_groups` | Admin API directory fallback |

  A single key carrying all read scopes is the simplest setup: enter it as
  the **Compliance API key** and leave the Analytics key field blank (the
  compliance key is reused automatically). Separate keys per concern also
  work.
- **Outbound HTTPS** from the collection tier to `https://api.anthropic.com`
  (directly or via the optional per-account HTTPS proxy).

### Installation

Download the [latest release](https://github.com/splunk-platform-apps/anthropic_compliance_app_for_splunk/releases) package and install it via
**Apps → Manage Apps → Install app from file** (Splunk Enterprise), the
self-service app install flow (Splunk Cloud), or
[ACS](https://docs.splunk.com/Documentation/SplunkCloud/latest/Config/ManageApps).

Where to install:

| Tier | Install? | Why |
|---|---|---|
| Search head | Yes | Dashboards, macros, props (search-time), saved searches |
| Indexers | Optional | Index-time settings are minimal (line breaking, timestamps); needed only if events arrive uncooked |
| Universal forwarder | No | Not applicable |

On a single instance, one installation does everything.

### Configuration

1. **(Recommended) Create a dedicated index on the SH** to collect your events, e.g. `claude`.
2. **Add the account, only admins can perform this task as they will have access to the Compliance API key** — open the add-on, go to
   **Configuration → Account → Add**, name it (e.g. `claude`), and paste
   your API key(s). Keys are stored encrypted and never logged.

   An optional HTTPS proxy URL can be set per account.

3. **Create inputs** under **Inputs → Create New Input**:

   | Input | What it collects | Suggested interval |
   |---|---|---|
   | Compliance Activity Feed | The audit trail: chats, files, artifacts, invites, admin changes, access failures | 300–3600 s |
   | Compliance Directory Sync | Users, organization, groups snapshots. Tries the Compliance directory API, then falls back to the Admin API (`read:members`) automatically | 43200–86400 s |
   | Analytics Reports | Adoption summaries, usage/cost by product & model, per-user usage/cost/activity, spend limits | 86400 s |
   | Compliance Content Export | On-demand chat/file content for eDiscovery-style workflows (see [Privacy](#privacy--data-handling) below) | on demand |

   Set the **Index** on each input to your dedicated index.

4. **Scope the search macro** — if you used a dedicated index, change the
   `claude_index` macro from the default `index=*` to e.g. `index=claude`
   via **Settings → Advanced search → Search macros**. Every dashboard and
   saved search reads through this macro.

### Usage

- **Claude Enterprise – Security Audit** — start here for SOC work. The
  top row counts access failures, admin/org changes, data exports, file
  uploads, and compliance-API reads for the selected window; tables below
  break down user activity by IP (with a multi-IP anomaly view), admin and
  change events, access-failure detail, file activity, and artifact
  publishing/sharing exposure.
- **Claude Enterprise – Governance** — user/group roster (directory sync
  with activity-feed fallback), invitations, project/chat/artifact
  activity, and agent lifecycle.
- **Claude Enterprise – Usage & Spend Analytics** — adoption, tokenomics,
  and billing. Note: Anthropic finalizes analytics with a **~3-day lag**,
  so the newest data point is about three days old — use *Last 7/30 days*
  ranges on this dashboard. A built-in banner explains setup and lag
  whenever the selected range has no analytics data.
- **Monitoring Dashboard** — UCC-generated add-on health: errors, resource
  usage, and event volume per input.

All dashboards default to **Last 24 hours** and include a **user filter**.

Money semantics: Anthropic API amounts are cents expressed as decimal
strings; the add-on converts them to USD (÷100) at collection time and the
dashboards recompute from the raw cents fields at search time, so values
match the Anthropic console.

## Troubleshooting

- **Add-on logs**:
  `index=_internal source=*anthropic_claude* (ERROR OR WARNING)`

- **Analytics panels empty** — in order: (1) widen the time range —
  analytics data is finalized with a ~3-day lag, so *Last 24 hours* is
  often legitimately empty; (2) confirm an **Analytics Reports** input
  exists and is enabled (`| rest /services/data/inputs/analytics_reports`);
  (3) confirm the key has `read:analytics`; (4) confirm the
  `claude_index` macro matches the index the input writes to.

- **401/403 errors** — the key in use is missing a scope or was pasted
  incorrectly. Note the Analytics key field *overrides* the compliance key
  when set; clear it if it holds an old key. The analytics client tries
  both `x-api-key` and bearer authentication before giving up, and the
  error message names the missing scope.

- **Directory panels hidden** — the Governance roster panels appear only
  after the Compliance Directory Sync input has ingested data. A built-in
  hint panel explains this in place.

- **Force an immediate collection** — disable and re-enable the input on
  the Inputs page.

- **Checkpoints** live in the KV Store collection
  `ta_anthropic_claude_enterprise_checkpoints`. To re-backfill a report
  window, create a new input under a different name (fresh checkpoint).

## Privacy & Data Handling

The **Compliance Content Export** input can collect end-user conversation
content. Enable it only if your organization's policy allows, and restrict
access to the target index with role-based access controls. API keys are
stored encrypted in Splunk's credential store and are never written to
logs.

## Versions Supported

Tested against Splunk Enterprise 9.3 and 10.0 (automated install tests),
with AppInspect passing on the `cloud`, `private_victoria`, and
`private_classic` tag sets.

## References

- [Anthropic Console](https://console.anthropic.com/) — create enterprise API keys
- [Anthropic API documentation](https://docs.anthropic.com/)
- [Splunk Add-on UCC Framework](https://splunk.github.io/addonfactory-ucc-generator/)
- [Splunk Common Information Model](https://docs.splunk.com/Documentation/CIM/latest/User/Overview)

## Contributing

See the [CONTRIBUTING.md](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md) file for details.
