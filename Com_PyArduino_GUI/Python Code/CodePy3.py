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

# Version 3
import serial
import time
import PID as pid

# Define Variable
# PID controller variable # need learn about Ziegler nichols
# KP = 0.36
# KI = 40.0
# KD = 0.0008099999999999997
KP = 0.90
KI = 100
KD = 0.00128
Setpoint = 2000  # Target RPM
Delta_time = 0.001

# Setup connection
# (Port::comport that arduino connect)
# (Baudrate::baudrate that use in arduino)
# (Timeout::Add some delay when send&get value)
Connection = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
Connection.close()  # close any connected serial connection
Connection.open()  # open serial connection


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
    return DATA1, DATA2, data_receive,t_data  # convert str to int


def control_speed_perRPM(in_Data):  # Control System via PID..............
    controller = pid.PID(KP, KI, KD, Setpoint) # Set PID and target rpm
    controller.setLims(0, 16) # Set fan limit speed like (min,max)
    pid_ouput = controller.compute(in_Data, Delta_time) # pid start calculated for pid output
    return pid_ouput


def connection_write(data1,data2):
    # Send value from pc to arduino
    stringToSend = "{data1},{data2}".format(data1=data1,data2=data2)
    stringWithMarkers = ('<')
    stringWithMarkers += stringToSend
    stringWithMarkers += ('>')
    Connection.write(stringWithMarkers.encode('utf-8'))
    time.sleep(0.001)


while True:
    try:
        RPM1, RPM2,reading,t_data = connection_data() #
        PID_RPM1 = control_speed_perRPM(int(RPM1))
        PID_RPM2 = control_speed_perRPM(int(RPM2))
        connection_write(PID_RPM1,PID_RPM2)

        print(RPM1, RPM2, PID_RPM1, PID_RPM2, reading,t_data)

    # Press CTRL + C to exit
    except KeyboardInterrupt:
        print("Exit")
        Connection.close
        exit(0)
