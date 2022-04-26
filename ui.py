import threading, time
from guizero import App, Text, Box,TextBox, PushButton, CheckBox, Slider
import globals

class ui(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def clamp(self,val,min_val,max_val):
        return max(min(val,max_val),min_val)

    def set_target_temperature(self,x):
        globals.temperature_target = self.clamp(x,30,200) #set bounds for temperature

    def run(self):

        #functions for GUI

        def set_temperature():
            try:
                self.set_target_temperature(float(settemp.value))
            except ValueError:
                pass

        def slider_set_temperature():
            settemp.value = settemp_slider.value

        def increase_temperature():
            self.set_target_temperature(globals.temperature_target + 1)
            settemp.value = globals.temperature_target
        
        def decrease_temperature():
            self.set_target_temperature(globals.temperature_target - 1)
            settemp.value = globals.temperature_target

        def update_time():
            clock.value = time.strftime("Clock: %I:%M:%S %p", time.localtime())

        def update_temperature():
            temp.value = "{:4.1f}".format(globals.temperature_average)
        
        def set_bypass_mode():
            globals.BYPASS_MODE = bypass_check.value

        def set_stop_regulating():
            globals.STOP_REGULATING = stop_regulating.value

        def numpad(n):
            settemp.value += n
        
        def numpad_del():
            settemp.value = settemp.value[:-1]

        def apply():
            try:
                self.set_target_temperature(float(settemp.value))
            except ValueError:
                pass


            
        def update():
            #check if bypass mode is enabled
            if globals.BYPASS_MODE:
                settemp.disable()
                increasetemp_button.disable()
                decreasetemp_button.disable()
            else:
                settemp.enable()
                increasetemp_button.enable()
                decreasetemp_button.enable()
            
            #check if Targettemperature is within bounds 

            



        app = App("Dream GUI",bg="#5B5A51",width=800,height=480)
        app.full_screen = False


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
        temp.repeat(100, update_temperature)

        #in left box
        crement_box = Box(left_box,align='right',border=True)
        increasetemp_button = PushButton(crement_box,text="+",command=increase_temperature,align='top',padx=5,pady=5,width=2,height=1)
        decreasetemp_button = PushButton(crement_box,text="-",command=decrease_temperature,align='bottom',padx=5,pady=5,width=2,height=1)
        apply_button = PushButton(app,text="apply",command=apply)

        set_box = Box(left_box,align='right',border=True)
        settemp_title = Text(set_box, text="Set Temperature",color= "white", width=13, height=1)
        settemp = TextBox(set_box, text="Set Temperature", command=set_temperature, width=13)
        settemp.text_color = "white"; settemp.text_size = 12; settemp.bg ="#7e7e7e"

        numpad_box = Box(left_box,layout='grid',align='right',border=True)
        button1 = PushButton(numpad_box, text="1", grid=[0,0],command=numpad,args=['1'])
        button2 = PushButton(numpad_box, text="2", grid=[1,0],command=numpad,args=['2'])
        button3  = PushButton(numpad_box, text="3", grid=[2,0],command=numpad,args=['3'])
        button4  = PushButton(numpad_box, text="4", grid=[0,1],command=numpad,args=['4'])
        button5  = PushButton(numpad_box, text="5", grid=[1,1],command=numpad,args=['5'])
        button6  = PushButton(numpad_box, text="6", grid=[2,1],command=numpad,args=['6'])
        button7  = PushButton(numpad_box, text="7", grid=[0,2],command=numpad,args=['7'])
        button8  = PushButton(numpad_box, text="8", grid=[1,2],command=numpad,args=['8'])
        button9  = PushButton(numpad_box, text="9", grid=[2,2],command=numpad,args=['9'])
        button0  = PushButton(numpad_box, text="0", grid=[1,3],command=numpad,args=['0'])
        buttondot  = PushButton(numpad_box, text=",", grid=[0,3],command=numpad,args=['.'])
        buttondel  = PushButton(numpad_box, text="c", grid=[2,3],command=numpad_del)

        settemp_slider = Slider(set_box,command=slider_set_temperature,start=30,end=200,align='bottom')

        #in bottom box
        bypass_check = CheckBox(bottom_box,text="Enter Bypass",command=set_bypass_mode);bypass_check.text_size = 24
        stop_regulating = CheckBox(bottom_box,text="Stop Regulating",command=set_stop_regulating);stop_regulating.text_size = 24

        #invisible button for check loops
        gui_loop = Text(app,visible=False)
        gui_loop.repeat(1000,update)


        app.display()

        globals.STOP_RUNNING = True

