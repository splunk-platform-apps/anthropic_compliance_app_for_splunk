# Anthropic Claude Enterprise Add-on for Splunk

Ingest audit, usage, cost, and spend-limit data from an Anthropic Claude
Enterprise organization into Splunk — with dashboards for **security
auditing**, **governance**, and **usage & spend analytics (tokenomics)**,
CIM-normalized events, and ready-made detections.

| Dashboard | Content Details |
|---|---|
| Security Audit | Access failures, admin/org changes (API keys, roles, spend limits, integrations), data exports, file & artifact exposure, user activity by IP with multi-IP anomalies, compliance-API access auditing |
| Governance | Directory users/groups roster, invitations, project/chat/artifact activity, agent lifecycle |
| Usage & Spend | DAU/WAU/adoption, token mix & cache hit rate, blended cost per 1M tokens, spend by product/model, top users, spend-vs-limit utilization |

Data is collected from Anthropic's **Compliance API** (audit feed,
directory, content export), **Enterprise Analytics API** (usage, cost,
per-user reports), and **Admin API** (spend limits, directory fallback)
using scoped enterprise API keys stored encrypted in Splunk.

:bookmark: Discover more on monitoring and governing enterprise AI platform in our [new blog post](https://lantern.splunk.com/Security_Use_Cases/Compliance/Monitoring_and_governing_enterprise_AI_platforms#) on Splunk Lantern.

## Getting Started

To install and run this app, download the latest compiled application directly from the releases page.

:package: [Download the latest release here](https://github.com/splunk-platform-apps/anthropic_compliance_app_for_splunk/releases)

Once downloaded, installation instructions can be found in the provided [documentation](https://splunk-platform-apps.github.io/anthropic_compliance_app_for_splunk/)

## Useful Links

:books: [Documentation](https://splunk-platform-apps.github.io/anthropic_compliance_app_for_splunk/)<br/>
:writing_hand: [Release Notes](./CHANGELOG.md)<br/>
:balance_scale: [License](./LICENSE)

:gear: [Development Guidelines](https://github.com/splunk-platform-apps/.github/blob/main/documentation/DEV_GUIDELINES.md#getting-started)<br/>
:heart_on_fire: [Contributing Guidelines](https://github.com/splunk-platform-apps/.github/blob/main/.github/CONTRIBUTING.md)
