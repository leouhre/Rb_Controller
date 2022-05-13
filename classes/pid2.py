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

        #self.C_num, self.C_den = self.calculate_tf(False)
        #self.b, self.a = self.bilinear_transform(self.C_num, self.C_den)
        #self.C_num_withoutI, self.C_den_withoutI = self.calculate_tf(True)
        #self.b_withoutI, self.a_withoutI = self.bilinear_transform(self.C_num_withoutI, self.C_den_withoutI)
    
    integral_error = 0
    prev_t = 0
    upper_lim = 28
    lower_lim = -4
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

    def update(self, t, t_target):
        error = t_target - t
        pidout = error
        pidout += self.integral_error * (1/self.freq) / self.taui
        if self.d_controller_enabled:
            derivative = t - self.prev_t
            pidout += derivative * self.taud / (1/self.freq)
            self.prev_t = t
        pidout *= self.kp
        if pidout > self.upper_lim:
            pidout = self.upper_lim
        elif pidout < self.lower_lim:
            pidout = self.lower_lim
        else:
            self.integral_error += error
        return pidout

    # def update2(self, t, t_target):
    #     self.e[0] = t_target - t
    #     self.u[0] = self.a[1]*self.u[1] + self.a[2]*self.u[2] + self.b[0]*self.e[0] + self.b[1]*self.e[1] + self.b[2]*self.e[2]
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