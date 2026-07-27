"""Compliance directory sync input handler."""

from __future__ import annotations

import time
from typing import Any, Dict, Iterator, Tuple

from solnlib import log
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise.account import build_client_from_account
from ta_anthropic_claude_enterprise.api.client import AnthropicAPIError
from ta_anthropic_claude_enterprise.api.compliance import ComplianceAPI
from ta_anthropic_claude_enterprise.checkpoint import CheckpointStore
from ta_anthropic_claude_enterprise.constants import (
    SOURCETYPE_COMPLIANCE_GROUP,
    SOURCETYPE_COMPLIANCE_ORGANIZATION,
    SOURCETYPE_COMPLIANCE_USER,
)
from ta_anthropic_claude_enterprise.events import wrap_directory_record
from ta_anthropic_claude_enterprise.input_utils import (
    configure_logger,
    logger_for_input,
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
            counts = _collect_directory(
                logger=logger,
                session_key=session_key,
                input_key=input_name,
                input_item=input_item,
                event_writer=event_writer,
            )
            total = sum(counts.values())
            for sourcetype, count in counts.items():
                log.events_ingested(
                    logger,
                    input_name,
                    sourcetype,
                    count,
                    input_item.get("index"),
                    account=input_item.get("account"),
                )
            logger.info("Directory sync complete: %s total records", total)
            log.modular_input_end(logger, normalized_input_name)
        except Exception as exc:
            log.log_exception(
                logger,
                exc,
                "compliance_directory_error",
                msg_before="Failed to sync compliance directory: ",
            )


def _collect_directory(
    logger,
    session_key: str,
    input_key: str,
    input_item: Dict[str, Any],
    event_writer: smi.EventWriter,
) -> Dict[str, int]:
    account_name = input_item.get("account")
    client = build_client_from_account(session_key, account_name)
    compliance = ComplianceAPI(client)
    index = input_item.get("index")
    source_prefix = f"anthropic:compliance:directory:{account_name}"
    counts = {
        SOURCETYPE_COMPLIANCE_USER: 0,
        SOURCETYPE_COMPLIANCE_ORGANIZATION: 0,
        SOURCETYPE_COMPLIANCE_GROUP: 0,
    }

    sync_handlers: Tuple[Tuple[str, str, Any], ...] = (
        ("users", SOURCETYPE_COMPLIANCE_USER, lambda: _iter_users(compliance, client)),
        (
            "organizations",
            SOURCETYPE_COMPLIANCE_ORGANIZATION,
            lambda: _iter_organizations(compliance, client),
        ),
        (
            "groups",
            SOURCETYPE_COMPLIANCE_GROUP,
            lambda: _iter_groups(compliance, client),
        ),
    )

    for resource_name, sourcetype, iterator in sync_handlers:
        try:
            for record in iterator():
                payload = wrap_directory_record(record, resource_name.rstrip("s"))
                write_json_event(
                    event_writer=event_writer,
                    payload=payload,
                    index=index,
                    sourcetype=sourcetype,
                    source=f"{source_prefix}:{resource_name}",
                )
                counts[sourcetype] += 1
        except AnthropicAPIError as exc:
            logger.warning(
                "Skipping %s sync: neither the Compliance directory API nor the "
                "Admin API is reachable with the configured keys (%s)",
                resource_name,
                exc,
            )

    CheckpointStore(session_key).set(input_key, {"last_sync_epoch": int(time.time())})
    return counts


def _is_fallback_status(exc: AnthropicAPIError) -> bool:
    """Compliance directory endpoints unavailable to this key -> try Admin API."""
    return exc.status_code in (401, 403, 404)


def _iter_users(compliance: ComplianceAPI, client) -> Iterator[Dict[str, Any]]:
    """Users from the Compliance directory, falling back to the Admin API."""
    try:
        yield from compliance.list_users()
        return
    except AnthropicAPIError as exc:
        if not _is_fallback_status(exc):
            raise
    for record in client.paginate_admin("/v1/organizations/users"):
        if record.get("email") and not record.get("email_address"):
            record["email_address"] = record["email"]
        yield record


def _iter_organizations(compliance: ComplianceAPI, client) -> Iterator[Dict[str, Any]]:
    """Organizations from the Compliance directory, falling back to Admin API."""
    try:
        yield from compliance.list_organizations()
        return
    except AnthropicAPIError as exc:
        if not _is_fallback_status(exc):
            raise
    record = client.admin_get("/v1/organizations/me")
    if isinstance(record, dict) and record:
        yield record


def _iter_groups(compliance: ComplianceAPI, client) -> Iterator[Dict[str, Any]]:
    """Groups from the Compliance directory, falling back to Admin API workspaces."""
    try:
        yield from compliance.list_groups()
        return
    except AnthropicAPIError as exc:
        if not _is_fallback_status(exc):
            raise
    yield from client.paginate_admin("/v1/organizations/workspaces")
