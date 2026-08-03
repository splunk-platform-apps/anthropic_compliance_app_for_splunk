"""Tests for Compliance API query parameters."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
sys.path.insert(0, str(BIN_DIR))

from ta_anthropic_claude_enterprise.api.client import AnthropicClient
from ta_anthropic_claude_enterprise.api.compliance import ComplianceAPI


class TestComplianceActivitiesParams(unittest.TestCase):
    @patch("urllib.request.OpenerDirector.open")
    def test_backfill_uses_created_at_gte_not_created_after(self, mock_open):
        response = MagicMock()
        response.read.return_value = json.dumps({"data": [], "has_more": False}).encode("utf-8")
        response.__enter__.return_value = response
        mock_open.return_value = response

        client = AnthropicClient(compliance_api_key="test-key")
        compliance = ComplianceAPI(client)
        list(compliance.list_activities(created_at_gte="2026-04-01T00:00:00Z"))

        request = mock_open.call_args[0][0]
        query = request.full_url.split("?", 1)[1]
        self.assertIn("created_at.gte=2026-04-01T00%3A00%3A00Z", query)
        self.assertNotIn("created_after", query)
        self.assertIn("order=asc", query)

    @patch("urllib.request.OpenerDirector.open")
    def test_incremental_uses_after_id(self, mock_open):
        response = MagicMock()
        response.read.return_value = json.dumps({"data": [], "has_more": False}).encode("utf-8")
        response.__enter__.return_value = response
        mock_open.return_value = response

        client = AnthropicClient(compliance_api_key="test-key")
        compliance = ComplianceAPI(client)
        list(compliance.list_activities(after_id="activity_01abc"))

        request = mock_open.call_args[0][0]
        query = request.full_url.split("?", 1)[1]
        self.assertIn("after_id=activity_01abc", query)
        self.assertNotIn("starting_after", query)


if __name__ == "__main__":
    unittest.main()
