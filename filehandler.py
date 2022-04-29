# Write temperature data to files /data/sensorX.txt
from collections import deque

#converts data of all sensors to a txt file with name data/sensor<x>.txt
def sensors_to_txtfile(data:list):
	for x in range(len(data)):
		f = open(f"data/sensor{x}.txt", "w")
		for i in range(len(data[x])):
			L = str(data[x][i]) + "\n"
			f.write(L)
		f.close()

#converts data of all passed deques to a txt file with name data/<key>.txt
def deques_to_txtfile(**data:deque):
    for name, list in data.items():
        with open(f"data/{name}.txt", "w") as f:
            for value in list:
                f.write(str(value) + "\n")
