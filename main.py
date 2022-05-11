#! regulates temperature of rubidium cell
#Python packages 
import threading, time
from guizero import App, Text, Box, PushButton, Window, TextBox, CheckBox, Slider, Combo
import tkinter as tk
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
#our scripts
# import loop
import loop_simulator
import globals

#names
globals.initialize_variables()
MAX_TEMP = 200
MIN_TEMP = 0
background_color = "#5B5A51"
text_color = 'white'

def set_target_temperature(temperature):
    globals.temperature_target = max(min(temperature,MAX_TEMP),MIN_TEMP)
    globals.TARGET_TEMP_CHANGED.BY_UI = True #will be set false by loop.py when it has reacted

#functions for Main GUI
def swap_windows():
    settings_window.visible = not settings_window.visible
    settings_window.full_screen = not settings_window.full_screen
    global selected_widget
    selected_widget = settemp
    #TODO: apply new settings when swapping windows


def check_for_errors():
    if globals.STOP_RUNNING:
        app.destroy()

def set_temperature():
    set_target_temperature(float(settemp.value))
    settemp.value = "{:3.2f}".format(float(settemp.value))
    globals.SET = True

def increment(n): 
    if not settemp.value:
        settemp.value = round(n*float(scale_button.text),1)
    elif not (float(settemp.value) + n*float(scale_button.text) > MAX_TEMP or float(settemp.value) + n*float(scale_button.text) < MIN_TEMP):
        settemp.value = round(float(settemp.value) + n*float(scale_button.text),1)
    globals.SET = False

def scale():
    if scale_button.text == '1':
        scale_button.text = str(0.1)
    else:
        scale_button.text = str(1)

def set_bypass_mode():
    globals.BYPASS_MODE = not globals.BYPASS_MODE

def set_stop_regulating():
    globals.STOP_REGULATING = not globals.STOP_REGULATING

def numpad(btn):
    match btn:
        case 1|2|3|4|5|6|7|8|9:
            selected_widget.append(btn)
        case '0':
            if selected_widget.value: #not empty
                selected_widget.append(btn)
        case '.':
            if '.' not in selected_widget.value:
                selected_widget.append(btn)
        case 'c':
            selected_widget.value = selected_widget.value[:-1]


def spawn_numpad(master,size):
    numpad_box = Box(master,layout='grid')
    for i in range(9):
        btn = PushButton(numpad_box, text=i+1, grid=[int(i%3),int(i/3)],command=numpad,args=[i+1],width=3)
        btn.text_color = text_color
        btn.text_size = size
    for i, x in enumerate(['.','0','c']):
        btn = PushButton(numpad_box, text=x, grid=[i,3],command=numpad,args=[x],width=3)
        btn.text_color = text_color
        btn.text_size = size

#These functions are used for periodic updates and checks on certain values
def update_time():
    clock.value = time.strftime("Clock: %H:%M:%S", time.localtime())
def update_temperature():
    temp.value = "{:4.1f}".format(globals.temperature_average)
def update_ready():
    if globals.READY:
        ready_text.text_color = 'green'
        ready_text.value = 'READY'
    else:
        ready_text.text_color = 'red'
        ready_text.value = 'NOT READY'

def check_bypass():
    #check if bypass mode is enabled
    #TODO: merge this function with the check_target_temperature below
    if globals.BYPASS_MODE:
        #left_box.disable()
        set_temp_button.disable()
    else:
        #left_box.enable()
        set_temp_button.enable()

def check_target_temperature():
    if globals.TARGET_TEMP_CHANGED.BY_MATLAB:
        settemp.value = globals.temperature_target
        globals.TARGET_TEMP_CHANGED.BY_MATLAB = False
    if globals.STOP_REGULATING:
        pause_output_button.bg = 'grey'
    else:
        pause_output_button.bg = background_color
    # if globals.BYPASS_MODE:
    #     bypass_check.bg = 'grey'
    # else:
    #     bypass_check.bg = background_color
    if globals.SET:
        set_temp_button.disable()
    else:
        set_temp_button.enable()


app = App()
app.visible = False

controller_window = Window(app,title='Rb-cell Temperature Controller',layout='grid',bg=background_color,height=480,width=800)
#row 0
Text(controller_window,text='Rubidium Cell Temperature Controller',align='left',color='white',grid=[0,0,3,1]) 
#brightness_slider = Slider(controller_window,start=0,end=100,grid=[4,0])

settings_button = PushButton(controller_window, text="Settings",align='right',grid=[4,0],command=swap_windows,pady=1)
settings_button.text_color = text_color
settings_button.text_size = 18
#row 1
#TODO: rename set_stop_regulating to match new name "pause output"
output_off_button = PushButton(controller_window,text="Output\nOff",grid=[0,1],height=1,width=4)
output_off_button.text_size = 20; output_off_button.text_color ='white'
pause_output_button = PushButton(controller_window,text="Pause\nOutput",grid=[1,1],command=set_stop_regulating,height=1,width=4)
pause_output_button.text_size = 20; pause_output_button.text_color ='white'
set_temp_button = PushButton(controller_window,text="Set\nTemp",grid=[2,1],command=set_temperature,height=1,width=4)
set_temp_button.text_size = 20;set_temp_button.text_color = 'white'

temp_box = Box(controller_window,grid=[3,0,1,2],align='right')
ready_text = Text(temp_box, text="NOT READY",color = "red")
ready_text.repeat(1000, update_ready)
temp_title = Text(temp_box, text="Actual Temperature",color= "white")
temp = Text(temp_box, text="0",color = "white")
temp.text_size = 28
temp.repeat(100, update_temperature)

time_scale_combo = Combo(controller_window,options=['last 10s',20,30,60,120,300,600],grid=[4,1],align='bottom',width=15)
time_scale_combo.text_size = 18
time_scale_combo.text_color = 'white'

#Row 2
spawn_numpad(Box(controller_window,grid=[0,2,2,9],align='left'),20)

#row 3 
plot_box = Box(controller_window,grid=[3,3,2,8],align='right',layout='grid',border=True)
f = plt.figure(figsize=(4,3.5))
axis = plt.axes(xlim =(0, 10), ylim =(0, 30))
line, = axis.plot([], [], linewidth = 2)
axis.set_xlabel('Time[s]')
axis.set_ylabel('Temperature[C]')

def init():
    line.set_data([], [])
    return line,

x,y = [],[]

def animate(i):
    x.append(len(y)+1)
    y.append(globals.temperature_average)
    line.set_data(x[-10:], y[-10:])
    axis.set_xlim(xmin=len(x[:-10]),xmax=len(x))
    canvas.draw()
    return line,

anim = animation.FuncAnimation(f, animate,
                    init_func = init,
                    frames = 500,
                    interval = 1000,
                    blit = True)

canvas = FigureCanvasTkAgg(f, plot_box.tk)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

#row 4
set_box = Box(controller_window,grid=[2,4,1,6])
Text(set_box, text="Set Temperature",color= "white")
settemp = Text(set_box, text='1')
settemp.text_size = 28; settemp.text_color = 'white'

#row 8
crement_box = Box(controller_window,grid=[2,10])
scale_button = PushButton(crement_box,text="1",command=scale,align='right',padx=12,pady=5,width=2,height=1)
scale_button.text_color = text_color
scale_button.text_size = 20
increasetemp_button = PushButton(crement_box,text="+",command=increment,args=[1],align='right',padx=12,pady=5,width=2,height=1)
increasetemp_button.text_color = text_color
increasetemp_button.text_size = 20
decreasetemp_button = PushButton(crement_box,text="-",command=increment,args=[-1],align='right',padx=12,pady=5,width=2,height=1)
decreasetemp_button.text_color = text_color
decreasetemp_button.text_size = 20

#invisible button for check loops
gui_loop = Text(app,visible=False)
gui_loop.repeat(1000,check_bypass)
gui_loop.repeat(1000,check_target_temperature)
gui_loop.repeat(1000,check_for_errors)

#Settings window
settings_window = Window(app,title='Settings',width=800,height=480,bg=background_color,visible=False,layout='grid')

#Title row 0
Text(settings_window,text='Rb-controller Settings',color=text_color,grid=[0,0],align='left')
use_power_supply_button = PushButton(settings_window,text='Use power supply',grid=[2,0,2,1]).text_color=text_color
controller_button = PushButton(settings_window, text="controller",align='right',command=swap_windows,grid=[4,0]).text_color = text_color

#Row 1 whitespaces
Text(settings_window,text='',color=text_color,grid=[0,1],align='left')
Text(settings_window,text='',color=text_color,grid=[3,1],width=13,align='left')

#PID row 2
Text(settings_window,text='Proportional:',grid=[1,2],color=text_color)
Text(settings_window,text='Intergral:',grid=[2,2],color=text_color)
Text(settings_window,text='Derivative:',grid=[3,2],color=text_color)
#PID textBoxes row 3
Text(settings_window,text='PID Gains:',grid=[0,3],color=text_color)
proportional_gain_textbox = TextBox(settings_window,text='2',grid=[1,3])
proportional_gain_textbox.text_color=text_color
integral_gain_textbox = TextBox(settings_window,grid=[2,3])
integral_gain_textbox.text_color=text_color
derivative_gain_textbox = TextBox(settings_window,grid=[3,3])
derivative_gain_textbox.text_color=text_color

#Temperature row 4
temperature_limit_title = Text(settings_window,text='Temperature Limit',grid=[1,4],color=text_color)
temperature_offset_title = Text(settings_window,text='Temperature Offset',grid=[2,4],color=text_color)

#Temperature textboxes row 5
Text(settings_window,text='Temperature:',grid=[0,5],color=text_color)
temperature_limit_textbox = TextBox(settings_window,grid=[1,5])
temperature_limit_textbox.text_color=text_color
temperature_offset_textbox = TextBox(settings_window,grid=[2,5])
temperature_offset_textbox.text_color=text_color

#row 6
Text(settings_window,text='\nSettling type:',grid=[0,6],color=text_color)

#row 7
Text(settings_window,text='Max Temperature \n Fluctuations[+/-]: ',grid=[1,7],color=text_color)
#row 8
contant_error_checkbox = CheckBox(settings_window,text='Constant Error',grid=[0,8])
contant_error_checkbox.text_color=text_color
settling_temperature_fluctuations_textbox = TextBox(settings_window,grid=[1,8])
settling_temperature_fluctuations_textbox.text_color=text_color

#row 9
Text(settings_window,text='Settle slope [C/s]:',grid=[1,9],color=text_color)
Text(settings_window,text='Slope length [s]:',grid=[2,9],color=text_color)
#row 10
slope_checkbox = CheckBox(settings_window,text='Slope',grid=[0,10]).text_color=text_color
settle_slope_textbox = TextBox(settings_window,grid=[1,10])
settle_slope_textbox.text_color=text_color
slope_length_textbox = TextBox(settings_window,grid=[2,10])
slope_length_textbox.text_color=text_color

#row 11
Text(settings_window,text='Settle wait time[s]:',grid=[1,11],color=text_color)
#row 12
slope_checkbox = CheckBox(settings_window,text='Timed',grid=[0,12]).text_color=text_color
wait_time_textbox = TextBox(settings_window,grid=[1,12])
wait_time_textbox.text_color=text_color

#numpad
spawn_numpad(Box(settings_window,grid=[4,2,1,12],border=True),size=24)

#events
def clicked(event_data):
    global selected_widget
    selected_widget = event_data.widget

proportional_gain_textbox.when_clicked = clicked
integral_gain_textbox.when_clicked = clicked
derivative_gain_textbox.when_clicked = clicked
temperature_limit_textbox.when_clicked = clicked
temperature_offset_textbox.when_clicked = clicked
settling_temperature_fluctuations_textbox.when_clicked = clicked
settle_slope_textbox.when_clicked = clicked
slope_length_textbox.when_clicked = clicked
wait_time_textbox.when_clicked = clicked  

#TODO: use the uncommented line when in lab
# main_loop_thread = loop.loop()
main_loop_thread = loop_simulator.loop()
main_loop_thread.start()

app.display()

main_loop_thread.join