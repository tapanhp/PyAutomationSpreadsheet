import datetime
import logging
import os
import time
from pathlib import Path

import pandas as pd
from dateutil.parser import parse
from pandas.errors import EmptyDataError

from constants import ERROR_UNKNOWN_RUNTIME_EXCEPTION, CSV_DATE_COL, CAMPAIGN_COL, \
    CSV_SPEND_COL, TAB_TYPE_DAILY, TAB_TYPE_MONTHLY, \
    WSHEET_DAILY_DATE_COL, WSHEET_MARGIN_COL_DAILY, WSHEET_MARGIN_COL_MONTHLY, WSHEET_MONTHLY_MONTH_COL, \
    WSHEET_MONTHLY_YEAR_COL, CSV_DATE_FORMAT
from constants import REPORT_TYPE
from constants import csv_column_name_reference_list
from utils import quit_script

WARNING_PLEASE_ENTER_VALID_REPORT_TYPE = "Please select valid Report."
WARNING_PLEASE_ENTER_NUMBER_ONLY = "Please enter numeric value only for file number"

"""
    COMMON NOTES
    
    Local files must have dates in dd-mm-yyyy format always
    Spreadsheet files must have dates in mm-dd-yyyy format always
"""


def get_input_file_csv(input_path):
    """
    As there is only single file in input we will just return that.
    This will eliminate the dynamic Logic
    param: input_path => Input directory path where to take reports from
    """

    if not __is_valid_dir(input_path):
        quit_script("{} is not a valid directory, Please make sure that directory exists.".format(input_path))

    try:
        first_csv_file = [i for i in os.listdir(input_path) if i.endswith('.csv')]
        if first_csv_file:
            return first_csv_file[0]
        else:
            raise NotImplementedError

    except NotImplementedError:
        raise Exception("No CSV files in {}. Please add the file and try again!".format(input_path))


def select_type_of_report_from_name(report_name):
    """
    This fun was created after change given by Andy
    and deprecating @show_report_options_and_select and @select_type_of_report
    :param report_name: Name of the report must exists in report config file.
    :return: dict : A specific report object dict from list of report objects in config file
    """
    report_obj = list(filter(lambda item: item[REPORT_TYPE] == report_name.strip(), csv_column_name_reference_list))
    return report_obj[0] if report_obj else quit_script("Please provide valid report name")


def calculate_margin(org, margin):
    """

    :param org: The original cell value from local CSV on which we need to apply logic
    :param margin: The margin value from Spread sheet to be applied using below calculation
    :return: float: Newly calculated value
    """
    try:
        original = float(org)
        margin = float(margin)

        if original == 0:
            return original
        else:
            return (original / (1 - margin / 100)) if margin > 0 else original
    except TypeError:
        quit_script("Spreadsheet or CSV may have some value which is not a number.")
    except ZeroDivisionError:
        quit_script("Divided by 0")


def get_daily_dataframe_from_sheet(wsheet_dict):
    """
    GET DATAFRAME OBJECT OF DAILY SHEET
    :param wsheet_dict:
    :return:
    """
    try:
        daily_sheet = wsheet_dict.get(TAB_TYPE_DAILY)
        return pd.DataFrame(daily_sheet.get_all_records())
    except AttributeError:
        return pd.DataFrame()
    except ValueError:
        return pd.DataFrame()


def get_monthly_dataframe_from_sheet(wsheet_dict):
    """
    GET DATAFRAME OBJECT OF MONTHLY SHEET
    :param wsheet_dict:
    :return:
    """
    try:
        monthly_sheet = wsheet_dict.get(TAB_TYPE_MONTHLY)
        return pd.DataFrame(monthly_sheet.get_all_records())
    except AttributeError:
        return pd.DataFrame()
    except ValueError:
        return pd.DataFrame()


def write_output_csv_file(report_obj, worksheets_dict: dict, input_path: str, output_path: str):
    """
    :param worksheets_dict:
    :param report_obj: The report type of file
    :param input_path: Input directory path to fetch the file from
    :param output_path: Output directory path so save the file
    :return:
    """

    filename = get_input_file_csv(input_path)

    try:
        local_csv_df = pd.read_csv(os.path.join(input_path, filename))

        # Safe check for local CSV data
        if local_csv_df.empty:
            quit_script("There is no data in input CSV file")

        daily_sheet_df = get_daily_dataframe_from_sheet(worksheets_dict)
        monthly_sheet_df = get_monthly_dataframe_from_sheet(worksheets_dict)

        # safe check of both type spread sheet data
        if daily_sheet_df.empty and monthly_sheet_df.empty:
            quit_script("Spread sheets empty")

        # main method call which manages everything
        process_sheets(filename, local_csv_df, report_obj, daily_sheet_df, monthly_sheet_df, output_path)

    except EmptyDataError:
        quit_script("No columns to parse from file, check if CSV and sheet has data")
    except KeyError as ke:
        logging.exception(ke)
        quit_script("Error while reading the Column with key {} from Spread sheet or CSV ".format(ke.args[0]))
    except ValueError as ve:
        # from dataframe get_all_records
        logging.exception(ve)
        quit_script(ERROR_UNKNOWN_RUNTIME_EXCEPTION)
    except IndexError as ie:
        logging.exception(ie)
        quit_script(ERROR_UNKNOWN_RUNTIME_EXCEPTION)
    except IOError as e:
        logging.exception(e)
        quit_script(ERROR_UNKNOWN_RUNTIME_EXCEPTION)
    except Exception as e:
        logging.exception(e)
        quit_script(ERROR_UNKNOWN_RUNTIME_EXCEPTION)


# As discussed in Slack chat with Francis: January 7th 2020, Change due to dynamic date format in local CSV files
def managed_dates_in_local_csv(report_obj, local_csv_df):
    """
    This function is to manage different types of date format in each report
    We need to always match the dd-MM-YYYY format as from Google sheet the coming format will always be
    MM-DD-YYYY and we are converting it to DD-MM-YYYY

    Whatever date comes in this function It must be converted to DD-MM-YYYY
    So,
    We first convert the date format from defined format in config file to DD-MM-YYYY format and then
    we will pass that to @process_sheets
    :return:
    """
    local_date = report_obj[CSV_DATE_COL]

    update_dates = local_csv_df[local_date].copy()
    local_csv_df.loc[:, local_date] = update_dates.apply(
        lambda date: datetime.datetime.strptime(date, report_obj[CSV_DATE_FORMAT]).strftime('%d-%m-%Y'))


def process_sheets(filename, local_csv_df, report_obj, worksheet_daily_df, worksheet_monthly_df, output_path):
    """
    This function is like major function for whole logic. Here, we check the value matching
    of Local CSV and Spreadsheet data.
    First it will check which kind of sheets are available?
    We basically try to match Local CSV's Date + Campaign to Spreadsheets Daily tab's Date + Campaign column values
    If it doesn't get any match then we check If same month's margin value is available in Monthly sheet and by
    comparing YEAR + MONTH to Local file date's Month year values and apply default margin if matches
    If nothing matches then we will skip that entry.

    :param filename: Current File name, For creating output file with same name
    :param local_csv_df: DataFrame for local CSV
    :param report_obj: The Report config for Any report type
    :param worksheet_daily_df: Dataframe for Daily Spreadsheet : Can be empty
    :param worksheet_monthly_df: Dataframe for Monthly Spreadsheet : Can be empty
    :param output_path: Path to output directory
    :return:
    """

    campaign_header = report_obj[CAMPAIGN_COL]
    local_date_header = report_obj[CSV_DATE_COL]
    wsheet_margin_header_daily = report_obj[WSHEET_MARGIN_COL_DAILY]
    wsheet_margin_header_monthly = report_obj[WSHEET_MARGIN_COL_MONTHLY]

    """
    This way we will remove all the junk details, basically it checks for which row the date and report 
    column values are Nan, Wherever it matched we take data upto the one row above that only.
    Why? Because as the gitlab issue was raised that files will contain junk values and we need to eliminate
    them from the output generated files as well. 
    What I did here is from very first I just removed rows like that from Original dataframe itself.
    So the generated file will be accurate
    """

    try:
        junk_condition = local_csv_df[campaign_header].isna() & local_csv_df[local_date_header].isna()
        slashed_df = (local_csv_df[:local_csv_df.index[junk_condition][0]])
        local_csv_df = slashed_df

    except IndexError:
        print("There is no Junk data in original file")

    managed_dates_in_local_csv(report_obj=report_obj, local_csv_df=local_csv_df)

    # As we have multiple columns in some reports,
    spend_col_name_list = [x.strip() for x in report_obj[CSV_SPEND_COL].split(',')]

    # If data in worksheet daily
    if not worksheet_daily_df.empty:
        # From daily sheets the format will always be MM-DD-YYYY so changed it to DD-MM-YYYY for consistency
        # As discussed in Slack chat with Francis: January 7th 2020
        worksheet_daily_df[WSHEET_DAILY_DATE_COL] = pd.to_datetime(
            worksheet_daily_df[WSHEET_DAILY_DATE_COL]).dt.strftime("%d-%m-%Y")

        for idx, row in local_csv_df.iterrows():
            local_date = getattr(row, local_date_header)
            local_campaign = getattr(row, campaign_header)

            daily_matched_df = worksheet_daily_df.loc[(worksheet_daily_df[WSHEET_DAILY_DATE_COL] == local_date) & (
                    worksheet_daily_df[campaign_header] == local_campaign)]

            # daily was not empty but didn't matched
            if not daily_matched_df.empty:
                for column in spend_col_name_list:
                    local_csv_df.at[idx, column] = calculate_margin(getattr(row, column),
                                                                    daily_matched_df[
                                                                        wsheet_margin_header_daily].values[0])
            # Then we checked if monthly has some data
            elif not worksheet_monthly_df.empty:

                month_value_match = worksheet_monthly_df[WSHEET_MONTHLY_MONTH_COL] == parse(local_date,
                                                                                            dayfirst=True).month
                year_value_match = worksheet_monthly_df[WSHEET_MONTHLY_YEAR_COL] == parse(local_date,
                                                                                          dayfirst=True).year
                campaign_match = (worksheet_monthly_df[campaign_header] == local_campaign)

                monthly_matched_df = worksheet_monthly_df.loc[year_value_match & month_value_match & campaign_match]

                # Monthly also didn't matched
                if not monthly_matched_df.empty:
                    for column in spend_col_name_list:
                        local_csv_df.at[idx, column] = calculate_margin(getattr(row, column),
                                                                        monthly_matched_df[
                                                                            wsheet_margin_header_monthly].
                                                                        values[0])
                else:
                    # Checked Daily and monthly both not matched in any of them
                    raise_row_not_matched(
                        "Checked Daily and monthly both. Not matched in any of them for date {} and campaign {}".format(
                            local_date, local_campaign))

            else:
                raise_row_not_matched(
                    " Not matched in daily and there was not any data in monthly sheet for date {} and campaign {}".format(
                        local_date, local_campaign))

    # If Daily spreadsheet is empty we will directly check the monthly sheet and check that only
    else:
        for idx, row in local_csv_df.iterrows():
            local_date = getattr(row, local_date_header)
            local_campaign = getattr(row, campaign_header)

            month_value_match = worksheet_monthly_df[WSHEET_MONTHLY_MONTH_COL] == parse(local_date, dayfirst=True).month
            year_value_match = worksheet_monthly_df[WSHEET_MONTHLY_YEAR_COL] == parse(local_date, dayfirst=True).year
            campaign_match = (worksheet_monthly_df[campaign_header] == local_campaign)

            monthly_matched_df = worksheet_monthly_df.loc[year_value_match & month_value_match & campaign_match]
            if not monthly_matched_df.empty:
                for column in spend_col_name_list:
                    local_csv_df.at[idx, column] = calculate_margin(getattr(row, column),
                                                                    monthly_matched_df
                                                                    [wsheet_margin_header_monthly].values[0])
            else:
                raise_row_not_matched(
                    " No data in daily sheet and no match value in monthly sheet for date {} and campaign {}".format(
                        local_date, local_campaign))

    # At last writing output file
    write_output(filename, local_csv_df, output_path, report_obj)


def write_output(filename, df, output_path, report_obj):
    """
    Checks if output directory doesn't exists => Create one, At last this func will be used to writing output file
    :param report_obj: Config Json report object
    :param filename: The actual input file name.
    :param df: The dataframe object of modified input file.
    :param output_path: Path to output dir
    :return: None
    """

    # Converting the date format again in YYYY-MM-DD as suggested by Francis
    # in slack on 8th Jan 2020
    local_date = report_obj[CSV_DATE_COL]
    update_dates = df[local_date].copy()
    df.loc[:, local_date] = update_dates.apply(
        lambda date: datetime.datetime.strptime(date, "%d-%m-%Y").strftime('%Y-%m-%d'))

    if not __is_valid_dir(dir_path=output_path):
        os.mkdir(output_path)

    output_name, extension = os.path.splitext(filename)
    df.to_csv(os.path.join(output_path, output_name + "_"
                           + time.strftime('%Y-%m-%d_%H_%M_%S') + extension), index=False)


def __is_valid_dir(dir_path):
    """
    :param dir_path: The directory path to check
    This function called from @write_output to ensure there must be OUTPUT_DIR_NAME folder created
    :return:
    """
    # Safe check for output dir, creates if not exists OUTPUT_DIR_NAME
    path = Path(dir_path)
    return os.path.exists(path)


def raise_row_not_matched(message_for_exception):
    """
    Just raise a simple custom exception and print relevant message
    """
    raise RowNotMatchedException(message_for_exception)


class RowNotMatchedException(Exception):
    """
    A custom exception class: Child of Exception
    """
    pass
