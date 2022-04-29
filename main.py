#our scripts
import ui
import loop
import globals


globals.initialize_variables()

#create and start threads 
ui_thread = ui.ui()
ui_thread.start()

main_loop_thread = loop.loop()
main_loop_thread.start()