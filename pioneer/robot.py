import time
from math import *
from serial import *
from serial.tools.list_ports import comports
from soar.pioneer.arcos import *
from threading import Lock,Timer

MAX_RVEL = 0.5
MAX_VEL = 0.5

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

N_SONARS = 8
THETA_CONV_FACTOR = 2*pi/4096.0
unpack_unsigned = lambda l,h: l|(h<<8)
unpack = lambda l,h: (lambda d: -((d^0xFFFF)+1) if (d>>15) == 1 else d)(l|(h<<8))
def unpack_string(data,i): # String starts at index i
    stream = []
    for j in range(i,len(data)):
        if chr(data[j]) == '\0':
            break
        stream.append(chr(data[j]))
    return ''.join(stream)

class SIPPac:
    def __init__(self, data):
        self.size = len(data) # statistics
        assert len(data) == data[2]+3
        # Header
        assert data[0] == 0xFA
        assert data[1] == 0xFB
        # Type
        assert (data[3]&0xF0) == 0x30
        assert (lambda d: d == 2 or d == 3)(data[3]&0x0F)
        self.moving = (data[3]&0x0F) == 3
        # Odometry
        self.x = unpack(*data[4:6]) # mm
        self.y = unpack(*data[6:8]) # mm
        self.theta = unpack_unsigned(*data[8:10])*THETA_CONV_FACTOR # radians
        # 9-10 Left wheel velocity in mm/second
        # 11-12 Right wheel velocity in mm/second
        # Battery charge
        self.charge = data[14] # dV
        # 15-16 Stall/Bumper status
        # 17-18 NOT USED IN 6.01 (Servo)
        # 19-20 Status flags
        # 21 NOT USED IN 6.01 (Compass)
        # Sonars
        count = data[22]
        self.sonars = {
            data[i]: (lambda r: r if r < 5000 else None)(unpack_unsigned(*data[i+1:i+3]))
            for i in range(23,23+count*3,3)
        }
        # The rest is not important to 6.01

ANALOG_CONV_FACTOR = 10./1023.
class IOPac:
    def __init__(self, data):
        self.size = len(data) # Statistics
        assert len(data) == data[2]+3
        # Header
        assert data[0] == 0xFA
        assert data[1] == 0xFB
        # Type
        assert data[3] == 0xF0
        # 4 Number of digital inputs
        # 5   User
        # 6   Front bumpers
        # 7   Rear bumpers
        # 8   IR inputs
        # 9 Number of digital outputs
        # 10  User
        # Number of analog inputs
        count = data[11]
        # Analog inputs
        self.analogInputs = [unpack_unsigned(*data[i:i+2])*ANALOG_CONV_FACTOR
                             for i in range(12,12+count*2,2)] # V
        # Battery analog input

class CONFIGPac:
    def __init__(self, data):
        self.size = len(data) # Statistics
        assert len(data) == data[2]+3
        # Header
        assert data[0] == 0xFA
        assert data[1] == 0xFB
        # Type
        assert data[3] == 0x20
        # Robot type string
        i = 4
        self.type = unpack_string(data,i)
        i += len(self.type)+1
        # Subtype string
        self.subtype = unpack_string(data,i)
        i += len(self.subtype)+1
        # Serial number string
        self.sernum = unpack_string(data,i)
        i += len(self.sernum)+1
        # i we don't care about for 6.01 (antiquated)
        i += 1
        # Maximum maximum rotational velocity
        self.the_very_max_omega = unpack(*data[i:i+2])
        i += 2
        # Maximum maximum forward velocity
        self.the_very_max_v = unpack(*data[i:i+2])
        i += 2
        # i - i+5 we don't care
        i += 6
        # name given to the robot
        self.name = unpack_string(data,i)
        i += len(self.name)+1
        # i - i+22 we don't care about for 6.01
        i += 23
        # Maximum omega
        self.max_omega = unpack(*data[i:i+2])
        i += 2
        # Maximum v
        self.max_v = unpack(*data[i:i+2])
        i += 2
        # We don't care about the rest for 6.01

class Robot:
    def __init__(self, port = 0, timeout = 1.0):
        self.serial_lock = Lock()
        if isinstance(port,(int)):
            # Find the port
            #
            ports = [p for p,desc,_ in comports() if 'PL2303' in desc]
            port = ports[port]
        self.port = port
        self.timeout = timeout
        if not self.connect(port, timeout):
            del self
            raise Exception("Failed to connect to Robot")

        self.active = True
        # Start pulsing timer
        # This timer gets reset on every command sent.
        #
        self.command_lock = Lock()
        self.pulse_timer = Timer(1.0, lambda: self.command(PULSE))
        self.pulse_timer.start() # 2.0 seconds is the default, 1.0 to be safe

        # Send OPEN/PULSE command to start up the robot
        #
        self.command(OPEN)
        self.command(PULSE)
        self.command(ENABLE,1) # Enable motors
        self.recv_packet()

        # Send CONFIG to get back the operational parameters of the robot.
        #
        self.command(CONFIG)
        d = self.recv_packet()
        while d[3] != 0x20:
            d = self.recv_packet()
        self.config = CONFIGPac(d)

        # Send IOREQUEST command to start IO packet streaming
        #
        self.command(IOREQUEST,2)

    # Connect to robot
    #
    def connect(self, port, timeout):
        bauds = [9600,19200,38400,57600,115200]
        conn = lambda baud: Serial(
            port = port,
            baudrate = baud,
            timeout = timeout,
            writeTimeout = timeout,
        )
        for baud in reversed(bauds):
            self.baud = baud
            # Reset the robot's connection
            #
            self.ser = conn(baud)
            self.send_packet(RESET) # Try to close so we get a clean connection
            self.ser.close()

            self.ser = conn(baud)
            self.ser.flushInput()
            self.ser.flushOutput()

            # Try to sync
            #
            try:
                info = "".join(chr(i) for i in self.sync()[4:])
                self.name,self.type,self.sub_type,_ = info.split('\0')
                break
            except:
                return False # no success
        return True

    # Initial Sync
    #
    def sync(self):
        SYNC_CMDS = (
            SYNC0,
            SYNC1,
            SYNC2,
        )
        SYNC_READY = 3
        s = 0
        while s != SYNC_READY:
            self.send_packet(SYNC_CMDS[s])
            pkt = self.recv_packet()
            s = pkt[3]+1
        return pkt

    def __del__(self):
        with self.command_lock:
            self.active = False
            self.pulse_timer.cancel()
        if self.ser.isOpen():
            self.send_packet(CLOSE) # To bypass the lock
            self.ser.close()

    # Call if using threads
    #
    terminate = __del__

    # Send a packet to the robot
    # Thread-safe
    #
    def send_packet(self, *data):
        data = [(d if isinstance(d,int) else ord(d)) for d in data]
        pkt = [0xFA,0xFB,len(data)+2] + data

        chk = calc_checksum(pkt)
        pkt.extend([(chk>>8),(chk&0xFF)])

        with self.serial_lock:
            self.ser.write(bytearray(pkt))

    # Receives packet from robot, and checks the checksum
    # ONLY ONE THREAD SHOULD USE THIS FUNCTION AT A TIME
    #
    def recv_packet(self):
        data = [0,0]
        while not (data[0] == 0xFA and data[1] == 0xFB): # Header
            data[0] = data[1]
            c = self.ser.read()
            assert len(c) != 0, "Read timeout"
            data[1] = ord(c)
        data.append(ord(self.ser.read())) # Length of data + 2 (chk)

        for _ in range(data[2]):
            data.append(ord(self.ser.read()))

        recv_crc = (data[-1]&0xFF) | (data[-2]<<8)
        crc = calc_checksum(data)
        assert recv_crc == crc, "Checksum failure"

        return data

    # Send a command to the robot
    # Thread-safe
    #
    def command(self, cmd, data = None):
        assert cmd in commands
        c = commands[cmd]
        if data is not None:
            c.set(data)
        with self.command_lock:
            if not self.active:
                return
            try:
                self.send_packet(*c)
            finally:
                # Still want to pulse
                #
                self.pulse_timer.cancel()
                self.pulse_timer = Timer(1.0,lambda: self.command(PULSE))
                self.pulse_timer.start()

    def receive(self, io_handler, sip_handler):
        max_timeouts = 10 # Arbitrary
        timeout_count = 0
        while self.active:
            try:
                d = self.recv_packet()
                timeout_count = 0
                if d[3] == 0xF0:
                    io_handler(IOPac(d))
                elif (d[3]&0xF0) == 0x30:
                    sip_handler(SIPPac(d))
                elif (d[3] == 0x20):
                    self.config = CONFIGPac(d)
                else:
                    raise Exception("Unknown message type from Robot %d" % d[3])
            except AssertionError as e:
                # We're ignoring checksum failures
                #
                if str(e) == "Read timeout":
                    timeout_count += 1
                    # If we timed out multiple times, we want to try to regain control
                    #
                    if timeout_count >= max_timeouts:
                        self.__init__(self.port,self.timeout)
