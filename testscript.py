import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import time
import sys

# Import functionality of RTD measurement device
import lucidIo
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
				#print('Serial No.: ' + str(rt8.getDeviceSnr()))
				#print('Firmware Rev.: ' + str(rt8.getRevisionFw()))
				#print('Hardware Rev.: ' + str(rt8.getRevisionHw()))
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
		#print('Identify Error')
		#rt8.close()
		else:
			print('Try re-inserting the USB cable')
			exit()

	"""
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
			#print('Serial No.: ' + str(rt8.getDeviceSnr()))
			#print('Firmware Rev.: ' + str(rt8.getRevisionFw()))
			#print('Hardware Rev.: ' + str(rt8.getRevisionHw()))
			print('Successfully connected to port ' + str(rt8.portName))
			break
		else:
			print('Identify Error')
			rt8.close()
			if x > 0:
				print('Try re-inserting the USB cable')
				exit()
	"""

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
#psu.remote_off()

# Initialize data list containing a double ended queue (deque) for each sensor. Initialize time queue as well
timer = time.time()
ret = rt8.getIoGroup(channels, values)
data = []
for x in range(num_of_sensors):
	data.append(deque())
	data[x].append(values[x].getTemperature())
tstamp = 0
t = deque()
t.append(tstamp)

# Initiate measurements at constant voltage
if len(sys.argv > 1):
	V = float(sys.argv[1])
	input("Press any key to begin")
else: 
	V = float(input('Set voltage: '))
psu.set_current(2)
psu.set_voltage(V)
psu.output_on()

# Append sensor values to their queues every second and update time. Stop the experiment with "Ctrl+c" raising Keyboardinterrupt
try:
	while True:
		if (time.time() - timer) > 1:
			ret = rt8.getIoGroup(channels, values)
			for x in range(num_of_sensors):
				if x < 3:
					continue
				data[x].append(values[x].getTemperature())
				print(values[x].getTemperature())
				#if values[x].getTemperature() > 200:
				#	raise KeyboardInterrupt
			print("_________")
			timer = time.time()
			tstamp += 1
			t.append(tstamp)
			#if values[0].getTemperature() > 25:
			#	break
except KeyboardInterrupt:
	pass

psu.output_off()

# Write temperature data to files /data/sensorX.txt
answer = ''
while (answer != "Y" and answer != "N"):
	answer = input('\nDo you want to write data to files? (Y/N): ')
if answer == "Y":
	for x in range(num_of_sensors):
		if x < 3:
			continue
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

# Plot the obtained temperature data
for x in range(num_of_sensors):
	if x < 3:
		continue
	plt.plot(t, data[x], label='sensor' + str(x))
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.show()