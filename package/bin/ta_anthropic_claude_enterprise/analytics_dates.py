"""Date window helpers for analytics collection."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def resolve_analytics_start_date(
    state: dict[str, Any],
    end_date: date,
    backfill_days: int,
) -> date:
    """Return the analytics start date from checkpoint or backfill window."""
    last = state.get("last_finalized_date")
    if last:
        try:
            parsed = date.fromisoformat(str(last))
            return min(parsed, end_date - timedelta(days=1))
        except ValueError:
            pass
    return end_date - timedelta(days=backfill_days)
