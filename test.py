import soar.brain.brain as brain
import soar.gui.robot_model as model
import soar.pioneer.geometry as geom
from soar.gui.robot import transform
import soar.gui.robot_model as model
from math import *
import time

def get_dright_angle(r):
    s5,s6,s7 = r.getSonars()[5:8]
    i = 6
    if s5 is not None:
        s6 = s5
        i = 5
    if s6 is None:
        return s7,None
    if s7 is None:
        return s6,None
    orig = geom.Point(0,0)
    p1 = geom.Point(*transform(model.sonar_poses[i],(s6,0.)))
    p2 = geom.Point(*transform(model.sonar_poses[7],(s7,0.)))
    w = geom.Segment(p1,p2)

    dist = w.distance(orig,segment=False)
    w_vec = p1-p2
    angle = -atan2(w_vec.y,w_vec.x)
    return dist,angle

def step(r):
    k_d = 7.5
    k_theta = 1.5
    k_v = 1.5
    dist,angle = get_dright_angle(r)
    ranges = [i for i in r.getSonars() if i is not None]
    if len(ranges) == 0:
        danger = 1.
    else:
        danger = min(ranges)
    if angle is None:
        r.setRotational(1.0)
        r.setForward(danger*k_v)
    else:
        desired_dist = 0.4
        desired_theta = k_d*(desired_dist-dist)
        omega = k_theta*(desired_theta-angle)
        r.setRotational(omega)
        r.setForward(danger*k_v)
    print("HERE")
    assert False
brain.main(step,period=0.1)
