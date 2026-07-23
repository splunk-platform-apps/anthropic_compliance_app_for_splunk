import import_declare_test
import sys

from splunklib import modularinput as smi

import compliance_content_helper


class ComplianceContentModInput(smi.Script):
    def get_scheme(self):
        scheme = smi.Scheme("compliance_content")
        scheme.title = "Compliance Content (On-Demand)"
        scheme.description = "On-demand chat and file content collection"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False
        for arg_name, title, required in (
            ("name", "Name", True),
            ("account", "Account", True),
            ("collection_mode", "Collection mode", True),
            ("target_user_email", "Target user email", False),
            ("target_chat_id", "Target chat ID", False),
            ("target_file_id", "Target file ID", False),
            ("include_messages", "Include message bodies", False),
            ("max_chats", "Max chats per run", False),
        ):
            scheme.add_argument(
                smi.Argument(arg_name, title=title, required_on_create=required)
            )
        return scheme

    def validate_input(self, definition):
        return compliance_content_helper.validate_input(definition)

    def stream_events(self, inputs, event_writer):
        return compliance_content_helper.stream_events(inputs, event_writer)


if __name__ == "__main__":
    sys.exit(ComplianceContentModInput().run(sys.argv))
