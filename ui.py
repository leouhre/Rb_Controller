import threading, time
from guizero import App, Text, Box, PushButton, Slider, Picture, Window, TextBox, CheckBox
import globals

class ui(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.MAX_TEMP = 200
        self.MIN_TEMP = 0
        self.show_outline = False
        self.background_color = "#5B5A51"
        self.text_color = 'white'

    def clamp(self,val,min_val,max_val):
        return max(min(val,max_val),min_val)

    def set_target_temperature(self,x):
        globals.temperature_target = self.clamp(x,0,200) #set bounds for temperature
        globals.TARGET_TEMP_CHANGED.BY_UI = True #will be set false by loop.py when it has reacted

    def run(self):
        #functions for Main GUI
        def swap_windows():
            settings_window.visible = not settings_window.visible
            settings_window.full_screen = not settings_window.full_screen


        def check_for_errors():
            if globals.STOP_RUNNING:
                app.destroy()

        def set_temperature():
            self.set_target_temperature(float(settemp.value))
            settemp.value = "{:3.2f}".format(float(settemp.value))

        def increment(n): 
            if not settemp.value:
                settemp.value = round(n*float(scale_button.text),1)
            elif not (float(settemp.value) + n*float(scale_button.text) > self.MAX_TEMP or float(settemp.value) + n*float(scale_button.text) < self.MIN_TEMP):
                settemp.value = round(float(settemp.value) + n*float(scale_button.text),1)

        def scale():
            if scale_button.text == '1':
                scale_button.text = str(0.1)
            else:
                scale_button.text = str(1)

        def update_time():
            clock.value = time.strftime("Clock: %H:%M:%S", time.localtime())

        def update_ready():
            if globals.READY:
                ready_text.text_color = 'green'
                ready_text.value = 'READY'
            else:
                ready_text.text_color = 'red'
                ready_text.value = 'NOT READY'

        def update_temperature():
            temp.value = "{:4.1f}".format(globals.temperature_average)
            if settemp.value and globals.temperature_target == float(settemp.value):
                apply_button.disable()
            else:
                apply_button.enable()

        def set_bypass_mode():
            globals.BYPASS_MODE = not globals.BYPASS_MODE
            if globals.BYPASS_MODE:
                bypass_check.bg = 'grey'
            else:
                bypass_check.bg = self.background_color

        def set_stop_regulating():
            globals.STOP_REGULATING = not globals.STOP_REGULATING
            if globals.STOP_REGULATING:
                stop_regulating.bg = 'grey'
            else:
                stop_regulating.bg = self.background_color

        def numpad(n):
            if settemp.value: #string not empty
                if n == 'c':
                    settemp.value = settemp.value[:-1]
                else:
                    match '.' in settemp.value:
                        case True: #decimal
                            if settemp.value[::-1].find('.') < 2 and n != '.':
                                settemp.value += n
                        case False: #no decimal
                            if len(settemp.value) < 3 and int(settemp.value) <= 20 or n == '.':
                                settemp.value += n
            elif n != '.' and n != '0':
                settemp.value += n

        #TODO: Make a numpad function that targets current textbox, or settemp if in controller window


        def spawn_numpad(master,size):
            numpad_box = Box(master,layout='grid',border=self.show_outline)
            for i in range(9):
                btn = PushButton(numpad_box, text=i+1, grid=[int(i%3),int(i/3)],command=numpad,args=[i+1],width=3)
                btn.text_color = self.text_color
                btn.text_size = size
            for i, x in enumerate(['.','0','c']):
                btn = PushButton(numpad_box, text=x, grid=[i,3],command=numpad,args=[x],width=3)
                btn.text_color = self.text_color
                btn.text_size = size


        def check_bypass():
            #check if bypass mode is enabled
            if globals.BYPASS_MODE:
                left_box.disable()
                apply_button.disable()
            else:
                left_box.enable()
                apply_button.enable()

        def check_target_temperature():
            if globals.TARGET_TEMP_CHANGED.BY_MATLAB:
                settemp.value = globals.temperature_target
                globals.TARGET_TEMP_CHANGED.BY_MATLAB = False


        # Wait with opening the GUI window until MATLAB creates the server to avoid issue with fullscreen
        # while globals.CONNECTED:
        #     pass
        
        app = App("Best GUI ever omg omg",bg=self.background_color,width=800,height=480)
        app.full_screen = True

        title_box = Box(app, width='fill',align='top',border=self.show_outline)
        bottom_box2 = Box(app, width='fill',align='bottom',border=self.show_outline)
        left_box_whitespace_l = Text(app,text='',width=3,align='left') 
        left_box = Box(app, width='fill',align='left',border=self.show_outline)
        left_box_whitespace_r = Text(app,text='',width=3,align='left') 
        right_box_whitespace_r = Text(app,text='',width=3,align='right') 
        right_box = Box(app, width='fill',align='right',border=self.show_outline)
        right_box_whitespace_l = Text(app,text='',width=3,align='right')
        bottom_box = Box(app, width='fill',align='bottom',border=self.show_outline)
        middle_box1 = Box(app, width='fill',height='fill',border=self.show_outline)
        middle_box2 = Box(app, width='fill',height='fill',border=self.show_outline)
        middle_box3 = Box(app, width='fill',height='fill',border=self.show_outline)
        middle_box4 = Box(app, width='fill',height='fill',border=self.show_outline)

        #in title box
        settings_button = PushButton(title_box, text="Settings",align='right',command=swap_windows);settings_button.text_color = self.text_color
        #settings_picture = Picture(title_box,image='pictures\settings_icon.jpg')
        clock = Text(title_box, text="Clock: ",color="white",align='right')
        clock.repeat(1000, update_time)
        title = Text(title_box, text="Rubidum Cell Temperature Controller",color="white",align="left")

        #in middle box
        apply_button = PushButton(middle_box2,text="Set",align='bottom',command=set_temperature)
        apply_button.text_size = 20;apply_button.text_color = 'white'

        #in right box
        right_box1 = Box(right_box,width='fill',height='fill',border=self.show_outline)
        right_box2 = Box(right_box,width='fill',height='fill',border=self.show_outline)
        right_box3 = Box(right_box,width='fill',height='fill',border=self.show_outline)
        temp_title = Text(right_box2, text="Actual Temperature",color= "white")
        ready_text = Text(right_box1, text="NOT READY",color = "red")
        ready_text.repeat(1000, update_ready)
        temp = Text(right_box2, text="",color = "white")
        temp.text_size = 28
        temp.repeat(100, update_temperature)
        right_box3_whitespace = Text(right_box3, text="",color = self.background_color)

        #in left box
        crement_box = Box(left_box,align='right',border=self.show_outline)
        scale_button = PushButton(crement_box,text="1",command=scale,align='top',padx=5,pady=5,width=2,height=1);scale_button.text_color = self.text_color
        increasetemp_button = PushButton(crement_box,text="+",command=increment,args=[1],align='top',padx=5,pady=5,width=2,height=1);increasetemp_button.text_color = self.text_color
        decreasetemp_button = PushButton(crement_box,text="-",command=increment,args=[-1],align='bottom',padx=5,pady=5,width=2,height=1);decreasetemp_button.text_color = self.text_color

        set_box = Box(left_box,width='fill',align='right',border=self.show_outline)
        settemp_title = Text(set_box, text="Set Temperature",color= "white", width=13, height=1)
        settemp = Text(set_box, text='1')
        settemp.text_size = 28; settemp.text_color = 'white'

        

        spawn_numpad(left_box,12)

        #in bottom box
        bypass_check = PushButton(bottom_box2,text="Enter Bypass",command=set_bypass_mode,align='right',width='fill')
        bypass_check.text_size = 24; bypass_check.text_color = 'white'
        stop_regulating = PushButton(bottom_box2,text="Stop Regulating",command=set_stop_regulating,align='left',width='fill')
        stop_regulating.text_size = 24; stop_regulating.text_color ='white'

        #invisible button for check loops
        gui_loop = Text(app,visible=False)
        gui_loop.repeat(1000,check_bypass)
        gui_loop.repeat(1000,check_target_temperature)
        gui_loop.repeat(1000,check_for_errors)




        #Settings window
        settings_window = Window(app,title='Settings',width=800,height=480,bg=self.background_color,visible=False,layout='grid')

        #Title row 0
        Text(settings_window,text='Rb-controller Settings',color=self.text_color,grid=[0,0],align='left')
        use_power_supply_button = PushButton(settings_window,text='Use power supply',grid=[2,0,2,1]).text_color=self.text_color
        controller_button = PushButton(settings_window, text="controller",align='right',command=swap_windows,grid=[4,0]).text_color = self.text_color

        #Row 1 whitespaces
        Text(settings_window,text='',color=self.text_color,grid=[0,1],align='left')
        Text(settings_window,text='',color=self.text_color,grid=[3,1],width=13,align='left')

        #PID row 2
        Text(settings_window,text='Proportional:',grid=[1,2],color=self.text_color)
        Text(settings_window,text='Intergral:',grid=[2,2],color=self.text_color)
        Text(settings_window,text='Derivative:',grid=[3,2],color=self.text_color)
        #PID textBoxes row 3
        Text(settings_window,text='PID Gains:',grid=[0,3],color=self.text_color)
        proportinal_gain_textbox = TextBox(settings_window,grid=[1,3]).text_color=self.text_color
        integral_gain_textbox = TextBox(settings_window,grid=[2,3]).text_color=self.text_color
        derivative_gain_textbox = TextBox(settings_window,grid=[3,3]).text_color=self.text_color

        #Temperature row 4
        temperature_limit_title = Text(settings_window,text='Temperature Limit',grid=[1,4],color=self.text_color)
        temperature_offset_title = Text(settings_window,text='Temperature Offset',grid=[2,4],color=self.text_color)
    
        #Temperature textboxes row 5
        Text(settings_window,text='Temperature:',grid=[0,5],color=self.text_color)
        temperature_limit_textbox = TextBox(settings_window,grid=[1,5]).text_color=self.text_color
        temperature_offset_textbox = TextBox(settings_window,grid=[2,5]).text_color=self.text_color

        #row 6
        Text(settings_window,text='\nSettling type:',grid=[0,6],color=self.text_color)

        #row 7
        Text(settings_window,text='Max Temperature \n Fluctuations[+/-]: ',grid=[1,7],color=self.text_color)
        #row 8
        contant_error_checkbox = CheckBox(settings_window,text='Constant Error',grid=[0,8]).text_color=self.text_color
        settling_temperature_fluctuations_textbox = TextBox(settings_window,grid=[1,8]).text_color=self.text_color

        #row 9
        Text(settings_window,text='Settle slope [C/s]:',grid=[1,9],color=self.text_color)
        Text(settings_window,text='Slope length [s]:',grid=[2,9],color=self.text_color)
        #row 10
        slope_checkbox = CheckBox(settings_window,text='Slope',grid=[0,10]).text_color=self.text_color
        settle_slope_textbox = TextBox(settings_window,grid=[1,10]).text_color=self.text_color
        slope_length_textbox = TextBox(settings_window,grid=[2,10]).text_color=self.text_color

        #row 11
        Text(settings_window,text='Settle wait time[s]:',grid=[1,11],color=self.text_color)
        #row 12
        slope_checkbox = CheckBox(settings_window,text='Timed',grid=[0,12]).text_color=self.text_color
        settle_slope_textbox = TextBox(settings_window,grid=[1,12]).text_color=self.text_color

        #numpad
        spawn_numpad(Box(settings_window,grid=[4,2,1,12],border=True),size=24)



        # TODO: Delete these test lines
        settings_window.visible = True
        app.full_screen = False
        


        app.display()

        #also stop loop when ui terminates
        globals.STOP_RUNNING = True

