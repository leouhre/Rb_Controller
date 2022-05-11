#python packages
import time, threading

#our scripts
import globals

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
