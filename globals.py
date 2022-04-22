def initialize_variables():
    global temperature_target
    global temperature_average
    global BYPASS_MODE
    global STOP_REGULATING

    temperature_target = 0
    temperature_average = 0
    BYPASS_MODE = False
    STOP_REGULATING = False