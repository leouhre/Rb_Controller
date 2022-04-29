# Write temperature data to files /data/sensorX.txt
from collections import deque

#converts data of all sensors to a txt file with name data/sensor<x>.txt
def sensors_to_txtfile(data:list):
    for i, sensor in enumerate(data):
        with open(f"data/sensor{i}.txt", "w") as f:
            for value in sensor:
                f.write(str(value) + "\n")

#converts data of all passed deques to a txt file with name data/<key>.txt
def deques_to_txtfile(**data:deque):
    for name, list in data.items():
        with open(f"data/{name}.txt", "w") as f:
            for value in list:
                f.write(str(value) + "\n")
