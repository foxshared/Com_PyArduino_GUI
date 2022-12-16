# Target project >>
# Flow with Application Fan control with Python
# Example:
# > Arduino read Fan tacho convert to rpm value <
# > rpm value send to PC(python) <
# > PC read fan rpm value <
# > User set target rpm example 2000 rpm <
# > PC calcuted value of fan speed percentage to match target rpm via PID < bad result
# > PC send value of fan speed percentage  to arduino <
# > Arduino set rpm fan <
# > LOOPBACK <

# Add PID realtime control
# Add Graf

# Version 4

import serial
import time
import PID as pid
import matplotlib.pyplot as plt
import time
import pyformulas as pf
import numpy as np

# Define Variable
# PID controller variable # need learn about Ziegler nichols
# KP = 0.36
# KI = 40.0
# KD = 0.0008099999999999997
KP = 0.90
KI = 200
KD = 0.2
Setpoint = 2000  # Target RPM
Delta_time = 0.1

minCtrl = 0
maxCtrl = 15

array1 = []
array2 = []
arraytime = []


# Setup connection
# (Port::comport that arduino connect)
# (Baudrate::baudrate that use in arduino)
# (Timeout::Add some delay when send&get value)
Connection = serial.Serial(port='COM12', baudrate=9600, timeout=0.1)
Connection.close()  # close any connected serial connection
Connection.open()  # open serial connection

fig = plt.figure()
screen = pf.screen(title='Plot')
start = time.time()


def connection_data():
    # Get any value from arduino to pc
    try:
        data_receive = Connection.readline()  # Read arduino serial reading
        decode_data = data_receive.decode('utf-8')  # Decode value from arduino
        rstrip_data = decode_data.rstrip()  # Clean value
        # Separated data like ['rpm1','rpm2']
        final_data = rstrip_data.split(",")
    except UnicodeDecodeError:  # Fix value cannot decode
        final_data = []
        pass
    # Depend total data that need to use
    # Separated value to single variable
    t_data = len(final_data)
    if (t_data == 6):  # Len use check total array
        DATA1 = final_data[0]
        DATA2 = final_data[1]
        # DATA3 = final_data[3]
    else:
        DATA1 = 0
        DATA2 = 0
        # DATA3 = 0
    return DATA1, DATA2, data_receive, t_data  # convert str to int


def control_speed_perRPM(in_Data, min,max):  # Control System via PID..............
    controller = pid.PID(KP, KI, KD, Setpoint)  # Set PID and target rpm
    controller.setLims(min, max)  # Set fan limit speed like (min,max)
    # pid start calculated for pid output
    pid_ouput = controller.compute(in_Data, Delta_time)
    return pid_ouput


def connection_write(data1, data2):
    # Send value from pc to arduino
    stringToSend = "{data1},{data2}".format(
        data1=data1, data2=data2)  # packing data
    stringWithMarkers = ('<')  # add marker to arduino read
    stringWithMarkers += stringToSend
    stringWithMarkers += ('>')  # end marker to arduino read
    Connection.write(stringWithMarkers.encode('utf-8'))  # encode
    time.sleep(0.001)


def graf(d1, d2, t):
    speed1 = d1
    speed2 = d2
    array1.append(speed1)
    array2.append(speed2)
    arraytime.append(t+1)
    plt.xlim(t+1, t)
    plt.ylim(0, 4000)
    plt.plot(arraytime, array1, c='blue')
    plt.plot(arraytime, array2, c='red')

    fig.canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    screen.update(image)


while True:
    try:
        t = time.time() - start
        RPM1, RPM2, reading, t_data = connection_data()
        RPM1 = int(RPM1)
        RPM2 = int(RPM2)
        PID_RPM1 = control_speed_perRPM(RPM1,minCtrl,maxCtrl)  # calculated pid for fan1
        PID_RPM2 = control_speed_perRPM(RPM2,minCtrl,maxCtrl)  # calculated pid for fan1
        graf(RPM1, RPM2, t=t)
        connection_write(PID_RPM1, PID_RPM2)  # disable to debug

        print(RPM1, RPM2, PID_RPM1, PID_RPM2, reading, t_data)

    # Press CTRL + C to exit
    except KeyboardInterrupt:
        print("Exit")
        Connection.close
        exit(0)
