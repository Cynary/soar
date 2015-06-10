from __future__ import absolute_import
from threading import Thread,Event,Lock
from .sPickle import *

# Python 2/3 quirks
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

try:
    input = raw_input
except NameError:
    pass

try:
    numbers = (long,int,float)
except NameError:
    numbers = (int,float)

SUB_MSG = 'SUB'
CLOSE_MSG = 'CLOSE'
OPEN_MSG = 'OPEN'

PAUSE_MSG = 'PAUSE'
CONTINUE_MSG = 'CONTINUE'
STEP_MSG = 'STEP'

SIM_STEP_MSG = 'SIM_STEP'
BRAIN_MSG = 'BRAIN_MESSAGE'
