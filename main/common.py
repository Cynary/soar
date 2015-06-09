from threading import Thread,Event,Lock
from soar.main.sPickle import *

# Python 2/3 quirks
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

try:
    input = raw_input
except NameError:
    pass

SUB_MSG = 'SUB'
CLOSE_MSG = 'CLOSE'
OPEN_MSG = 'OPEN'

PAUSE_MSG = 'PAUSE'
CONTINUE_MSG = 'CONTINUE'
STEP_MSG = 'STEP'

SIM_STEP_MSG = 'SIM_STEP'
BRAIN_MSG = 'BRAIN_MESSAGE'
