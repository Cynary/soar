from __future__ import absolute_import

from soar.brain.templates import *
from soar.main.common import *
from soar.gui.robot import parse_map,transform
import soar.gui.robot_model as model
import soar.main.client as client
import soar.pioneer.geometry as geom

from getopt import getopt
from threading import Event
from math import pi,sin,cos
import time
import sys

# Simulator limits
MAX_V = 0.75
MAX_OMEGA = pi/2.

MIN_SONAR_RANGE = 0.05
MAX_SONAR_RANGE = 1.5

class RobotStatus(RobotIO):
    def __init__(self,initial=(0,0,0),port=0):
        self.port = port
        self.v = 0.0
        self.omega = 0.0
        self.voltage = 0.0
        self.position = (0,0,0)
        self.colliding = False
        self.initial = initial

        self.paused = Event()
        self.stop = Event()

        client.subscribe(SPEED_TOPIC(port),self.setForward)
        client.subscribe(OMEGA_TOPIC(port),self.setRotational)
        client.subscribe(VOLTAGE_TOPIC(port),self.setVoltage)

        client.subscribe(BRAIN_MSG,self.brain_background)
        client.subscribe(SIM_MSG,self.brain_background)
        client.subscribe(SIM_STEP_MSG,self.step)

    def setForward(self,v):
        assert isinstance(v,numbers), "Forward velocity should be number"
        self.v = max(-MAX_V,min(MAX_V,v))

    def setRotational(self,omega):
        assert isinstance(omega,numbers), "Rotational velocity should be number"
        self.omega = max(-MAX_OMEGA,min(MAX_OMEGA, omega))

    def setVoltage(self,v):
        assert isinstance(v,numbers), "Voltage should be number"
        self.voltage = max(-10.,min(10,v))

    def setEnvironment(self,walls,w,h):
        self.walls = []
        limits = [(0,0,w,0),(w,0,w,h),(w,h,0,h),(0,h,0,0)]
        for (x1,y1,x2,y2) in walls+limits:
            self.walls.append(geom.Segment(geom.Point(x1,y1),geom.Point(x2,y2)))

    def step(self,dt,expect_paused=True):
        client.message(INITIAL_TOPIC(port),self.initial)
        if expect_paused and (not self.paused.is_set()):
            return
        x,y,theta = self.position
        x += self.v*cos(theta)*dt
        y += self.v*sin(theta)*dt
        theta += self.omega*dt
        ix,iy,itheta = self.initial
        # Check if we are colliding.
        # Build robot segments
        robot_segments = []
        px,py = transform((ix,iy,itheta),(x,y))
        pos = (px,py,itheta+theta-pi/2.)
        robot_points = (transform(pos,point) for point in model.points)
        prev = None
        first = None
        for p in robot_points:
            if prev is not None:
                robot_segments.append(geom.Segment(geom.Point(*prev),geom.Point(*p)))
            else:
                first = p
            prev = p
        robot_segments.append(geom.Segment(geom.Point(*prev),geom.Point(*first)))
        for w in self.walls:
            self.colliding = any(r.intersects(w) for r in robot_segments)
            if self.colliding:
                break
        # If we are, then don't move.
        client.message(COLLIDES_TOPIC(self.port),self.colliding)
        if not self.colliding:
            self.position = (x,y,theta)
        client.message(POSITION_TOPIC(self.port),self.position)

        # Calculate sonars, and send them.
        sonars = {}
        # Create sonar beams in [MIN_SONAR_RANGE,MAX_SONAR_RANGE]
        # Then find the walls it collides with, and choose the nearest one.
        x,y,theta = self.position
        px,py = transform((ix,iy,itheta),(x,y))
        pos = (px,py,itheta+theta)
        for i,(sx,sy,stheta) in enumerate(model.sonar_poses):
            (x,y) = transform(pos,(sx,sy))
            origin = (x,y,itheta+theta+stheta)
            p1 = geom.Point(*transform(origin,(MIN_SONAR_RANGE,0)))
            p2 = geom.Point(*transform(origin,(MAX_SONAR_RANGE,0)))
            beam = geom.Segment(p1,p2)
            intersects = (beam.intersection_point(w) for w in self.walls)
            intersects = (i for i in intersects if i is not None)
            ranges = (p1.distance(i) for i in intersects)
            try:
                r = min(ranges)
                r = int((r+MIN_SONAR_RANGE)*1000) # This is what the robot sends
            except ValueError: # No intersections
                r = None
            sonars[i] = r
        client.message(SONARS_TOPIC(self.port),sonars)

    def brain_background(self,msg):
        assert not self.stop.is_set(), "The simulator is terminated"
        assert msg in (PAUSE_MSG,CONTINUE_MSG,STEP_MSG,CLOSE_MSG), "Message not recognized"
        if msg == PAUSE_MSG:
            self.paused.set()
        elif msg == CONTINUE_MSG:
            if self.paused.is_set():
                self.paused.clear()
                Thread(target=self.go).start()
        elif msg == STEP_MSG:
            pass # Ignore
        elif msg == CLOSE_MSG:
            self.stop.set()
            client.terminate()

    def go(self):
        t0 = time.time()
        while not (self.paused.is_set() or self.stop.is_set()):
            t1 = time.time()
            self.step(t1-t0,expect_paused=False)
            t0 = t1
            time.sleep(max(0,0.02-(time.time()-t0)))

def main(argv):
    global status
    map_file = None
    port = 0
    initial = (0,0,0)
    opts,args = getopt(argv[1:],"p:i:m:",["port=","initial=","map="])
    for opt,arg in opts:
        if opt in ("-p","--port"):
            port = eval(arg)
        if opt in ("-i","--initial"):
            initial = eval(arg)
        if opt in ("-m","--map"):
            map_file = arg

    w,h = 7.,7.
    initial = w/2.,h/2.,0.
    walls = []
    if map_file is not None:
        (w,h),walls,initial = parse_map(map_file)

    status = RobotStatus(initial,port)
    status.setEnvironment(walls,w,h)
    status.paused.set()
    status.step(0) # For position, etc.
    client.keep_alive()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
