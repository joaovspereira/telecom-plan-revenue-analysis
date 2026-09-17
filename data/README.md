# Data requirements

Supply your authorized original course files locally in this directory. These files are not bundled or downloaded automatically.

| File | Expected fields and units |
|---|---|
| `megaline_users.csv` | user_id, plan, reg_date, churn_date (blank for active users). |
| `megaline_plans.csv` | plan_name, usd_monthly_pay, minutes_included, messages_included, mb_per_month_included, usd_per_minute, usd_per_message, usd_per_gb. |
| `megaline_calls.csv` | id, user_id, call_date, duration in minutes. |
| `megaline_messages.csv` | id, user_id, message_date. |
| `megaline_internet.csv` | id, user_id, session_date, mb_used. All files comma-delimited. |

The notebook's synthetic example runs without these files. To analyze the original dataset, set `RUN_ORIGINAL_DATA = True` in `notebooks/analysis.ipynb` after adding them. The corrected implementation will compute new results; previous empirical outputs are not reused.

CSV, TSV, spreadsheets and this directory's datasets are excluded from Git by default. No permission to redistribute the original datasets is implied.
