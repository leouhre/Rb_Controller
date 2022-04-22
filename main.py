#python packages
import threading

#our scripts
import ui
#import loop

target_temperature = 0
temperature = 0
BYPASS_MODE = False
STOP_REGULATING = False



ui_thread = ui.ui()
main_loop_thread = loop.loop()


ui_thread.start()
#main_loop_thread.start()

ui_thread.join()
#main_loop_thread.join()

loop.psu.output_off()
loop.tcp_socket.close()
loop.rt8.close()