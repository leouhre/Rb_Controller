#python packages
import threading

#our scripts
import ui
#import loop

temperature_target = 0
temperature_average = 0
BYPASS_MODE = False
STOP_REGULATING = False

#create threads
ui_thread = ui.ui()
#main_loop_thread = loop.loop()

#start threads
ui_thread.start()
#main_loop_thread.start()

#make sure both threads are terminated before ending script
#ui_thread.join()
#main_loop_thread.join()

#loop.psu.output_off()
#loop.tcp_socket.close()
#loop.rt8.close()