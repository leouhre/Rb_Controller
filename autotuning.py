# Python packages
import time, atexit
import matplotlib.pyplot as plt
import os
from collections import deque

# Our scripts
import globals
import filehandler

# Import RTD measurement device
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS4

# Import power supply unit
import ea_psu_controller as ea

# Initialize the LucidControl RTD measurement device
rt8 = LucidControlRT8('/dev/lucidRI8')
rt8.open()

# Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
    ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

# Initialize a boolean tuple for channels to read
# Make sure this tuple matches the physical setup on the LucidControl device (sensors should be connected from starting from input 1)
channels = (True, )*globals.NUMBER_OF_SENSORS + (False, )*(8-globals.NUMBER_OF_SENSORS)

# Initialize the Elektro-Automatik Power Supply
psu = ea.PsuEA()
psu.remote_on()

# Initialize data list containing a double ended queue (deque) for each sensor. Initialize voltage and time queue as well
rt8.getIoGroup(channels, values)
data = []
for x in range(globals.NUMBER_OF_SENSORS):
	data.append(deque())
	data[x].append(values[x].getTemperature())
# Average
data.append(deque())
data[globals.NUMBER_OF_SENSORS].append(values[0].getTemperature())

# Voltage data
v = deque()
v.append(0)

# Time data
t_start = time.perf_counter()
t = deque()
t.append(t_start)

# Clock data
c = deque()
c.append(time.strftime("Clock: %H:%M:%S", time.localtime()))

# Initiate measurements at constant voltage
psu.set_current(4)
psu.set_voltage(0)
psu.output_on()

def safeExit():
    try:
        psu.output_off()
        psu.remote_off()
        psu.close()
        print("PSU output if off")
    except:
        print("Connection to EA PSU lost")
    try:        
        rt8.close()
    except:
        print("Connection to LucidControl RI8 lost")

atexit.register(safeExit)

try:
    while not globals.STOP_RUNNING:
        os.system('clear')
        try:
            ret = rt8.getIoGroup(channels, values)
        except ValueError:
            print(ret)
    
        t_temp = time.perf_counter() - t_start
        print(f"time:{t_temp:5.1f}")

        globals.temperature_average = 0
        for value in values:
            globals.temperature_average += value.getTemperature()/globals.NUMBER_OF_SENSORS
            data[x].append(value.getTemperature())
            print(value.getTemperature())
        data[globals.NUMBER_OF_SENSORS].append(globals.temperature_average)
        print(f"Average = {globals.temperature_average:3.1f}")
        print("____________")       

        if globals.temperature_average < 190:
            psu.set_voltage(28)
            v.append(28 + 176)
        else: 
            psu.set_voltage(0)
            v.append(0 + 176)

        t.append(t_temp)
        c.append(time.strftime("%H:%M:%S", time.localtime()))

        time.sleep(0.1)
except KeyboardInterrupt:
    pass

# In case KeyboardInterrupt happens in the middle of loop, discard last element to make all the data the same size
l = len(data[0])
for x in range(globals.NUMBER_OF_SENSORS + 1):
	while len(data[x]) > l:
		data[x].pop()
while len(t) > l:
	t.pop()
while len(t) < l:
	t.append(t_temp)
    
# Write temperature data to files /data/sensorX.txt
answer = ''
while (answer != "Y" and answer != "N"):
	answer = input('\nDo you want to write data to files? (Y/N): ')
if answer == "Y":	
	filehandler.deques_to_txtfile(time=t,clock=c)
	filehandler.sensors_to_txtfile(data)
	filehandler.all_textfile(data,t,c)

psu.output_off()
rt8.close()

# Plot the obtained temperature data
#for x in range(globals.NUMBER_OF_SENSORS):
#	plt.plot(t, data[x], label='sensor' + str(x))
plt.plot(t, data[globals.NUMBER_OF_SENSORS], label='Average temperature')
plt.plot(t, v, label='Control voltage (+176V)')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Temperature/Voltage (C/V)')
plt.show()

exit()