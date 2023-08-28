
import json

class CException(Exception):
    def __init__(self, message, *args):

        error_obj = {
            "code": message,
            "args": args,
        }

        str_error_obj = json.dumps(error_obj, ensure_ascii=False)

        self.args = [str_error_obj]
