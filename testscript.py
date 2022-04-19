print("Starting up...")

#python packages
import matplotlib.pyplot as plt
import numpy as np
import time, sys
from collections import deque


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
print("Connecting to /dev/ttyACM", end="")
for x in range(2):
	print(str(x) + "...")
	rt8 = LucidControlRT8('/dev/ttyACM' + str(x))

	try:
		if (rt8.open() == False):
			print('LucidControl device not found at port ' + str(x))
			rt8.close()
			print("Connecting to /dev/ttyACM", end="")
		else:
			# Identify device
			ret = rt8.identify(0)
			if ret == IoReturn.IoReturn.IO_RETURN_OK:
				print('Device Class: ' + str(rt8.getDeviceClassName()))
				print('Device Type: ' + str(rt8.getDeviceTypeName()))
				print('Successfully connected to port ' + str(rt8.portName))
				break
			else:
				print('Identify Error')
				rt8.close()
				if x < 1:
					print("Connecting to /dev/ttyACM", end="")
				else:	
					print('Try re-inserting the USB cable')
					exit()
	except:
		print('LucidControl device not found at port ' + str(x))
		rt8.close()
		if x < 1:
			print("Connecting to /dev/ttyACM", end="")
		else:
			print('Try re-inserting the USB cable')
			exit()


# Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
	ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

# Initialize a boolean tuple for channels to read
# Make sure this tuple matches the physical setup on the LucidControl device
num_of_sensors = int(input('Enter number of sensors starting from IO1/2: '))
channels = ()
for x in range(8):
    if x < num_of_sensors:
        channels += (True, )
    else:
        channels += (False, )

# Initialize the Elektro-Automatik Power Supply
# Make sure that 99-ea-psu.rules is in /etc/udev/rules.d/ as recommended at https://pypi.org/project/ea-psu-controller/
print("Connecting to the EA power supply...")
try:
	psu = ea.PsuEA()
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
tstamp = 0
t = deque()
t.append(tstamp)

# Initiate measurements at constant voltage
psu.set_current(4)
psu.set_voltage(int(input("set voltage")))
psu.output_on()

#temperature from terminal 
T_target = float(sys.argv[1])
#initialize PID
#PI = PID() 


# Append sensor values to their queues every second and update time. Stop the experiment with "Ctrl+c" raising Keyboardinterrupt
try:
	while True:
		if (time.time() - timer) > 0.1:
			ret = rt8.getIoGroup(channels, values)
			temp_average = 0
			print(tstamp) 
			for x in range(num_of_sensors):
				temp_average = temp_average + values[x].getTemperature()
				data[x].append(values[x].getTemperature())
				print(values[x].getTemperature())
			print("____________")
			"""
			temp_average = temp_average/num_of_sensors 	
			data[num_of_sensors].append(temp_average)			
			print("average: " + str(temp_average)) 
			print("_________")

			PI.update_error(temp_average,T_target)
			psu.set_voltage(max(min(PI.proportional() + PI.integral(),28),0)) 
			v.append(PI.proportional() + PI.integral())
			"""

			timer = time.time()
			tstamp += 0.1
			t.append(tstamp)

except KeyboardInterrupt:
	pass

#in case keyboardInterrupt happens before in the middle of storing data, discard last element take make the data equal size
l = len(data[0])
for x in range(num_of_sensors + 1):
	if len(data[x]) > l:
		data[x].pop()
if len(t) > l:
	t.pop()

psu.output_off()

# Write temperature data to files /data/sensorX.txt
answer = ''
while (answer != "Y" and answer != "N"):
	answer = input('\nDo you want to write data to files? (Y/N): ')
if answer == "Y":
	"""
	filehandler.deques_to_txtfile(time=t,voltage=v)
	filehandler.sensors_to_txtfile(data)
	"""
	for x in range(num_of_sensors):
		f = open("data/sensor" + str(x) + ".txt", "w")
		for i in range(len(data[x])):
			L = str(data[x][i]) + "\n"
			f.write(L)
		f.close()
	f = open("data/time.txt", "w")
	for i in range(len(t)):
		L = str(t[i]) + "\n"
		f.write(L)
	f.close()

	f = open("data/voltage.ftxt", "w")
	for i in range(len(v)):
		L = str(v[i]) + "\n"
		f.write(L)
	f.close()
	
# Plot the obtained temperature data
for x in range(num_of_sensors):
	plt.plot(t, data[x], label='sensor' + str(x))
#plt.plot(t, data[num_of_sensors], label='avg')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.show()
