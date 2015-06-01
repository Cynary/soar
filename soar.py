#!/usr/bin/python
from __future__ import print_function
import shlex
import sys
import time
from subprocess import Popen,PIPE
from threading import Thread,Event,Lock

# Python 2/3 quirks
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

try:
    input = raw_input
except NameError:
    pass

threads = set()
processes = set()
process_lock = Lock()
message_queue = Queue()
soar_commands = {"CLOSE",""}
stop = Event()
subscribers = {'ALL':[]}
subscribe_lock = Lock()

def gen_garbage():
    return "ALSKNDKLASD"

def parse_message(message,hash,stdin):
    h,s,msg = message.partition(':')
    if s == '' or h != hash: # Not a SOAR message, just print, and continue
        print(message[:-1]) # take out the newline
        return
    topic,_,msg = msg.partition(':')

    if topic == 'SUB':
        topic_to_sub = msg[:-1]
        with subscribe_lock:
            if topic_to_sub not in subscribers:
                subscribers[topic_to_sub] = []
            subscribers[topic_to_sub].append(stdin)
    else:
        message_queue.put((topic,msg))

def input_thread():
    while not stop.is_set():
        message = ':' + input() + '\n'
        parse_message(message,'',sys.stdin)

def terminate_cleanly(p, shell_string):
    if p.poll() is not None:
        return # Yay! we're done
    print("Terminating process %s" % shell_string)
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
    p = Popen(args,stdin=PIPE,stdout=PIPE)
    with process_lock:
        if stop.is_set():
            return
        processes.add((p,shell_string))
    try:
        hash = gen_garbage()
        p.stdin.write(bytes(hash+'\n','UTF-8'))
        p.stdin.flush()

        while p.poll() is None:
            message = p.stdout.readline().decode('UTF-8')
            if message == '' or message[-1] != '\n':
                assert p.poll() is not None
                print("Process %s died." % shell_string,
                      file=sys.stderr)
                return
            parse_message(message,hash,p.stdin)
    finally:
        terminate_cleanly(p,shell_string)

def main(argv):
    try:
        # Start command line argument processes
        for shell_string in argv[1:]:
            t = Thread(target=process_thread,args=[shell_string])
            threads.add(t)
            t.start()
        # Special direct input thread
        Thread(target=input_thread, daemon=True).start()

        while True:
            topic,message = message_queue.get()
            if topic == "CLOSE":
                print("SOAR is closing now")
                return 0
            elif topic == "OPEN":
                t = Thread(target=process_thread,args=[message])
                threads.add(t)
                t.start()
            else:
                # message variable ends in newline
                for out in subscribers['ALL']:
                    out.write(bytes("TOPIC:%s,MESSAGE:%s" % (topic,message),'UTF-8'))
                    out.flush()
                if topic in subscribers:
                    for out in subscribers[topic]:
                        out.write(bytes(message,'UTF-8'))
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
