#!/usr/bin/python2
import sys
from serial import *
from arcos import *
import fcntl
import time

# Calculate checksum on P2OS packet (see Pioneer manual)
def calc_checksum(data):
    c = 0
    i = 3
    n = data[2]-2
    while (n>1):
      c += (data[i]<<8) | (data[i+1])
      c = c & 0xFFFF
      n -= 2
      i += 2
    if (n>0):
      c = c ^ data[i]
    return c

class Robot:
    def connect(self, port, timeout):
        bauds = [9600,19200,38400,57600,115200]
        for baud in reversed(bauds):
            self.baud = baud

            # Reset the robot's connection
            #
            conn = lambda: Serial(
                  port = port
                , baudrate = baud
                , timeout = timeout
                , writeTimeout = timeout
            )
            self.port = conn()
            self.send_packet(CLOSE) # Try to close so we get a clean connection
            self.port.close()

            self.port = conn()
            self.port.flushInput()
            self.port.flushOutput()

            # Try to sync
            #
            try:
                info = "".join(chr(i) for i in self.sync()[4:])
                self.name,self.type,self.sub_type,_ = info.split('\0')
                break
            except:
                return False # no success

        # Send OPEN command to start up the robot
        #
        self.send_packet(OPEN)

        return True
    
    def __init__(self, port = 0, timeout = 1.0):
        if not self.connect(port, timeout):
            del self
            raise Exception("Failed to connect to Robot")

    def __del__(self):
        if self.port.isOpen():
            self.send_packet(CLOSE)
            self.port.close()

    def sync(self):
        SYNC_CMDS = (
            CMD_SYNC0
            , CMD_SYNC1
            , CMD_SYNC2
        )
        SYNC_READY = 3
        s = 0
        while s != SYNC_READY:
            self.send_packet(SYNC_CMDS[s])
            pkt = self.recv_packet()
            s = pkt[3]+1
        return pkt

    def send_packet(self, *data):
        pkt = [0xFA,0xFB,len(data)+2] + list(data)

        chk = calc_checksum(pkt)
        pkt.extend([(chk>>8),(chk&0xFF)])
        
        s = "".join(chr(y) for y in pkt)
        self.port.write(s)

    def recv_packet(self):
        data = [0,0]
        while not (data[0] == 0xFA and data[1] == 0xFB): # Header
            data[0] = data[1]
            c = self.port.read()
            assert c != '', "Read timeout"
            data[1] = ord(c)
        data.append(ord(self.port.read())) # Length of data + 2 (chk)

        for _ in range(data[2]):
            data.append(ord(self.port.read()))

        recv_crc = (data[-1]&0xFF) | (data[-2]<<8)
        crc = calc_checksum(data)
        assert recv_crc == crc, "Checksum failure"

        return data
