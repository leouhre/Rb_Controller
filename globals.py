def initialize_variables():
    global temperature_target
    global temperature_average
    global BYPASS_MODE
    global OUTPUT_OFF
    global OUTPUT_PAUSE
    global STOP_RUNNING
    global READY
    global CONNECTED_TO_INSTRUMENTS
    global SET
    global TARGET_TEMP_CHANGED
    global CONNECTED_TO_MATLAB
    global ATTEMPT_TO_CONNECT
    global NUMBER_OF_SENSORS
    global SETTINGS_CHANGED
    global error_msg
    global MAX_TEMP
    global MAX_TEMP_FLUCTUATION
    global SETTLE_WAIT_TIME


    temperature_target = 0
    temperature_average = 0
    BYPASS_MODE = False
    STOP_RUNNING = False
    OUTPUT_OFF = False
    OUTPUT_PAUSE = False
    READY = False
    CONNECTED_TO_INSTRUMENTS = False
    SET = False
    SETTINGS_CHANGED = False
    class TARGET_TEMP_CHANGED():
        BY_UI = False
        BY_MATLAB = False
    error_msg = ""
    MAX_TEMP = 209
    MAX_TEMP_FLUCTUATION = 1
    SETTLE_WAIT_TIME = 10
    CONNECTED_TO_MATLAB = False
    ATTEMPT_TO_CONNECT= False
    NUMBER_OF_SENSORS = 4
