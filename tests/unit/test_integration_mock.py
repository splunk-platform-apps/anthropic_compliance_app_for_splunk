"""Integration tests using mock API keys — no Splunk instance required."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
LIB_DIR = (
    Path(__file__).resolve().parents[2]
    / "output"
    / "TA-anthropic_claude_enterprise"
    / "lib"
)
if LIB_DIR.is_dir():
    sys.path.insert(0, str(LIB_DIR))
sys.path.insert(0, str(BIN_DIR))

MOCK_COMPLIANCE_KEY = "sk-ant-mock-compliance-key-for-testing"
MOCK_ANALYTICS_KEY = "sk-ant-mock-analytics-key-for-testing"

MOCK_ACTIVITY_RESPONSE = {
    "data": [
        {
            "id": "activity_01MockTest123",
            "created_at": "2026-04-10T08:09:10Z",
            "organization_id": "org_01MockOrg",
            "type": "user_signed_in_sso",
            "actor": {
                "type": "user_actor",
                "email_address": "alice@example.com",
                "user_id": "user_01MockUser",
                "ip_address": "192.0.2.34",
            },
        },
        {
            "id": "activity_01MockTest456",
            "created_at": "2026-04-10T09:15:00Z",
            "organization_id": "org_01MockOrg",
            "type": "file_uploaded",
            "actor": {
                "type": "user_actor",
                "email_address": "alice@example.com",
                "user_id": "user_01MockUser",
            },
        },
    ],
    "has_more": False,
}

MOCK_ANALYTICS_SUMMARY = {
    "summaries": [
        {
            "starting_at": "2026-04-08T00:00:00Z",
            "daily_active_user_count": 42,
            "daily_adoption_rate": 84.0,
        }
    ]
}


def _mock_http_response(payload: dict):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__.return_value = response
    return response


class TestMockApiPipeline(unittest.TestCase):
    """End-to-end API + normalization pipeline with mock keys."""

    @patch("urllib.request.OpenerDirector.open")
    def test_compliance_activity_pipeline(self, mock_open):
        from ta_anthropic_claude_enterprise.api.client import AnthropicClient
        from ta_anthropic_claude_enterprise.api.compliance import ComplianceAPI
        from ta_anthropic_claude_enterprise.events import normalize_activity

        mock_open.return_value = _mock_http_response(MOCK_ACTIVITY_RESPONSE)
        client = AnthropicClient(compliance_api_key=MOCK_COMPLIANCE_KEY)
        compliance = ComplianceAPI(client)

        events = [
            normalize_activity(a) for a in compliance.list_activities(max_items=10)
        ]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "user_signed_in_sso")
        self.assertTrue(events[0]["is_authentication_event"])
        self.assertEqual(events[1]["event_type"], "file_uploaded")

    @patch("urllib.request.OpenerDirector.open")
    def test_analytics_summary_pipeline(self, mock_open):
        from datetime import timedelta

        from ta_anthropic_claude_enterprise.api.analytics import AnalyticsAPI
        from ta_anthropic_claude_enterprise.api.client import AnthropicClient
        from ta_anthropic_claude_enterprise.events import wrap_analytics_record

        mock_open.return_value = _mock_http_response(MOCK_ANALYTICS_SUMMARY)
        client = AnthropicClient(analytics_api_key=MOCK_ANALYTICS_KEY)
        analytics = AnalyticsAPI(client)
        end = AnalyticsAPI.latest_finalized_date()
        start = end - timedelta(days=1)
        response = analytics.get_summaries(start, end)

        events = [
            wrap_analytics_record(s, "summary") for s in response.get("summaries", [])
        ]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["daily_active_user_count"], 42)
        self.assertEqual(events[0]["report_type"], "summary")

    @patch("urllib.request.OpenerDirector.open")
    def test_mock_key_validation(self, mock_open):
        from ta_anthropic_claude_enterprise.api.client import AnthropicClient

        def side_effect(request, timeout=None):
            if "compliance" in request.full_url:
                return _mock_http_response({"data": [], "has_more": False})
            return _mock_http_response(MOCK_ANALYTICS_SUMMARY)

        mock_open.side_effect = side_effect
        compliance_client = AnthropicClient(compliance_api_key=MOCK_COMPLIANCE_KEY)
        ok, _ = compliance_client.validate_compliance_key()
        self.assertTrue(ok)

        analytics_client = AnthropicClient(analytics_api_key=MOCK_ANALYTICS_KEY)
        ok, _ = analytics_client.validate_analytics_key()
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
