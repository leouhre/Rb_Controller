from collections import deque
import time, sys

import numpy as np
from classes.pid import PID

PI = PID()


d1 = deque()
d1.append(1)
d1.append(1)
d1.append(1)

d2 = deque()
d2.append(2)
d2.append(2)
d2.append(2)
values = (d1,d2)
print(str(sum(d1)))
print(str(sum(values.pop)))
    
timer = time.time()

print(str(np.random.random_sample()))