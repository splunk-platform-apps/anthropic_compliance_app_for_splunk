# Anthropic Claude Enterprise Add-on for Splunk

Ingest audit, usage, cost, and spend-limit data from an Anthropic Claude
Enterprise organization into Splunk — with dashboards for **security
auditing**, **governance**, and **usage & spend analytics (tokenomics)**,
CIM-normalized events, and ready-made detections.

| | |
|---|---|
| Security Audit | Access failures, admin/org changes (API keys, roles, spend limits, integrations), data exports, file & artifact exposure, user activity by IP with multi-IP anomalies, compliance-API access auditing |
| Governance | Directory users/groups roster, invitations, project/chat/artifact activity, agent lifecycle |
| Usage & Spend | DAU/WAU/adoption, token mix & cache hit rate, blended cost per 1M tokens, spend by product/model, top users, spend-vs-limit utilization |

Data is collected from Anthropic's **Compliance API** (audit feed,
directory, content export), **Enterprise Analytics API** (usage, cost,
per-user reports), and **Admin API** (spend limits, directory fallback)
using scoped enterprise API keys stored encrypted in Splunk.

## Getting Started

To install and run this app, download the latest compiled application directly from the releases page.

:package: [Download the latest release here](https://github.com/splunk-platform-apps/anthropic_compliance_app_for_splunk/releases)

Once downloaded, installation instructions can be found in the provided [documentation](https://splunk-platform-apps.github.io/anthropic_compliance_app_for_splunk/)

Quick start:

1. Create an enterprise API key in the [Anthropic Console](https://console.anthropic.com/) with the read scopes you need (`read:compliance_activities`, `read:analytics`, `read:spend_limits`, `read:members`, ...).
2. Install the add-on, add the key under **Configuration → Account**.
3. Create the **Compliance Activity Feed**, **Compliance Directory Sync**, and **Analytics Reports** inputs, pointing at your Claude index.
4. Scope the `claude_index` search macro to that index. Done — dashboards populate as data arrives (analytics has a ~3-day finalization lag).

## Useful Links

:books: [Documentation](https://splunk-platform-apps.github.io/anthropic_compliance_app_for_splunk/)<br/>
:writing_hand: [Release Notes](./CHANGELOG.md)<br/>
:balance_scale: [License](./LICENSE)

:gear: [Development Guidelines](https://github.com/splunk-platform-apps/.github/blob/main/documentation/DEV_GUIDELINES.md#getting-started)<br/>
:heart_on_fire: [Contributing Guidelines](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md)
