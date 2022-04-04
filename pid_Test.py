

import time


class PID():
    def __init__(self, kp, taui):
        self.kp = kp
        self.taui = taui
        self.ki = kp/taui

    integral_error = 0
    error = 0
    
    def update_error(self,t,t_target):
        self.error = t_target - t
        if abs(self.error) < 5: # only activate integrator if error is less than 5 C
            self.integral_error = self.integral_error + self.error
        else:
            self.integral_error = 0 # reset      #TODO check if this causes errors later?



def integral(PI:PID):
    return PI.ki*PI.integral_error


def proportional(PI:PID):
    return PI.kp*PI.error


timerA = time.time()
t_target = 90
t = 0
PI = PID(0.2,2)


def get_pid_parameters():
    config = open('config.txt', 'r')
    kp = config.readline()
    taui = config.readline()

    print(str(kp))
    print(str(taui))
    print(str(kp+taui))


get_pid_parameters()
    

while True:
    if (time.time() - timerA) > 2:
        timerA = time.time()
        # TODO PID
        PI.update_error(t,t_target)
        if (abs(t_target - t) < 1):
            break
        t = t + max(min(proportional(PI) + integral(PI),28),0) #saturation at 28V and o lower than 0V

        print("target " + str(t_target))
        print("actual " + str(t))

        t = t - 2


print("target " + str(t_target))
print("actual " + str(t))
    
  

