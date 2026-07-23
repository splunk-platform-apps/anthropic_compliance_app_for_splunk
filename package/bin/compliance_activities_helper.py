import import_declare_test

from ta_anthropic_claude_enterprise.inputs.compliance_activities import (
    stream_events as _stream_events,
)
from ta_anthropic_claude_enterprise.inputs.compliance_activities import (
    validate_input as _validate_input,
)


def validate_input(definition):
    return _validate_input(definition)


def stream_events(inputs, event_writer):
    return _stream_events(inputs, event_writer)
