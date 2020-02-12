import argparse
import os
import sys

from cloud_module.cloud_operations import get_spreadsheet
from constants import REPORT_TYPE, ERROR_INVALID_ARGS
from local_module.local_operations import write_output_csv_file, select_type_of_report_from_name
from utils import quit_script

"""
We need to execute this line to add Current directory in PATH variable 
As, Python needs to trace cross package modules.
"""
sys.path.append(os.getcwd())


def start_everything(input_dir, output_dir, report_name):  # report_name=None, local_file=None
    """
    Initial point of interaction from App.py.
    """

    # STEP 1: GET LOCAL FILE NAME TO PROCESS
    # local_file = get_csv_file_name_from_user()

    # STEP 2: ASK USER TO PROVIDE REPORT TYPE FOR SELECTED LOCAL FILE, To MANAGE NAMES DYNAMICALLY
    report_obj = select_type_of_report_from_name(report_name)

    # STEP 3: BASED ON @report_type FETCH WORKSHEET AND TYPE SPREADSHEET : MONTHLY/DAILY
    worksheets = get_spreadsheet(report_obj[REPORT_TYPE])

    # STEP 4: BASED ON DATA FROM LOCAL AND SPREADSHEET APPLY OPERATION
    write_output_csv_file(report_obj=report_obj, worksheets_dict=worksheets, input_path=input_dir,
                          output_path=output_dir)  # filename=local_file,


# just for convenient testing
# def call_without_args():
#     start_everything("input", "output", REPORT_TYPE_DBM_WEB)


if __name__ == "__main__":
    """
    We should take exactly three command line arguments
        Input:  Input directory path from where we will take the first file
        Output: The output directory where we will write files
        Report type: The type of report to be generated
    """

    # call_without_args()

    try:
        argparser = argparse.ArgumentParser(description="Please provide report type, input and output folders")

        argparser.add_argument("--input", type=str, help="Path of the directory from where original report is coming")
        argparser.add_argument("--output", type=str, help="Path of the directory where modified report will be saved")
        argparser.add_argument("--report_type", type=str, help="Type of report")

        args = argparser.parse_args()

        input_path = args.input
        output_path = args.output
        report_type = args.report_type

        if input_path and output_path and report_type:
            start_everything(input_path, output_path, report_type)
        else:
            quit_script(ERROR_INVALID_ARGS)

    except argparse.ArgumentError:
        quit_script(ERROR_INVALID_ARGS)
    except argparse.ArgumentTypeError:
        quit_script(ERROR_INVALID_ARGS)
