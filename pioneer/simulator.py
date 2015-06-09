from __future__ import absolute_import

from soar.brain.templates import *
from soar.main.common import *
from soar.gui.robot import parse_map
import soar.main.client as client

from getopt import getopt
from threading import Event
from math import pi,sin,cos
import time
import sys

# Simulator limits
MAX_V = 0.75
MAX_OMEGA = pi/2.

class RobotStatus(RobotIO):
    def __init__(self,initial=(0,0,0),port=0):
        self.port = port
        self.v = 0.0
        self.omega = 0.0
        self.voltage = 0.0
        self.position = (0,0,0)
        self.colliding = False

        self.paused = Event()
        self.stop = Event()

        client.message(INITIAL_TOPIC(port),initial)
        client.subscribe(SPEED_TOPIC(port),self.setForward)
        client.subscribe(OMEGA_TOPIC(port),self.setRotational)
        client.subscribe(VOLTAGE_TOPIC(port),self.setVoltage)

        client.subscribe(BRAIN_MSG,self.brain_background)
        client.subscribe(SIM_STEP_MSG,self.step)

    def setForward(self,v):
        assert isinstance(v,(int,float)), "Forward velocity should be number"
        self.v = max(-MAX_V,min(MAX_V,v))

    def setRotational(self,omega):
        assert isinstance(omega,(int,float)), "Rotational velocity should be number"
        self.omega = max(-MAX_OMEGA,min(MAX_OMEGA, omega))

    def setVoltage(self,v):
        assert isinstance(v,(int,float)), "Voltage should be number"
        self.voltage = max(-10.,min(10,v))

    def step(self,dt):
        x,y,theta = self.position
        x += self.v*cos(theta)*dt
        y += self.v*sin(theta)*dt
        theta += self.omega*dt
        # Check if we are colliding.
        # If we are, then don't move.
        client.message(COLLIDES_TOPIC(self.port),self.colliding)
        if self.colliding:
            return

        self.position = (x,y,theta)
        client.message(POSITION_TOPIC(self.port),self.position)

        # Calculate sonars, and send them.

    def brain_background(self):
        assert not self.stop.is_set(), "The simulator is terminated"
        assert msg in (PAUSE_MSG,CONTINUE_MSG,STEP_MSG,CLOSE_MSG), "Message not recognized"
        if msg == PAUSE_MSG:
            self.paused.set()
        elif msg == CONTINUE_MSG:
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
            self.step(t1-t0)
            t0 = t1
            time.sleep(0.01)

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
    initial_loc = w/2.,h/2.
    walls = []
    if map_file is not None:
        (w,h),walls,initial_loc = parse_map(map_file)


    status = RobotStatus(initial,port)
    client.keep_alive()
    Thread(target=status.go).start()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
