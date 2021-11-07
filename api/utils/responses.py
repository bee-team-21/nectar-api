from api.models.result import Result
import ast
import os
from api import configuration
import traceback
import json

LANG = configuration.LANG
dirpath = os.path.dirname(__file__)
path = os.path.join(dirpath, "..", "lang", LANG)
dictionary = dict()
with open(path, encoding="utf-8") as fh:
    dictionary = json.load(fh)


def get_error_message(key="default"):
    message = get_message(type="error", key=key)
    return Result(code=0, message=message)


def get_success_message(key="default"):
    message = get_message(type="success", key=key)
    return Result(code=1, message=message)


def get_message(type="success", key="default"):
    try:
        message = dictionary[type][key]
        return message
    except:
        try:
            traceback.print_exc()
            return dictionary[type]["default"]
        except:
            traceback.print_exc()
            return 'Something went wrong with the dictionary "{0}"'.format(LANG)


class KEYS_SUCCESS:
    default = "default"
    send_notify = "send_notify"

class KEYS_ERROR:
    default = "default"
    token_no_valid = "token_no_valid"
    send_notify = "send_notify"