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

def all_textfile(sensors,time,clock):
    with open(f"all_data.txt", "w") as f:
        for i in range(len(time)):
            f.write(str(time[i]) + ",")
            f.write(str(clock[i]) + ",")
            for sensor in sensors:
                f.write(str(sensor[i]) + ",")
        
