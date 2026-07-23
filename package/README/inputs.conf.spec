[compliance_activities://<name>]
account = 
backfill_days = (Default: 7)
index = (Default: default)
interval = (Default: 60)
max_events_per_cycle = (Default: 1000)
python.required = {3.7|3.9|3.13}
* For Python scripts only, selects which Python version to use.
* Set to "3.9" to use the Python 3.9 version.
* Set to "3.13" to use the Python 3.13 version.
* Optional.
* Default: not set

[compliance_directory://<name>]
account = 
index = (Default: default)
interval = (Default: 43200)
python.required = {3.7|3.9|3.13}
* For Python scripts only, selects which Python version to use.
* Set to "3.9" to use the Python 3.9 version.
* Set to "3.13" to use the Python 3.13 version.
* Optional.
* Default: not set

[compliance_content://<name>]
account = 
collection_mode = (Default: chat_id)
include_messages = 
index = (Default: default)
interval = (Default: 86400)
max_chats = (Default: 10)
target_chat_id = 
target_file_id = 
target_user_email = 
python.required = {3.7|3.9|3.13}
* For Python scripts only, selects which Python version to use.
* Set to "3.9" to use the Python 3.9 version.
* Set to "3.13" to use the Python 3.13 version.
* Optional.
* Default: not set

[analytics_reports://<name>]
account = 
backfill_days = Days of finalized analytics to collect on first run (max 90). Subsequent runs use checkpoint. (Default: 7)
bucket_width = (Default: 1d)
collect_cost = (Default: true)
collect_spend_limits = (Default: true)
collect_summaries = (Default: true)
collect_usage = (Default: true)
collect_user_activity = (Default: true)
collect_user_cost = (Default: true)
collect_user_usage = (Default: true)
index = (Default: default)
interval = (Default: 86400)
python.required = {3.7|3.9|3.13}
* For Python scripts only, selects which Python version to use.
* Set to "3.9" to use the Python 3.9 version.
* Set to "3.13" to use the Python 3.13 version.
* Optional.
* Default: not set
