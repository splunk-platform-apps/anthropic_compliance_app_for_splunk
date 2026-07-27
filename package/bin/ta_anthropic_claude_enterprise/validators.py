"""External validation for Anthropic API account credentials."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

import import_declare_test  # noqa: F401  # adds lib/ to sys.path
from splunklib import modularinput as smi

from ta_anthropic_claude_enterprise.account import get_account_config, resolve_analytics_api_key
from ta_anthropic_claude_enterprise.api.client import AnthropicClient


def validate_account_credentials(session_key: str, account_name: str) -> None:
    account = get_account_config(session_key, account_name)
    analytics_api_key = resolve_analytics_api_key(account)
    client = AnthropicClient(
        compliance_api_key=account.get("compliance_api_key"),
        analytics_api_key=analytics_api_key,
        proxy_url=account.get("proxy_url"),
    )

    if account.get("compliance_api_key"):
        ok, message = client.validate_compliance_key()
        if not ok:
            _exit_validation_error(message)

    if analytics_api_key:
        ok, message = client.validate_analytics_key()
        if not ok:
            _exit_validation_error(message)


def validate_input_definition(definition: smi.ValidationDefinition) -> None:
    session_key = definition.metadata["session_key"]
    for input_name, input_item in definition.parameters.items():
        account_name = input_item.get("account")
        if not account_name:
            _exit_validation_error("Account is required for all inputs")
        validate_account_credentials(session_key, account_name)


def _exit_validation_error(message: str) -> None:
    sys.stderr.write(f"<message>{message}</message>")
    sys.exit(1)


def parse_validation_xml() -> smi.ValidationDefinition:
    root = ET.fromstring(sys.stdin.read())
    metadata = {"session_key": root.findtext("./session_key")}
    parameters = {}
    for item in root.findall("./configuration/item"):
        key = item.get("name")
        params = {child.get("name"): child.text for child in item.findall("./param")}
        parameters[key] = params
    return smi.ValidationDefinition(metadata=metadata, parameters=parameters)
