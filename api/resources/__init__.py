from flask import request
import json


def load_json():
    try:
        json_data = json.loads(request.get_json(force=True))
    except TypeError:
        json_data = request.get_json(force=True)

    return json_data
