from __future__ import absolute_import
from __future__ import print_function
from .common import *
from signal import signal,SIGTERM
import sys
import io

initialized = False
# Set to False if there's no main loop
# Daemon threads die when the program dies
# Non-daemon threads need to be explicitly killed, or program will block until they die
__SOAR_INPUT__ = io.TextIOWrapper(io.BufferedReader(io.open(sys.stdin.fileno(),"rb",0,closefd=False)))
__SOAR_STDOUT__ = io.TextIOWrapper(io.BufferedWriter(io.open(sys.stdout.fileno(),"wb",0,closefd=False)))
__terminate__ = Event()

def __init__():
    global __handlers__,initialized
    sys.stdout = sys.stderr
    __handlers__ = {}
    recv = Thread(target=__recv_thread__)
    recv.daemon = True
    recv.start()
    initialized = True

def keep_alive():
    Thread(target=__keep_alive__).start()
def __keep_alive__():
    __terminate__.wait()
def terminate():
    __terminate__.set()

def message(topic,msg=None):
    if not initialized:
        __init__()
    s_dump_elt((topic,msg),__SOAR_STDOUT__)
    __SOAR_STDOUT__.flush()

# handler is a function that gets messages, in order.
# If the handler is slow, it WILL block all other handlers,
#
def subscribe(topic, handler):
    global __handlers__
    if not initialized:
        __init__()
    __handlers__[topic] = handler
    message(SUB_MSG,topic)

def terminate_soar():
    if not initialized:
        __init__()
    message(CLOSE_MSG)

def start_process(shell_string):
    if not initialized:
        __init__()
    message(OPEN_MSG,shell_string)

def __recv_thread__():
    global __handlers__
    for (topic,msg) in s_load(__SOAR_INPUT__):
        assert topic in __handlers__
        __handlers__[topic](msg)
    # lost soar
    terminate()

def on_kill(handler):
    def kill_handler(sig_no,stack_frame):
        terminate()
        handler()
        sys.exit(0)
    signal(SIGTERM,kill_handler)
