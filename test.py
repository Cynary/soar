import soar.brain.brain as brain
import soar.gui.robot_model as model
import time

def get_dright_angle(r):
    s6,s7 = r.getSonars()[6:8]
    return 0.,0.

def step(r):
    k = 3.
    distance = r.getSonars()[3]
    r.setForward(k*(distance-0.5))
brain.main(step,period=0.1)
