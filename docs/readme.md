# Anthropic Claude Enterprise App for Splunk

The Anthropic Claude Enterprise App for Splunk provides dashboards for **security auditing**, **governance**, and **usage & spend analytics (tokenomics)**, enabling organizations to monitor and govern their Anthropic Claude Enterprise platform effectively.

## Features

**Set of Dashboards** to easily visualize and gain insights into your Anthropic Claude Enterprise data:
- **Security Audit** — Access failures (e.g., `claude_chat_access_failed`), admin/org changes (API keys, roles, spend limits, integrations), data exports, file activity, artifact publishing/sharing exposure, user activity by IP with multi-IP anomaly detection, and auditing of who reads your compliance data via the API.
- **Governance** — Directory users/groups roster, invitations, project/conversation/artifact activity, agent lifecycle. Panels that depend on optional inputs hide themselves until data exists.
- **Usage & Spend Analytics** — DAU/WAU/stickiness, adoption rate, token mix (output / uncached input / cache read / cache creation), prompt-cache hit rate, blended cost per 1M tokens, spend by product and model, top users by cost/tokens, spend-vs-limit utilization, pending limit requests, Claude Code tool acceptance, and connector usage.

## Getting Started

### Requirements

- **Splunk** Enterprise or Splunk Cloud Platform 9.x/10.x,
- **Anthropic Claude Enterprise Add-on for Splunk**:
   - The Anthropic Claude Enterprise App for Splunk expects data to be retrieved from the Anthropic Claude Enterprise APIs using the **Anthropic Claude Enterprise Add-on for Splunk**.
   - Ensure such add-on is installed and configured to collect the required data as per [documentation](https://github.com/splunk-platform-apps/anthropic_claude_enterprise_add-on_for_splunk).

### Installation

Download the [latest release](https://github.com/splunk-platform-apps/anthropic_compliance_app_for_splunk/releases) package and install it via
**Apps → Manage Apps → Install app from file** (Splunk Enterprise), the
self-service app install flow (Splunk Cloud), or
[ACS](https://docs.splunk.com/Documentation/SplunkCloud/latest/Config/ManageApps).

Where to install:

| Tier | Install? | Why |
|---|---|---|
| Search head | Yes | Dashboards, macros, props (search-time), saved searches |
| Heavy forwarder / IDM | No | Not applicable (data collection is handled by the add-on) |
| Indexers | No | Not applicable |
| Universal forwarder | No | Not applicable |

### Configuration

Splunk Admins are requested to:
- Create a dedicated index on the Search head to collect your events, if not done yet (e.g. `claude`).
  - **Scope the search macro in the Search Head** — Update the `claude_index` macro to point to the appropriate index where the data is stored. This can be done via **Settings → Advanced search → Search macros**. Every dashboard and saved search reads through this macro.

### Usage

Open the app to visualize data on the following dashboards:

- **Security Audit** — Start here for SOC work. The top row counts access failures, admin/org changes, data exports, file uploads, and compliance-API reads for the selected window. Tables below break down user activity by IP (with a multi-IP anomaly view), admin and change events, access-failure detail, file activity, and artifact publishing/sharing exposure.
- **Governance** — User/group roster (directory sync with activity-feed fallback), invitations, project/chat/artifact activity, and agent lifecycle.
- **Usage & Spend Analytics** — Adoption, tokenomics, and billing. Note: Anthropic finalizes analytics with a **~3-day lag**, so the newest data point is about three days old — use *Last 7/30 days* ranges on this dashboard. A built-in banner explains setup and lag whenever the selected range has no analytics data.

The **Monitoring Dashboard** displays data about the add-on health: errors, resource usage, and event volume per input.

All dashboards default to **Last 24 hours** and include a **user filter**.

> [!IMPORTANT]
> **Money semantics**
>
> Anthropic API amounts are cents expressed as decimal strings; the add-on converts them to USD (÷100) at collection time and the dashboards recompute from the raw cents fields at search time, so values match the Anthropic console.

## Troubleshooting

- **Analytics panels empty** — in order: (1) widen the time range —
  analytics data is finalized with a ~3-day lag, so *Last 24 hours* is
  often legitimately empty; (2) confirm an **Analytics Reports** input
  exists and is enabled (`| rest /services/data/inputs/analytics_reports`);
  (3) confirm the key has `read:analytics`; (4) confirm the
  `claude_index` macro matches the index the input writes to.

- **Directory panels hidden** — the Governance roster panels appear only
  after the Compliance Directory Sync input has ingested data. A built-in
  hint panel explains this in place.

## Versions Supported

Tested against Splunk Enterprise 9.3 and 10.0 (automated install tests).

## Contributing

See the [CONTRIBUTING.md](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md) file for details.
