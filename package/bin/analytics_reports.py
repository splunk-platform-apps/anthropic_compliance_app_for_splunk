import import_declare_test
import sys

from splunklib import modularinput as smi

import analytics_reports_helper


class AnalyticsReportsModInput(smi.Script):
    def get_scheme(self):
        scheme = smi.Scheme("analytics_reports")
        scheme.title = "Analytics Reports"
        scheme.description = "Collect Claude Enterprise usage, cost, and adoption analytics"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False
        for arg_name, title, required in (
            ("name", "Name", True),
            ("account", "Account", True),
            ("bucket_width", "Usage bucket width", False),
            ("collect_summaries", "Collect summaries", False),
            ("collect_usage", "Collect usage report", False),
            ("collect_cost", "Collect cost report", False),
            ("collect_user_usage", "Collect per-user usage", False),
            ("collect_user_cost", "Collect per-user cost", False),
            ("collect_user_activity", "Collect user activity", False),
            ("collect_spend_limits", "Collect spend limits", False),
            ("backfill_days", "Initial backfill days", False),
        ):
            scheme.add_argument(
                smi.Argument(arg_name, title=title, required_on_create=required)
            )
        return scheme

    def validate_input(self, definition):
        return analytics_reports_helper.validate_input(definition)

    def stream_events(self, inputs, event_writer):
        return analytics_reports_helper.stream_events(inputs, event_writer)


if __name__ == "__main__":
    sys.exit(AnalyticsReportsModInput().run(sys.argv))
