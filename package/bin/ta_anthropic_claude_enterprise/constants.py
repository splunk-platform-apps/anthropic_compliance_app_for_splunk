"""Sourcetype constants for indexed events."""

SOURCETYPE_COMPLIANCE_ACTIVITY = "anthropic:compliance:activity"
SOURCETYPE_COMPLIANCE_USER = "anthropic:compliance:user"
SOURCETYPE_COMPLIANCE_ORGANIZATION = "anthropic:compliance:organization"
SOURCETYPE_COMPLIANCE_GROUP = "anthropic:compliance:group"
SOURCETYPE_COMPLIANCE_CHAT_CONTENT = "anthropic:compliance:chat_content"
SOURCETYPE_COMPLIANCE_FILE_METADATA = "anthropic:compliance:file_metadata"
SOURCETYPE_ANALYTICS_SUMMARY = "anthropic:analytics:summary"
SOURCETYPE_ANALYTICS_USAGE = "anthropic:analytics:usage"
SOURCETYPE_ANALYTICS_COST = "anthropic:analytics:cost"
SOURCETYPE_ANALYTICS_USER_USAGE = "anthropic:analytics:user_usage"
SOURCETYPE_ANALYTICS_USER_COST = "anthropic:analytics:user_cost"
SOURCETYPE_ANALYTICS_USER_ACTIVITY = "anthropic:analytics:user_activity"
SOURCETYPE_ANALYTICS_SPEND_LIMIT = "anthropic:analytics:spend_limit"
SOURCETYPE_ANALYTICS_SPEND_LIMIT_REQUEST = "anthropic:analytics:spend_limit_request"

AUTH_EVENT_TYPES = frozenset(
    {
        "user_signed_in_sso",
        "user_signed_in_google",
        "user_signed_in_apple",
        "user_signed_out",
        "user_signed_in_magic_link",
        "user_signed_in_phone_code",
        "claude_chat_created",
        "conversation_created",
    }
)

CHANGE_EVENT_TYPES = frozenset(
    {
        "org_sso_toggled",
        "org_sso_add_initiated",
        "org_sso_connection_activated",
        "org_sso_connection_deactivated",
        "org_sso_connection_deleted",
        "org_jit_toggled",
        "org_domain_add_initiated",
        "org_domain_verified",
        "org_data_export_started",
        "org_data_export_completed",
        "project_created",
        "project_deleted",
        "project_renamed",
        "project_visibility_changed",
        "project_document_created",
        "project_document_deleted",
        "org_user_invite_sent",
        "org_user_invite_accepted",
        "org_user_invite_rejected",
        "org_user_invite_deleted",
        "org_user_invite_re_sent",
        "org_user_deleted",
        "user_name_changed",
        "conversation_renamed",
        "conversation_deleted",
    }
)
