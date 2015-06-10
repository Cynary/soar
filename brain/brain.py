from __future__ import absolute_import
from .templates import *
from soar.main.common import *
import soar.main.client as client
import time
from threading import Event,Timer

class RobotClient(RobotIO):
    def __init__(self,port=0):
        self.sonars = [None]*N_SONARS
        self.initial = (0,0,0)
        self.position = (0,0,0)
        self.analog_inputs = [None]*N_ANALOG_INPUTS
        self.port = port
        self.sonars_updated = Event()
        self.track_sonars = set(range(N_SONARS))
        client.subscribe(SONARS_TOPIC(port),self.__update_sonars__)
        client.subscribe(POSITION_TOPIC(port),self.__update_position__)
        client.subscribe(ANALOG_INPUTS_TOPIC(port),self.__update_analog_inputs__)
        client.subscribe(INITIAL_TOPIC(port),self.__update_initial__)

    def __update_sonars__(self,sonars):
        for i,r in sonars.items():
            self.track_sonars.discard(i)
            self.sonars[i] = r/1000. if r is not None else r # Convert to meters
        if not self.sonars_updated.is_set() and len(self.track_sonars) == 0:
            self.sonars_updated.set()
    def getSonars(self):
        return self.sonars[:]

    def __update_initial__(self,initial):
        self.initial = initial
    def __update_position__(self,position):
        self.position = position
    def getPosition(self,cheat=False):
        position = self.position[:]
        if cheat:
            position = (p+i for p,i in zip(position,self.initial))
        return position

    def __update_analog_inputs__(self,analog_inputs):
        self.analog_inputs = analog_inputs[N_ANALOG_INPUTS:]
    def getAnalogInputs(self):
        return self.analog_inputs[:]

    def setForward(self,v):
        assert isinstance(v,numbers), "Forward velocity should be number"
        client.message(SPEED_TOPIC(self.port),v)
    def setRotational(self,omega):
        assert isinstance(omega,numbers), "Rotational velocity should be number"
        client.message(OMEGA_TOPIC(self.port),omega)
    def setVoltage(self,v):
        assert isinstance(v,numbers), "Voltage should be number"
        client.message(VOLTAGE_TOPIC(self.port),v)
    def stopAll(self):
        self.setForward(0)
        self.setRotational(0)
        self.setVoltage(0)


def brain_background(msg):
    global paused,g_step,g_robot,g_timer,g_period
    assert not stop.is_set(), "The brain is terminated"
    assert msg in (PAUSE_MSG,CONTINUE_MSG,STEP_MSG,CLOSE_MSG), "Message not recognized"
    if msg == PAUSE_MSG:
        g_timer.cancel()
        paused.set()
    elif msg == CONTINUE_MSG:
        paused.clear()
        step_thread()
    elif msg == STEP_MSG:
        g_step(g_robot)
        client.message(SIM_STEP_MSG,g_period)
    elif msg == CLOSE_MSG:
        terminate()

def step_thread():
    global stop,paused,g_period,g_step,g_robot,g_timer
    if stop.is_set() or paused.is_set():
        return
    start = time.time()
    g_step(g_robot)
    if g_timer is not None:
        g_timer.cancel()
    g_timer = Timer(max(0.,g_period-(time.time()-start)), step_thread)
    g_timer.start()

def main(step,period=0.1,port=0):
    global stop,paused,g_robot,g_step,g_period,g_timer
    paused = Event()
    stop = Event()
    client.keep_alive()
    g_robot = RobotClient(port)
    g_step = step
    g_period = period
    g_timer = None
    client.subscribe(BRAIN_MSG,brain_background)
    g_robot.sonars_updated.wait()
    step_thread()

def terminate():
    global stop,g_robot,g_timer
    stop.set()
    g_timer.cancel()
    g_robot.stopAll()
    client.terminate()
