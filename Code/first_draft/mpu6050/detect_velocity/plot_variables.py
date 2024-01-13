from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# USB PORT
portName = '/dev/tty.usbserial-0001'

# Create Serial object:
ser = Serial(portName, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1)

# Maximum number of data points to show on the plot
max_length = 100
acc_x, acc_y, acc_z = deque(maxlen=max_length), deque(maxlen=max_length), deque(maxlen=max_length)
gyro_x, gyro_y, gyro_z = deque(maxlen=max_length), deque(maxlen=max_length), deque(maxlen=max_length)
temp = deque(maxlen=max_length)

with ser:
    ser.reset_input_buffer()

    # Initialize your figure and subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))

    # Create line objects for each type of data
    lines = {
        'acc_x': axs[0].plot([], [], label='Acc X')[0],
        'acc_y': axs[0].plot([], [], label='Acc Y')[0],
        'acc_z': axs[0].plot([], [], label='Acc Z')[0],
        'gyro_x': axs[1].plot([], [], label='Gyro X')[0],
        'gyro_y': axs[1].plot([], [], label='Gyro Y')[0],
        'gyro_z': axs[1].plot([], [], label='Gyro Z')[0],
        'temp': axs[2].plot([], [], label='Temperature')[0],
    }

    # Set labels and titles
    axs[0].set_title('Acceleration')
    axs[1].set_title('Gyro')
    axs[2].set_title('Temperature')
    axs[2].set_xlabel('Time')

    # Set y-titles
    axs[0].set_ylabel('Acceleration (m/s^2)')
    axs[1].set_ylabel('Angular velocity (deg/s)')
    axs[2].set_ylabel('Temperature (Celsius)')

    # Adding legends
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')
    axs[2].legend(loc='upper right')

    # This function is called periodically from FuncAnimation
    def animate(i):
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            data = line.split(',')
            if len(data) == 7:
                acc_x.append(float(data[0]))
                acc_y.append(float(data[1]))
                acc_z.append(float(data[2]))
                gyro_x.append(float(data[3]))
                gyro_y.append(float(data[4]))
                gyro_z.append(float(data[5]))
                temp.append(float(data[6]))

                # Update the data of each line object
                lines['acc_x'].set_data(range(len(acc_x)), acc_x)
                lines['acc_y'].set_data(range(len(acc_y)), acc_y)
                lines['acc_z'].set_data(range(len(acc_z)), acc_z)
                lines['gyro_x'].set_data(range(len(gyro_x)), gyro_x)
                lines['gyro_y'].set_data(range(len(gyro_y)), gyro_y)
                lines['gyro_z'].set_data(range(len(gyro_z)), gyro_z)
                lines['temp'].set_data(range(len(temp)), temp)

                # Dynamically adjust the x-axis limits
                for ax in axs:
                    ax.set_xlim(0, len(acc_x))
                # Adjust y-axis limits
                axs[0].set_ylim(-30, 30)
                axs[1].set_ylim(-15, 15)
                axs[2].set_ylim(25, 30)

    # Set up plot to call animate() function periodically
    ani = FuncAnimation(fig, animate, interval=0)  # Adjust the interval as needed

    plt.show()
