#
# Helper functions and utility classes to process and encapsulate
# XpressNet data.
#
# Aushacker
# 9 Aug 2019
#

import datetime

# Convert a single hex character to its decimal equivalent
def hex_to_int(c):
    try:
        return int(c, 16)
    except ValueError:
        return None

# Convert a hex string to a list of integers (bytes)
def hex_to_bytes(str):
    # Bytes require pairs of hex digits
    # str should be an even number of chars followed by an LF
    if (len(str) == 1) | (len(str) % 2 == 0):
        return None

    # Convert two characters at a time to their decimal equivalent
    result = []
    for i in range(0, len(str) - 1, 2):
        hi = hex_to_int(str[i])
        low = hex_to_int(str[i+1])
        if hi is not None and low is not None:
            result.append((hi << 4) + low)
    return result

#
# Captures a single XpressNet command or command/response
#
class Exchange:

    @staticmethod
    def parse(str):
        return Exchange(hex_to_bytes(str))

    def __init__(self, data):
        self.datetime = datetime.datetime.now()
        self.data = data
        self.validate()
        self.address = data[0] & 0x1f

    def __str__(self):
        return "{} {} - {}".format(self.datetime.time().isoformat(), self.address, self.short_desc())

    def decode_dev_basic_request(self):
        return {
            0x10 : 'D  Request for service mode results',
            0x21 : 'D  Command station software version request',
            0x24 : 'D  Command station status request',
            0x80 : 'D  Stop operations request (emergency off)',
            0x81 : 'D  Resume operations request'
    }.get(self.data[2], 'Undecoded device basic request') 

    def decode_dev_request(self):
        if self.data[1] == 0x21:
            return self.decode_dev_basic_request()
        return {
            0x20 : 'D  Acknowledgement response'                # 2.2.1
        }.get(self.data[1], 'Undecoded device request') 
    
    def decode_cs_request(self):
        return {
            0x61 : 'CS Transfer errors',
            0x62 : 'CS Software version (XBus V1 and V2)',
            0x63 : 'CS Software version (XpressNet)',
            0x80 : ''
        }.get(self.data[1], 'Undecoded command station request 0x{:X}'.format(self.data[1])) 
    
    def short_desc(self):
        callbyte = self.data[0] & 0x60
        if callbyte == 0x00:
            return 'Request Ack from Device'
        if callbyte == 0x20:
            return 'CS Illegal call byte - not defined by 2003 standard'
        if callbyte == 0x40:
            if len(self.data) == 1:
                return 'CS Normal Enquiry'
            else:
                return self.decode_dev_request()
        # callbyte must be 0x60 i.e. most command station requests and response
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
