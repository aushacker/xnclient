#
# Helper functions and utility classes to process and encapsulate
# XpressNet data.
#
# Aushacker
# 9 Aug 2019
#

import datetime

#
# Captures a single XpressNet command or command/response
#
class Exchange:
    CMD_MASK = 0x60        # Call byte command mask

    @staticmethod
    def parse(s):
        data = bytearray.fromhex(s)
        if len(data) == 0:
            raise ValueError('Empty hex string')
        return Exchange(data)

    def __init__(self, data):
        self.dt = datetime.datetime.now()
        self.data = data
        self.validate()
        self.address = data[0] & 0x1f
        self.isenquiry = len(data) == 1 and self.__cmd() == 0x40 

    def __str__(self):
        return "{} {} - {}".format(self.dt.time().isoformat(), self.address, self.short_desc())

    # Extract the command bits from the call byte
    def __cmd(self):
        return self.data[0] & self.CMD_MASK

    def __decode_dev_basic_request(self):
        return {
            0x10 : 'D  Request for service mode results',         # 2.2.10
            0x21 : 'D  Command station software version request', # 2.2.14
            0x24 : 'D  Command station status request',           # 2.2.15
            0x80 : 'D  Stop operations request (emergency off)',  # 2.2.3
            0x81 : 'D  Resume operations request'                 # 2.2.2
        }.get(self.data[2], 'Undecoded device basic request') 

    def __decode_dev_loco_ops_request(self):
        return {
            0x10 : 'D  Locomotive speed and direction 14 (XpressNet)', # 2.2.20.3
            0x11 : 'D  Locomotive speed and direction 27 (XpressNet)', # 2.2.20.3
            0x12 : 'D  Locomotive speed and direction 28 (XpressNet)', # 2.2.20.3
            0x13 : 'D  Locomotive speed and direction 128 (XpressNet)' # 2.2.20.3
        }.get(self.data[2], 'Undecoded device loco ops request') 
    
    def decode_dev_request(self):
        if self.__header() == 0x21:
            return self.__decode_dev_basic_request()
        if self.__header() == 0xE4:
            return self.__decode_dev_loco_ops_request()
        return {
            0x20 : 'D  Acknowledgement response',                 # 2.2.1
            0x42 : 'D  Accessory decoder information request',    # 2.2.17
            0x52 : 'D  Accessory decoder operation request',      # 2.2.18
            0x80 : 'D  Stop all locomotives request (emergency stop)', # 2.2.4
            0x91 : 'D  Emergency stop a locomotive (V1 and V2)',       # 2.2.5.1
            0x92 : 'D  Emergency stop a locomotive (XpressNet)',       # 2.2.5.2
            0xA1 : 'D  Locomotive information request (V1)',           # 2.2.19.1
            0xA2 : 'D  Locomotive information request (V1 and V2)',    # 2.2.19.2
            0xB3 : 'D  Locomotive operations (V1)',                    # 2.2.20.1
            0xB4 : 'D  Locomotive operations (V2)'                     # 2.2.20.2
        }.get(self.data[1], 'Undecoded device request') 

    def __decode_cs_basics(self):
        return {
            0x00 : 'CS Track power off',                          # 2.1.4.2
            0x01 : 'CS Normal operation resumed',                 # 2.1.4.1
            0x02 : 'CS Service mode entry',                       # 2.1.4.4
            0x11 : 'CS Programming info (command station ready)', # 2.1.5.4
            0x12 : 'CS Programming info (short circuit)',         # 2.1.5.1
            0x13 : 'CS Programming info (data byte not found)',   # 2.1.5.2
            0x1F : 'CS Programming info (command station busy)',  # 2.1.5.3
            0x80 : 'CS Transfer errors',                          # 2.1.8
            0x81 : 'CS Command station busy',                     # 2.1.9
            0x82 : 'CS Unsupported instruction'                   # 2.1.10
        }.get(self.data[2], 'Undecoded cs basic')

    def decode_cs_request(self):
        if self.__header() == 0x61:
            return self.__decode_cs_basics()
        if self.__header() == 0x62:
            if self.data[2] == 0x21:
                return 'CS Software version (XBus V1 and V2)'     # 2.1.6.1
            return 'CS Command station status response'           # 2.1.7
        if self.__header() == 0x63:
            if self.data[2] == 0x10:
                return 'CS Service mode response (register and paged)' # 2.1.5.5
            if self.data[2] == 0x14:
                return 'CS Service mode response (direct cv)'     # 2.1.5.6
            return 'CS Software version (XpressNet)'              # 2.1.6.2
        return {
            0x42 : 'CS Accessory decoder information response',   # 2.1.11
            0x81 : 'CS Emergency stop',                           # 2.1.4.3
            0x83 : 'CS Locomotive is available for operation (V1)',          # 2.1.12.1
            0x84 : 'CS Locomotive is available for operation (V2)',          # 2.1.13.1
            0xA3 : 'CS Locomotive is being operated by another device (V1)', # 2.1.12.2
            0xA4 : 'CS Locomotive is being operated by another device (V2)'  # 2.1.13.2
        }.get(self.data[1], 'Undecoded command station request 0x{:X}'.format(self.data[1])) 

    def __header(self):
        return self.data[1]

    def short_desc(self):
        cmd = self.__cmd()
        if cmd == 0x00:
            return 'Request Ack from Device'                      # 2.1.2
        if cmd == 0x20:
            if self.data[0] == 0xA0:
                return 'CS Feedback broadcast'                    # 2.1.4.5
            return 'TBD (Future Command)'                         # 2.1.3
        if cmd == 0x40:
            if self.isenquiry:
                return 'CS Normal Enquiry'                        # 2.1.1
            else:
                # device has responded
                return self.decode_dev_request()
        # cmd must be 0x60 i.e. most command station requests and response
        return self.decode_cs_request()

    def validate(self):
        if len(self.data) == 1:
            self.isvalid = True
        else:
            if len(self.data) == 2:
                self.isvalid = False
            else:
                checksum = 0
                for i in range(1, len(self.data) - 1):
                    checksum = checksum ^ self.data[i]
                self.isvalid = checksum == self.data[-1]
