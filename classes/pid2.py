from pathlib import Path
#import scipy.signal as sig
#import numpy as np

class PID2():
    def __init__(self):
        P = Path('C:\\','Users','leouh', 'Documents', 'Rb_Controller')
        with open(P / 'config.txt', 'r') as config:
            self.kp = float(config.readline())
            self.taui = float(config.readline())
            self.taud = float(config.readline())
            self.alpha = float(config.readline())
            self.freq = float(config.readline())
            self.d_controller_enabled = int(config.readline())
        self.Ts = 1/self.freq

        #self.C_num, self.C_den = self.calculate_tf(False)
        #self.b, self.a = self.bilinear_transform(self.C_num, self.C_den)
        #self.C_num_withoutI, self.C_den_withoutI = self.calculate_tf(True)
        #self.b_withoutI, self.a_withoutI = self.bilinear_transform(self.C_num_withoutI, self.C_den_withoutI)
    
    integral_error = 0
    prev_t = 0
    upper_lim = 28
    lower_lim = -4
    u_past = 0
    y_past = 0
    uD_past = 0
    Du_max = 10000000000
    Du_min = -10000000000
    # e = [0, 0, 0]
    # u = [0, 0, 0]
    
    # def calculate_tf(self,withoutI):
    #     self.I_num = [self.taui, 1]
    #     self.I_den = [self.taui, 0]
    #     self.D_num = [self.taud, 1]
    #     self.D_den = [self.taud*self.alpha, 1]
    #     if withoutI:
    #         return np.multiply(self.D_num,self.kp), self.D_den
    #     else:
    #         return self.kp*np.polymul(self.I_num, self.D_num), np.polymul(self.I_den, self.D_den)

    # def bilinear_transform(self, num, den):
    #     return sig.bilinear(num, den, self.freq)   

    # PID implemented using approach from https://www.mstarlabs.com/apeng/techniques/pidsoftw.html
    def update(self, t, t_target):
        error = t_target - t
        pidout = error
        pidout += self.integral_error * self.Ts / self.taui
        if self.d_controller_enabled:
            derivative = t - self.prev_t
            pidout += derivative * self.taud / self.Ts
            self.prev_t = t
        pidout *= self.kp
        
        if self.lower_lim < pidout < self.upper_lim:
            self.integral_error += error

        return max(min(pidout,self.upper_lim),self.lower_lim)

    # PID implemented using [Niemann ch. 18] (no wind-up compensation but bilinear transformation)
    # def update2(self, t, t_target):
    #     self.e[0] = t_target - t
    #     self.u[0] = self.a[1]*self.u[1] + self.a[2]*self.u[2] + self.b[0]*self.e[0] + self.b[1]*self.e[1] + \
    #         self.b[2]*self.e[2]
    #     self.e[2] = self.e[1]
    #     self.e[1] = self.e[0]
    #     self.u[2] = self.u[1]
    #     self.u[1] = self.u[0]
    #     if self.u[0] > self.upper_lim:
    #         return self.upper_lim
    #     elif self.u[0] < self.lower_lim:
    #         return self.lower_lim
    #     else:
    #         return self.u[0]

    # PID controller implemented using [Wang ch. 4.4.2] (note that fs should be as fast as possible)
    def update3(self, y_current, r_current):
        uD_current = ((self.alpha*self.taud) / (self.alpha*self.taud + self.Ts)) * self.uD_past  + \
            ((self.kp*self.taud) / (self.alpha*self.taud + self.Ts)) * (y_current - self.y_past)
        print(uD_current)
        u_current = self.u_past + self.kp*(self.y_past - y_current) + ((self.kp*self.Ts) / self.taui) * \
            (r_current - y_current) - uD_current + self.uD_past
        print(u_current)
        Du = (u_current - self.u_past) / self.Ts
        if Du > self.Du_max:
            u_current = self.u_past + self.Du_max*self.Ts
            Du = self.Du_max
        if Du < self.Du_min:
            u_current = self.u_past + self.Du_min*self.Ts
            Du = self.Du_min
        if u_current > self.upper_lim:
            u_current = self.upper_lim
        if u_current < self.lower_lim:
            u_current = self.lower_lim
        self.uD_past = uD_current
        self.u_past = u_current
        self.y_past = y_current
        return u_current