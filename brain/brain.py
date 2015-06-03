from soar.brain.templates import *
from soar.main.common import *
import soar.main.client as client
import time

class RobotClient(RobotIO):
    def __init__(self,port=0): # x,y,theta position
        self.sonars = [None]*N_SONARS
        self.initial = (0,0,0)
        self.position = (0,0,0)
        self.analog_inputs = [None]*N_ANALOG_INPUTS
        self.port = port
        client.subscribe(SONARS_TOPIC(port),self.__update_sonars__)
        client.subscribe(POSITION_TOPIC(port),self.__update_position__)
        client.subscribe(ANALOG_INPUTS_TOPIC(port),self.__update_analog_inputs__)
        client.subscribe(INITIAL_TOPIC(port),self.__update_initial__)

    def __update_sonars__(self,sonar_msg):
        d = eval(sonar_msg)
        d = {}
        for i,r in d.items():
            self.sonars[i] = r
    def getSonars(self):
        return self.sonars[:]

    def __update_initial__(self,initial_msg):
        p = eval(initial_msg)
        self.initial = p
    def __update_position__(self,position_msg):
        p = eval(initial_msg)
        self.position = p
    def getPosition(self,cheat=False):
        position = self.position[:]
        if cheat:
            position = (p+i for p,i in zip(position,self.initial))
        return position

    def __update_analog_inputs__(self,analog_inputs_msg):
        analog_inputs = eval(analog_inputs_msg)[4:]
        self.analog_inputs = analog_inputs
    def getAnalogInputs(self):
        return self.analog_inputs[:]

    def setForward(self,v):
        assert isinstance(v,(int,float)), "Forward velocity should be number"
        msg = repr(v)
        client.message(SPEED_TOPIC(self.port),msg)
    def setRotational(self,omega):
        assert isinstance(omega,(int,float)), "Rotational velocity should be number"
        msg = repr(omegax)
        client.message(OMEGA_TOPIC(self.port),msg)
    def setVoltage(self,v):
        assert isinstance(v,(int,float)), "Voltage should be number"
        msg = repr(v)
        client.message(VOLTAGE_TOPIC(self.port),msg)
    def stopAll(self):
        self.setForward(0)
        self.setRotational(0)
        self.setVoltage(0)

def main(step,period=0.1,port=0):
    global active
    active = True
    r = RobotClient()
    while active:
        start = time.time()
        step(r)
        time.sleep(max(0.,period-(time.time()-start)))
    r.stopAll()
def terminate():
    global active
    active = False
