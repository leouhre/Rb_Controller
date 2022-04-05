from collections import deque
import time, sys
from classes.pid import PID
import classes.myfile_test as m

a = deque()
a.append(1)
a.append(1)
a.append(1)

b = deque()
b.append(2)
b.append(2)
b.append(2)

data = []
for x in range(8):
	data.append(deque())
	data[x].append(x)

m.deques_to_txtfile(time=a,voltage=b)
m.sensors_to_txtfile(data)

timerA = time.time()
t_target = float(sys.argv[1])
t = 0

PI = PID()
    

while True:
    if (time.time() - timerA) > 2:
        timerA = time.time()

        PI.update_error(t,t_target)
        t = t + max(min(PI.proportional() + PI.integral(),28),0) #saturation at 28V and o lower than 0V

        print("tempearture " + str(t))

        t = t - 2
        if abs(t_target - t) < 10:
            break

