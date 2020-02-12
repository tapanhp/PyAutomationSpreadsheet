# This file manages all the app level constants
# Todo : Manage these constants at file level
from utils import get_dict_from_report_config

# === Removed this constants as we need to take input and output directories dynamic
# INPUT_DIR_NAME = "input"
# OUTPUT_DIR_NAME = "output"

CAMPAIGN_COL = "campaign_col"
WSHEET_MARGIN_COL_MONTHLY = "monthly_margin_column_name"
WSHEET_MARGIN_COL_DAILY = "daily_margin_column_name"
WSHEET_DAILY_DATE_COL = "date"
WSHEET_MONTHLY_MONTH_COL = "month"
WSHEET_MONTHLY_YEAR_COL = "year"

CSV_DATE_COL = "csv_date_column"
CSV_SPEND_COL = "spend_col"
CSV_DATE_FORMAT = "csv_date_format"

ERROR_UNKNOWN_RUNTIME_EXCEPTION = "Unknown Runtime exception"
ERROR_SYSTEM_INPUT_READING = "System error while reading input"

# Report types
REPORT_TYPE = "report_type"
REPORT_TYPE_APPRECIATE = "Appreciate"
REPORT_TYPE_SMADEX = "Smadex"
REPORT_TYPE_TDD = "The Trade Desk"
REPORT_TYPE_DBM_WEB = "DBM (Web)"
REPORT_TYPE_DBM = "DBM"

TAB_TYPE_DAILY = 1
TAB_TYPE_MONTHLY = 2

ERROR_INVALID_ARGS = "Please provide valid report type, input and output folder paths"

WARNING_DEPRECATION_FOR_AUTOMATION = "Use this method only for local testing as this is automation script"

csv_column_name_reference_list = get_dict_from_report_config("reports")
spread_sheet_link = get_dict_from_report_config("spread_sheet")
google_creds_file = get_dict_from_report_config("google_credentials_file")
