"""Spend Limits API resource helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ta_anthropic_claude_enterprise.api.client import AnthropicClient


class SpendLimitsAPI:
    """Wrapper for Anthropic Enterprise Spend Limits API endpoints."""

    def __init__(self, client: AnthropicClient):
        self._client = client

    def list_effective_spend_limits(
        self,
        user_ids: list[str] | None = None,
        period: list[str] | None = None,
        limit: int = 100,
    ) -> Iterator[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
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
        status: list[str] | None = None,
        actor_ids: list[str] | None = None,
        limit: int = 100,
    ) -> Iterator[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status[]"] = status
        if actor_ids:
            params["actor_ids[]"] = actor_ids
        return self._client.paginate_admin(
            "/v1/organizations/spend_limit_increase_requests",
            params,
        )
