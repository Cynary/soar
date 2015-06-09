#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
import shlex
import sys
import time
import string
import random
import io
import os
from subprocess import Popen,PIPE
from .common import *

threads = set()
processes = set()
process_lock = Lock()
message_queue = Queue()
soar_commands = {"CLOSE",""}
stop = Event()
subscribers = {'ALL':set()}
subscribe_lock = Lock()

def gen_garbage(n=20): # Hash does NOT contain new lines
    allowed = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(allowed) for _ in range(n))

def parse_message(topic,msg,stdin,sub_set):
    if topic == SUB_MSG:
        topic_to_sub = msg
        print("HERE")
        with subscribe_lock:
            if topic_to_sub not in subscribers:
                subscribers[topic_to_sub] = set()
            subscribers[topic_to_sub].add(stdin)
            sub_set.add(topic_to_sub)
    else:
        message_queue.put((topic,msg))

def input_thread():
    while not stop.is_set():
        topics_sub = set()
        message = input()
        # Ignore empty messages
        if message == ':\n':
            continue
        topic,_,msg = message.partition(':')
        try:
            msg = eval(msg)
        except (SyntaxError,NameError):
            pass
        parse_message(topic,msg,sys.stdin,topics_sub)

def terminate_cleanly(p, shell_string):
    if p.poll() is not None:
        return # Yay! we're done
    print("Cleanly terminating process %s" % shell_string)
    p.terminate()
    # Wait for it to terminate for WAIT_TIME
    #
    delta = 0.1
    for _ in range(int(WAIT_TIME/delta)):
        if p.poll() is not None:
            break
        time.sleep(delta)
    # If process hasn't terminated after WAIT_TIME
    # kill it dead
    #
    if p.poll() is None:
        print("Killing %s dead" % shell_string)
        p.kill()

WAIT_TIME = 1.0 # seconds
def process_thread(shell_string):
    print("Launching process %s" % shell_string)
    args = shlex.split(shell_string)
    p = Popen(args,stdin=PIPE,stdout=PIPE,preexec_fn=os.setpgrp,bufsize=0)
    topics_sub=set()
    with process_lock:
        if stop.is_set():
            return
        processes.add((p,shell_string))
    try:
        try:
            stdin = io.TextIOWrapper(p.stdin)
            stdout = io.TextIOWrapper(p.stdout)
        except AttributeError: # Python 2 error :(, this feels like a giant hack
            stdin = p.stdin
            stdout = p.stdout

        for (topic,message) in s_load(stdout):
            parse_message(topic,message,stdin,topics_sub)
        print("Process %s has died" % shell_string)
    finally:
        with subscribe_lock:
            for topic in topics_sub:
                subscribers[topic].remove(stdin)
        terminate_cleanly(p,shell_string)

def main(argv):
    try:
        # Start command line argument processes
        for shell_string in argv[1:]:
            t = Thread(target=process_thread,args=[shell_string])
            threads.add(t)
            t.start()
        # Special direct input thread
        special = Thread(target=input_thread)
        special.daemon = True
        special.start()

        while True:
            topic,message = message_queue.get()
            if topic == CLOSE_MSG:
                print("SOAR is closing now")
                return 0
            elif topic == OPEN_MSG:
                t = Thread(target=process_thread,args=[message])
                threads.add(t)
                t.start()
            else:
                for out in subscribers['ALL']:
                    s_dump_elt(("ALL",(topic,message)),out)
                    out.flush()
                if topic in subscribers:
                    for out in subscribers[topic]:
                        s_dump_elt((topic,message),out)
                        out.flush()
    finally:
        # Cleanup
        print("SOAR is cleaning up")
        stop.set()
        with process_lock:
            for p in processes:
                terminate_cleanly(*p)
        for t in threads:
            t.join()
    return 1 # We should not be here unless an error happened

if __name__ == "__main__":
    sys.exit(main(sys.argv))
