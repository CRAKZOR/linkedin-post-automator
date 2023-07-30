from datetime import datetime
from enum import Enum
import mimetypes

import json
from os import path


class MEDIA_CATEGORY(Enum):
    IMAGE = 1,
    # OTHERS


def custom_print(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")


def get_content_type(file_path):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type


def get_file_data (fname, protocol="r", incl_meta=False):
    # Load websites from the JSON file
    with open(fname, protocol) as file:
        data = None
        if "json" in str.lower(fname):
            data = json.load(file)
        else:
            data = file.read().strip()
        return ( data, path.getsize(fname), get_content_type(fname) ) if incl_meta else data

