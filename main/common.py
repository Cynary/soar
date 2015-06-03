from threading import Thread,Event,Lock
# Python 2/3 quirks
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    input = raw_input
except NameError:
    pass

# These messages can NOT have a ':' character
SUB_MSG = 'SUB'
CLOSE_MSG = 'CLOSE'
OPEN_MSG = 'OPEN'
