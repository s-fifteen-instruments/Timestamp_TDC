from __future__ import print_function  # Needed for compatibility with Py2
"""
Author: Alessandro Cere
Created: 2017.10.16

Description:
General serial device
"""
import serial
import time

from serial import SerialException


ser = serial.Serial('COM3')  # open serial port
print(ser.name)         # check which port was really used
ser.write(('MODE?;' + '\n').encode())
time.sleep(1)
Buffer_length = ser.in_waiting
print(str(Buffer_length) + " Bytes Recorded")
print (ser.read(Buffer_length))


