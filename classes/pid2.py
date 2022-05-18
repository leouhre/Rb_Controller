from pathlib import Path

class PID2():
    def __init__(self):
        P = Path('C:\\','Users','leouh', 'Documents', 'Rb_Controller')
        with open(P / 'config.txt', 'r') as config:
            self.kp = float(config.readline())
            self.ki = float(config.readline())
            self.kd = float(config.readline())
            self.alpha = float(config.readline())
            self.freq = float(config.readline())
        self.Ts = 1/self.freq
        # Avoid division with zero if integral gain is 0 (disabled)
        if self.ki:
            self.taui = self.kp/self.ki
        if self.kd:
            self.taud = self.kd/self.kp
    
    integral_error = 0
    prev_t = 0

    upper_lim = 28
    lower_lim = -4
    
    u_past = 0
    y_past = 0
    uD_past = 0

    # Simple PID controller. Explicitly dealing with wind-up
    def update(self, t, t_target):
        error = t_target - t
        pidout = self.kp * error
        pidout += self.ki * self.integral_error * self.Ts
        derivative = t - self.prev_t
        pidout += self.kd * derivative / self.Ts
        self.prev_t = t
        #pidout *= self.kp
        if self.lower_lim < pidout < self.upper_lim:
            self.integral_error += error
        return max(min(pidout,self.upper_lim),self.lower_lim)

    # PI-Lead controller implemented using [Wang 4.4.2]. Implicitly dealing with wind-up
    def update3(self, y_current, r_current):
        if not self.ki:
            print("update3() requires an PI or PI-Lead controller")
            return 0
        uD_current = ((self.alpha*self.taud) / (self.alpha*self.taud + self.Ts)) * self.uD_past  + \
            ((self.kp*self.taud) / (self.alpha*self.taud + self.Ts)) * (y_current - self.y_past)
        u_current = self.u_past + self.kp*(self.y_past - y_current) + ((self.kp*self.Ts) / self.taui) * \
            (r_current - y_current) - uD_current + self.uD_past
        u_current = max(min(u_current,self.upper_lim),self.lower_lim)
        self.uD_past = uD_current
        self.u_past = u_current
        self.y_past = y_current
        return u_current