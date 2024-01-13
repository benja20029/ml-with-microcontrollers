from serial import Serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# USB PORT
portName = '/dev/tty.usbserial-0001'

# Create Serial object:
ser = Serial(portName, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0)

# Maximum number of data points to show on the plot
max_length = 100
acc_x, acc_y, acc_z = deque(maxlen=max_length), deque(maxlen=max_length), deque(maxlen=max_length)
gyro_x, gyro_y, gyro_z = deque(maxlen=max_length), deque(maxlen=max_length), deque(maxlen=max_length)
temp = deque(maxlen=max_length)

with ser:
    ser.reset_input_buffer()

    # Initialize your figure and subplots
    fig, axs = plt.subplots(3, 3, figsize=(30, 12))

    # Remove original axes
    for ax in axs[2]:
        fig.delaxes(ax)

    # Use the final row for only one plot
    axs_1 = plt.subplot2grid((3, 3), loc=(2, 0), colspan=3, fig=fig)



    # Create line objects for each type of data
    lines = {
        'acc_x': axs[0][0].plot([], [], label='Acc X')[0],
        'acc_y': axs[0][1].plot([], [], label='Acc Y')[0],
        'acc_z': axs[0][2].plot([], [], label='Acc Z')[0],
        'gyro_x': axs[1][0].plot([], [], label='Gyro X')[0],
        'gyro_y': axs[1][1].plot([], [], label='Gyro Y')[0],
        'gyro_z': axs[1][2].plot([], [], label='Gyro Z')[0],
        'temp': axs_1.plot([], [], label='Temperature')[0]
    }

    # Set labels and titles
    axs[0][0].set_title('Acceleration X Axis')
    axs[0][1].set_title('Acceleration Y Axis')
    axs[0][2].set_title('Acceleration Z Axis')
    axs[1][0].set_title('Gyro X Axis')
    axs[1][1].set_title('Gyro Y Axis')
    axs[1][2].set_title('Gyro Z Axis')
    axs_1.set_title('Temperature')
    axs_1.set_xlabel('Time')

    # Set y-titles
    axs[0][0].set_ylabel('Acceleration (m/s^2)')
    axs[1][0].set_ylabel('Angular velocity (deg/s)')
    axs_1.set_ylabel('Temperature (Celsius)')

    # Adding legends
    axs[0][2].legend(loc='upper right')
    axs[1][2].legend(loc='upper right')
    axs_1.legend(loc='upper right')

    # This function is called periodically from FuncAnimation
    def animate(i):
        if ser.in_waiting:
            line = ser.readline()
            try:
                decoded_line = line.decode('utf-8').strip()
                data = decoded_line.split(',')
                if len(data) == 7 and all(d.strip() for d in data):
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
                        for axis in ax:
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

            except UnicodeDecodeError:
                print('UnicodeDecodeError')
                pass

    # Set up plot to call animate() function periodically
    ani = FuncAnimation(fig, animate, interval=0)  # Adjust the interval as needed

    plt.show()
