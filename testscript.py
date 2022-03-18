import matplotlib.pyplot as plt
import numpy as mp
from collections import deque
import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
import time

rt8 = LucidControlRT8('/dev/ttyACM0')

rt8.open()

values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
	ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

channels = (True, True, True, True, True, True, True, False)

timer = time.time()
num_of_sensors = 7
ret = rt8.getIoGroup(channels, values)
data = []
for x in range(num_of_sensors):
	data.append(deque())
	data[x].append(values[x].getTemperature())
count = 0
t = deque()
t.append(count)

while True:
	if (time.time() - timer) > 5:
		ret = rt8.getIoGroup(channels, values)
		for x in range(num_of_sensors):
			data[x].append(values[x].getTemperature())
			print(values[x].getTemperature())
		print("_________")
		timer = time.time()
		count += 5
		t.append(count)
		if values[0].getTemperature() > 25:
			break

for x in range(num_of_sensors):
	plt.plot(t, data[x])
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.show()
