#!/usr/bin/python

import serial

from xnclient.helpers import hextobytes, Exchange

ser = serial.Serial('/dev/cu.usbserial-AH03FLFP', 115200)
while True:
#for x in range(10):
    s = ser.readline()
    v = hextobytes(s)
    if v is not None:
        e = Exchange(v)
        print(e)