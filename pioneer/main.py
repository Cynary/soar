#!/usr/bin/python
from __future__ import absolute_import
import sys
from .robot import Robot
from threading import Thread,Lock
import time

count = 0

def main(argv):
    global count
    r = Robot()
    # Count byte rate
    l = Lock()
    def h(pac):
        global count
        with l:
            count += pac.size

    t = time.time()
    Thread(target=r.receive,args=(h,h)).start()
    while time.time()-t <= 10.0:
        time.sleep(1.0)
    r.terminate()
    t2 = time.time()
    print("%.3f bytes/sec" % (count/(t2-t)))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
