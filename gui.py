from guizero import App, Text, Picture
import time
import threading 

# Action you would like to perform
def gui():

    image_path = "images\elvis\\frame_%02d_delay-0.06s.gif"

    def update_time():
        clock.value = time.strftime("Clock: %I:%M:%S %p", time.localtime())

    def update_amimation():
        if int(elvis.image[19:21]) == 14: 
            elvis.image = image_path % 0
        else:    
            elvis.image = image_path % (int(elvis.image[19:21]) + 1)


    app = App("Dream GUI")

    clock = Text(app, text="Clock: ")
    clock.repeat(1000, update_time)

    elvis = Picture(app,image= image_path % 0)
    elvis.repeat(100,update_amimation)

    app.display()

def main_loop():
    count = 0
    while True:
        print("Iterations: " + str(count))
        count = count + 1

        time.sleep(1)


gui_thread = threading.Thread(target=gui,)
main_loop_thread = threading.Thread(target=main_loop)


gui_thread.start()
main_loop_thread.start()