from collections import deque
import time, sys
from classes.pid import PID

PI = PID()
    
timer = time.time()
    

while True:
    if (time.time() - timer) > 1:
        x = input()
        match x:
            case "0": #no message  
                print("0")
            case "1": #Temperatur given
                temperature_target = sys
                STOP_REGULATING = False
                print("1")
            case "2": #stop regulating
                STOP_REGULATING = True
                print("2")
            case "3": #stop program
                STOP_RUNNING = True
                print("3")
            case "4": #Bypass mode
                BYPASS_MODE = True
                print("4")
                while BYPASS_MODE:
                    print("while")
                    if int(input()) == 4:

                        print("break")
                        break


