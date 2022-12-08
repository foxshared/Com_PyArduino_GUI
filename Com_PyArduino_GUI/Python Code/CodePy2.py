# Target project >>
# Flow with Application Fan control with Python
# Example: 
# > Arduino read Fan tacho convert to rpm value
# > rpm value send to PC(python)
# > PC read fan rpm value
# > User set target rpm example 2000 rpm
# > PC calcuted value of fan speed percentage to match target rpm via PID
# > PC send value of fan speed percentage  to arduino
# > Arduino set rpm fan
# > LOOPBACK

# Version 2
# Import library
import serial
import time

# Setup connection
# (Port::comport that arduino connect)
# (Baudrate::baudrate that use in arduino)
# (Timeout::Add some delay when send&get value)
Connection = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
Connection.close()  # close any connected serial connection
Connection.open()  # open serial connection


def write_read(x):
    # Send and get value from pc to arduino back to pc
    Convert2byteValue = bytes(x, 'utf-8')
    Connection.write(Convert2byteValue)
    time.sleep(0.05)
    data_receive = Connection.readline()
    return data_receive


while True:
    try:
        # value = input("Enter something: ")
        # get_value = write_read(value)
        # print(get_value)
        print(Connection.readline())

    # Press CTRL + C to exit
    except KeyboardInterrupt:
        print("Exit")
        Connection.close
        exit(0)

