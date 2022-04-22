#python packages
from ast import Global
import time, sys, threading, socket

#our scripts
from classes.pid import PID

# Import functionality of RTD measurement device
# import lucidIo
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
from lucidIo import IoReturn

# Import functionality of power supply unit
import ea_psu_controller as ea

class loop(threading.Thread):

    def __init__(self):
        self.FREQUENCY = 0.1
        # Initialize the LucidControl RTD measurement device. Can be /dev/ttyACM0 or /dev/ttyACM1:
        for x in range(2):
            self.rt8 = LucidControlRT8('/dev/ttyACM' + str(x))
            try:
                if (self.rt8.open() == False):
                    self.rt8.close()
                else:
                    # Identify device
                    ret = self.rt8.identify(0)
                    if ret == IoReturn.IoReturn.IO_RETURN_OK:
                        break
                    else:
                        self.rt8.close()
            except:
                self.rt8.close()

        # Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
        self.values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
            ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

        # Initialize a boolean tuple for channels to read
        # Make sure this tuple matches the physical setup on the LucidControl device
        self.num_of_sensors = 2
        self.channels = (True, )*self.num_of_sensors + (False, )*(8-self.num_of_sensors)

        # Initialize the Elektro-Automatik Power Supply
        self.psu = ea.PsuEA()
        self.psu.remote_on()

        # Initiate measurements at constant voltage
        self.psu.set_current(4)
        self.psu.set_voltage(0)
        self.psu.output_on()

        #initialize PID
        self.pid = PID()

        #FLAG
        global STOP_RUNNING
        STOP_RUNNING = False

        # Create a connection to the server application on port 81
        self.tcp_socket = socket.create_connection(('192.168.137.1', 4000))
        self.tcp_socket.setblocking(0)

        self.tcp_socket.sendall("connected".encode())

def run(self):
    global temperature_average
    global temperature_target
    global BYPASS_MODE
    global STOP_REGULATING # maybe unused

    # Loop
    while not STOP_RUNNING:
        self.rt8.getIoGroup(self.channels, self.values)

        temperature_average = 0
        for value in self.values:
            temperature_average = temperature_average + value.getTemperature()

        try:
            message = self.tcp_socket.recv(1024).decode("utf_8")
        except:
            message = "hello"
            print("no message")	

        match str(message[0]):
            case "t": #Temperatur given
                temperature_target = int(message[2:5])
                print(temperature_target)
                STOP_REGULATING = False
            case "r": #stop regulating
                STOP_REGULATING = True
                print("2")
            case "o": #stop program
                STOP_RUNNING = True
                print("3")
            case "b": #Bypass mode
                BYPASS_MODE = True
                print("4")
                print("psu.remote_off()")
                while BYPASS_MODE:
                    print("bypass mode")
                    if "not bypass mode":
                        print("psu.remote_on()")
                        break

        if not STOP_REGULATING:
            self.pid.update_error(temperature_average,temperature_target)
            self.psu.set_voltage(self.pid.regulate_output()) 
        

        if abs(temperature_target - temperature_average) < 1:
            count = count + 1
            if count == 100: #Temperature has been within 1C of target for more at least 100 samples
                self.tcp_socket.sendall("READY".encode()) #Send READY to matlab via serial
        else: 
            count = 0
        

        time.sleep(self.FREQUENCY)
