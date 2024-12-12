import streamlit as st
import pymongo
from bson.json_util import dumps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from datetime import datetime
import uuid
uri = r"mongodb+srv://zijiel18:zijiel18@iot.uel8j.mongodb.net/?retryWrites=true&w=majority&appName=IoT"


# Main page
def main_page():
    st.title("Welcome to the Training Plan App")
    st.write("Your personal fitness journey starts here!")

    # Displaying the slogan
    st.subheader("Discipline today, freedom tomorrow")

    # Create two options (buttons) to navigate to different pages
    option = st.radio(
        "Select a option:",
        ("Create Training Plan", "View Training Records")
    )

    if option == "Create Training Plan":
        create_training_plan()
    elif option == "View Training Records":
        view_training_records()

# Page to create a training plan
def create_training_plan():
    client = pymongo.MongoClient(uri)
    db = client.spt

    st.title("Create a New Training Plan")

    # Placeholder for the training plan creation form (reusing your previous code)
    st.write("Please enter your exercise details below and save them.")

    # Initialize the training plan session
    if "training_plans" not in st.session_state:
        st.session_state.training_plans = []

    def add_exercise():
        st.session_state.training_plans.append(
            {"exercise_type": "", "weight": 0.0, "sets": 3, "reps": 10, "rest_time": 60}
        )

    def remove_exercise(index):
        if 0 <= index < len(st.session_state.training_plans):
            st.session_state.training_plans.pop(index)

    if st.button("Add New Exercise"):
        add_exercise()

    st.subheader("Fill in the Training Plan")
    for i, plan in enumerate(st.session_state.training_plans):
        st.write(f"### Exercise {i + 1}")
        plan["exercise_type"] = st.text_input(
            f"Exercise Type {i + 1}", value=plan["exercise_type"], placeholder="e.g., Squats", key=f"exercise_{i}"
        )
        plan["weight"] = st.number_input(
            f"Weight (kg) {i + 1}", value=plan["weight"], min_value=0.0, step=0.1, key=f"weight_{i}"
        )
        plan["sets"] = st.number_input(
            f"Number of Sets {i + 1}", value=plan["sets"], min_value=1, step=1, key=f"sets_{i}"
        )
        plan["reps"] = st.number_input(
            f"Reps per Set {i + 1}", value=plan["reps"], min_value=1, step=1, key=f"reps_{i}"
        )
        plan["rest_time"] = st.number_input(
            f"Rest Time Between Sets (seconds) {i + 1}", value=plan["rest_time"], min_value=0, step=1, key=f"rest_{i}"
        )
        if st.button(f"Remove Exercise {i + 1}", key=f"remove_{i}"):
            remove_exercise(i)

    if st.button("Save All Training Plans"):
        st.success("All training plans have been successfully saved!")
        st.write("Your training plans:")
        st.json(st.session_state.training_plans)

        plan_record = {
            "plan_id": "plan_" + uuid.uuid4().hex[:10],
            "device_id": 1,
            "date": datetime.now(),
            "exercises": st.session_state.training_plans
        }

        db.plans.insert_one(plan_record)


# Page to view training records
def view_training_records():
    st.title("View Your Training Records")

    # Placeholder for dummy training records (this would be pulled from a database in the real application)
    dummy_records = [
        {"exercise_type": "Squats", "weight": 60, "sets": 5, "reps": 10, "rest_time": 30},
        {"exercise_type": "Bench Press", "weight": 40, "sets": 4, "reps": 12, "rest_time": 30},
    ]

    if dummy_records:  # Replace with actual data from your database
        for i, record in enumerate(dummy_records, start=1):
            st.write(f"**Record {i}:**")
            st.json(record)
    else:
        st.info("No training records found.")
    
    client = pymongo.MongoClient(uri)
    db = client.spt
    cursor = db.motions.find().sort('start_date', -1).skip(3).limit(1)  # 跳过第一个，限制返回一个文档
    result = list(cursor)  # 转为列表
    if result:
        doc = result[0]  # 提取第二大的文档
    else:
        print("No data found.")

    n = 3
    time = doc['timestamp']
    acc_x = doc['acc_x']
    acc_y = doc['acc_y']
    acc_z = doc['acc_z']
    total_acc = np.sqrt(np.array(acc_x)**2 + np.array(acc_y)**2 + np.array(acc_z)**2)

    peaks, _ = find_peaks(total_acc)
    peak_times = [time[i] for i in peaks]
    peak_values = [total_acc[i] for i in peaks]

    # 获取最大的三个峰值及其时间
    sorted_indices = np.argsort(peak_values)[-n:]
    top_peak_times = [peak_times[i] for i in sorted_indices]
    top_peak_values = [peak_values[i] for i in sorted_indices]

    # 按时间排序
    sorted_peaks = sorted(zip(top_peak_times, top_peak_values), key=lambda x: x[0])
    top_peak_times, top_peak_values = zip(*sorted_peaks)

    gaps = []
    for i in range(len(sorted_peaks)):
        if i == 0:
            print(sorted_peaks[i][0])
            gaps.append(sorted_peaks[i][0]/1000) 
        else:
            print(sorted_peaks[i][0]-sorted_peaks[i-1][0])
            gaps.append((sorted_peaks[i][0]-sorted_peaks[i-1][0])/1000)

    plt.bar(range(1,n+1),gaps)
    ticks = []
    for i in range(1,n+1):
        ticks.append('rep '+str(i))
    plt.xticks(range(1,n+1),ticks)
    st.pyplot(plt)



# Run the app
if __name__ == "__main__":
    main_page()
