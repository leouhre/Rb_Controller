FREQUENCY = 0.1

#python packages
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

#timer
timer = time.time()

# Initiate measurements at constant voltage
psu.set_current(4)
psu.set_voltage(0)
psu.output_on()

#initialize PID
pid = PID() 

#FLAG
STOP_RUNNING = False

# Create a connection to the server application on port 81
tcp_socket = socket.create_connection(('192.168.137.1', 4000))

# Append sensor values to their queues every second and update time. Stop the experiment with "Ctrl+c" raising Keyboardinterrupt
while not STOP_RUNNING:
    if (time.time() - timer) > FREQUENCY:

        ret = rt8.getIoGroup(channels, values)

        temperature_average = 0
        for x in range(num_of_sensors):
            temperature_average = temperature_average + values[x].getTemperature()
        temperature_average = temperature_average/num_of_sensors 	

        match x:
            case 1: #Temperatur given
                temperature_target = sys
                STOP_REGULATING = False
            case 2: #stop regulating
                STOP_REGULATING = True
            case 3: #stop program
                STOP_RUNNING = True
            case 4: #Bypass mode
                BYPASS_MODE = True
                psu.remote_off()
                while BYPASS_MODE:
                    if "not bypass mode":
                        psu.remote_on()
                        break

        if not STOP_REGULATING:
            pid.update_error(temperature_average,temperature_target)
            psu.set_voltage(max(min(pid.proportional() + pid.integral(),28),0)) 
        

        if abs(temperature_target - temperature_average) < 1:
            count = count + 1
            if count == 100: #Temperature has been within 1C of target for more at least 100 samples
                tcp_socket.sendall("READY".encode()) #Send READY to matlab via serial
        else: 
            count = 0
        

        timer = time.time()
                


psu.output_off()
tcp_socket.close()

