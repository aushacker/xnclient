#!/usr/local/bin/python3

#import types

import serial

from xnclient.helpers import Exchange

ser = serial.Serial('/dev/cu.usbserial-AH03FLFP', 115200)

# Ensure synchronisation
ser.readline()
ser.readline()

while True:
#for x in range(10):
    s = ser.readline()
    # Ugly hack to get around odd typing problems between v2 and v3
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    try:
        e = Exchange.parse(s)
        if (e.address == 1 or e.address == 0) and not e.isenquiry:
            print(e)
            print(e.data.hex())
    except ValueError as err:
        print(err)
