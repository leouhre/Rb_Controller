from pathlib import Path
import shelve

class PID():
    P = Path('C:\\','Users','leouh', 'Documents', 'Rb_Controller')
    def __init__(self):
        with shelve.open('config') as config:
            self.cfg = dict(config)
        self.Ts = 1/self.cfg['freq']
        if self.cfg['ki']:
            self.taui = self.cfg['kp']/self.cfg['ki']
        self.taud = self.cfg['kd']/self.cfg['kp']
        
    integral_error = 0
    integral_error2 = 0
    prev_t = 0
    prev_t2 = 0

    upper_lim = 28
    lower_lim = 0

    settlecount = 0
    active_controller = 1

    def settle_update(self, t, t_target,error,slope):
        within_error = error and self.cfg['max_fluctuations'] > abs(t_target - t)
        within_slope = slope and self.cfg['settle_slope'] >= abs(t - self.prev_t) / self.Ts

        if within_error or within_slope:
            self.settlecount += 1
        else:
            self.settlecount = 0

    def settle_check(self,slope,timed):
        if slope and timed:
            res = self.settlecount > self.cfg['settle_wait_time']*self.cfg['freq'] or \
                self.settlecount > self.cfg['slope_length']*self.cfg['freq']
        elif slope:
            res = self.settlecount > self.cfg['slope_length']*self.cfg['freq']
        elif timed:
            res = self.settlecount > self.cfg['settle_wait_time']*self.cfg['freq']
        else:
            res = False
        return res 

    def swap_controller(self,to):
        if to == self.active_controller:
            return
        if to == 1:
            self.integral_error = self.integral_error2*self.cfg['ki2']/self.cfg['ki']
        if to == 2:
            self.integral_error2 = self.integral_error*self.cfg['ki']/self.cfg['ki2']
        self.active_controller = to


    # Simple PID controller. Explicitly dealing with wind-up
    def update(self, t, t_target):
        error = t_target - t
        p = self.cfg['kp'] * error
        i = self.cfg['ki'] * self.integral_error * self.Ts
        derivative = t - self.prev_t
        d = self.cfg['kd'] * derivative / self.Ts
        self.prev_t = t
        pidout = p + i + d
        if self.lower_lim < pidout < self.upper_lim:
            self.integral_error += error
        else:
            self.integral_error = 0
        return max(min(pidout,self.upper_lim),self.lower_lim)

    def update2(self, t, t_target):
        error = t_target - t
        p = self.cfg['kp2'] * error
        i = self.cfg['ki2'] * self.integral_error2 * self.Ts
        derivative = t - self.prev_t2
        d = self.cfg['kd2'] * derivative / self.Ts
        self.prev_t2 = t
        pidout = p + i + d
        if self.lower_lim < pidout < self.upper_lim:
            self.integral_error2 += error
        else:
            self.integral_error2 = 0
        return max(min(pidout,self.upper_lim),self.lower_lim)