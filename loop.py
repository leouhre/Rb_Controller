#python packages
import time, threading, socket

#our scripts
from classes.pid import PID
import globals

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
        threading.Thread.__init__(self)
        self.FREQUENCY = 0.1

        # Initialize the LucidControl RTD measurement device
        self.rt8 = LucidControlRT8('/dev/lucidRI8')
        self.rt8.open()

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

        # Create a connection to the server application on port 81
        while True:
            try:
                self.tcp_socket = socket.create_connection(('192.168.137.1', 4000),timeout=4)
            except TimeoutError:
                pass
            else:
                self.tcp_socket.setblocking(0)
                self.tcp_socket.sendall("connected\n".encode())
                break

    def run(self):
        # Loop
        while not globals.STOP_RUNNING:
            self.rt8.getIoGroup(self.channels, self.values)

            globals.temperature_average = 0
            for value in self.values:
                globals.temperature_average += value.getTemperature()/self.num_of_sensors

            try:
                message = self.tcp_socket.recv(1024).decode("utf_8")
            except OSError:
                message = "hello"

            match str(message[0]):
                case "t": #Temperatur given
                    globals.temperature_target = int(message[2:5])
                    print(globals.temperature_target)
                    globals.STOP_REGULATING = False
                    
                case "r": #stop regulating
                    globals.STOP_REGULATING = True

                case "o": #stop program
                    globals.STOP_RUNNING = True

                case "b": #Bypass mode
                    globals.BYPASS_MODE = True

            while globals.BYPASS_MODE:
                self.psu.output_off()
                self.psu.remote_off()
                time.sleep(1)
            
            self.psu.remote_on()

            if not globals.STOP_REGULATING:
                self.pid.update_error(globals.temperature_average, globals.temperature_target)
                self.psu.set_voltage(self.pid.regulate_output())
            

            if abs(globals.temperature_target - globals.temperature_average) < 1:
                count += 1
                if count == 100: #Temperature has been within 1C of target for more at least 100 samples
                    self.tcp_socket.sendall("READY\n".encode()) #Send READY to matlab via serial
            else: 
                count = 0
            

            time.sleep(self.FREQUENCY)

        self.psu.output_off()
        self.tcp_socket.close()
        self.rt8.close()
