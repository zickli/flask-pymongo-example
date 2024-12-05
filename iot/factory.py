import os

from flask import Flask, render_template
from json import JSONEncoder
from flask_cors import CORS

from bson import json_util, ObjectId
from datetime import datetime, timedelta

from iot.api.trainer import trainer_api_v1


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            print("RRRUNRUNRUNRUNRUNRU")
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def create_app():
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(APP_DIR, 'build/static')
    TEMPLATE_FOLDER = os.path.join(APP_DIR, 'build')

    app = Flask(__name__, static_folder=STATIC_FOLDER,
                template_folder=TEMPLATE_FOLDER,
                )
    CORS(app)
    app.json_provider_class = MongoJsonEncoder
    app.register_blueprint(trainer_api_v1)

    return app
