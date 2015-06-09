#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
import time
from .common import *
import soar.main.client as client
import sys

def printer(inp):
    topic,message = inp
    print("%s:%s" % (topic,message))
    sys.stderr.flush()
client.keep_alive()
client.subscribe("ALL",printer)
