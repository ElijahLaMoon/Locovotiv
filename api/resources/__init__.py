from flask import request
import json

# make a constant for how long until timeout
TOKEN_MINUTES = 120


def load_json():
    try:
        json_data = json.loads(request.get_json(force=True))
    except TypeError:
        json_data = request.get_json(force=True)

    return json_data
