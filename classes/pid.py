from pathlib import Path

class PID():
    def __init__(self):
        P = Path('~/','Rb_Controller')
        with open(P / 'config.txt', 'r') as config:
            self.kp = float(config.readline())
            self.taui = float(config.readline())
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
    
    def regulate_output(self):
        return max(min(self.proportional() + self.integral(),28),0)
