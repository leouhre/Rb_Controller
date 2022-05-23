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
                globals.error_msg = "Error when connecting to LucidControl RI8"
                self.safemsg_matlab("Error when connecting to LucidControl RI8")
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
                globals.error_msg = "Error when connecting to EA PSU"
                self.safemsg_matlab("Error when connecting to EA PSU")
                time.sleep(5)                
            else:
                break

        globals.CONNECTED_TO_INSTRUMENTS = True
        self.safemsg_matlab("CONNECTED")

        # Initiate measurements at constant voltage
        self.psu.set_current(4)
        self.psu.set_voltage(0)
        self.psu.output_on()

        # Initialize PID
        self.pid = PID2()

        atexit.register(self.safeexit)

    def safeexit(self):
        globals.error_msg = "Regulation crashed"
        self.safemsg_matlab("Regulation crashed")
        try:
            self.psu.output_off()
            self.psu.remote_off()
            self.psu.close()
        except:
            globals.error_msg = "Connection to PSU lost. Turn off output manually"
            self.safemsg_matlab("Connection to PSU lost. Turn off output manually")
        self.rt8.close()

    def safemsg_matlab(self,msg):
        if not globals.CONNECTED_TO_MATLAB:
            return False
        try:
            self.tcp_socket.sendall(f"{msg}\n".encode())
        except:
            globals.error_msg = "Connection to matlab lost"
            globals.CONNECTED_TO_MATLAB = False
        return True

    def saferecv_matlab(self):
        if not globals.CONNECTED_TO_MATLAB:
            return ''
        try:
            msg = self.tcp_socket.recv(1024).decode("utf_8")
        except:
            globals.error_msg = "Connection to matlab lost"
            globals.CONNECTED_TO_MATLAB = False
        return msg
    
    def decodemsg(self,msg):
        if not msg:
            return

        match str(msg[0]):
            case "t": #Temperature given
                globals.temperature_target = float(msg[2:7])
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
    
    def get_average_temp(self,n):
        t = 0
        for value in self.values:
            t += value.getTemperature()
        return t/n
            


    def run(self):
        # Loop
        while not globals.STOP_RUNNING:
            # TODO: Test if this way of producing the error works. Maybe use value.getValue to check if short-circuited
            try:
                ret = self.rt8.getIoGroup(self.channels, self.values)
            except ValueError:
                print(ret)

            globals.temperature_average = self.get_average_temp(globals.NUMBER_OF_SENSORS)
            self.safemsg_matlab("AVG_TEMP\n{:.1f}".format(globals.temperature_average))

            # SAFETY
            if globals.temperature_average > globals.MAX_TEMP:
                globals.error_msg = f"Temperature exceeded limit of {globals.MAX_TEMP}"
                globals.OUTPUT_OFF = True
                self.psu.output_off()

            message = self.saferecv_matlab()
            self.decodemsg(message)

            #TODO: Check if if statement can be removed with no exceptions then more readable
            if globals.BYPASS_MODE:
                if self.psu.get_status()['output on']:
                    self.psu.output_off()
                if self.psu.get_status()['remote on']:
                    self.psu.remote_off()
                time.sleep(1)
                continue

            if not self.psu.get_status()['output on']:
                self.psu.remote_on()

            if not (globals.OUTPUT_PAUSE and globals.OUTPUT_OFF):
                pidout = self.pid.update(globals.temperature_average, globals.temperature_target)
                self.psu.set_voltage(pidout)          

            self.pid.settle_update(globals.temperature_average,globals.temperature_target)

            if self.pid.settle_check():
                globals.READY = True
                self.safemsg_matlab("READY")
            else:
                if globals.READY:
                    self.safemsg_matlab("NOT_READY")
                globals.READY = False
                            
            if globals.TARGET_TEMP_CHANGED.BY_UI:
                self.safemsg_matlab("TARGET_CHANGED\n{:.2f}".format(globals.temperature_target))
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