# Python packages
import time, threading, socket, atexit,serial
from matplotlib.cbook import maxdict

# Import RTD measurement device
from lucidIo.LucidControlRT8 import LucidControlRT8
from lucidIo.Values import ValueTMS2
from lucidIo.Values import ValueTMS4
# Import power supply unit
import ea_psu_controller as ea

# Our scripts
from classes.pid import PID
import globals

class loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # Initialize the LucidControl RTD measurement device
        while True:
            try:
                self.rt8 = LucidControlRT8('/dev/lucidRI8')
                self.rt8.open()
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
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
            except ea.psu_ea.ExceptionPSU as ex:

                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)

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
        self.pid = PID()

        atexit.register(self.safeexit)

    def safeexit(self):
        try:
            self.psu.output_off()
            self.psu.remote_off()
            self.psu.close()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
        try:
            self.rt8.close()
        except TimeoutError as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

    def safemsg_matlab(self,msg):
        if not globals.CONNECTED_TO_MATLAB:
            return
        try:
            self.tcp_socket.sendall(f"{msg}\n".encode())
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            globals.error_msg = "Connection to matlab lost"
            globals.CONNECTED_TO_MATLAB = False

    def saferecv_matlab(self):
        if not globals.CONNECTED_TO_MATLAB:
            return ''
        try:
            msg = self.tcp_socket.recv(1024).decode("utf_8")
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            return ''
        else:
            return msg

    def listen_to_matlab(self):
        if globals.CONNECTED_TO_MATLAB:
            return
        while globals.ATTEMPT_TO_CONNECT:
            try:
                self.tcp_socket = socket.create_connection(('10.209.193.44', 4000),timeout=2)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                time.sleep(1)
            else:
                self.tcp_socket.setblocking(0)
                globals.CONNECTED_TO_MATLAB = True
                self.safemsg_matlab("CONNECTED")
                globals.ATTEMPT_TO_CONNECT = False
                break
    
    def decodemsg(self,msg):
        if msg:
            match str(msg[0]):
                case "t": #Temperature given
                    globals.temperature_target = float(msg[2:7])
                    globals.TARGET_TEMP_CHANGED.BY_MATLAB = True 
                    globals.SET = True
                    globals.OUTPUT_PAUSE = False
                    
                case "o": #output off
                    globals.OUTPUT_OFF = not globals.OUTPUT_OFF
                    self.psu.output_off()
                
                case "p": #output pause
                    globals.OUTPUT_PAUSE = not globals.OUTPUT_PAUSE

                case "s": #stop program
                    globals.STOP_RUNNING = True

                case "b": #Bypass mode
                    globals.BYPASS_MODE = not globals.BYPASS_MODE
    
    def get_average_temp(self,n):
        try:
            self.rt8.getIoGroup(self.channels, self.values)
        except serial.SerialException as ex:

            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)

        t = 0
        max_temperature = 0
        for value in self.values:
            sensor_temp = value.getTemperature()
            if -1000 > sensor_temp: 
                globals.error_msg = f"sensor{self.values.index(value)+1} is shortcircuited"
                self.safemsg_matlab(f"sensor{self.values.index(value)+1} is shortcircuited")
            elif sensor_temp > 1000:
                globals.error_msg= f"sensor{self.values.index(value)+1} is disconected"
                self.safemsg_matlab(f"sensor{self.values.index(value)+1} is disconected")
            else:
                if self.values.index(value) > globals.SENSORS_ON_GLASS:
                    t += sensor_temp
                max_temperature = max(sensor_temp,max_temperature)
        return [t/n,max_temperature]

    def regulate(self,sensor_max):
        if sensor_max > globals.MAX_OP - 7:
            globals.MAX_TEMP_REACHED = True

        if not globals.MAX_TEMP_REACHED or globals.temperature_average > globals.temperature_target:
            pidout = self.pid.update(globals.temperature_average, globals.temperature_target)
            globals.MAX_TEMP_REACHED = False
        else:
            pidout = self.pid.update2(sensor_max, globals.MAX_OP - 2)
            if sensor_max < globals.MAX_OP - 12:
                globals.MAX_TEMP_REACHED = False
        self.psu.set_voltage(pidout)
    
    def _loop(self):
        globals.temperature_average,sensor_max = self.get_average_temp(globals.NUMBER_OF_SENSORS)
        self.safemsg_matlab("AVG_TEMP\n{:.1f}".format(globals.temperature_average))

        # SAFETY
        if globals.temperature_average > globals.MAX_TEMP:
            globals.error_msg = f"Temperature exceeded limit of {globals.MAX_TEMP}"
            globals.OUTPUT_OFF = True

        message = self.saferecv_matlab()
        self.decodemsg(message)

        if globals.BYPASS_MODE:
            self.psu.output_off()
            self.psu.remote_off()
            time.sleep(1)
            return

        if globals.OUTPUT_OFF:
            self.psu.output_off()
        else:
            self.psu.output_on()

        self.psu.remote_on()

        if not (globals.OUTPUT_PAUSE or globals.OUTPUT_OFF):
            self.regulate(sensor_max)          

        self.pid.settle_update(globals.temperature_average,globals.temperature_target)
        
        if self.pid.settle_check():
            if not globals.READY:
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

    def run(self):
        while not globals.STOP_RUNNING:
            self.listen_to_matlab()
            self._loop()
            time.sleep(self.pid.Ts)