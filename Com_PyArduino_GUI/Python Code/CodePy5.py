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

# Add PID realtime control using txt
# Add Graf

# Idea to make to same as setpoint....use final output find its average with time in 30sec and add as offset to get zero error


# Version 5
import os
import serial
import time
import PID as pid
import matplotlib.pyplot as plt
import time
import pyformulas as pf
import numpy as np

import configparser

# Make current file path as working environment
folder_path = os.path.dirname(__file__)
os.chdir(folder_path)

# Define Variable
# PID controller variable # need learn about Ziegler nichols
# KP = 0.36
# KI = 40.0
# KD = 0.0008099999999999997
KP = 0.90
KI = 200
KD = 0.2
# Setpoint = 2000  # Target RPM
Delta_time = 0.1

t = 0.0
last_t = 0.0

config = configparser.ConfigParser()

minCtrl = -100
maxCtrl = 100

array1 = []
array2 = []
arraytime = []


# Setup connection
# (Port::comport that arduino connect)
# (Baudrate::baudrate that use in arduino)
# (Timeout::Add some delay when send&get value)
Connection = serial.Serial(port='COM5', baudrate=9600, timeout=0.1)
Connection.close()  # close any connected serial connection
Connection.open()  # open serial connection

fig = plt.figure()
screen = pf.screen(title='Plot')

start = time.time()
start_ = time.time()

average_count = 0
offset1 = 0
offset2 = 0


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


# Control System via PID..............
def control_speed_perRPM(in_Data, min, max, dt):
    controller = pid.PID(KP, KI, KD, Setpoint)  # Set PID and target rpm
    controller.setLims(min, max)  # Set fan limit speed like (min,max)
    # pid start calculated for pid output
    pid_ouput = controller.compute(in_Data, dt)
    return int(pid_ouput)


def calSpeedPer(Max_setpoint, set, input_):
    cal_speed = int((set/Max_setpoint)*100)
    cal_error = int((input_/Max_setpoint)*100)  # calculate speed error
    final_cal = cal_speed + cal_error
    return cal_speed, cal_error, final_cal


def connection_write(data1, data2):
    # Send value from pc to arduino
    stringToSend = "{data1},{data2}".format(
        data1=data1, data2=data2)  # packing data
    stringWithMarkers = ('<')  # add marker to arduino read
    stringWithMarkers += stringToSend
    stringWithMarkers += ('>')  # end marker to arduino read
    Connection.write(stringWithMarkers.encode('utf-8'))  # encode
    # time.sleep(0.1)


def graf(d1, d2, t):
    speed1 = d1
    speed2 = d2

    array1.append(speed1)
    array2.append(speed2)
    arraytime.append(t)

    plt.xlim(0, 10)
    plt.ylim(0, 4000)
    plt.plot(arraytime, array1, c='blue')
    plt.plot(arraytime, array2, c='red')

    fig.canvas.draw()

    image = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    screen.update(image)


def get_save(type):
    config.read("tune.txt")
    data_read = config["SETUP"]
    return data_read[type]


def limit_k(out_, max, min):

    if out_ > max and max is not None:out_ = max
    elif out_ < min and min is not None:out_ = min
    return out_


    # if out_ >= max:
    #     out_ = max
    # elif out_ < min:
    #     out_ = min
    # return out_


while True:
    try:
        start = time.time()
        t_ = time.time() - start_
        average_count = average_count + 1

        RPM1, RPM2, reading, t_data = connection_data()
        RPM1 = int(RPM1)
        RPM2 = int(RPM2)

        Max_setpoint = int(get_save("max_Setpoint"))
        Setpoint = int(get_save("setpoint"))
        KP = float(get_save("KP"))
        KI = float(get_save("KI"))
        KD = float(get_save("KD"))
        Delta_time = float(get_save("Delta_time")) + last_t
        Manual = int(get_save("Manual_speed"))
        mode = int(get_save("Mode"))

        # offset = int(get_save("offset"))

        PID_RPM1 = control_speed_perRPM(
            RPM1, minCtrl, maxCtrl, Delta_time)  # calculated pid for fan1
        PID_RPM2 = control_speed_perRPM(
            RPM2, minCtrl, maxCtrl, Delta_time)  # calculated pid for fan2

        if average_count >= 40:
            offset1 = PID_RPM1
            offset2 = PID_RPM2
            average_count = 0

        S1 = PID_RPM1+offset1
        S2 = PID_RPM2+offset2

        S1_ = limit_k(S1, 99, 0)
        S2_ = limit_k(S2, 99, 0)

        if mode == 0:
            connection_write(S1_, S2_)  # auto speed
        elif mode == 1:
            connection_write(Manual, Manual)  # Manual speed

        graf(RPM1, RPM2, t=t_)
        if t_ > 10:
            array1.clear()
            array2.clear()
            arraytime.clear()
            t_ = 0
            start_ = time.time()
            plt.cla()

        print_out = "Target== {target} ,RPM1: {rpm1} RPM2: {rpm2}, Output: 1({fin1}), 2({fin2}), ({all})".format(
            target=Setpoint, rpm1=RPM1, rpm2=RPM2, fin1=S1_, fin2=S2_, all=reading)
        print(print_out)

        t = time.time() - start
        last_t = t

    # Press CTRL + C to exit
    except KeyboardInterrupt:
        print("Exit")
        connection_write(1000, 1000)
        Connection.close
        exit(0)
