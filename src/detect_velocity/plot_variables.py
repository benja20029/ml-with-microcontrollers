"""
This module aims to convert the data get from the microcontroller, to a handleable
visualization that allows to see how the different variables behavior through time.
"""

import sys
import time
from collections import deque

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox
from serial import Serial

# Check if the CSV file name was passed as a command-line argument
if len(sys.argv) > 1:
    csv_filename = sys.argv[1]
else:
    print(
        "CSV file name not provided. Please provide a CSV file name as a command-line"
        " argument."
    )
    sys.exit()

# USB PORT
port_name: str = "/dev/tty.usbserial-0001"

# Create Serial object:
ser = Serial(port_name, baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0)

# Maximum number of data points to show on the plot
max_length: int = 100
acc_x, acc_y, acc_z = (
    deque(maxlen=max_length),
    deque(maxlen=max_length),
    deque(maxlen=max_length),
)
gyro_x, gyro_y, gyro_z = (
    deque(maxlen=max_length),
    deque(maxlen=max_length),
    deque(maxlen=max_length),
)
temp = deque(maxlen=max_length)

# Initialize flags and data containers
recording = False
data_store = {
    "time": [],
    "acc_x": [],
    "acc_y": [],
    "acc_z": [],
    "gyro_x": [],
    "gyro_y": [],
    "gyro_z": [],
    "temp": [],
}


def save_data(data):
    """
    Save the data collected from the microcontroller to a CSV file.

    Args:
        data (dict): Dictionary with the data collected from the microcontroller.
    """
    collected_data_df = pd.DataFrame(data)
    collected_data_df.to_csv(f"data_collection/{csv_filename}.csv", index=False)
    print(f"Data saved to {csv_filename}.csv.")


# This function is called periodically from FuncAnimation
def animate():
    """
    Update the data of the plots, and store the data if the recording flag is True.
    """
    if ser.in_waiting:
        line = ser.readline()
        try:
            decoded_line = line.decode("utf-8").strip()
            data = decoded_line.split(",")
            if len(data) == 7 and all(d.strip() for d in data):
                # Store timestamp
                current_time = time.time()
                acc_x.append(float(data[0]))
                acc_y.append(float(data[1]))
                acc_z.append(float(data[2]))
                gyro_x.append(float(data[3]))
                gyro_y.append(float(data[4]))
                gyro_z.append(float(data[5]))
                temp.append(float(data[6]))

                # Update the data of each line object
                lines["acc_x"].set_data(range(len(acc_x)), acc_x)
                lines["acc_y"].set_data(range(len(acc_y)), acc_y)
                lines["acc_z"].set_data(range(len(acc_z)), acc_z)
                lines["gyro_x"].set_data(range(len(gyro_x)), gyro_x)
                lines["gyro_y"].set_data(range(len(gyro_y)), gyro_y)
                lines["gyro_z"].set_data(range(len(gyro_z)), gyro_z)
                lines["temp"].set_data(range(len(temp)), temp)

                # Dynamically adjust the x-axis limits
                for ax_row in axs:
                    for axis in ax_row:
                        axis.set_xlim(0, len(acc_x))

                axs_1.set_xlim(0, len(acc_x))
                # Adjust y-axis limits
                axs[0][0].set_ylim(-30, 30)
                axs[0][1].set_ylim(-30, 30)
                axs[0][2].set_ylim(-30, 30)
                axs[1][0].set_ylim(-15, 15)
                axs[1][1].set_ylim(-15, 15)
                axs[1][2].set_ylim(-15, 15)
                axs_1.set_ylim(25, 35)

                # If recording, store the data
                if recording:
                    data_store["time"].append(current_time)
                    data_store["acc_x"].append(acc_x[-1])
                    data_store["acc_y"].append(acc_y[-1])
                    data_store["acc_z"].append(acc_z[-1])
                    data_store["gyro_x"].append(gyro_x[-1])
                    data_store["gyro_y"].append(gyro_y[-1])
                    data_store["gyro_z"].append(gyro_z[-1])
                    data_store["temp"].append(temp[-1])

        except UnicodeDecodeError:
            print("UnicodeDecodeError")


# Initialize your figure and subplots
fig, axs = plt.subplots(3, 3, figsize=(30, 12))

# Remove original axes
for ax in axs[2]:
    fig.delaxes(ax)

# Use the final row for only one plot
axs_1 = plt.subplot2grid((3, 3), loc=(2, 0), colspan=3, fig=fig)

# Create line objects for each type of data
lines = {
    "acc_x": axs[0][0].plot([], [], label="Acc X")[0],
    "acc_y": axs[0][1].plot([], [], label="Acc Y")[0],
    "acc_z": axs[0][2].plot([], [], label="Acc Z")[0],
    "gyro_x": axs[1][0].plot([], [], label="Gyro X")[0],
    "gyro_y": axs[1][1].plot([], [], label="Gyro Y")[0],
    "gyro_z": axs[1][2].plot([], [], label="Gyro Z")[0],
    "temp": axs_1.plot([], [], label="Temperature")[0],
}
# Set labels and titles
axs[0][0].set_title("Acceleration X Axis")
axs[0][1].set_title("Acceleration Y Axis")
axs[0][2].set_title("Acceleration Z Axis")
axs[1][0].set_title("Gyro X Axis")
axs[1][1].set_title("Gyro Y Axis")
axs[1][2].set_title("Gyro Z Axis")
axs_1.set_title("Temperature")
axs_1.set_xlabel("Time")

# Set y-titles
axs[0][0].set_ylabel("Acceleration (m/s^2)")
axs[1][0].set_ylabel("Angular velocity (deg/s)")
axs_1.set_ylabel("Temperature (Celsius)")

# Adding legends
axs[0][2].legend(loc="upper right")
axs[1][2].legend(loc="upper right")
axs_1.legend(loc="upper right")

# Change color lines
axs[0][0].lines[0].set_color("red")
axs[0][1].lines[0].set_color("green")
axs[0][2].lines[0].set_color("blue")
axs[1][0].lines[0].set_color("red")
axs[1][1].lines[0].set_color("green")
axs[1][2].lines[0].set_color("blue")

# Add button
ax_button = plt.axes([0.92, 0.95, 0.05, 0.02])
button = plt.Button(ax_button, "Record", color="white")


# Button callback function
def button_callback(event):
    """
    Callback function for the button.

    Args:
        event (matplotlib.backend_bases.MouseEvent): Event object.
    """
    global recording, data_store
    if event.inaxes == ax_button:
        recording = not recording
        if recording:
            data_store = {key: [] for key in data_store}  # Reset data store
            button.label.set_text("Stop")

        else:
            button.label.set_text("Record")
            save_data(data_store)


# Add pause button
ax_button_pause = plt.axes([0.92, 0.92, 0.05, 0.02])
button_pause = plt.Button(ax_button_pause, "Pause", color="white")

# Add write filename box
ax_filename = plt.axes([0.92, 0.89, 0.05, 0.02])
text_box = TextBox(ax_filename, "Filename", initial="data")


# Add write filename box callback function
def text_box_callback(text):
    """
    Callback function for the text box.

    Args:
        text (str): Text entered in the box.
    """
    global csv_filename
    csv_filename = text


# Button callback function
def button_callback_pause(event):
    """
    Callback function for the button.

    Args:
        event (matplotlib.backend_bases.MouseEvent): Event object.
    """
    global recording
    if event.inaxes == ax_button_pause:
        recording = not recording
        if recording:
            button_pause.label.set_text("Pause")
        else:
            button_pause.label.set_text("Resume")


# Add button callback function
button.on_clicked(button_callback)
button_pause.on_clicked(button_callback_pause)
text_box.on_submit(text_box_callback)


# Set up plot to call animate() function periodically
ani = FuncAnimation(fig, animate, interval=0)  # Adjust the interval as needed

plt.show()
