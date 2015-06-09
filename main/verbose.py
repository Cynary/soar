#!/usr/bin/python
import time
from soar.main.common import *
import soar.main.client as client

def printer(inp):
    topic,message = inp
    print("%s:%s" % (topic,message))
client.keep_alive()
client.subscribe("ALL",printer)
