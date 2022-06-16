# Python packages
import time, threading, socket, atexit,serial

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
            except serial.SerialException:
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
            except ea.psu_ea.ExceptionPSU:
                time.sleep(5)                
            else:
                break

        globals.CONNECTED_TO_INSTRUMENTS = True

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
        except serial.SerialException:
            pass
        try:
            self.rt8.close()
        except TimeoutError:
            pass

    def safemsg_matlab(self,msg):
        if not globals.CONNECTED_TO_MATLAB:
            return
        try:
            self.tcp_socket.sendall(f"{msg}\n".encode())
        except ConnectionResetError:
            globals.error_msg = "Connection to matlab lost"
            globals.CONNECTED_TO_MATLAB = False

    def saferecv_matlab(self):
        if not globals.CONNECTED_TO_MATLAB:
            return ''
        try:
            msg = self.tcp_socket.recv(1024).decode("utf_8")
        except BlockingIOError:
            return ''
        else:
            return msg

    def listen_to_matlab(self):
        if globals.CONNECTED_TO_MATLAB:
            return
        while globals.ATTEMPT_TO_CONNECT:
            try:
                self.tcp_socket = socket.create_connection(('169.254.145.229', 4000),timeout=2)
            except TimeoutError:
                time.sleep(1)
            else:
                self.tcp_socket.setblocking(0)
                globals.CONNECTED_TO_MATLAB = True
                self.safemsg_matlab("CONNECTED")
                globals.ATTEMPT_TO_CONNECT = False
    
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
    
    def get_average_temp(self):
        try:
            self.rt8.getIoGroup(self.channels, self.values)
        except serial.SerialException:
            self.safemsg_matlab("RT8 lost. Restart required")
            globals.error_msg = "RT8 lost. Restart required"
            self.safeexit()
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
                if self.values.index(value) < globals.SENSORS_ON_GLASS:
                    t += sensor_temp
                max_temperature = max(sensor_temp,max_temperature)
        t = t/(globals.NUMBER_OF_SENSORS - globals.SENSORS_ON_GLASS)
        return [t,max_temperature]

    def regulate(self,sensor_max):
        self.psu.output_on()
        self.psu.remote_on()
        if sensor_max > globals.MAX_OP - 7:
            globals.MAX_TEMP_REACHED = True

        if not globals.MAX_TEMP_REACHED or globals.temperature_average > globals.temperature_target:
            self.pid.swap_controller(1)
            pidout = self.pid.update(globals.temperature_average, globals.temperature_target)
            globals.MAX_TEMP_REACHED = False
        else:
            self.pid.swap_controller(2)
            pidout = self.pid.update2(sensor_max, globals.MAX_OP - 2)
            if sensor_max < globals.MAX_OP - 12:
                globals.MAX_TEMP_REACHED = False
        self.psu.set_voltage(pidout)

    def safeoutput_off(self,sensor_max):
        if sensor_max > globals.MAX_OP - 7:
            self.psu.output_on()
            self.regulate(sensor_max)
            globals.error_msg = f"Maximum operating temperature of heater exceeded limit of {globals.MAX_OP}\n Safety regulation initialized"
            self.safemsg_matlab(f"Maximum operating temperature of heater exceeded limit of {globals.MAX_OP}\n Safety regulation initialized")
        else:
            self.psu.output_off()

    def bypass_mode(self):
        self.psu.output_off()
        self.psu.remote_off()
        for index, value in zip(range(globals.NUMBER_OF_SENSORS),self.values):
            globals.sensors_val[index] = value.getTemperature()
        time.sleep(1)
    
    def _loop(self):
        globals.temperature_average, sensor_max = self.get_average_temp()
        self.safemsg_matlab("AVG_TEMP\n{:.1f}".format(globals.temperature_average))

        # SAFETY
        if globals.temperature_average > globals.MAX_TEMP:
            globals.error_msg = f"Temperature exceeded limit of {globals.MAX_TEMP}"
            self.safemsg_matlab(f"Temperature exceeded limit of {globals.MAX_TEMP}")
            globals.OUTPUT_OFF = True

        if globals.TARGET_TEMP_CHANGED.BY_UI:
            self.safemsg_matlab("TARGET_CHANGED\n{:.2f}".format(globals.temperature_target))
            globals.TARGET_TEMP_CHANGED.BY_UI = False

        message = self.saferecv_matlab()
        self.decodemsg(message)

        try:
            self.psu.get_status()
        except serial.SerialException:
            globals.error_msg = "PSU lost. Restart required"
            self.safemsg_matlab("PSU lost. Restart required")
            self.safeexit()

        if globals.BYPASS_MODE:
            self.bypass_mode()
            return
        
        if globals.OUTPUT_OFF:
            self.psu.output_off()
            #self.safeoutput_off(sensor_max)
            return

        if globals.SETTINGS_CHANGED:
            self.pid.__init__() 
            globals.SETTINGS_CHANGED = False

        self.pid.settle_update(globals.temperature_average,globals.temperature_target,globals.CONSTANT_ERROR,globals.SLOPE)
        if self.pid.settle_check(globals.SLOPE,globals.TIMED):
            if not globals.READY:
                globals.READY = True
                self.safemsg_matlab("READY")
        else:
            if globals.READY:
                self.safemsg_matlab("NOT_READY")
                globals.READY = False

        if not globals.OUTPUT_PAUSE:
            self.regulate(sensor_max)          

    def run(self):
        while not globals.STOP_RUNNING:
            self.listen_to_matlab()
            self._loop()
            time.sleep(self.pid.Ts)