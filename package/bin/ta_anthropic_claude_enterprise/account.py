"""Account credential loading from Splunk encrypted storage."""

from __future__ import annotations

from typing import Any, Dict, Optional

from solnlib import conf_manager

from ta_anthropic_claude_enterprise import ADDON_NAME


def get_account_config(session_key: str, account_name: str) -> Dict[str, Any]:
    """Load account stanza including encrypted API keys."""
    cfm = conf_manager.ConfManager(
        session_key,
        ADDON_NAME,
        realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-ta-anthropic_claude_enterprise_account",
    )
    account_conf = cfm.get_conf("ta-anthropic_claude_enterprise_account")
    stanza = account_conf.get(account_name)
    return {
        "name": account_name,
        "compliance_api_key": stanza.get("compliance_api_key"),
        "compliance_key_type": stanza.get("compliance_key_type", "compliance_full"),
        "analytics_api_key": stanza.get("analytics_api_key"),
        "proxy_url": stanza.get("proxy_url") or None,
    }


def resolve_analytics_api_key(account: Dict[str, Any]) -> Optional[str]:
    """Use dedicated analytics key, or fall back to compliance key when scopes overlap."""
    return account.get("analytics_api_key") or account.get("compliance_api_key")


def build_client_from_account(session_key: str, account_name: str, require_analytics: bool = False):
    """Build AnthropicClient from stored account credentials."""
    from ta_anthropic_claude_enterprise.api.client import AnthropicClient

    account = get_account_config(session_key, account_name)
    analytics_api_key = resolve_analytics_api_key(account)
    if not account.get("compliance_api_key") and not (
        require_analytics and analytics_api_key
    ):
        raise ValueError(f"Account '{account_name}' is missing required API keys")

    if require_analytics and not analytics_api_key:
        raise ValueError(f"Account '{account_name}' is missing Analytics API key")

    return AnthropicClient(
        compliance_api_key=account.get("compliance_api_key"),
        analytics_api_key=analytics_api_key,
        proxy_url=account.get("proxy_url"),
    )
