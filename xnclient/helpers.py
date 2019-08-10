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

    def decode_dev_basic_request(self):
        return {
            0x10 : 'D  Request for service mode results',         # 2.2.10
            0x21 : 'D  Command station software version request', # 2.2.14
            0x24 : 'D  Command station status request',           # 2.2.15
            0x80 : 'D  Stop operations request (emergency off)',  # 2.2.3
            0x81 : 'D  Resume operations request'                 # 2.2.2
        }.get(self.data[2], 'Undecoded device basic request') 

    def decode_dev_request(self):
        if self.__header() == 0x21:
            return self.decode_dev_basic_request()
        return {
            0x20 : 'D  Acknowledgement response'                  # 2.2.1
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
                return 'CS Software version (XBus V1 and V2)'
            return 'CS Command station status'
        if self.__header() == 0x63:
            if self.data[2] == 0x10:
                return 'CS Service mode response (register and paged)'
            if self.data[2] == 0x14:
                return 'CS Service mode response (direct cv)'
            return 'CS Software version (XpressNet)'
        return {
            0x81 : 'CS Emergency stop'
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
