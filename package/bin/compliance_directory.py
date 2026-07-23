import import_declare_test
import sys

from splunklib import modularinput as smi

import compliance_directory_helper


class ComplianceDirectoryModInput(smi.Script):
    def get_scheme(self):
        scheme = smi.Scheme("compliance_directory")
        scheme.title = "Compliance Directory Sync"
        scheme.description = "Sync Anthropic Compliance API users, organizations, and groups"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False
        for arg_name, title, required in (
            ("name", "Name", True),
            ("account", "Account", True),
        ):
            scheme.add_argument(
                smi.Argument(arg_name, title=title, required_on_create=required)
            )
        return scheme

    def validate_input(self, definition):
        return compliance_directory_helper.validate_input(definition)

    def stream_events(self, inputs, event_writer):
        return compliance_directory_helper.stream_events(inputs, event_writer)


if __name__ == "__main__":
    sys.exit(ComplianceDirectoryModInput().run(sys.argv))
