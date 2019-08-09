#
# Helper functions and utility classes to process and encapsulate
# XpressNet data.
#
# Aushacker
# 9 Aug 2019
#

import datetime

# Convert a single hex character to its decimal equivalent
def hextoint(c):
    return int(c, 16)

# Convert a hex string to a list of integers (bytes)
def hextobytes(str):
    # Bytes require pairs of hex digits
    # str should be an even number of chars followed by an LF
    if (len(str) == 1) | (len(str) % 2 == 0):
        return None

    # Convert two characters at a time to their decimal equivalent
    result = []
    for i in range(0, len(str) - 1, 2):
        result.append(int(str[i:i+2], 16))
    return result

#
# Captures a single XpressNet command or command/response
#
class Exchange:

    def __init__(self, data):
        self.datetime = datetime.datetime.now()
        self.data = data

    def __str__(self):
        return "{} {} - {}".format(self.datetime.time().isoformat(), self.address(), self.shortdesc())

    def address(self):
        return self.data[0] & 0x1f

    def shortdesc(self):
        callbyte = self.data[0] & 0x60
        if callbyte == 0x40:
            if len(self.data) == 1:
                return 'Normal Enquiry'
            else:
                return 'Undecoded device response'
        if callbyte == 0x00:
            return 'Request Ack from Device'
        return 'Unknown'