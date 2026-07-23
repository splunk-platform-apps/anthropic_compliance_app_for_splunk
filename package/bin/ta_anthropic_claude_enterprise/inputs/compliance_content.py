"""On-demand compliance content collection input handler."""

from __future__ import annotations

from typing import Any, Dict, List

from solnlib import log
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise.account import build_client_from_account, get_account_config
from ta_anthropic_claude_enterprise.api.compliance import ComplianceAPI
from ta_anthropic_claude_enterprise.constants import (
    SOURCETYPE_COMPLIANCE_CHAT_CONTENT,
    SOURCETYPE_COMPLIANCE_FILE_METADATA,
)
from ta_anthropic_claude_enterprise.events import wrap_directory_record
from ta_anthropic_claude_enterprise.input_utils import (
    configure_logger,
    logger_for_input,
    parse_bool,
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
            counts = _collect_content(
                logger=logger,
                session_key=session_key,
                input_item=input_item,
                event_writer=event_writer,
            )
            for sourcetype, count in counts.items():
                log.events_ingested(
                    logger,
                    input_name,
                    sourcetype,
                    count,
                    input_item.get("index"),
                    account=input_item.get("account"),
                )
            log.modular_input_end(logger, normalized_input_name)
        except Exception as exc:
            log.log_exception(
                logger,
                exc,
                "compliance_content_error",
                msg_before="Failed to collect compliance content: ",
            )


def _collect_content(
    logger,
    session_key: str,
    input_item: Dict[str, Any],
    event_writer: smi.EventWriter,
) -> Dict[str, int]:
    account_name = input_item.get("account")
    account = get_account_config(session_key, account_name)
    if account.get("compliance_key_type") == "admin_activities_only":
        raise ValueError(
            "Content collection requires a Compliance Access Key (compliance_full)"
        )

    mode = (input_item.get("collection_mode") or "chat_id").strip()
    include_messages = parse_bool(input_item.get("include_messages"), False)
    max_chats = parse_int(input_item.get("max_chats"), 10)
    index = input_item.get("index")
    source_prefix = f"anthropic:compliance:content:{account_name}"

    client = build_client_from_account(session_key, account_name)
    compliance = ComplianceAPI(client)
    counts = {
        SOURCETYPE_COMPLIANCE_CHAT_CONTENT: 0,
        SOURCETYPE_COMPLIANCE_FILE_METADATA: 0,
    }

    if mode == "file_id":
        file_id = (input_item.get("target_file_id") or "").strip()
        if not file_id:
            raise ValueError("target_file_id is required when collection_mode is file_id")
        file_record = compliance.get_file(file_id)
        payload = wrap_directory_record(file_record, "file")
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=SOURCETYPE_COMPLIANCE_FILE_METADATA,
            source=f"{source_prefix}:file",
        )
        counts[SOURCETYPE_COMPLIANCE_FILE_METADATA] = 1
        return counts

    chat_ids: List[str] = []
    if mode == "chat_id":
        chat_id = (input_item.get("target_chat_id") or "").strip()
        if not chat_id:
            raise ValueError("target_chat_id is required when collection_mode is chat_id")
        chat_ids = [chat_id]
    elif mode == "user_email":
        user_email = (input_item.get("target_user_email") or "").strip()
        if not user_email:
            raise ValueError("target_user_email is required when collection_mode is user_email")
        chat_ids = _resolve_chat_ids_for_user(compliance, user_email, max_chats, logger)
    else:
        raise ValueError(f"Unsupported collection_mode: {mode}")

    for chat_id in chat_ids:
        chat = compliance.get_chat(chat_id)
        payload = wrap_directory_record(chat, "chat")
        if not include_messages and "messages" in payload:
            payload["messages"] = "[REDACTED]"
            payload["message_count"] = len(chat.get("messages") or [])
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=SOURCETYPE_COMPLIANCE_CHAT_CONTENT,
            source=f"{source_prefix}:chat",
        )
        counts[SOURCETYPE_COMPLIANCE_CHAT_CONTENT] += 1

    return counts


def _resolve_chat_ids_for_user(
    compliance: ComplianceAPI,
    user_email: str,
    max_chats: int,
    logger,
) -> List[str]:
    user_id = None
    for user in compliance.list_users():
        email = user.get("email_address") or user.get("email")
        if email and email.lower() == user_email.lower():
            user_id = user.get("id") or user.get("user_id")
            break

    if not user_id:
        raise ValueError(f"No user found with email: {user_email}")

    chats = compliance.list_chats_for_user(user_id, limit=max_chats)
    chat_ids = [chat.get("id") for chat in chats if chat.get("id")]
    if not chat_ids:
        logger.warning("No chats found for user %s", user_email)
    return chat_ids[:max_chats]
