"""Compliance API resource helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from ta_anthropic_claude_enterprise.api.client import AnthropicClient


class ComplianceAPI:
    """Wrapper for Anthropic Compliance API endpoints."""

    def __init__(self, client: AnthropicClient):
        self._client = client

    def list_activities(
        self,
        after_id: Optional[str] = None,
        before_id: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lt: Optional[str] = None,
        order: str = "asc",
        max_items: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": 100, "order": order}
        if after_id:
            params["after_id"] = after_id
        if before_id:
            params["before_id"] = before_id
        if created_at_gte:
            params["created_at.gte"] = created_at_gte
        if created_at_lt:
            params["created_at.lt"] = created_at_lt
        return self._client.paginate_compliance(
            "/v1/compliance/activities",
            params=params,
            max_items=max_items,
        )

    def list_users(self) -> Iterator[Dict[str, Any]]:
        return self._client.paginate_compliance("/v1/compliance/users")

    def list_organizations(self) -> Iterator[Dict[str, Any]]:
        return self._client.paginate_compliance("/v1/compliance/organizations")

    def list_roles(self) -> Iterator[Dict[str, Any]]:
        return self._client.paginate_compliance("/v1/compliance/roles")

    def list_groups(self) -> Iterator[Dict[str, Any]]:
        return self._client.paginate_compliance("/v1/compliance/groups")

    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return self._client.compliance_get(f"/v1/compliance/chats/{chat_id}")

    def list_chats_for_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        params = {"user_id": user_id, "limit": limit}
        return list(
            self._client.paginate_compliance("/v1/compliance/chats", params=params, max_items=limit)
        )

    def get_file(self, file_id: str) -> Dict[str, Any]:
        return self._client.compliance_get(f"/v1/compliance/files/{file_id}")
