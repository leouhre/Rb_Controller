#python packages
import threading


#our scripts
import ui
import loop
import globals

globals.initialize_variables()

#create threads
ui_thread = ui.ui()
main_loop_thread = loop.loop()

#start threads
ui_thread.start()
main_loop_thread.start()

exit()

#make sure both threads are terminated before ending script
#ui_thread.join()
#main_loop_thread.join()