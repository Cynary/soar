import sys
from robot import Robot
from arcos import *

def main(argv):
    robot = Robot()

    t = time.time()
    while True:
        s = port.read()
        p = t
        t = time.time()
        print(len(s)/float(t-p))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
