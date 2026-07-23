Anthropic Claude Enterprise Add-on for Splunk
==============================================

Version: 1.2.2
Author: Manan Grover
License: Apache-2.0

OVERVIEW
--------
This add-on ingests audit, usage, cost, and spend-limit data from Anthropic
Claude Enterprise into Splunk and ships dashboards for security auditing,
governance, and usage/spend analytics (tokenomics).

Data sources:
* Anthropic Compliance API - activity (audit) feed, directory (users,
  organizations, groups), and on-demand chat/file content export.
* Anthropic Enterprise Analytics API - adoption summaries, usage report
  (tokens by product/model), cost report, per-user usage/cost, and
  per-user activity metrics.
* Anthropic Admin API - effective spend limits and pending spend-limit
  increase requests.

PREREQUISITES
-------------
* Splunk Enterprise 9.x/10.x or Splunk Cloud Platform.
* A Claude Enterprise organization.
* An enterprise API key created by a Claude Enterprise admin. Scopes are
  selected when the key is created; grant the ones for the inputs you use:
  - read:compliance_activities            Compliance Activity Feed input
  - read:compliance_user_data,
    read:compliance_org_data              Compliance Directory Sync and
                                          Content Export inputs
  - read:analytics                        Analytics Reports input
  - read:spend_limits                     spend-limit panels/reports
  - read:members, read:rbac_groups        Admin API directory fallback
  A single key with all read scopes can be entered as the Compliance key;
  the Analytics key field may then stay blank (the compliance key is
  reused). Separate keys per concern also work.
* Outbound HTTPS access from the collection node to https://api.anthropic.com
  (directly or through the optional proxy configured on the account).

INSTALLATION
------------
Single instance: install the add-on on that instance.
Distributed: install on a heavy forwarder or IDM/inputs node (data
collection), and on search heads (dashboards, props, macros). Do not enable
inputs on search heads. Index-time settings in this add-on are minimal
(line breaking and timestamps); installing on indexers is recommended when
events are forwarded uncooked, otherwise install where parsing occurs.

CONFIGURATION
-------------
1. Optional but recommended: create a dedicated index (for example
   claude_compliance).
2. Open the add-on, go to Configuration > Account, and add an account with
   your Compliance and/or Analytics API keys. Keys are stored encrypted in
   Splunk's credential store. An optional HTTPS proxy URL can be set per
   account.
3. Go to Inputs and create the inputs you need:
   * Compliance Activity Feed - the audit trail (sign-ins, admin/SSO
     changes, data exports, file uploads, project/conversation events).
     Suggested interval: 300-3600 seconds.
   * Compliance Directory Sync - users, organizations, groups snapshots.
     Tries the Compliance directory API first and automatically falls back
     to the Anthropic Admin API (users, organization, workspaces) when the
     key cannot access the directory endpoints; requires read:members (or
     the compliance directory read scopes) on the key.
     Suggested interval: 43200-86400 seconds.
   * Analytics Reports - adoption, usage, cost, per-user reports, and
     spend limits. Suggested interval: 86400 seconds (data is finalized
     with about a 3-day lag; the input tracks this automatically).
   * Compliance Content Export - on-demand chat/file content collection
     for eDiscovery-style workflows.
4. If you send data to a dedicated index, scope the `claude_index` search
   macro (Settings > Advanced search > Search macros) from the default
   index=* to your index, e.g. index=claude_compliance. All dashboards and
   saved searches use this macro.

SOURCETYPES
-----------
anthropic:compliance:activity            Audit/activity feed events
anthropic:compliance:user                Directory user snapshots
anthropic:compliance:organization        Directory organization snapshots
anthropic:compliance:group               Directory group snapshots
anthropic:compliance:chat_content        On-demand chat content export
anthropic:compliance:file_metadata       On-demand file metadata export
anthropic:analytics:summary              Daily adoption summaries
anthropic:analytics:usage                Token usage by product/model
anthropic:analytics:cost                 Cost by product/model
anthropic:analytics:user_usage           Per-user token usage
anthropic:analytics:user_cost            Per-user cost
anthropic:analytics:user_activity        Per-user product activity metrics
anthropic:analytics:spend_limit          Effective spend-limit snapshots
anthropic:analytics:spend_limit_request  Spend-limit increase requests

CIM COMPLIANCE
--------------
anthropic:compliance:activity is normalized for the Authentication and
Change data models (user, src, src_user, action, app, vendor_product,
object, object_category, change_type, status, authentication_method).
Eventtypes anthropic_claude_auth_events and anthropic_claude_change_events
are tagged authentication/change/audit accordingly.

DASHBOARDS
----------
* Usage & Spend Analytics - active users, adoption, token mix and cache
  hit rate (tokenomics), spend by product/model, blended cost per 1M
  tokens, top users, spend-limit utilization, pending limit requests,
  Claude Code tool acceptance, connector usage.
* Security Audit - access failures, admin and org changes (API keys,
  roles, spend limits, integrations), data exports, file activity,
  artifact publishing/sharing exposure, user activity by IP with
  multi-IP anomalies, and compliance-API access auditing.
* Governance - directory users/groups, invitations, project and
  conversation activity, agent lifecycle events.
* Monitoring Dashboard (UCC) - add-on internal health, errors, and
  ingestion volume.

SAVED SEARCHES
--------------
Six saved searches ship disabled and unscheduled (multi-IP user activity,
access failures, SSO configuration change, data export started, top cost
users, users near spend limit). Review, adjust thresholds, then enable
and schedule.

TROUBLESHOOTING
---------------
* Add-on logs: index=_internal source=*anthropic_claude*
* Blank analytics panels: the Analytics API finalizes data with about a
  3-day lag; make sure the Analytics Reports input has run and that the
  claude_index macro matches your index.
* 401/403 errors: the API key is missing a required scope (see
  PREREQUISITES), or the Compliance API is not enabled for your
  organization. The analytics client tries both x-api-key and bearer
  authentication before giving up.
* Checkpoints are stored in the KV Store collection
  ta_anthropic_claude_enterprise_checkpoints (search-head-cluster safe).

PRIVACY AND DATA HANDLING
-------------------------
The Compliance Content Export input can collect end-user conversation
content. Only enable it if your organization's policy allows it, and
restrict access to the target index appropriately. API keys are stored
encrypted and are never written to logs.

RELEASE NOTES
-------------
1.2.2
* Lint-clean Python across bin/ (ruff, trailing whitespace) with the
  import_declare_test sys.path bootstraps preserved.
* Corrected internal log source references in documentation and
  dashboard setup hints.
* Packaging hygiene release for Splunkbase / splunk-platform-apps CI.

1.2.1
* Analytics API client authenticates with x-api-key first (matching
  unified scope-based enterprise keys) and retries with bearer auth,
  fixing 401s when a single all-scope key is used for analytics.
* Clear, actionable error message when the key lacks read:analytics.
* Documentation updated for scope-based enterprise API keys.

1.2.0
* All dashboards default to Last 24 hours and include a user filter.
* Security Audit rebuilt around the real Compliance API event taxonomy
  (claude_* events): access failures, admin/org changes, file activity,
  artifact publishing/sharing exposure, user activity by IP, and
  compliance-API access auditing; API polling noise separated out.
* Analytics dashboard shows a setup/lag notice when the selected range
  has no analytics data; directory and agent panels hide automatically
  when their data sources are absent.
* Directory sync falls back to the Anthropic Admin API (users,
  organization, workspaces) when the Compliance directory endpoints are
  unavailable to the configured key.
* JSON null values are no longer indexed as literal "null" strings.
* Claude starburst app icons.

1.1.0
* Removed bundled grpc/protobuf/opentelemetry libraries (including
  platform-specific binaries) for Splunk Cloud vetting compliance.
* Fixed per-user activity collection (argument mismatch caused the
  collection to fail on every run).
* Rewrote props.conf with valid parsing settings and CIM Authentication/
  Change normalization.
* Reworked dashboards: added tokenomics (token mix, cache hit rate, cost
  per 1M tokens), removed duplicate and permanently-blank panels, and
  standardized on the claude_index macro.
* Saved searches now aggregate correctly and use valid scheduling
  attributes.

SUPPORT
-------
Community-supported. Contact: mgrover@splunk.com
