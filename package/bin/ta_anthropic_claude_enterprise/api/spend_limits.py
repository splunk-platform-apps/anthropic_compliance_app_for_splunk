"""Spend Limits API resource helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from ta_anthropic_claude_enterprise.api.client import AnthropicClient


class SpendLimitsAPI:
    """Wrapper for Anthropic Enterprise Spend Limits API endpoints."""

    def __init__(self, client: AnthropicClient):
        self._client = client

    def list_effective_spend_limits(
        self,
        user_ids: Optional[List[str]] = None,
        period: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Iterator[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if user_ids:
            params["user_ids[]"] = user_ids
        if period:
            params["period[]"] = period
        return self._client.paginate_admin(
            "/v1/organizations/spend_limits/effective",
            params,
        )

    def list_spend_limit_increase_requests(
        self,
        status: Optional[List[str]] = None,
        actor_ids: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Iterator[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status[]"] = status
        if actor_ids:
            params["actor_ids[]"] = actor_ids
        return self._client.paginate_admin(
            "/v1/organizations/spend_limit_increase_requests",
            params,
        )
