#!/usr/bin/python2

# SYNC commands
#
CMD_SYNC0 = 0
CMD_SYNC1 = 1
CMD_SYNC2 = 2

# Argument types
#
ARGINT	= 0x3B,
ARGNINT	= 0x1B,
ARGSTR	= 0x2B,

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
ROTATE	    =   9
SETRV	    =  10
VEL	    =  11
HEAD	    =  12
DHEAD	    =  13
SAY	    =  15
JOYREQUEST  =  17
CONFIG	    =  18
ENCODER	    =  19
RVEL	    =  21
DCHEAD	    =  22
SETRA	    =  23
SONAR	    =  28
STOP	    =  29
DIGOUT	    =  30
VEL2	    =  32
GRIPPER	    =  33
ADSEL	    =  35
GRIPPERVAL  =  36
GRIPREQUEST =  37
IOREQUEST   =  40
TTY2	    =  42
GETAUX	    =  43
BUMPSTALL   =  44
TCM2	    =  45
JOYDRIVE    =  47
SONARCYCLE  =  48
HOSTBAUD    =  50
AUX1BAUD    =  51
AUX2BAUD    =  52
AUX3BAUD    =  53
E_STOP	    =  55
M_STALL	    =  56
GYROREQUEST =  58
LCDWRITE    =  59
TTY4	    =  60
GETAUX3	    =  61
TTY3	    =  66
GETAUX2	    =  67
CHARGE	    =  68
RESET	    = 254
MAINTENANCE = 255
