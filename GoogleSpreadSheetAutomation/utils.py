# Just simple function to break script
import sys
from json import load, JSONDecodeError

REPORT_CONFIG_FILE_NAME = "report_config.json"


def quit_script(reason=None):
    if reason:
        print(reason)
    sys.exit(0)


def get_dict_from_report_config(key_to_fetch):
    """
    As we have added Json file for Report config, This method use it to get dict object out of it
    :return:
    """
    try:
        with open(REPORT_CONFIG_FILE_NAME) as config_file:
            return load(config_file).get(key_to_fetch)

    except JSONDecodeError:
        quit_script("Please make sure that {} file is not corrupt".format(REPORT_CONFIG_FILE_NAME))
    except IOError:
        quit_script("Please make sure that {} file exists".format(REPORT_CONFIG_FILE_NAME))
