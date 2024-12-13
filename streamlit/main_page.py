import streamlit as st
import pymongo
from bson.json_util import dumps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from datetime import datetime
import uuid
from datetime import datetime, timedelta

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


def view_training_records():
    st.title("View Your Training Records")

    client = pymongo.MongoClient(uri)
    db = client.spt

    
    latest_record = db.motions.find().sort('start_date', -1).limit(1)
    latest_record = list(latest_record)
    if not latest_record:
        st.write("No records found.")
        return

    device_number = latest_record[0]['device_id']
    plan_id = latest_record[0]['plan_id']
    records = db.motions.find({
        'device_id': device_number,
        'plan_id': plan_id
    }).sort('start_date', 1)

    for record in records:
        n = record['reps']
        time = record['timestamp']
        
        time_str = (record["start_date"]-timedelta(hours=8)).strftime(r"%Y-%m-%d %H:%M:%S")
        acc_x = record['acc_x']
        acc_y = record['acc_y']
        acc_z = record['acc_z']

        total_acc = np.sqrt(np.array(acc_x)**2 + np.array(acc_y)**2 + np.array(acc_z)**2)

        peaks, _ = find_peaks(total_acc,distance=30)
        peak_times = [time[i] for i in peaks]
        peak_values = [total_acc[i] for i in peaks]

        sorted_indices = np.argsort(peak_values)[-n:]
        top_peak_times = [peak_times[i] for i in sorted_indices]
        top_peak_values = [peak_values[i] for i in sorted_indices]

        sorted_peaks = sorted(zip(top_peak_times, top_peak_values), key=lambda x: x[0])
        top_peak_times, top_peak_values = zip(*sorted_peaks) if sorted_peaks else ([], [])

        gaps = []
        for i in range(len(sorted_peaks)):
            if i == 0:
                gaps.append(sorted_peaks[i][0] / 1000)  
            else:
                gaps.append((sorted_peaks[i][0] - sorted_peaks[i - 1][0]) / 1000)

        set_num = record["set_idx"]
        st.write(f"### Plan ID: {plan_id},{record['exercise_name']}, Set:{set_num}")
        st.write(f"Finished at: {time_str}")
        plt.figure(figsize=(8, 4))
        plt.bar(range(1, n + 1), gaps, color='skyblue')
        ticks = [f'Rep {i}' for i in range(1, n + 1)]
        plt.xticks(range(1, n + 1), ticks)
        plt.xlabel('Repetitions')
        plt.ylabel('Time(seconds)')
        st.pyplot(plt)


    client.close()

# Run the app
if __name__ == "__main__":
    main_page()
