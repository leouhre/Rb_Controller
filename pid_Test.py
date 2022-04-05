import time, sys

class PID():
    def __init__(self):
        config = open('config.txt', 'r')
        self.kp = float(config.readline())
        self.taui = float(config.readline())
        #self.kp = kp
        #self.taui = taui
        self.ki = self.kp/self.taui

    integral_error = 0
    error = 0
    
    def update_error(self,t,t_target):
        self.error = t_target - t
        if abs(self.error) < 10: # only activate integrator if error is less than 5 C
            self.integral_error = self.integral_error + self.error
        else:
            self.integral_error = 0 # reset      #TODO check if this causes errors later?
    
    def integral(self):
        return self.ki*self.integral_error


    def proportional(self):
        return self.kp*self.error


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

