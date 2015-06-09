import soar.brain.brain as brain
import time

def step(r):
    k = 3.
    try:
        front = sum(r.getSonars()[3:5])/2.
    except:
        r.setForward(0)
        return
    r.setForward(k*(front-0.5))

brain.main(step,period=0.01)
