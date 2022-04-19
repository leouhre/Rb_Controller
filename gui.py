from turtle import right
from guizero import App, Text, Picture, Box,TextBox, PushButton
import time
import threading
import numpy as np

target_temperature = 0
temperature = 0

# Action you would like to perform
def gui():

    image_path = "images\elvis\\frame_%02d_delay-0.06s.gif"

    def set_temperature():
        global target_temperature
        try:
            target_temperature = float(settemp.value) 
        except ValueError:
            pass
    
    def increase_temperature():
        global target_temperature
        target_temperature = target_temperature + 1
    
    def decrease_temperature():
        global target_temperature
        target_temperature = target_temperature - 1

    def update_time():
        clock.value = time.strftime("Clock: %I:%M:%S %p", time.localtime())

    def update_temperature():
        global temperature
        temp.value = "{:4.1f}".format(temperature)

    def update_amimation():
        if int(elvis.image[19:21]) == 14: 
            elvis.image = image_path % 0
        else:    
            elvis.image = image_path % (int(elvis.image[19:21]) + 1)


    app = App("Dream GUI",bg="#5B5A51",width=800,height=480)
    app.full_screen = True


    title_box = Box(app, width='fill',align='top',border=True)
    clock = Text(title_box, text="Clock: ",color="white",align='right')
    clock.repeat(1000, update_time)
    title = Text(title_box, text="Rubidum Cell Temperature Controller",color="white",align="left")


    temp_box = Box(app, width='fill',align='right',border=True)
    temp_title = Text(temp_box, text="Actual Temperature",color= "white")
    temp = Text(temp_box, text="",color = "white")
    temp.repeat(1000, update_temperature)


    settemp_box = Box(app, width='fill',align='left',border=True)

    crement_box = Box(settemp_box,align='right',border=True)
    increasetemp_button = PushButton(crement_box,text="+",command=increase_temperature,align='top',padx=5,pady=5,width=2,height=1)
    decreasetemp_button = PushButton(crement_box,text="-",command=decrease_temperature,align='bottom',padx=5,pady=5,width=2,height=1)

    set_box = Box(settemp_box,align='right',border=True)
    settemp_title = Text(set_box, text="Set Temperature",color= "white", width=13, height=1)
    settemp = TextBox(set_box, text="Set Temperature", command=set_temperature, width=13, height=3); settemp.text_color = "white";settemp.text_size = 12;settemp.bg ="#7e7e7e"
    


    """
    elvis = Picture(app,image= image_path % 0)
    elvis.repeat(100,update_amimation)
    """

  

    app.display()

def main_loop():
    global temperature
    global target_temperature
    count = 0
    while True:
        print("Iterations: " + str(count))
        print(f"Target temperature: {target_temperature:.1f}")
        count = count + 1
        temperature = temperature + np.random.random()

        time.sleep(1)


gui_thread = threading.Thread(target=gui,)
main_loop_thread = threading.Thread(target=main_loop)


gui_thread.start()
main_loop_thread.start()