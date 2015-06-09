class RobotIO:
    def setForward(self,v):
        raise NotImplementedError("Set Forward is not implemented")
    def setRotational(self,omega):
        raise NotImplementedError("Set Rotational is not implemented")
    def setVoltage(self,v):
        raise NotImplementedError("Set Voltage is not implemented")
    def stopAll(self):
        raise NotImplementedError("Stop All is not implemented")
    def getSonars(self):
        raise NotImplementedError("Get Sonars is not implemented")
    def getPosition(self):
        raise NotImplementedError("Get Position is not implemented")
    def getAnalogInputs(self):
        raise NotImplementedError("Get Analog Inputs is not implemented")

SPEED_TOPIC = lambda p: "PIONEER_FORWARD_VEL_%s" % str(p)
OMEGA_TOPIC = lambda p: "PIONEER_ROTATIONAL_VEL_%s" % str(p)
VOLTAGE_TOPIC = lambda p: "PIONEER_VOLTAGE_%s" % str(p)
SONARS_TOPIC = lambda p: "PIONEER_SONARS_%s" % str(p)
POSITION_TOPIC = lambda p: "PIONEER_POSITION_%s" % str(p)
ANALOG_INPUTS_TOPIC = lambda p: "PIONEER_ANALOG_INPUTS_%s" % str(p)

N_SONARS = 8
N_ANALOG_INPUTS = 4

INITIAL_TOPIC = lambda p: "SIM_INITIAL_%s" % str(p) # Simulator cheat
COLLIDES_TOPIC = lambda p: "SIM_COLLIDING_%s" % str(p)
