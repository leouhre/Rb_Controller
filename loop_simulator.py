#python packages
import time, threading, socket, atexit

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
        self.FREQUENCY = 0.4
        # Initialize the Elektro-Automatik Power Supply
        globals.CONNECTED = True
        self.count = 0

    def run(self):
        # Loop
        while not globals.STOP_RUNNING:


            if globals.STOP_REGULATING:
                globals.temperature_average -= 0.1
            else:
                globals.temperature_average += min(max(globals.temperature_target - globals.temperature_average,0-1),5)

            while globals.BYPASS_MODE:
                time.sleep(1)


            if abs(globals.temperature_target - globals.temperature_average) < 1:
                self.count += 1
                if self.count == 20: #Temperature has been within 1C of target for more at least 100 samples
                    globals.READY = True
            else: 
                self.count = 0
                globals.READY = False

            time.sleep(self.FREQUENCY)
        exit()
