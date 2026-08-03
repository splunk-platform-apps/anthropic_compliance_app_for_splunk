"""Tests for analytics date window helpers."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
sys.path.insert(0, str(BIN_DIR))

from ta_anthropic_claude_enterprise.analytics_dates import resolve_analytics_start_date


class TestResolveAnalyticsStartDate(unittest.TestCase):
    def test_first_run_uses_backfill_days(self):
        end = date(2026, 4, 10)
        start = resolve_analytics_start_date({}, end, 14)
        self.assertEqual(start, end - timedelta(days=14))

    def test_checkpoint_overrides_backfill(self):
        end = date(2026, 4, 10)
        state = {"last_finalized_date": "2026-04-05"}
        start = resolve_analytics_start_date(state, end, 30)
        self.assertEqual(start, date(2026, 4, 5))

    def test_invalid_checkpoint_falls_back_to_backfill(self):
        end = date(2026, 4, 10)
        start = resolve_analytics_start_date({"last_finalized_date": "bad-date"}, end, 7)
        self.assertEqual(start, end - timedelta(days=7))


if __name__ == "__main__":
    unittest.main()
