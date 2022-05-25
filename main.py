#! Creates UI and initializes loop for regulating temperature.
#Python packages 
import time
import sys
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from guizero import App, Text, Box, PushButton, Window, TextBox, CheckBox, Slider, Combo
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#our scripts
# import loop
import loop_simulator
import globals

#names
globals.initialize_variables()
MIN_TEMP = 0
background_color = "#5B5A51"
text_color = 'white'
config_path = 'config.txt'

def set_temperature():
    settemp.value = "{:3.2f}".format(max(min(float(settemp.value),globals.MAX_TEMP),MIN_TEMP))
    globals.temperature_target = float(settemp.value)
    globals.SET = True
    globals.TARGET_TEMP_CHANGED.BY_UI = True 

#GUI related methods 
def close_popup_message():
    popup_msg.value = ""
    popup_window.visible = False

def swap_windows(to):
    global selected_widget
    if to == 'controller':
        save_changes_window.visible = True
    if to == 'settings':
        selected_widget = proportional_gain_textbox
        settings_window.visible = True
        settings_window.full_screen = True

def apply_settings(answer):
    global selected_widget
    global textboxes
    if answer == 'no':
        with open(config_path,'r') as config:
            for textbox in textboxes:
                textbox.value = float(config.readline())
    
    if answer == 'yes':
        with open(config_path,'w') as config:
            for textbox in textboxes:
                config.write(textbox.value + "\n")
        globals.MAX_TEMP = float(temperature_limit_textbox.value)
        globals.SETTINGS_CHANGED = True

    save_changes_window.visible = False
    settings_window.visible = False
    selected_widget = settemp

def show_brightness_window():
    brightness_window.visible = not brightness_window.visible

def adjust_brightnes():
    #TODO: implement this
    print(f"brightness={brightness_slider.value}")
    globals.error_msg = "Hi"

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

def set_output_pause():
    globals.OUTPUT_PAUSE = not globals.OUTPUT_PAUSE

def set_output_off():
    globals.OUTPUT_OFF = not globals.OUTPUT_OFF

def get_min_xlim():
    if 'all' in time_scale_combo.value:
        return sys.maxsize
    return max(int(time_scale_combo.value[10:-1]),0)

def connect_to_matlab():
    globals.ATTEMPT_TO_CONNECT = True
    connecting_window.visible = True
    controller_window.disable()

def stop_connecting_to_matlab():
    globals.ATTEMPT_TO_CONNECT = False
    connecting_window.visible = False
    controller_window.enable()

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
        btn = PushButton(numpad_box, text=i+1, grid=[int(i%3),int(i/3)],command=numpad,args=[i+1],width=3)
        btn.text_size = size
    for i, x in enumerate(['.',0,'c']):
        btn = PushButton(numpad_box, text=x, grid=[i,3],command=numpad,args=[x],width=3)
        btn.text_size = size

def update_temperature():
    temp.value = "{:4.1f}".format(globals.temperature_average)

def updates_controller():
    if globals.STOP_RUNNING:
        app.destroy()

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
        connect_to_matlab_button.text_color = 'green'
        connect_to_matlab_button.disable()
    else:
        connect_to_matlab_button.text_color = 'red'
        connect_to_matlab_button.enable()

def updates_settings():
    if globals.BYPASS_MODE:
        use_power_supply_button.bg = 'grey'
    else:
        use_power_supply_button.bg = background_color

def updates_popup():
    if globals.error_msg:
        msg = globals.error_msg
        splits = len(msg)//14
        for x in range(1,splits+1):
            i = msg.rfind(' ',0,14*x)
            msg = msg[:i] + '\n' + msg[i:]
        popup_msg.value = msg
        popup_window.visible = True
        globals.error_msg = ""
        
def updates_connecting():
    if globals.CONNECTED_TO_MATLAB:
        connecting_window.visible = False
    else:
        if '...' in connecting_text.value:
            connecting_text.value = "Connecting to matlab"
        else:
            connecting_text.append('.')


#GUI
app = App(visible=False)
app.text_color = 'white'

connecting_window = Window(app,title="connecting",visible=False,width=300,height=120)
connecting_window.text_size = 18
connecting_window.bg = background_color
connecting_text = Text(connecting_window,text="Connecting to matlab")
cancel_pushbutton = PushButton(connecting_window,text="Cancel",width=10,command=stop_connecting_to_matlab)

popup_window = Window(app,title="WARNING",visible=False,width=300,height=300)
popup_window.text_size = 28
popup_window.bg = background_color
Text(popup_window,text="",size=10)
popup_msg = Text(popup_window,text="",color='red')
Text(popup_window,text="",size=10)
PushButton(popup_window,text="Close",command=close_popup_message,width=10)

brightness_window = Window(app,title="Brightness settings",visible=False,height=200,width=400)
brightness_window.text_size = 40
brightness_slider = Slider(brightness_window,start=0,end=100,command=adjust_brightnes,width=280,height=70)

save_changes_window = Window(app,title="Brightness settings",visible=False,height=140,width=260)
Text(save_changes_window,text='Save Changes?',align='top')
PushButton(save_changes_window,text='YES',align='left',width='fill',command=apply_settings,args=['yes'])
PushButton(save_changes_window,text='NO',align='right',width='fill',command=apply_settings,args=['no'])
save_changes_window.bg = background_color
save_changes_window.text_size = 24

controller_window = Window(app,title='Rb-cell Temperature Controller',layout='grid',bg=background_color,height=480,width=800)
#row 0
Text(controller_window,text='Rubidium Cell Temperature Controller',align='left',grid=[1,0,2,1]) 
connect_to_matlab_button = PushButton(controller_window,text='Connect to matlab',align='left',grid=[0,0],command=connect_to_matlab) 
settings_button = PushButton(controller_window, text="Settings",align='right',grid=[4,0],command=swap_windows,args=['settings'],pady=1)
settings_button.text_size = 18
brightness_button = PushButton(controller_window, text="¤",grid=[3,0,2,1],padx=14,pady=1,command=show_brightness_window)
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
spawn_numpad(Box(controller_window,grid=[0,2,2,9],align='left'),20)
#row 3 
plot_box = Box(controller_window,grid=[3,3,2,8],align='right',layout='grid',border=True)
#row 4
set_box = Box(controller_window,grid=[2,4,1,6])
Text(set_box, text="Set Temperature")
settemp = Text(set_box, text='1')
settemp.text_size = 28
#row 8
crement_box = Box(controller_window,grid=[2,10])
scale_button = PushButton(crement_box,text="1",command=scale,align='right',padx=12,pady=5,width=2,height=1)
scale_button.text_size = 20
increasetemp_button = PushButton(crement_box,text="+",command=increment,args=[1],align='right',padx=12,pady=5,width=2,height=1)
increasetemp_button.text_size = 20
decreasetemp_button = PushButton(crement_box,text="-",command=increment,args=[-1],align='right',padx=12,pady=5,width=2,height=1)
decreasetemp_button.text_size = 20

#Settings window
settings_window = Window(app,title='Settings',width=800,height=480,bg=background_color,visible=False,layout='grid')
settings_window.text_size = 13 
#Title row 0
Text(settings_window,text='Rb-controller Settings',grid=[0,0,2,1],align='left')
use_power_supply_button = PushButton(settings_window,text='Use power supply',grid=[2,0,2,1],command=set_bypass_mode)
use_power_supply_button.text_size = 16
controller_button = PushButton(settings_window, text="controller",align='right',grid=[4,0],command=swap_windows,args=['controller'])
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
slope_checkbox = CheckBox(settings_window,text='Timed',grid=[0,12])
wait_time_textbox = TextBox(settings_window,grid=[1,12])
#numpad
spawn_numpad(Box(settings_window,grid=[4,2,1,12]),size=24)

#temperature/time plot
f = plt.figure(figsize=(4,3.5))
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
    tmin_index = np.argmax(np.isclose(current_time-get_min_xlim(),time_data,atol=1))
    line.set_data(time_data, temperature_data)
    axis.set_xlim(xmin=tmin_index,xmax=time_data[-1])
    canvas.draw()

anim = animation.FuncAnimation(f, animate, interval = 1000)

canvas = FigureCanvasTkAgg(f, plot_box.tk)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

#schduled updates
controller_window.repeat(100, updates_controller)
settings_window.repeat(100, updates_settings)
popup_window.repeat(100, updates_popup)
connecting_window.repeat(1000, updates_connecting)
temp.repeat(100, update_temperature)

#events
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

with open(config_path, 'r') as config:
    for textbox in textboxes:
        textbox.value = float(config.readline())
    globals.MAX_TEMP = float(temperature_limit_textbox.value)

#TODO: use the uncommented line when in lab
# main_loop_thread = loop.loop()
main_loop_thread = loop_simulator.loop()
main_loop_thread.start()
app.display() # infinite loo

globals.STOP_RUNNING = True
main_loop_thread.join