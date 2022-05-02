import threading, time
from guizero import App, Text, Box, PushButton, Slider
import globals

class ui(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.MAX_TEMP = 200
        self.MIN_TEMP = 0
        self.show_outline = False
        self.background_color = "#5B5A51"

    def clamp(self,val,min_val,max_val):
        return max(min(val,max_val),min_val)

    def set_target_temperature(self,x):
        globals.temperature_target = self.clamp(x,0,200) #set bounds for temperature

    def run(self):

        #functions for GUI
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
                match '.' in settemp.value:
                    case True: #decimal
                        if settemp.value[::-1].find('.') < 2 and n != '.':
                            settemp.value += n
                    case False: #no decimal
                        if len(settemp.value) < 3 and int(settemp.value) <= 20 or n == '.':
                            settemp.value += n
            elif n != '.' and n != '0':
                settemp.value += n

        def numpad_del():
            settemp.value = settemp.value[:-1]

        def update():
            #check if bypass mode is enabled
            if globals.BYPASS_MODE:
                left_box.disable()
                apply_button.disable()
            else:
                left_box.enable()
                apply_button.enable()

            
        app = App("Best GUI ever omg omg",bg=self.background_color,width=800,height=480)
        app.full_screen = False


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
        clock = Text(title_box, text="Clock: ",color="white",align='right')
        clock.repeat(1000, update_time)
        title = Text(title_box, text="Rubidum Cell Temperature Controller",color="white",align="left")


        #in middle box
        apply_button = PushButton(middle_box2,text="Apply",align='bottom',command=set_temperature)
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
        scale_button = PushButton(crement_box,text="1",command=scale,align='top',padx=5,pady=5,width=2,height=1)
        increasetemp_button = PushButton(crement_box,text="+",command=increment,args=[1],align='top',padx=5,pady=5,width=2,height=1)
        decreasetemp_button = PushButton(crement_box,text="-",command=increment,args=[-1],align='bottom',padx=5,pady=5,width=2,height=1)

        set_box = Box(left_box,width='fill',align='right',border=self.show_outline)
        settemp_title = Text(set_box, text="Set Temperature",color= "white", width=13, height=1)
        settemp = Text(set_box, text='1')
        settemp.text_size = 28; settemp.text_color = 'white'

        
        numpad_box = Box(left_box,layout='grid',align='right',border=self.show_outline)
        button1 = PushButton(numpad_box, text="1", grid=[1,0],command=numpad,args=['1'])
        button2 = PushButton(numpad_box, text="2", grid=[2,0],command=numpad,args=['2'])
        button3  = PushButton(numpad_box, text="3", grid=[3,0],command=numpad,args=['3'])
        button4  = PushButton(numpad_box, text="4", grid=[1,1],command=numpad,args=['4'])
        button5  = PushButton(numpad_box, text="5", grid=[2,1],command=numpad,args=['5'])
        button6  = PushButton(numpad_box, text="6", grid=[3,1],command=numpad,args=['6'])
        button7  = PushButton(numpad_box, text="7", grid=[1,2],command=numpad,args=['7'])
        button8  = PushButton(numpad_box, text="8", grid=[2,2],command=numpad,args=['8'])
        button9  = PushButton(numpad_box, text="9", grid=[3,2],command=numpad,args=['9'])
        button0  = PushButton(numpad_box, text="0", grid=[2,3],command=numpad,args=['0'])
        buttondot  = PushButton(numpad_box, text=".", grid=[1,3],padx=12,command=numpad,args=['.'])
        buttondel  = PushButton(numpad_box, text="c", grid=[3,3],command=numpad_del)

        #in bottom box
        bypass_check = PushButton(bottom_box2,text="Enter Bypass",command=set_bypass_mode,align='right',width='fill')
        bypass_check.text_size = 24; bypass_check.text_color = 'white'
        stop_regulating = PushButton(bottom_box2,text="Stop Regulating",command=set_stop_regulating,align='left',width='fill')
        stop_regulating.text_size = 24; stop_regulating.text_color ='white'

        #invisible button for check loops
        gui_loop = Text(app,visible=False)
        gui_loop.repeat(1000,update)

        app.display()

        #also stop loop when ui terminates
        globals.STOP_RUNNING = True

