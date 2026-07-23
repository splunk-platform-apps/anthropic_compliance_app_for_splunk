
import import_declare_test

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    DataInputModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunktaucclib.rest_handler.admin_external import AdminExternalHandler
import logging

util.remove_http_proxy_env_vars()


special_fields = [
    field.RestField(
        'name',
        required=True,
        encrypted=False,
        default=None,
        validator=validator.AllOf(
            validator.Pattern(
                regex=r"""^[a-zA-Z]\w*$""", 
            ), 
            validator.String(
                max_len=100, 
                min_len=1, 
            )
        )
    )
]

fields = [
    field.RestField(
        'interval',
        required=True,
        encrypted=False,
        default='86400',
        validator=validator.AllOf(
            validator.Pattern(
                regex=r"""^((?:-1|\d+(?:\.\d+)?)|(([\*\d{1,2}\,\-\/]+\s){4}[\*\d{1,2}\,\-\/]+))$""", 
            ), 
            validator.Number(
                max_val=604800, 
                min_val=3600, 
            )
        )
    ), 
    field.RestField(
        'index',
        required=False,
        encrypted=False,
        default='default',
        validator=validator.IndexName()
    ), 
    field.RestField(
        'account',
        required=True,
        encrypted=False,
        default=None,
        validator=None
    ), 
    field.RestField(
        'bucket_width',
        required=False,
        encrypted=False,
        default='1d',
        validator=None
    ), 
    field.RestField(
        'collect_summaries',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_usage',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_cost',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_user_usage',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_user_cost',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_user_activity',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'collect_spend_limits',
        required=False,
        encrypted=False,
        default=True,
        validator=None
    ), 
    field.RestField(
        'backfill_days',
        required=False,
        encrypted=False,
        default='7',
        validator=None
    ), 

    field.RestField(
        'disabled',
        required=False,
        validator=None
    )

]
model = RestModel(fields, name=None, special_fields=special_fields)



endpoint = DataInputModel(
    'analytics_reports',
    model,
)


if __name__ == '__main__':
    logging.getLogger().addHandler(logging.NullHandler())
    admin_external.handle(
        endpoint,
        handler=AdminExternalHandler,
    )
