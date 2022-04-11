FREQUENCY = 2

#python packages
from encodings import utf_8
import string
import matplotlib.pyplot as plt
import numpy as np
import time, sys
from collections import deque
import socket

#our scripts
from classes.pid import PID
import filehandler

# Import functionality of RTD measurement device
# import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
from lucidIo import IoReturn

# Import functionality of power supply unit
import ea_psu_controller as ea
"""
# Initialize the LucidControl RTD measurement device. Can be /dev/ttyACM0 or /dev/ttyACM1:
for x in range(2):
	rt8 = LucidControlRT8('/dev/ttyACM' + str(x))
	try:
		if (rt8.open() == False):
			rt8.close()
		else:
			# Identify device
			ret = rt8.identify(0)
			if ret == IoReturn.IoReturn.IO_RETURN_OK:
				break
			else:
				rt8.close()
	except:
		rt8.close()

# Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
	ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

# Initialize a boolean tuple for channels to read
# Make sure this tuple matches the physical setup on the LucidControl device
num_of_sensors = 2
channels = ()
for x in range(8):
    if x < num_of_sensors:
        channels += (True, )
    else:
        channels += (False, )

# Initialize the Elektro-Automatik Power Supply
psu = ea.PsuEA()
psu.remote_on()
"""
#timer
timer = time.time()
num_of_sensors = 2
# Initiate measurements at constant voltage
"""
psu.set_current(4)
psu.set_voltage(0)
psu.output_on()
"""
#initialize PID
pid = PID() 

#FLAG
STOP_RUNNING = False
STOP_REGULATING = True
BYPASS_MODE = False
temperature_target = 0
count = 0

# Create a connection to the server application on port 81
tcp_socket = socket.create_connection(('localhost', 4000))
tcp_socket.setblocking(0)

tcp_socket.sendall("ready".encode())
print('what')

# Append sensor values to their queues every second and update time. Stop the experiment with "Ctrl+c" raising Keyboardinterrupt
while not STOP_RUNNING:
    if (time.time() - timer) > FREQUENCY:

        #ret = rt8.getIoGroup(channels, values)

        temperature_average = 0
        for x in range(num_of_sensors):
            temperature_average = temperature_average + np.random.random_sample() #values[x].getTemperature()
        temperature_average = temperature_average/num_of_sensors 

        try:
            message = tcp_socket.recv(1024).decode("utf_8")
        except:
            message = "hello"
            print("no message")	

        match str(message[0]):
            case "t": #Temperatur given
                temperature_target = int(message[2:5])
                print(temperature_target)
                STOP_REGULATING = False
            case "r": #stop regulating
                STOP_REGULATING = True
                print("2")
            case "o": #stop program
                STOP_RUNNING = True
                print("3")
            case "b": #Bypass mode
                BYPASS_MODE = True
                print("4")
                print("psu.remote_off()")
                while BYPASS_MODE:
                    print("bypass mode")
                    if "not bypass mode":
                        print("psu.remote_on()")
                        break

        if not STOP_REGULATING:
            print("regulating")
            #pid.update_error(temperature_average,temperature_target)
            #psu.set_voltage(pid.regulate_output()) 
        

        if abs(temperature_target - temperature_average) < 1:
            count = count + 1
            if count == 100: #Temperature has been within 1C of target for more at least 100 samples
                tcp_socket.sendall("READY".encode()) #Send READY to matlab via serial
        else: 
            count = 0
        

        timer = time.time()
                


#psu.output_off()
tcp_socket.close()

