from common import *

def __init__():
    global __hash__,__handlers__
    __hash__ = input()
    __handlers__ = {}
    Thread(target=__recv_thread__,  daemon=True).start()

def __message__(topic,msg=''):
    global __hash__
    soar_msg = __hash__ + ':' + topic + ':' + msg
    print(soar_msg)

# handler is a function that gets messages, in order.
# If the handler is slow, it WILL block all other handlers,
#
def subscribe(topic, handler):
    global __handlers__
    assert ':' not in topic
    __handlers__[topic] = handler
    __message__(SUB_MSG,topic)

def terminate_soar():
    __message__(CLOSE_MSG)

def start_process(shell_string):
    __message__(OPEN_MSG,shell_string)

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
