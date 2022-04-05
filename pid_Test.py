import time, sys
from classes.pid import PID
import classes.myfile_test



timerA = time.time()
t_target = float(sys.argv[1])
t = 0

PI = PID()
#print(globals())


classes.myfile_test.declare()
    

while True:
    if (time.time() - timerA) > 2:
        timerA = time.time()

        PI.update_error(t,t_target)
        t = t + max(min(PI.proportional() + PI.integral(),28),0) #saturation at 28V and o lower than 0V

        print("tempearture " + str(t))

        t = t - 2
        if abs(t_target - t) < 10:
            break

