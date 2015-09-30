#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
import time
from .common import *
from . import client
import sys

def printer(inp):
    topic,message = inp
    print("VERBOSE:%s:%s" % (topic,message),file=sys.stderr)
    sys.stderr.flush()
client.keep_alive()
client.subscribe("ALL",printer)
