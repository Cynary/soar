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
    global __handlers__,initialized,__msg_queue__
    sys.stdout = sys.stderr
    __handlers__ = {}
    __msg_queue__ = Queue()
    recv = Thread(target=__recv_thread__)
    recv.daemon = True
    recv.start()
    exc = Thread(target=__execute_thread__)
    exc.daemon = True
    exc.start()
    initialized = True

def keep_alive():
    Thread(target=__keep_alive__).start()
def __keep_alive__():
    __terminate__.wait()
def terminate():
    global __msg_queue__
    __terminate__.set()
    # Dummy message queue message to terminate that thread
    #
    __msg_queue__.put((None,None))

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

# This dequeues the messages, and executes on them
# The decoupling of these threads makes it so that we get
# asynchronous input, and execution.
# It also allows us to manipulate the queue so we're acting
# on mostly fresh data if execution takes too long
# If the queue size goes over a certain amount, we discard old messages.
# This helps make sure that we are acting on recent data most of the time
#
QUEUE_SIZE=1000
def __execute_thread__():
    global __handlers__,__msg_queue__
    while True:
        (topic,msg) = __msg_queue__.get()
        if __terminate__.is_set():
            break
        assert topic in __handlers__
        __handlers__[topic](msg)
        # If we have a lot of old data, just throw it all away
        #
        with __msg_queue__.mutex:
            if len(__msg_queue__.queue) > QUEUE_SIZE:
                __msg_queue__.queue.clear()

# Enqueues messages received from the message exchange service.
# This way the pipe won't block
#
def __recv_thread__():
    global __handlers__,__msg_queue__
    for (topic,msg) in s_load(__SOAR_INPUT__):
        if __terminate__.is_set():
            break

        __msg_queue__.put((topic,msg))
    # lost soar/terminated
    terminate()

def on_kill(handler):
    def kill_handler(sig_no,stack_frame):
        terminate()
        handler()
        sys.exit(0)
    signal(SIGTERM,kill_handler)
