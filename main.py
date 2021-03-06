#!/home/pi/.venv/RbController/bin/python
#Creates UI and initializes loop for regulating temperature.
#Python packages 
import time
import sys
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import shelve
from guizero import App, Text, Box, PushButton, Window, TextBox, CheckBox, Slider, Combo
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rpi_backlight import Backlight

#our scripts
import loop
import globals

#names
globals.initialize_variables()
backlight = Backlight()
MIN_TEMP = 0
background_color = "#5B5A51"
text_color = 'white'

def set_temperature():
    try:
        settemp.value = "{:3.2f}".format(max(min(float(settemp.value),globals.MAX_TEMP),MIN_TEMP))
    except ValueError:
        controller_window.error(title='Error in Set Temperature',text='value entered is not a number')
    else:
        globals.temperature_target = float(settemp.value)
        globals.SET = True
        globals.TARGET_TEMP_CHANGED.BY_UI = True 

def load_settings():
    with shelve.open('config') as config:
        for textbox, val in zip(textboxes,config.values()):
            textbox.value = val
        globals.MAX_TEMP = config['temperature_limit']

def save_settings():
    if not settings_changed:
        return

    with shelve.open('config') as config:
        for textbox, key in zip(textboxes,config.keys()):
            config[key] = float(textbox.value)

    globals.SETTINGS_CHANGED = True

def settings_changed():
    with shelve.open('config') as config:
        for textbox, val in zip(textboxes,config.values()):
            try:
                settings_changed = float(textbox.value) != float(val)
            except ValueError:
                settings_window.error(title='Error in parameters',text='value entered is not a number \n settings discarded')
                load_settings()
                return False
            else:
                if settings_changed:
                    return True
    
#GUI related methods 
def when_settings_closed():
    global selected_widget
    if settings_changed():
        answer = settings_window.yesno(title="Settings have been changed", text='Do you want to apply the settings?')
    else:
        answer = False            
    if answer:
        save_settings()
    else:
        load_settings()
    settings_window.visible = False
    selected_widget = settemp

def swap_windows():
    global selected_widget
    selected_widget = proportional_gain_textbox
    settings_window.visible = True

def show_brightness_window():
    brightness_window.visible = not brightness_window.visible

def adjust_brightnes(slider_value):
    backlight.brightness = int(slider_value)

def increment(n): 
    if not settemp.value:
        settemp.value = round(n*float(scale_button.text),1)
    elif not (float(settemp.value) + n*float(scale_button.text) > globals.MAX_TEMP or float(settemp.value) + n*float(scale_button.text) < MIN_TEMP):
        settemp.value = round(float(settemp.value) + n*float(scale_button.text),1)
    globals.SET = False

def scale():
    if scale_button.text == '1':
        scale_button.text = '0.1'
    else:
        scale_button.text = '1'

def set_bypass_mode():
    globals.BYPASS_MODE = not globals.BYPASS_MODE
    if globals.BYPASS_MODE:
        bypass_window.visible = True
    else:
        bypass_window.visible = False

def set_output_pause():
    globals.OUTPUT_PAUSE = not globals.OUTPUT_PAUSE

def set_output_off():
    globals.OUTPUT_OFF = not globals.OUTPUT_OFF

def get_graphl():
    if 'all' in time_scale_combo.value:
        return sys.maxsize
    return int(time_scale_combo.value[10:-1])

def connect_to_matlab():
    globals.ATTEMPT_TO_CONNECT = True
    controller_window.disable()
    connecting_window.visible = True

def stop_connecting_to_matlab():
    globals.ATTEMPT_TO_CONNECT = False
    connecting_window.visible = False
    controller_window.enable()

def close_program():
    controller_window.cancel(updates_controller)
    settings_window.cancel(updates_settings)
    app.cancel(updates_popup)
    connecting_window.cancel(updates_connecting)
    temp.cancel(update_temperature)
    bypass_window.cancel(updates_bypass)
    plt.close(f)
    app.destroy()

def reset_plot():
    global start_time, time_data, temperature_data
    start_time = time.perf_counter()
    time_data,temperature_data = [],[]

def numpad(btn):
    match btn:
        case '.':
            if '.' not in selected_widget.value:
                selected_widget.append(btn)
        case 'c':
            selected_widget.value = selected_widget.value[:-1]
        case _:
            selected_widget.append(btn)
    globals.SET = False

def spawn_numpad(master,size):
    numpad_box = Box(master,layout='grid')
    for i in range(9):
        btn = PushButton(numpad_box, text=i+1, grid=[int(i%3),int(i/3)],command=numpad,args=[i+1],width=2)
        btn.text_size = size
    for i, x in enumerate(['.',0,'c']):
        btn = PushButton(numpad_box, text=x, grid=[i,3],command=numpad,args=[x],width=2)
        btn.text_size = size

def center_window(width, height, window):
    # get screen width and height
    screen_width = window.tk.winfo_screenwidth()
    screen_height = window.tk.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.tk.geometry('%dx%d+%d+%d' % (width, height, x, y))

def update_temperature():
    try:
        float(temperature_offset_textbox.value)
    except ValueError:
        temp.value = "{:4.1f}".format(globals.temperature_average)
    else:
        temp.value = "{:4.1f}".format(globals.temperature_average - float(temperature_offset_textbox.value))
    

def updates_controller():
    if globals.STOP_RUNNING:
        close_program()

    if globals.TARGET_TEMP_CHANGED.BY_MATLAB:
        settemp.value = globals.temperature_target
        globals.TARGET_TEMP_CHANGED.BY_MATLAB = False

    if globals.READY:
        ready_text.text_color = 'green'
        ready_text.value = 'READY'
    else:
        ready_text.text_color = 'red'
        ready_text.value = 'NOT READY'

    if globals.OUTPUT_PAUSE:
        pause_output_button.bg = 'grey'
    else:
        pause_output_button.bg = background_color
    
    if globals.OUTPUT_OFF:
        output_off_button.bg = 'grey'
    else:
        output_off_button.bg = background_color

    if globals.SET:
        set_temp_button.disable()
    else:
        set_temp_button.enable()

    if globals.CONNECTED_TO_MATLAB:
        connect_to_matlab_button.disable()
    else:
        connect_to_matlab_button.enable()

def updates_settings():
    if not settings_window.visible:
        return

    if globals.BYPASS_MODE:
        use_power_supply_button.bg = 'grey'
    else:
        use_power_supply_button.bg = background_color

    globals.CONSTANT_ERROR = contant_error_checkbox.value
    globals.SLOPE = slope_checkbox.value
    globals.TIMED = time_checkbox.value

def updates_popup():
    if globals.error_msg:
        msg = globals.error_msg
        globals.error_msg = ""
        app.warn(title='error',text=msg)
        
def updates_connecting():
    if not connecting_window.visible:
        controller_window.enable()
        return
    if globals.CONNECTED_TO_MATLAB:
        connecting_window.visible = False
    else:
        if '...' in connecting_text.value:
            connecting_text.value = "Connecting to matlab"
        else:
            connecting_text.append('.')

def updates_bypass():
    if not bypass_window.visible:
        return
    s1_text.value = f"sensor1 temperature: {globals.sensors_val[0]}C\n"
    s2_text.value = f"sensor2 temperature: {globals.sensors_val[1]}C\n"
    s3_text.value = f"sensor3 temperature: {globals.sensors_val[2]}C\n"
    s4_text.value = f"sensor4 temperature: {globals.sensors_val[3]}C\n"

#GUI
app = App(visible=False)
app.text_color = 'white'

bypass_window = Window(app,title="Bypass mode",bg=background_color,height=480,width=800)
center_window(bypass_window.width,bypass_window.height,bypass_window)
bypass_window.text_size = 30
Text(bypass_window,text=f"MAX OPERATING TEMP = {globals.MAX_OP}C", bg='red')
s1_text = Text(bypass_window,text="sensor 1:")
s2_text = Text(bypass_window,text="sensor 2:")
s3_text = Text(bypass_window,text="sensor 3:")
s4_text = Text(bypass_window,text="sensor 4:")
bypass_window.visible = False

connecting_window = Window(app,title="connecting",bg = background_color,width=300,height=120)
center_window(connecting_window.width,connecting_window.height,connecting_window)
connecting_window.text_size = 18
connecting_text = Text(connecting_window,text="Connecting to matlab")
cancel_pushbutton = PushButton(connecting_window,text="Cancel",width=10,command=stop_connecting_to_matlab)
connecting_window.visible = False

brightness_window = Window(app,title="Brightness settings",height=200,width=400)
center_window(brightness_window.width,brightness_window.height,brightness_window)
brightness_window.text_size = 40
brightness_slider = Slider(brightness_window,start=10,end=100,command=adjust_brightnes,width=280,height=70)
brightness_slider.value = 100
brightness_window.visible = False

controller_window = Window(app,title='Rb-cell Temperature Controller',layout='grid',bg=background_color,height=480,width=800)
center_window(controller_window.width,controller_window.height,controller_window)
#row 0
Text(controller_window,text=' ',grid=[1,0],width=16)
connect_to_matlab_button = PushButton(controller_window,text='Connect to matlab',align='left',grid=[0,0],command=connect_to_matlab) 
settings_button = PushButton(controller_window, text="Settings",align='right',grid=[4,0],command=swap_windows,pady=1)
settings_button.text_size = 18
brightness_button = PushButton(controller_window, text="??",grid=[3,0,2,1],padx=14,pady=1,command=show_brightness_window)
brightness_button.text_size = 16
#row 1
output_off_button = PushButton(controller_window,text="Output\nOff",grid=[0,1],height=1,width=4,command=set_output_off)
output_off_button.text_size = 20
pause_output_button = PushButton(controller_window,text="Pause\nOutput",grid=[1,1],command=set_output_pause,height=1,width=4)
pause_output_button.text_size = 20
set_temp_button = PushButton(controller_window,text="Set\nTemp",grid=[2,1],command=set_temperature,height=1,width=4)
set_temp_button.text_size = 20
temp_box = Box(controller_window,grid=[3,0,1,2],align='right')
ready_text = Text(temp_box, text="NOT READY",color = "red")
temp_title = Text(temp_box, text="Actual Temperature")
temp = Text(temp_box, text="0")
temp.text_size = 28
time_scale_combo = Combo(controller_window,options=['show last 10s','show last 20s',
                                                    'show last 30s','show last 60s',
                                                    'show last 120s','show last 300s',
                                                    'show last 600s','show all'], grid=[4,1],align='bottom',width=15)
time_scale_combo.text_size = 18
#Row 2
spawn_numpad(Box(controller_window,grid=[0,2,2,9],align='left'),22)
#row 3 
plot_box = Box(controller_window,grid=[3,3,2,8],align='right',layout='grid',border=True)
#row 4
set_box = Box(controller_window,grid=[1,4,2,6],align='right')
Text(set_box, text=' ',width=20)
Text(set_box, text="Set Temperature")
settemp = Text(set_box, text='1')
settemp.text_size = 28
#row 8
crement_box = Box(controller_window,grid=[1,9,2,1],align='right')
scale_button = PushButton(crement_box,text="1",command=scale,align='right',width=2)
scale_button.text_size = 20
increasetemp_button = PushButton(crement_box,text="+",command=increment,args=[1],align='right',width=2)
increasetemp_button.text_size = 20
decreasetemp_button = PushButton(crement_box,text="-",command=increment,args=[-1],align='right',width=2)
decreasetemp_button.text_size = 20

#Settings window
settings_window = Window(app,title='Rb-controller Settings',width=800,height=480,bg=background_color,layout='grid')
center_window(settings_window.width,settings_window.height,settings_window)
settings_window.text_size = 13 
settings_window.visible = False
#Title row 0
reset_button = PushButton(settings_window, text="Reset plot",grid=[0,0],command=reset_plot)
reset_button.bg = 'red'
use_power_supply_button = PushButton(settings_window,text='Use power supply',grid=[1,0,3,1],command=set_bypass_mode)
use_power_supply_button.text_size = 16
controller_button = PushButton(settings_window, text="Save settings",align='right',grid=[4,0],command=save_settings)
controller_button.text_size = 16
#PID row 2
Text(settings_window,text='Proportional:',grid=[1,2])
Text(settings_window,text='Intergral:',grid=[2,2])
Text(settings_window,text='    Derivative:     ',grid=[3,2])
#PID textBoxes row 3
Text(settings_window,text='PID Gains:',grid=[0,3])
proportional_gain_textbox = TextBox(settings_window,grid=[1,3])
integral_gain_textbox = TextBox(settings_window,grid=[2,3])
derivative_gain_textbox = TextBox(settings_window,grid=[3,3])
#Temperature row 4
temperature_limit_title = Text(settings_window,text='Temperature Limit',grid=[1,4])
temperature_offset_title = Text(settings_window,text='Temperature Offset',grid=[2,4])
#Temperature textboxes row 5
Text(settings_window,text='Temperature:',grid=[0,5])
temperature_limit_textbox = TextBox(settings_window,grid=[1,5])
temperature_offset_textbox = TextBox(settings_window,grid=[2,5])
#settling type row 6 
Text(settings_window,text='Settling type:',grid=[0,7])
#settlings param row 7
Text(settings_window,text='Max Temperature \n Fluctuations[+/-]: ',grid=[1,7])
#row 8
contant_error_checkbox = CheckBox(settings_window,text='Constant Error',grid=[0,8])
settling_temperature_fluctuations_textbox = TextBox(settings_window,grid=[1,8])
#row 9
Text(settings_window,text='Settle slope [C/s]:',grid=[1,9])
Text(settings_window,text='Slope length [s]:',grid=[2,9])
#row 10
slope_checkbox = CheckBox(settings_window,text='Slope',grid=[0,10])
settle_slope_textbox = TextBox(settings_window,grid=[1,10])
slope_length_textbox = TextBox(settings_window,grid=[2,10])
#row 11
Text(settings_window,text='Settle wait time[s]:',grid=[1,11])
#row 12
time_checkbox = CheckBox(settings_window,text='Timed',grid=[0,12])
wait_time_textbox = TextBox(settings_window,grid=[1,12])
#numpad
spawn_numpad(Box(settings_window,grid=[3,5,2,12],align='right'),size=28)

#temperature/time plot
f = plt.figure(figsize=(4,3.2))
axis = plt.axes(xlim =(0, 10), ylim =(0, 200))
line, = axis.plot([], [], linewidth = 2)
axis.set_xlabel('Time[s]')
axis.set_ylabel('Temperature[C]')

start_time = time.perf_counter()
time_data,temperature_data = [],[]

def animate(i):
    current_time = time.perf_counter() - start_time
    time_data.append(current_time)
    temperature_data.append(globals.temperature_average)
    tmin = current_time-get_graphl()
    tempmin_index = np.argmax(np.isclose(tmin,time_data,atol=1))
    line.set_data(time_data, temperature_data)
    axis.set_xlim(xmin=max(tmin,0),xmax=time_data[-1])
    axis.set_ylim(ymin=max(min(temperature_data[tempmin_index:])-10,0),ymax=max(temperature_data[tempmin_index:])+10)
    canvas.draw()

anim = animation.FuncAnimation(f, animate, interval = 1000)

canvas = FigureCanvasTkAgg(f, plot_box.tk)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

#schduled updates
controller_window.repeat(100, updates_controller)
settings_window.repeat(100, updates_settings)
app.repeat(100, updates_popup)
connecting_window.repeat(1000, updates_connecting)
temp.repeat(100, update_temperature)
bypass_window.repeat(100, updates_bypass)

#events
controller_window.when_closed = close_program
connecting_window.when_closed = stop_connecting_to_matlab
settings_window.when_closed = when_settings_closed
bypass_window.when_closed = set_bypass_mode

def clicked(event_data):
    global selected_widget
    selected_widget = event_data.widget

    #Tuple of all settings textboxes
textboxes = (
    proportional_gain_textbox, 
    integral_gain_textbox,
    derivative_gain_textbox,
    temperature_limit_textbox,
    temperature_offset_textbox,
    settling_temperature_fluctuations_textbox,
    settle_slope_textbox,
    slope_length_textbox,
    wait_time_textbox)

    #assing event method "clicked" to textboxes
for textbox in textboxes:
    textbox.when_clicked = clicked 

#initializations
selected_widget = settemp
contant_error_checkbox.value = 1
slope_checkbox.value = 0
time_checkbox.value = 1
load_settings()

main_loop_thread = loop.loop()
main_loop_thread.start()
app.display() # infinite loop 

globals.STOP_RUNNING = True
main_loop_thread.join
