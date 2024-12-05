from flask import Blueprint, request, jsonify
from iot.db import *

from flask_cors import CORS
from iot.api.utils import expect
from datetime import datetime

trainer_api_v1 = Blueprint(
    'spt_api_v1', 'spt_api_v1', url_prefix='/spt')

CORS(trainer_api_v1)


@trainer_api_v1.route('/', methods=['GET'])
def api_get_motions():
    response = {
        "count": get_motion_count(),
    }

    return jsonify(response)


@trainer_api_v1.route('/upload', methods=['POST'])
def api_upload():
    data = request.data
    device_id, sensors = parse_device_data(data)

    record = sensors
    record["device_id"] = device_id
    record["start_date"] = datetime.now()

    print(record)

    insert_record_to_motions(record)

    return "motion inserted", 200