import import_declare_test
import sys

from splunklib import modularinput as smi

import compliance_activities_helper


class ComplianceActivitiesModInput(smi.Script):
    def get_scheme(self):
        scheme = smi.Scheme("compliance_activities")
        scheme.title = "Compliance Activity Feed"
        scheme.description = "Poll Anthropic Compliance API activity feed"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False
        for arg_name, title, required in (
            ("name", "Name", True),
            ("account", "Account", True),
            ("backfill_days", "Initial backfill days", False),
            ("max_events_per_cycle", "Max events per cycle", False),
        ):
            scheme.add_argument(
                smi.Argument(arg_name, title=title, required_on_create=required)
            )
        return scheme

    def validate_input(self, definition):
        return compliance_activities_helper.validate_input(definition)

    def stream_events(self, inputs, event_writer):
        return compliance_activities_helper.stream_events(inputs, event_writer)


if __name__ == "__main__":
    sys.exit(ComplianceActivitiesModInput().run(sys.argv))
