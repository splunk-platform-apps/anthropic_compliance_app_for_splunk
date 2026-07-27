"""Enterprise Analytics API resource helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Iterator, List, Optional

from ta_anthropic_claude_enterprise.api.client import AnthropicAPIError, AnthropicClient


class AnalyticsAPI:
    """Wrapper for Anthropic Enterprise Analytics API endpoints."""

    FINALIZATION_LAG_DAYS = 3

    def __init__(self, client: AnthropicClient):
        self._client = client

    @classmethod
    def latest_finalized_date(cls) -> date:
        return date.today() - timedelta(days=cls.FINALIZATION_LAG_DAYS)

    def get_summaries(
        self,
        starting_date: date,
        ending_date: date,
    ) -> Dict[str, Any]:
        return self._client.analytics_get(
            "/v1/organizations/analytics/summaries",
            {
                "starting_date": starting_date.isoformat(),
                "ending_date": ending_date.isoformat(),
            },
        )

    def _paginate_grouped(
        self,
        path: str,
        params: Dict[str, Any],
        group_by: Optional[List[str]],
    ) -> Iterator[Dict[str, Any]]:
        """Paginate a report, requesting group_by via the API's array-param
        convention (group_by[]); if the API rejects the grouping with a 400,
        retry ungrouped rather than failing the whole collection."""
        if group_by:
            grouped = dict(params)
            grouped["group_by[]"] = group_by
            try:
                yield from self._client.paginate_analytics(path, grouped)
                return
            except AnthropicAPIError as exc:
                if exc.status_code != 400:
                    raise
        yield from self._client.paginate_analytics(path, params)

    def get_usage_report(
        self,
        starting_at: str,
        ending_at: Optional[str] = None,
        bucket_width: str = "1d",
        group_by: Optional[List[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "starting_at": starting_at,
            "bucket_width": bucket_width,
        }
        if ending_at:
            params["ending_at"] = ending_at
        return self._paginate_grouped(
            "/v1/organizations/analytics/usage_report", params, group_by
        )

    def get_cost_report(
        self,
        starting_at: str,
        ending_at: Optional[str] = None,
        bucket_width: str = "1d",
        group_by: Optional[List[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "starting_at": starting_at,
            "bucket_width": bucket_width,
        }
        if ending_at:
            params["ending_at"] = ending_at
        return self._paginate_grouped(
            "/v1/organizations/analytics/cost_report", params, group_by
        )

    def get_user_usage_report(
        self,
        starting_at: str,
        ending_at: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "starting_at": starting_at,
            "limit": limit,
        }
        if ending_at:
            params["ending_at"] = ending_at
        return self._client.analytics_get("/v1/organizations/analytics/user_usage_report", params)

    def get_user_cost_report(
        self,
        starting_at: str,
        ending_at: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "starting_at": starting_at,
            "limit": limit,
        }
        if ending_at:
            params["ending_at"] = ending_at
        return self._client.analytics_get("/v1/organizations/analytics/user_cost_report", params)

    def list_user_activity(
        self,
        starting_date: date,
        ending_date: date,
    ) -> Iterator[Dict[str, Any]]:
        params = {
            "starting_date": starting_date.isoformat(),
            "ending_date": ending_date.isoformat(),
        }
        return self._client.paginate_analytics("/v1/organizations/analytics/users", params)
