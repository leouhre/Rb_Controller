import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import time
import _thread

# Import functionality of RTD measurement device
import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
from lucidIo import IoReturn

# Import functionality of power supply unit
import ea_psu_controller as ea

# Initialize the LucidControl RTD measurement device. Can be /dev/ttyACM0 or /dev/ttyACM1:
for x in range(2):
	print("Connecting to /dev/ttyACM" + str(x) + "...")
	rt8 = LucidControlRT8('/dev/ttyACM' + str(x))

	if (rt8.open() == False):
		print('Error connecting to port {0}'.format(rt8.portName))
		rt8.close()
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
try:
	psu = ea.PsuEA()
except: 
	print('ERROR: No PSU found. Try re-connecting the USB cable')
	exit()

psu.remote_on()
#psu.remote_off()

# Initialize list of sensor values and time
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
V = float(input('Set voltage: '))
psu.set_current(4)
psu.set_voltage(V)
psu.output_on()

try:
	while True:
		if (time.time() - timer) > 1:
			ret = rt8.getIoGroup(channels, values)
			for x in range(num_of_sensors):
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

# Write data to files /data/sensorX.txt
answer = ''
while (answer != "Y" and answer != "N"):
	answer = input('\nDo you want to write data to files? (Y/N): ')
if answer == "Y":
	for x in range(num_of_sensors):
		if x < 3:
			continue
		f = open("data/sensor" + str(x) + ".txt", "w")
		for i in range(len(data[x])):
			L = str(t[i]) + "\t" + str(data[x][i]) + "\n"
			f.write(L)
		f.close()

for x in range(num_of_sensors):
	if x < 3:
		continue
	plt.plot(t, data[x], label='sensor' + str(x))
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.show()
