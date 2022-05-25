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
<<<<<<< Updated upstream
        for sensor in sensors:
            for value, t, c in zip(sensor,time,clock):
                f.write(str(value) + ",")
=======
        for t,c in zip(time,clock):
            for sensor in sensors:
                f.write(str(sensor[time.index(t)]) + ",")
>>>>>>> Stashed changes
            f.write(str(t) + ",")
            f.write(str(c) + "\n")
        
