# Python packages
import time, threading, socket, atexit

# Our scripts
from classes.pid2 import PID2
import globals

# Import RTD measurement device
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4

# Import power supply unit
import ea_psu_controller as ea

class loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # TODO: Move into function called by "connect to matlab" button on ui
        while True:
            try:
                self.tcp_socket = socket.create_connection(('192.168.137.1', 4000),timeout=2)
            except OSError:
                pass
            else:
                self.tcp_socket.setblocking(0)
                break

        # Initialize the LucidControl RTD measurement device
        while True:
            try:
                self.rt8 = LucidControlRT8('/dev/lucidRI8')
                self.rt8.open()
            except:
                # TODO: Do not only send to MATLAB but also show on pop-up screen
                if globals.CONNECTED_TO_MATLAB:
                    self.tcp_socket.sendall("Error when connecting to LucidControl RI8\n".encode())
                    time.sleep(5)
            else:
                break

        # Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
        self.values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
            ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

        # Initialize a boolean tuple for channels to read
        # Make sure this tuple matches the physical setup on the LucidControl device (sensors should be connected from starting from input 1)
        self.channels = (True, )*globals.NUMBER_OF_SENSORS + (False, )*(8-globals.NUMBER_OF_SENSORS)

        # Initialize the Elektro-Automatik Power Supply
        while True:
            try:
                self.psu = ea.PsuEA()
                self.psu.remote_on()
            except:
                # TODO: Do not only send to MATLAB but also show on pop-up screen
                self.tcp_socket.sendall("Error when connecting to EA PSU\n".encode())
                time.sleep(5)                
                pass
            else:
                break

        globals.CONNECTED_TO_INSTRUMENTS = True
        #self.tcp_socket.sendall("CONNECTED\n".encode())

        # Initiate measurements at constant voltage
        self.psu.set_current(4)
        self.psu.set_voltage(0)
        self.psu.output_on()

        # Initialize PID
        self.pid = PID2()

        # TODO: Should be made compatible with pop-up screens and CONNECTED_TO_MATLAB
        def safeExit():
            try:
                self.tcp_socket.sendall("Python application has ended\n".encode())
            except OSError:
                print("Connection lost")
            try:
                self.psu.output_off()
                self.psu.remote_off()
                self.psu.close()
                print("PSU output if off")
            except:
                print("Connection to EA PSU lost")
            try:
                self.rt8.close()
            except:
                print("Connection to LucidControl RI8 lost")

        atexit.register(safeExit)

    def run(self):
        # Loop
        while not globals.STOP_RUNNING:
            # TODO: Test if this way of producing the error works. Maybe use value.getValue to check if short-circuited
            try:
                ret = self.rt8.getIoGroup(self.channels, self.values)
            except ValueError:
                print(ret)

            globals.temperature_average = 0
            for value in self.values:
                globals.temperature_average += value.getTemperature()/globals.NUMBER_OF_SENSORS
            try:
                self.tcp_socket.sendall("AVG_TEMP\n{:.1f}\n".format(globals.temperature_average).encode())
            except ConnectionResetError:
                #globals.STOP_RUNNING = True
                break

            # SAFETY: AVERAGE MUST NO BE HIGHER THAN 200C
            if globals.temperature_average > 203:
                # Send warning to pop-up box
                globals.OUTPUT_OFF = True
                self.psu.output_off()

            try:
                message = self.tcp_socket.recv(1024).decode("utf_8")
            except OSError:
                message = "hello"
            except:
                #globals.STOP_RUNNING = True
                break

            match str(message[0]):
                case "t": #Temperatur given
                    globals.temperature_target = float(message[2:7])
                    globals.TARGET_TEMP_CHANGED.BY_MATLAB = True #will be set false by ui.py when it has reacted
                    globals.SET = True
                    globals.OUTPUT_PAUSE = False
                    
                case "o": #output off
                    globals.OUTPUT_OFF = True
                    self.psu.output_off()
                
                case "p": #outputpause
                    globals.OUTPUT_PAUSE = True

                case "!": #stop program
                    globals.STOP_RUNNING = True

                case "b": #Bypass mode
                    globals.BYPASS_MODE = True

                case "s": #release Set button
                    globals.SET = False

            if globals.BYPASS_MODE:
                self.psu.output_off()
                self.psu.remote_off()
                time.sleep(1)
                continue
            
            self.psu.remote_on()

            if not globals.OUTPUT_PAUSE or not globals.globals.OUTPUT_OFF:
                pidout = self.pid.update(globals.temperature_average, globals.temperature_target)
                self.psu.set_voltage(pidout)          

            if abs(globals.temperature_target - globals.temperature_average) < 1: #TODO: This 1 is user defined now
                count += 1
                if count == 10/self.pid.freq: # Temperature has been within 1C of target for more at least 10 seconds
                    globals.READY = True
                    if globals.CONNECTED_TO_MATLAB:
                        self.tcp_socket.sendall("READY\n".encode()) # Send READY to matlab via serial
            else: 
                count = 0
                if globals.READY and globals.CONNECTED_TO_MATLAB:
                    self.tcp_socket.sendall("NOT_READY\n".encode()) # Send NOT_READY to matlab via serial
                globals.READY = False
                            
            if globals.TARGET_TEMP_CHANGED.BY_UI:
                if globals.CONNECTED_TO_MATLAB:
                    self.tcp_socket.sendall("TARGET_CHANGED\n{:.2f}\n".format(globals.temperature_target).encode())
                globals.TARGET_TEMP_CHANGED.BY_UI = False
            
            if globals.SETTINGS_CHANGED:
                self.pid.__init__() 
                globals.SETTINGS_CHANGED = False
                #TODO: CHeck if this even works?

            time.sleep(self.pid.Ts)

        self.psu.close()
        self.tcp_socket.close()
        self.rt8.close()
        exit()