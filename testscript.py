print("Starting up...")

#python packages
import matplotlib.pyplot as plt
import numpy as np
import time, sys
import os
from collections import deque


#our scripts
from classes.pid import PID
import filehandler
import globals


# Import functionality of RTD measurement device
# import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
from lucidIo import IoReturn

# Import functionality of power supply unit
import ea_psu_controller as ea

globals.initialize_variables()

# Initialize the LucidControl RTD measurement device
rt8 = LucidControlRT8('/dev/lucidRI8')
#rt8 = LucidControlRT8('COM3')
rt8.open()


# Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
	ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

# Initialize a boolean tuple for channels to read
# Make sure this tuple matches the physical setup on the LucidControl device
num_of_sensors = int(input('Enter number of sensors starting from IO1/2: '))
channels = (True,)*(num_of_sensors) + (False,)*(8-num_of_sensors)

# Initialize the Elektro-Automatik Power Supply
# Make sure that 99-ea-psu.rules is in /etc/udev/rules.d/ as recommended at https://pypi.org/project/ea-psu-controller/
print("Connecting to the EA power supply...")
try:
	psu = ea.PsuEA()
	#psu = ea.PsuEA('COM4')
except: 
	print('ERROR: No PSU found. Try re-connecting the USB cable')
	exit()
print("Successfully connected to the EA power supply")
psu.remote_on()

# Initialize data list containing a double ended queue (deque) for each sensor. Initialize voltage and time queue as well
timer = time.time()
rt8.getIoGroup(channels, values)
data = []
for x in range(num_of_sensors):
	data.append(deque())
	data[x].append(values[x].getTemperature())
#average
data.append(deque())
data[num_of_sensors].append(values[0].getTemperature())

# voltage data
v = deque()
v.append(0)

#time data
t_start = time.perf_counter()
t = deque()
t.append(0)

#clock
c = deque()
c.append(time.strftime("Clock: %H:%M:%S", time.localtime()))

# Initiate measurements at constant voltage
psu.set_current(4)
psu.set_voltage(0)
psu.output_on()

#temperature from terminal 
T_target = float(sys.argv[1])
#psu.set_voltage(float(sys.argv[1]))
#initialize PID
PI = PID() 



# Append sensor values to their queues every second and update time. Stop the experiment with "Ctrl+c" raising Keyboardinterrupt
try:
	while True:
		#os.system('clear')
		maxt = 0
		ret = rt8.getIoGroup(channels, values)

		temp_average = 0
		t_temp = time.perf_counter() - t_start
		print(f"time:{t_temp:5.1f}") 

		for x in range(num_of_sensors):
			if x < 2:
				temp_average += values[x].getTemperature()/2
			data[x].append(values[x].getTemperature())
			maxt = max(values[x].getTemperature(),maxt)

			if maxt > 225:
				globals.MAX_TEMP_REACHED = True
			print(values[x].getTemperature())
		data[num_of_sensors].append(temp_average)
		print(f"Average = {temp_average:3.1f}")
		print("____________")


		#pidout = PI.update(temp_average,T_target)
		if not globals.MAX_TEMP_REACHED or temp_average > T_target:
			pidout = PI.update(temp_average,T_target)
			globals.MAX_TEMP_REACHED = False
		else:
			pidout = PI.update2(maxt,230)
			if maxt < 223:
				globals.MAX_TEMP_REACHED = False
			
		psu.set_voltage(pidout) 
		v.append(pidout)

		t.append(t_temp)
		c.append(time.strftime("%H:%M:%S", time.localtime()))

		time.sleep(PI.Ts)

except KeyboardInterrupt:
	pass

#in case keyboardInterrupt happens before in the middle of storing data, discard last element take make the data equal size
l = len(data[0])
for x in range(num_of_sensors + 1):
	if len(data[x]) > l:
		data[x].pop()
if len(t) > l:
	t.pop()
if len(t) < l:
	t.append(t_temp)
if len(v) > l:
	v.pop()
if len(v) < l:
	v.append(pidout)

# Write temperature data to files /data/sensorX.txt
answer = ''
while (answer != "Y" and answer != "N"):
	answer = input('\nDo you want to write data to files? (Y/N): ')
if answer == "Y":
	
	filehandler.deques_to_txtfile(time=t,clock=c,voltage=v)
	filehandler.sensors_to_txtfile(data)

psu.output_off()

# Plot the obtained temperature data
for x in range(num_of_sensors):
	plt.plot(t, data[x], label='sensor' + str(x))
plt.plot(t, data[num_of_sensors], label='avg')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.show()
