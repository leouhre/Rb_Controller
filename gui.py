#python packages
import time, sys
import socket
from guizero import App, Text, Box,TextBox, PushButton, CheckBox, Slider
import time, threading, numpy as np

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

FREQUENCY = 0.1
target_temperature = 0
temperature = 0
BYPASS_MODE = 0
STOP_REGULATING = 0

def clamp(val,min_val,max_val):
    return max(min(val,max_val),min_val)

def set_target_temperature(x):
    global target_temperature
    target_temperature = clamp(x,30,200) #set bounds for temperature

def gui():

    #functions for GUI

    def set_temperature():
        try:
            set_target_temperature(float(settemp.value))
        except ValueError:
            pass
    
    def increase_temperature():
        global target_temperature
        set_target_temperature(target_temperature + 1)
        settemp.value = target_temperature
    
    def decrease_temperature():
        global target_temperature
        set_target_temperature(target_temperature - 1)
        settemp.value = target_temperature

    def update_time():
        clock.value = time.strftime("Clock: %I:%M:%S %p", time.localtime())

    def update_temperature():
        global temperature
        temp.value = "{:4.1f}".format(temperature)
    
    def set_bypass_mode():
        global BYPASS_MODE
        BYPASS_MODE = bypass_check.value

    def set_stop_regulating():
        global STOP_REGULATING
        STOP_REGULATING = stop_regulating.value

        
    def update():
        #check if bypass mode is enabled
        if BYPASS_MODE:
            settemp.disable()
            increasetemp_button.disable()
            decreasetemp_button.disable()
        else:
            settemp.enable()
            increasetemp_button.enable()
            decreasetemp_button.enable()
        
        #check if Targettemperature is within bounds 

        



    app = App("Dream GUI",bg="#5B5A51",width=800,height=480)
    app.full_screen = True


    title_box = Box(app, width='fill',align='top',border=True)
    left_box = Box(app, width='fill',align='left',border=True)
    right_box = Box(app, width='fill',align='right',border=True)
    bottom_box = Box(app, width='fill',align='bottom',border=True)

    #in title box
    clock = Text(title_box, text="Clock: ",color="white",align='right')
    clock.repeat(1000, update_time)
    title = Text(title_box, text="Rubidum Cell Temperature Controller",color="white",align="left")


    #in right box
    temp_title = Text(right_box, text="Actual Temperature",color= "white")
    temp = Text(right_box, text="",color = "white")
    temp.repeat(1000, update_temperature)

    #in left box
    crement_box = Box(left_box,align='right',border=True)
    increasetemp_button = PushButton(crement_box,text="+",command=increase_temperature,align='top',padx=5,pady=5,width=2,height=1)
    decreasetemp_button = PushButton(crement_box,text="-",command=decrease_temperature,align='bottom',padx=5,pady=5,width=2,height=1)

    set_box = Box(left_box,align='right',border=True)
    settemp_title = Text(set_box, text="Set Temperature",color= "white", width=13, height=1)
    settemp = TextBox(set_box, text="Set Temperature", command=set_temperature, width=13, height=3)
    settemp.text_color = "white"; settemp.text_size = 12; settemp.bg ="#7e7e7e"

    numpad_box = Box(left_box,layout='grid',align='right',border=True)
    button1 = PushButton(numpad_box, text="1", grid=[0,0])
    button2 = PushButton(numpad_box, text="2", grid=[1,0])
    button3  = PushButton(numpad_box, text="3", grid=[2,0])
    button4  = PushButton(numpad_box, text="4", grid=[0,1])
    button5  = PushButton(numpad_box, text="5", grid=[1,1])
    button6  = PushButton(numpad_box, text="6", grid=[2,1])
    button7  = PushButton(numpad_box, text="7", grid=[0,2])
    button8  = PushButton(numpad_box, text="8", grid=[1,2])
    button9  = PushButton(numpad_box, text="9", grid=[2,2])
    button0  = PushButton(numpad_box, text="0", grid=[1,3])
    buttondel  = PushButton(numpad_box, text="c", grid=[2,3])

    settemp_slider = Slider(set_box,start=30,end=200,align='bottom')

    #in bottom box
    bypass_check = CheckBox(bottom_box,text="Enter Bypass",command=set_bypass_mode)
    stop_regulating = CheckBox(bottom_box,text="Stop Regulating",command=set_stop_regulating)

    #invisible button for check loops
    gui_loop = Text(app,visible=False)
    gui_loop.repeat(1000,update)


    app.display()


def main_loop():
    # Initialize the LucidControl RTD measurement device. Can be /dev/ttyACM0 or /dev/ttyACM1:
    for n in range(2):
        rt8 = LucidControlRT8(f'/dev/ttyACM{n}')
        try:
            if (rt8.open() == False):
                rt8.close()
            else:
                # Identify device
                ret = rt8.identify(0)
                if ret == IoReturn.IoReturn.IO_RETURN_OK:
                    break
                else:
                    rt8.close()
        except:
            rt8.close()

    # Initialize tuple of 8 temperature objects (high resolution - otherwise use ValueTMS2)
    values = (ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4(), 
        ValueTMS4(), ValueTMS4(), ValueTMS4(), ValueTMS4())

    # Initialize a boolean tuple for channels to read
    # Make sure this tuple matches the physical setup on the LucidControl device
    num_of_sensors = 2
    
    channels = (True, )*num_of_sensors + (False, )*(8-num_of_sensors)
    
    """
    channels = ()
    for x in range(8):
        if x < num_of_sensors:
            channels += (True, )
        else:
            channels += (False, )
    """

    # Initialize the Elektro-Automatik Power Supply
    psu = ea.PsuEA()
    psu.remote_on()

    # Initiate measurements at constant voltage
    psu.set_current(4)
    psu.set_voltage(0)
    psu.output_on()

    #initialize PID
    pid = PID

    #FLAG
    STOP_RUNNING = False

    # Create a connection to the server application on port 81
    tcp_socket = socket.create_connection(('192.168.137.1', 4000))
    tcp_socket.setblocking(0)
    tcp_socket.sendall("connected".encode())


    # Loop 
    while not STOP_RUNNING:
        global temperature
        global temperature_target
        global STOP_REGULATING
        global BYPASS_MODE

        ret = rt8.getIoGroup(channels, values)

        temperature_average = 0
        for x in range(num_of_sensors):
            temperature_average = temperature_average + values[x].getTemperature() #change to for sensors in values  and  sensor.getTemperature
        temperature_average = temperature_average/num_of_sensors 	

        try:
            message = tcp_socket.recv(1024).decode("utf_8") # try a with statement here
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
            pid.update_error(temperature_average,temperature_target)
            psu.set_voltage(pid.regulate_output()) 
        

        if abs(temperature_target - temperature_average) < 1:
            count = count + 1
            if count == 100: #Temperature has been within 1C of target for more at least 100 samples
                tcp_socket.sendall("READY".encode()) #Send READY to matlab via serial
        else: 
            count = 0
        
        time.sleep(FREQUENCY)
                
    
    psu.output_off()
    tcp_socket.close()
    rt8.close()



gui_thread = threading.Thread(target=gui,)
main_loop_thread = threading.Thread(target=main_loop)


gui_thread.start()
main_loop_thread.start()