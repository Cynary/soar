# SYNC commands
#
SYNC0 = 0
SYNC1 = 1
SYNC2 = 2

# Argument types
#
ARGINT	= 0x3B
ARGNINT	= 0x1B
ARGSTR	= 0x2B

class Command:
    def __init__(self,cmd,t):
        self.cmd = cmd
        self.type = t
        assert self.type in (str,int,None)
        if self.type is str:
            self.arg = ARGSTR
        self.data = []

    def set(self,data):
        assert self.type is not None
        assert isinstance(data,self.type)
        if self.type is int:
            self.arg = ARGINT if data >= 0 else ARGNINT
            data = abs(data)
            self.data = [data&0xFF,(data>>8)]
        elif self.type is str:
            self.data = [ord(d) for d in data]
        else:
            raise Exception("UNIMPLEMENTED TYPE")

    def __iter__(self):
        assert self.type is None or self.data is not []
        yield self.cmd
        if self.type is not None:
            yield self.arg
            for d in self.data:
                yield d
            self.data = []

# Client commands
#
PULSE       =   0
OPEN        =   1
CLOSE       =   2
POLLING     =   3
ENABLE      =   4
SETA        =   5
SETV        =   6
SETO        =   7
MOVE        =   8
ROTATE      =   9
SETRV       =  10
VEL         =  11
HEAD        =  12
DHEAD       =  13
SAY         =  15
JOYREQUEST  =  17
CONFIG      =  18
ENCODER     =  19
RVEL        =  21
DCHEAD      =  22
SETRA       =  23
SONAR       =  28
STOP        =  29
DIGOUT      =  30
VEL2        =  32
GRIPPER     =  33
ADSEL       =  35
GRIPPERVAL  =  36
GRIPREQUEST =  37
GYROCALCW   =  38
GYROCALCCW  =  39
IOREQUEST   =  40
TTY2        =  42
GETAUX      =  43
BUMPSTALL   =  44
TCM2        =  45
JOYDRIVE    =  47
SONARCYCLE  =  48
HOSTBAUD    =  50
AUX1BAUD    =  51
AUX2BAUD    =  52
AUX3BAUD    =  53
E_STOP      =  55
M_STALL     =  56
GYROREQUEST =  58
LCDWRITE    =  59
TTY4        =  60
GETAUX3     =  61
TTY3        =  66
GETAUX2     =  67
CHARGE      =  68
ROTKP       =  82
ROTKV       =  83
ROTKI       =  84
TRANSKP     =  85
TRANSKI     =  87
REVCOUNT    =  88
DRIFTFACTOR =  89
SOUNDTOG    =  92
TICKSMM     =  93
BATTEST     = 250
RESET       = 253
MAINTENANCE = 255

# Command objects
#
commands = {
    PULSE       : Command(PULSE,None),
    OPEN        : Command(OPEN,None),
    CLOSE       : Command(CLOSE,None),
    POLLING     : Command(POLLING,str),
    ENABLE      : Command(ENABLE,int),
    SETA        : Command(SETA,int),
    SETV        : Command(SETV,int),
    SETO        : Command(SETO,None),
    MOVE        : Command(MOVE,int),
    ROTATE      : Command(ROTATE,int),
    SETRV       : Command(SETRV,int),
    VEL         : Command(VEL,int),
    HEAD        : Command(HEAD,int),
    DHEAD       : Command(DHEAD,int),
    SAY         : Command(SAY,str),
    JOYREQUEST  : Command(JOYREQUEST,int),
    CONFIG      : Command(CONFIG,None),
    ENCODER     : Command(ENCODER,int),
    RVEL        : Command(RVEL,int),
    DCHEAD      : Command(DCHEAD,int),
    SETRA       : Command(SETRA,int),
    SONAR       : Command(SONAR,int),
    STOP        : Command(STOP,None),
    DIGOUT      : Command(DIGOUT,int),
    VEL2        : Command(VEL2,int),
    GRIPPER     : Command(GRIPPER,int),
    ADSEL       : Command(ADSEL,int),
    GRIPPERVAL  : Command(GRIPPERVAL,int),
    GRIPREQUEST : Command(GRIPREQUEST,int),
    GYROCALCW   : Command(GYROCALCW,int),
    GYROCALCCW  : Command(GYROCALCCW,int),
    IOREQUEST   : Command(IOREQUEST,int),
    TTY2        : Command(TTY2,str),
    GETAUX      : Command(GETAUX,int),
    BUMPSTALL   : Command(BUMPSTALL,int),
    TCM2        : Command(TCM2,int),
    JOYDRIVE    : Command(JOYDRIVE,int),
    SONARCYCLE  : Command(SONARCYCLE,int),
    HOSTBAUD    : Command(HOSTBAUD,int),
    AUX1BAUD    : Command(AUX1BAUD,int),
    AUX2BAUD    : Command(AUX2BAUD,int),
    AUX3BAUD    : Command(AUX3BAUD,int),
    E_STOP      : Command(E_STOP,None),
    M_STALL     : Command(M_STALL,int),
    GYROREQUEST : Command(GYROREQUEST,int),
    LCDWRITE    : Command(LCDWRITE,str),
    TTY4        : Command(TTY4,str),
    GETAUX3     : Command(GETAUX3,int),
    TTY3        : Command(TTY3,str),
    GETAUX2     : Command(GETAUX2,int),
    CHARGE      : Command(CHARGE,int),
    ROTKP       : Command(ROTKP,int),
    ROTKV       : Command(ROTKV,int),
    ROTKI       : Command(ROTKI,int),
    TRANSKP     : Command(TRANSKP,int),
    TRANSKI     : Command(TRANSKI,int),
    REVCOUNT    : Command(REVCOUNT,int),
    DRIFTFACTOR : Command(DRIFTFACTOR,int),
    SOUNDTOG    : Command(SOUNDTOG,int),
    TICKSMM     : Command(TICKSMM,int),
    BATTEST     : Command(BATTEST,int),
    RESET       : Command(RESET,None),
    MAINTENANCE : Command(MAINTENANCE,None),
}
