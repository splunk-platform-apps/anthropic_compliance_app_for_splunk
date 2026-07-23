"""Shared modular input utilities."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from solnlib import conf_manager, log
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise import ADDON_NAME


def logger_for_input(input_name: str) -> logging.Logger:
    return log.Logs().get_logger(f"{ADDON_NAME.lower()}_{input_name}")


def configure_logger(logger: logging.Logger, session_key: str) -> None:
    log_level = conf_manager.get_log_level(
        logger=logger,
        session_key=session_key,
        app_name=ADDON_NAME,
        conf_name="ta-anthropic_claude_enterprise_settings",
    )
    logger.setLevel(log_level)


def parse_event_time(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).timestamp()
    except ValueError:
        return None


def write_json_event(
    event_writer: smi.EventWriter,
    payload: Dict[str, Any],
    index: Optional[str],
    sourcetype: str,
    source: str,
    event_time: Optional[str] = None,
) -> None:
    # Drop null values so Splunk's JSON extraction never yields literal
    # "null" strings for fields like actor_email.
    compact_payload = {k: v for k, v in payload.items() if v is not None}
    event = smi.Event(
        data=json.dumps(compact_payload, ensure_ascii=False, default=str),
        index=index,
        sourcetype=sourcetype,
        source=source,
        time=parse_event_time(event_time),
    )
    event_writer.write_event(event)


def parse_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes", "on"}
