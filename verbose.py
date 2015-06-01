import time
import sys

try:
    input = raw_input
except NameError:
    pass
hash = input()
print(hash+":SUB:ALL")
while True:
    print(input(),file=sys.stderr)
