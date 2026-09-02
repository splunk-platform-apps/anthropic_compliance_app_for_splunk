"""Tests for event normalization."""
# ruff: noqa: E402

import sys
import unittest
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
sys.path.insert(0, str(BIN_DIR))

from ta_anthropic_claude_enterprise.events import (
    normalize_activity,
    wrap_analytics_record,
    wrap_spend_limit_record,
)


class TestNormalizeActivity(unittest.TestCase):
    def test_flattens_actor_and_flags(self):
        activity = {
            "id": "activity_123",
            "created_at": "2026-04-10T08:09:10Z",
            "type": "user_signed_in_sso",
            "organization_id": "org_abc",
            "actor": {
                "type": "user_actor",
                "email_address": "alice@example.com",
                "user_id": "user_123",
                "ip_address": "192.0.2.1",
            },
        }
        result = normalize_activity(activity)
        self.assertEqual(result["activity_id"], "activity_123")
        self.assertEqual(result["event_type"], "user_signed_in_sso")
        self.assertEqual(result["type"], "user_signed_in_sso")
        self.assertEqual(result["actor_email"], "alice@example.com")
        self.assertTrue(result["is_authentication_event"])
        self.assertFalse(result["is_change_event"])

    def test_uses_entity_email_when_actor_missing(self):
        activity = {
            "id": "activity_invite",
            "created_at": "2026-04-10T08:09:10Z",
            "type": "org_user_invite_sent",
            "actor": {"type": "api_actor", "api_key_id": "key_123"},
            "entity_info": {"email_address": "invitee@example.com"},
        }
        result = normalize_activity(activity)
        self.assertEqual(result["actor_email"], "invitee@example.com")
        self.assertEqual(result["entity_email"], "invitee@example.com")
        self.assertEqual(result["actor_api_key_id"], "key_123")


class TestWrapAnalyticsRecord(unittest.TestCase):
    def test_adds_report_metadata(self):
        payload = wrap_analytics_record({"daily_active_user_count": 10}, "summary")
        self.assertEqual(payload["report_type"], "summary")
        self.assertEqual(payload["daily_active_user_count"], 10)

    def test_user_cost_converts_cents_to_usd(self):
        payload = wrap_analytics_record(
            {"amount": "50000", "actor": {"email": "alice@example.com"}},
            "user_cost",
        )
        self.assertEqual(payload["email"], "alice@example.com")
        self.assertEqual(payload["total_cost_usd"], 500.0)


class TestWrapSpendLimitRecord(unittest.TestCase):
    def test_normalizes_utilization(self):
        payload = wrap_spend_limit_record(
            {
                "amount": "50000",
                "period_to_date_spend": "40000",
                "actor": {"email_address": "alice@example.com"},
                "source": {"type": "seat_tier", "seat_tier": "enterprise_standard"},
            },
            "spend_limit",
        )
        self.assertEqual(payload["email"], "alice@example.com")
        self.assertEqual(payload["spend_limit_usd"], 500.0)
        self.assertEqual(payload["period_spend_usd"], 400.0)
        self.assertEqual(payload["utilization_pct"], 80.0)
        self.assertEqual(payload["limit_source_type"], "seat_tier")

    def test_period_spend_decimal_cents_string(self):
        payload = wrap_spend_limit_record(
            {
                "amount": "0",
                "period_to_date_spend": "16696",
                "actor": {"email_address": "beau@splunk.com", "name": "Beau"},
                "source": {"type": "seat_tier", "seat_tier": "enterprise_standard"},
            },
            "spend_limit",
        )
        self.assertEqual(payload["period_spend_usd"], 166.96)
        self.assertEqual(payload["user_name"], "Beau")


if __name__ == "__main__":
    unittest.main()
