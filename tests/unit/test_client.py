"""Tests for Anthropic API client."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
sys.path.insert(0, str(BIN_DIR))

from ta_anthropic_claude_enterprise.api.client import AnthropicAPIError, AnthropicClient


class TestAnthropicClient(unittest.TestCase):
    @patch("urllib.request.OpenerDirector.open")
    def test_compliance_get_parses_json(self, mock_open):
        response = MagicMock()
        response.read.return_value = json.dumps({"data": []}).encode("utf-8")
        response.__enter__.return_value = response
        mock_open.return_value = response

        client = AnthropicClient(compliance_api_key="test-key")
        result = client.compliance_get("/v1/compliance/activities", {"limit": 1})
        self.assertEqual(result, {"data": []})

    @patch("urllib.request.OpenerDirector.open")
    def test_raises_on_http_error(self, mock_open):
        import urllib.error

        body = json.dumps({"error": {"message": "forbidden"}}).encode("utf-8")
        mock_open.side_effect = urllib.error.HTTPError(
            url="https://api.anthropic.com/v1/compliance/activities",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=MagicMock(read=lambda: body),
        )
        client = AnthropicClient(compliance_api_key="test-key")
        with self.assertRaises(AnthropicAPIError) as ctx:
            client.compliance_get("/v1/compliance/activities")
        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
