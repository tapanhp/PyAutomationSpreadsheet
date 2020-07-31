import re

import gspread
from gspread import SpreadsheetNotFound
from gspread.exceptions import APIError, WorksheetNotFound
from gspread.exceptions import GSpreadException
from oauth2client.service_account import ServiceAccountCredentials

from constants import TAB_TYPE_DAILY, TAB_TYPE_MONTHLY, ERROR_UNKNOWN_RUNTIME_EXCEPTION, spread_sheet_link, \
    google_creds_file
from utils import quit_script


def connect_spreadsheet():
    # Regex of checking proper spreadsheet link
    regex = re.compile('^(https://docs.google.com/spreadsheets/d/)w*')

    while True:
        try:
            spreadsheet_url = spread_sheet_link

            if regex.match(spreadsheet_url):
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

                # fetching credentials from json file
                credentials = ServiceAccountCredentials.from_json_keyfile_name(google_creds_file, scope)
                # authorizing spreadsheet credential
                client = gspread.authorize(credentials)
                return client.open_by_url(spreadsheet_url)

            else:
                print("Please enter valid link of spreadsheet")

        except EOFError as eof:
            quit_script("System Error while reading the spreadsheet link")

        except IOError as io_err:
            quit_script("Credential file with .json extension does not exist")

        except ValueError as val_err:
            quit_script("Credential type is not :data:`SERVICE_ACCOUNT`")

        except KeyError as key_err:
            quit_script("One of the expected keys is not present in the keyfile")

        except SpreadsheetNotFound as spr_nt_found:
            quit_script("Can't find spreadsheet on given URL. Please try again")

        except APIError as api_err:
            quit_script("API error while fetching spreadsheet, Check if you have provided authorisation in sheet")

        except GSpreadException as gspread_exception:
            quit_script("Error while loading the spreadsheet")

        except Exception as e:
            quit_script(ERROR_UNKNOWN_RUNTIME_EXCEPTION)


def get_spreadsheet(report_type):
    """
    For any given report type this method checks whether Relevant worksheets are available or not?
    This function basically checks whether data is available or not if tabs are available.
    :param report_type:
    :return:
    """
    dict_worksheet = {}
    try:
        sheet = connect_spreadsheet()
        worksheet_daily = sheet.worksheet(report_type + " - Daily")
        worksheet_monthly = sheet.worksheet(report_type + " - Monthly")

        if len(worksheet_daily.get_all_values()) > 1:
            dict_worksheet[TAB_TYPE_DAILY] = worksheet_daily

        if len(worksheet_monthly.get_all_values()) > 1:
            dict_worksheet[TAB_TYPE_MONTHLY] = worksheet_monthly

        # If no such data available in spread sheet then we will quit the script right away
        return dict_worksheet if dict_worksheet else quit_script(
            reason="There is no data in monthly and daily tab of {} sheet".format(report_type))

    except WorksheetNotFound as e:
        # Need to check this as may be exceptions could raise due to monthly sheet is not available but daily is,
        # then script must work.
        return dict_worksheet if dict_worksheet else quit_script("Work sheet not found related to this report type")
