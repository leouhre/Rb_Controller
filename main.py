#our scripts
import ui
# import loop
import loop_simulator
import globals


globals.initialize_variables()

#create and start threads 
ui_thread = ui.ui()
ui_thread.start()

main_loop_thread = loop_simulator.loop()
main_loop_thread.start()

# main_loop_thread = loop.loop()
# main_loop_thread.start()