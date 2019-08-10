#!/usr/bin/python

import serial

from xnclient.helpers import hex_to_bytes, Exchange

ser = serial.Serial('/dev/cu.usbserial-AH03FLFP', 115200)
while True:
#for x in range(10):
    s = ser.readline()
    v = hex_to_bytes(s)
    if v is not None:
        e = Exchange(v)
        if e.address == 1:
            print(e)