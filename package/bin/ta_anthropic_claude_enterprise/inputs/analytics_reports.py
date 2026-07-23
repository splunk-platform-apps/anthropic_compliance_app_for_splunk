"""Analytics reports input handler."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List

from solnlib import log
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise.analytics_dates import resolve_analytics_start_date
from ta_anthropic_claude_enterprise.account import build_client_from_account
from ta_anthropic_claude_enterprise.api.analytics import AnalyticsAPI
from ta_anthropic_claude_enterprise.api.spend_limits import SpendLimitsAPI
from ta_anthropic_claude_enterprise.checkpoint import CheckpointStore
from ta_anthropic_claude_enterprise.constants import (
    SOURCETYPE_ANALYTICS_COST,
    SOURCETYPE_ANALYTICS_SPEND_LIMIT,
    SOURCETYPE_ANALYTICS_SPEND_LIMIT_REQUEST,
    SOURCETYPE_ANALYTICS_SUMMARY,
    SOURCETYPE_ANALYTICS_USAGE,
    SOURCETYPE_ANALYTICS_USER_ACTIVITY,
    SOURCETYPE_ANALYTICS_USER_COST,
    SOURCETYPE_ANALYTICS_USER_USAGE,
)
from ta_anthropic_claude_enterprise.events import wrap_analytics_record, wrap_spend_limit_record
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
            counts = _collect_analytics(
                logger=logger,
                session_key=session_key,
                input_key=input_name,
                input_item=input_item,
                event_writer=event_writer,
            )
            for sourcetype, count in counts.items():
                if count:
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
                "analytics_reports_error",
                msg_before="Failed to collect analytics reports: ",
            )


def _collect_analytics(
    logger,
    session_key: str,
    input_key: str,
    input_item: Dict[str, Any],
    event_writer: smi.EventWriter,
) -> Dict[str, int]:
    account_name = input_item.get("account")
    client = build_client_from_account(session_key, account_name, require_analytics=True)
    analytics = AnalyticsAPI(client)
    checkpoint = CheckpointStore(session_key)
    state = checkpoint.get(input_key)

    index = input_item.get("index")
    bucket_width = input_item.get("bucket_width") or "1d"
    source_prefix = f"anthropic:analytics:{account_name}"

    end_date = AnalyticsAPI.latest_finalized_date()
    backfill_days = min(parse_int(input_item.get("backfill_days"), 7), 90)
    start_date = resolve_analytics_start_date(state, end_date, backfill_days)
    starting_at = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    ending_at = datetime.combine(end_date, datetime.min.time(), tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    counts: Dict[str, int] = {
        SOURCETYPE_ANALYTICS_SUMMARY: 0,
        SOURCETYPE_ANALYTICS_USAGE: 0,
        SOURCETYPE_ANALYTICS_COST: 0,
        SOURCETYPE_ANALYTICS_USER_USAGE: 0,
        SOURCETYPE_ANALYTICS_USER_COST: 0,
        SOURCETYPE_ANALYTICS_USER_ACTIVITY: 0,
        SOURCETYPE_ANALYTICS_SPEND_LIMIT: 0,
        SOURCETYPE_ANALYTICS_SPEND_LIMIT_REQUEST: 0,
    }

    if parse_bool(input_item.get("collect_summaries"), True):
        counts[SOURCETYPE_ANALYTICS_SUMMARY] = _emit_summaries(
            analytics, start_date, end_date, event_writer, index, source_prefix
        )

    group_by = ["product", "model"]
    if parse_bool(input_item.get("collect_usage"), True):
        counts[SOURCETYPE_ANALYTICS_USAGE] = _emit_paginated_report(
            iterator=analytics.get_usage_report(
                starting_at=starting_at,
                ending_at=ending_at,
                bucket_width=bucket_width,
                group_by=group_by,
            ),
            report_type="usage",
            sourcetype=SOURCETYPE_ANALYTICS_USAGE,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:usage",
        )

    if parse_bool(input_item.get("collect_cost"), True):
        counts[SOURCETYPE_ANALYTICS_COST] = _emit_paginated_report(
            iterator=analytics.get_cost_report(
                starting_at=starting_at,
                ending_at=ending_at,
                bucket_width=bucket_width,
                group_by=group_by,
            ),
            report_type="cost",
            sourcetype=SOURCETYPE_ANALYTICS_COST,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:cost",
        )

    if parse_bool(input_item.get("collect_user_usage"), True):
        response = analytics.get_user_usage_report(starting_at=starting_at, ending_at=ending_at)
        counts[SOURCETYPE_ANALYTICS_USER_USAGE] = _emit_list_report(
            response.get("data", []),
            report_type="user_usage",
            sourcetype=SOURCETYPE_ANALYTICS_USER_USAGE,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:user_usage",
        )

    if parse_bool(input_item.get("collect_user_cost"), True):
        response = analytics.get_user_cost_report(starting_at=starting_at, ending_at=ending_at)
        counts[SOURCETYPE_ANALYTICS_USER_COST] = _emit_list_report(
            response.get("data", []),
            report_type="user_cost",
            sourcetype=SOURCETYPE_ANALYTICS_USER_COST,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:user_cost",
        )

    if parse_bool(input_item.get("collect_user_activity"), True):
        counts[SOURCETYPE_ANALYTICS_USER_ACTIVITY] = _emit_paginated_report(
            iterator=analytics.list_user_activity(starting_date=start_date, ending_date=end_date),
            report_type="user_activity",
            sourcetype=SOURCETYPE_ANALYTICS_USER_ACTIVITY,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:user_activity",
        )

    if parse_bool(input_item.get("collect_spend_limits"), True):
        spend_limits = SpendLimitsAPI(client)
        counts[SOURCETYPE_ANALYTICS_SPEND_LIMIT] = _emit_spend_limit_report(
            iterator=spend_limits.list_effective_spend_limits(),
            record_type="spend_limit",
            sourcetype=SOURCETYPE_ANALYTICS_SPEND_LIMIT,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:spend_limits",
        )
        counts[SOURCETYPE_ANALYTICS_SPEND_LIMIT_REQUEST] = _emit_spend_limit_report(
            iterator=spend_limits.list_spend_limit_increase_requests(status=["pending"]),
            record_type="spend_limit_request",
            sourcetype=SOURCETYPE_ANALYTICS_SPEND_LIMIT_REQUEST,
            event_writer=event_writer,
            index=index,
            source=f"{source_prefix}:spend_limit_requests",
        )

    checkpoint.set(input_key, {"last_finalized_date": end_date.isoformat()})
    logger.info("Analytics collection window %s to %s", start_date, end_date)
    return counts


def _emit_summaries(
    analytics: AnalyticsAPI,
    start_date: date,
    end_date: date,
    event_writer: smi.EventWriter,
    index: str,
    source_prefix: str,
) -> int:
    response = analytics.get_summaries(start_date, end_date)
    summaries = response.get("summaries", [])
    count = 0
    for summary in summaries:
        payload = wrap_analytics_record(summary, "summary")
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=SOURCETYPE_ANALYTICS_SUMMARY,
            source=f"{source_prefix}:summary",
            event_time=summary.get("starting_at"),
        )
        count += 1
    return count


def _emit_paginated_report(
    iterator,
    report_type: str,
    sourcetype: str,
    event_writer: smi.EventWriter,
    index: str,
    source: str,
) -> int:
    count = 0
    for record in iterator:
        payload = wrap_analytics_record(record, report_type)
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=sourcetype,
            source=source,
            event_time=record.get("starting_at") or record.get("date"),
        )
        count += 1
    return count


def _emit_list_report(
    records: List[Dict[str, Any]],
    report_type: str,
    sourcetype: str,
    event_writer: smi.EventWriter,
    index: str,
    source: str,
) -> int:
    count = 0
    for record in records:
        payload = wrap_analytics_record(record, report_type)
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=sourcetype,
            source=source,
            event_time=record.get("date") or record.get("starting_at"),
        )
        count += 1
    return count


def _emit_spend_limit_report(
    iterator,
    record_type: str,
    sourcetype: str,
    event_writer: smi.EventWriter,
    index: str,
    source: str,
) -> int:
    count = 0
    snapshot_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for record in iterator:
        payload = wrap_spend_limit_record(record, record_type)
        write_json_event(
            event_writer=event_writer,
            payload=payload,
            index=index,
            sourcetype=sourcetype,
            source=source,
            event_time=snapshot_time,
        )
        count += 1
    return count
