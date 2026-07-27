"""Event normalization for Splunk indexing."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ta_anthropic_claude_enterprise.constants import AUTH_EVENT_TYPES, CHANGE_EVENT_TYPES


def normalize_activity(activity: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten Compliance Activity feed records for Splunk search."""
    actor = activity.get("actor") or {}
    if not isinstance(actor, dict):
        actor = {}
    event_type = activity.get("type") or activity.get("event")
    actor_email = _extract_email(actor)
    normalized = {
        "activity_id": activity.get("id"),
        "created_at": activity.get("created_at"),
        "event_type": event_type,
        "type": event_type,
        "organization_id": activity.get("organization_id"),
        "organization_uuid": activity.get("organization_uuid"),
        "actor_type": actor.get("type"),
        "actor_user_id": actor.get("user_id"),
        "actor_email": actor_email,
        "actor_ip_address": actor.get("ip_address"),
        "actor_user_agent": actor.get("user_agent"),
        "claude_chat_id": activity.get("claude_chat_id"),
        "claude_project_id": activity.get("claude_project_id"),
        "file_id": activity.get("file_id"),
        "is_authentication_event": event_type in AUTH_EVENT_TYPES,
        "is_change_event": event_type in CHANGE_EVENT_TYPES,
        "vendor": "anthropic",
        "product": "claude_enterprise",
        "source_type_category": "compliance_activity",
    }
    if actor.get("type") == "api_actor" and actor.get("api_key_id"):
        normalized["actor_api_key_id"] = actor.get("api_key_id")
    event_info = activity.get("event_info") or activity.get("eventInfo")
    if event_info:
        normalized["event_info"] = event_info
    entity_info = activity.get("entity_info") or activity.get("entityInfo")
    if entity_info:
        normalized["entity_info"] = entity_info
        entity_email = _extract_email(entity_info) if isinstance(entity_info, dict) else None
        if entity_email:
            normalized["entity_email"] = entity_email
            if not normalized.get("actor_email"):
                normalized["actor_email"] = entity_email
    target_email = activity.get("email_address") or activity.get("email")
    if target_email and not normalized.get("actor_email"):
        normalized["actor_email"] = target_email
        normalized["target_email"] = target_email
    return normalized


def _extract_email(record: Dict[str, Any]) -> Optional[str]:
    """Return the first non-empty email-like field from a nested API object."""
    for key in ("email_address", "email", "invited_email", "invitee_email"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def wrap_directory_record(
    record: Dict[str, Any],
    record_type: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Wrap directory sync records with common metadata."""
    payload = {
        "record_type": record_type,
        "vendor": "anthropic",
        "product": "claude_enterprise",
        "source_type_category": f"compliance_{record_type}",
    }
    payload.update(record)
    if extra:
        payload.update(extra)
    return payload


def wrap_analytics_record(
    record: Dict[str, Any],
    report_type: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Wrap analytics API payloads with report metadata."""
    payload = {
        "report_type": report_type,
        "vendor": "anthropic",
        "product": "claude_enterprise",
        "source_type_category": f"analytics_{report_type}",
    }
    payload.update(record)
    _flatten_actor_fields(payload)
    _normalize_cost_fields(payload, report_type)
    if extra:
        payload.update(extra)
    return payload


def wrap_spend_limit_record(
    record: Dict[str, Any],
    record_type: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Normalize spend limit API rows."""
    payload = {
        "record_type": record_type,
        "vendor": "anthropic",
        "product": "claude_enterprise",
        "source_type_category": f"analytics_{record_type}",
    }
    payload.update(record)
    _flatten_actor_fields(payload)
    _normalize_spend_limit_amounts(payload)
    source = record.get("source") or {}
    if isinstance(source, dict):
        payload["limit_source_type"] = source.get("type")
        payload["limit_source_seat_tier"] = source.get("seat_tier")
        payload["limit_source_rbac_group_id"] = source.get("rbac_group_id")
    if record_type == "spend_limit_request":
        spend_summary = record.get("spend_summary") or {}
        if isinstance(spend_summary, dict):
            payload["request_spend_limit_cents"] = spend_summary.get("amount")
            payload["request_period_spend_cents"] = spend_summary.get("period_to_date_spend")
            _apply_cents_to_usd(payload, "request_spend_limit_cents", "request_spend_limit_usd")
            _apply_cents_to_usd(payload, "request_period_spend_cents", "request_period_spend_usd")
    if extra:
        payload.update(extra)
    return payload


def _flatten_actor_fields(record: Dict[str, Any]) -> None:
    actor = record.get("actor")
    if not isinstance(actor, dict):
        return
    email = actor.get("email") or actor.get("email_address")
    if email and "email" not in record:
        record["email"] = email
    if email and "actor_email" not in record:
        record["actor_email"] = email
    user_id = actor.get("user_id")
    if user_id and "user_id" not in record:
        record["user_id"] = user_id
    name = actor.get("name")
    if name and "user_name" not in record:
        record["user_name"] = name


def _normalize_cost_fields(record: Dict[str, Any], report_type: str) -> None:
    if report_type not in {"user_cost", "cost"}:
        return
    if "total_cost_usd" not in record and record.get("amount") is not None:
        _apply_cents_to_usd(record, "amount", "total_cost_usd")


def _normalize_spend_limit_amounts(record: Dict[str, Any]) -> None:
    _apply_cents_to_usd(record, "amount", "spend_limit_usd")
    _apply_cents_to_usd(record, "period_to_date_spend", "period_spend_usd")
    limit_usd = record.get("spend_limit_usd")
    spend_usd = record.get("period_spend_usd")
    if limit_usd is not None and limit_usd > 0 and spend_usd is not None:
        record["utilization_pct"] = round(100.0 * spend_usd / limit_usd, 1)
    elif record.get("amount") == "0":
        record["utilization_pct"] = 100.0


def _apply_cents_to_usd(record: Dict[str, Any], cents_field: str, usd_field: str) -> None:
    raw = record.get(cents_field)
    usd = _money_to_usd(raw)
    if usd is not None:
        record[usd_field] = usd


def _money_to_usd(raw: Any) -> Optional[float]:
    """Convert API money amounts to USD.

    Anthropic Analytics/Admin API amounts are cents expressed as decimal
    strings (e.g. "50009.883" cents == 500.09883 USD), so always divide
    by 100. Never guess dollars from the presence of a decimal point.
    """
    if raw in (None, ""):
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return round(value / 100.0, 6)
