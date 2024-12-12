"""
This module contains all database interfacing methods for the MFlix
application. You will be working on this file for the majority of M220P.

Each method has a short description, and the methods you must implement have
docstrings with a short explanation of the task.

Look out for TODO markers for additional help. Good luck!
"""
import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
import pymongo
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId
import csv
import io


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:
        uri = current_app.config.get("MONGO_URI", None)
        client = pymongo.MongoClient(uri)
        db = client.spt

    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def get_motion_count():
    result = db.motions.count_documents({})
    return result


def insert_record_to_motions(record):
    db.motions.insert_one(record)


def get_lastest_plan(device_id):
    lastest_plan = db.plans.find({"device_id": device_id}).sort("date", -1).limit(1)

    plan_list = list(lastest_plan)

    if len(plan_list) == 0:
        return None
    
    plan = plan_list[0]
    print(plan)
    return plan


def plan_to_csv(plan):
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    writer.writerow([plan['plan_id'], len(plan['exercises'])])
    
    for exercise in plan['exercises']:
        writer.writerow([
            exercise['exercise_type'],
            exercise['weight'],
            exercise['sets'],
            exercise['reps'],
            exercise['rest_time']
        ])
    
    csv_string = csv_buffer.getvalue()
    csv_buffer.close()

    return csv_string


def parse_motion_data(data):
    data_str = data.decode('utf-8')
    lines = data_str.strip().splitlines()
    
    first_line = lines[0].split(",")
    device_id = int(first_line[0])
    total_samples = int(first_line[1])

    assert len(first_line) == 2
    
    sensors = {
        "acc_x": [],
        "acc_y": [],
        "acc_z": [],
        "gyro_x": [],
        "gyro_y": [],
        "gyro_z": [],
        "timestamp": []
    }
    
    for line in lines[1:]:
        values = list(map(float, line.split(",")))
        assert len(values) == 7
        sensors["acc_x"].append(values[0])
        sensors["acc_y"].append(values[1])
        sensors["acc_z"].append(values[2])
        sensors["gyro_x"].append(values[3])
        sensors["gyro_y"].append(values[4])
        sensors["gyro_z"].append(values[5])
        sensors["timestamp"].append(values[6])
    
    return device_id, sensors

def parse_device_id(data):
    data_str = data.decode('utf-8')
    try:
        device_id = int(data_str.strip())
    except:
        device_id = 1
    return device_id