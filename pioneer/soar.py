from __future__ import absolute_import
from math import pi
from soar.brain.templates import *
from soar.main.common import *
from .robot import *
import soar.main.client as client
from getopt import getopt

class RobotStatus(RobotIO):
    def __init__(self,initial=(0,0,0),port=0):
        self.robot = Robot(port)
        self.port = port
        client.message(INITIAL_TOPIC(port),initial)
        client.subscribe(SPEED_TOPIC(port),self.setForward)
        client.subscribe(OMEGA_TOPIC(port),self.setRotational)
        client.subscribe(VOLTAGE_TOPIC(port),self.setVoltage)

    def go(self):
        self.robot.receive(self.__update_io__,self.__update_sip__)

    # Send messages
    #
    def __update_sip__(self, sip_pac):
        position = (sip_pac.x/1000.,sip_pac.y/1000.,sip_pac.theta) # in meters
        client.message(SONARS_TOPIC(self.port),sip_pac.sonars)
        client.message(POSITION_TOPIC(self.port),position)
    def __update_io__(self, io_pac):
        client.message(ANALOG_INPUTS_TOPIC(self.port),io_pac.analogInputs)

    def setForward(self,v):
        assert isinstance(v,numbers), "Forward velocity should be number"
        v = int(v*1000.) # Robot takes int, in mm/sec
        max_v = self.robot.config.max_v
        v = max(-max_v,min(max_v, v))
        self.robot.command(VEL,v)

    def setRotational(self,omega):
        assert isinstance(omega,numbers), "Rotational velocity should be number"
        omega = int(omega*180./pi) # Robot takes int, in deg/sec; 180 deg in pi rad
        max_omega = self.robot.config.max_omega
        omega = max(-max_omega,min(max_omega, omega))
        self.robot.command(RVEL,omega)

    def setVoltage(self,v):
        assert isinstance(v,numbers), "Voltage should be number"
        v = max(-10.,min(10,v))
        v = int(v*255./10.) # Robot takes int, in 0-255 for the first byte
        msg = (v&0xFF)<<8|0xFF # Second byte means we are setting everything

def main(argv):
    global status
    port = 0
    initial = (0,0,0)
    map_file = None
    opts,args = getopt(argv[1:],"p:i:",["port=","initial="])
    for opt,arg in opts:
        if opt in ("-p","--port"):
            port = eval(arg)
        if opt in ("-i","--initial"):
            initial = eval(arg)
    status = RobotStatus(initial,port)
    client.on_kill(status.robot.terminate)
    status.go()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
