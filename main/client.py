from soar.main.common import *
import sys

def __init__():
    global __hash__,__handlers__
    __hash__ = input()
    __handlers__ = {}
    recv = Thread(target=__recv_thread__,  daemon=True)
    recv.daemon = True
    recv.start()

def message(topic,msg=''):
    global __hash__
    soar_msg = __hash__ + ':' + topic + ':' + msg
    print(soar_msg)
    sys.stdout.flush()

# handler is a function that gets messages, in order.
# If the handler is slow, it WILL block all other handlers,
#
def subscribe(topic, handler):
    global __handlers__
    assert ':' not in topic
    __handlers__[topic] = handler
    message(SUB_MSG,topic)

def terminate_soar():
    message(CLOSE_MSG)

def start_process(shell_string):
    message(OPEN_MSG,shell_string)

def soar_print(*print_out):
    print(' '.join(print_out),file=sys.stderr)

def __recv_thread__():
    global __handlers__
    while True:
        message = input()
        topic,_,msg = message.partition(':')
        assert topic in __handlers__
        __handlers__[topic](msg)

__init__()
