
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
    global MAX_TEMP_REACHED
    global MAX_TEMP_FLUCTUATION
    global SETTLE_WAIT_TIME
    global ATTEMPT_TO_CONNECT
    global CONSTANT_ERROR
    global SLOPE
    global TIMED
    global MAX_OP
    global SENSORS_ON_GLASS
    global sensors_val
    

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
    MAX_TEMP_REACHED = False
    MAX_TEMP_FLUCTUATION = 1
    SETTLE_WAIT_TIME = 10
    CONNECTED_TO_MATLAB = False
    ATTEMPT_TO_CONNECT= False
    CONSTANT_ERROR = True
    SLOPE = False
    TIMED = True

    NUMBER_OF_SENSORS = 4
    SENSORS_ON_GLASS = 2

    sensors_val = [0]*NUMBER_OF_SENSORS

    MAX_OP = 232
