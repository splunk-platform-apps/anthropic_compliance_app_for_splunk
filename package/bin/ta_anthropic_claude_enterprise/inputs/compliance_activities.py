"""Compliance Activity Feed input handler."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from solnlib import log
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise.account import build_client_from_account
from ta_anthropic_claude_enterprise.api.compliance import ComplianceAPI
from ta_anthropic_claude_enterprise.checkpoint import CheckpointStore
from ta_anthropic_claude_enterprise.constants import SOURCETYPE_COMPLIANCE_ACTIVITY
from ta_anthropic_claude_enterprise.events import normalize_activity
from ta_anthropic_claude_enterprise.input_utils import (
    configure_logger,
    logger_for_input,
    parse_int,
    write_json_event,
)


def validate_input(definition: smi.ValidationDefinition) -> None:
    return


def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter) -> None:
    for input_name, input_item in inputs.inputs.items():
        normalized_input_name = input_name.split("/")[-1]
        logger = logger_for_input(normalized_input_name)
        session_key = inputs.metadata["session_key"]
        configure_logger(logger, session_key)
        log.modular_input_start(logger, normalized_input_name)

        try:
            count = _collect_activities(
                logger=logger,
                session_key=session_key,
                input_key=input_name,
                input_item=input_item,
                event_writer=event_writer,
            )
            log.events_ingested(
                logger,
                input_name,
                SOURCETYPE_COMPLIANCE_ACTIVITY,
                count,
                input_item.get("index"),
                account=input_item.get("account"),
            )
            log.modular_input_end(logger, normalized_input_name)
        except Exception as exc:
            log.log_exception(
                logger,
                exc,
                "compliance_activities_error",
                msg_before="Failed to collect compliance activities: ",
            )


def _collect_activities(
    logger,
    session_key: str,
    input_key: str,
    input_item: Dict[str, Any],
    event_writer: smi.EventWriter,
) -> int:
    account_name = input_item.get("account")
    client = build_client_from_account(session_key, account_name)
    compliance = ComplianceAPI(client)
    checkpoint = CheckpointStore(session_key)
    state = checkpoint.get(input_key)

    max_events = parse_int(input_item.get("max_events_per_cycle"), 1000)
    backfill_days = min(parse_int(input_item.get("backfill_days"), 7), 180)

    after_id = state.get("last_activity_id")
    created_at_gte = None
    if not after_id:
        created_at_gte = (
            datetime.now(timezone.utc) - timedelta(days=backfill_days)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    count = 0
    last_activity_id = after_id
    last_created_at = state.get("last_created_at")

    for activity in compliance.list_activities(
        after_id=after_id,
        created_at_gte=created_at_gte,
        order="asc",
        max_items=max_events,
    ):
        normalized = normalize_activity(activity)
        write_json_event(
            event_writer=event_writer,
            payload=normalized,
            index=input_item.get("index"),
            sourcetype=SOURCETYPE_COMPLIANCE_ACTIVITY,
            source=f"anthropic:compliance:activities:{account_name}",
            event_time=normalized.get("created_at"),
        )
        count += 1
        last_activity_id = activity.get("id", last_activity_id)
        last_created_at = activity.get("created_at", last_created_at)

    if count > 0:
        checkpoint.set(
            input_key,
            {
                "last_activity_id": last_activity_id,
                "last_created_at": last_created_at,
            },
        )
        logger.info("Ingested %s compliance activities", count)
    else:
        logger.debug("No new compliance activities")

    return count
