def initialize_variables():
    global temperature_target
    global temperature_average
    global BYPASS_MODE
    global STOP_REGULATING
    global STOP_RUNNING
    global READY
    global CONNECTED_TO_INSTRUMENTS
    global SET
    global TARGET_TEMP_CHANGED
    global CONNECTED_TO_MATLAB
    global NUMBER_OF_SENSORS

    temperature_target = 0
    temperature_average = 0
    BYPASS_MODE = False
    STOP_REGULATING = False
    STOP_RUNNING = False
    READY = False
    CONNECTED_TO_INSTRUMENTS = False
    SET = False
    class TARGET_TEMP_CHANGED():
        BY_UI = False
        BY_MATLAB = False
    CONNECTED_TO_MATLAB = False
    NUMBER_OF_SENSORS = 8
