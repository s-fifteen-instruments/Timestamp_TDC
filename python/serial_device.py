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


class SerialDevice(serial.Serial):
    """
    The usb device is seen as an object through this class,
    inherited from the generic serial one.
    """

    def __init__(self, device_path=None, timeout=.2):
        """
        Initializes the USB device.
        It requires the full path to the serial device as arguments
        """
        try:
            serial.Serial.__init__(self, device_path, timeout)
            self.timeout = timeout
            self._reset_buffers()
        except SerialException:
            print('Connection failed')

    def _reset_buffers(self):
        self.reset_input_buffer()
        self.reset_output_buffer()

    def _getresponse(self, cmd):
        """
        function to send commands and read the response of the device.
        it contains a workaroud for the 'Unknown command' problem.
        Make sure that the command implies a reply, otherwise...

        :param command: string containing the command.
        :return: the reply of the device,
        only the first line and stripped of decorations
        """
        self._reset_buffers()
        self.write((cmd + '\n').encode())
        return self.readlines()

    def _getresponseTime(self, cmd, t_sleep):
        """
        function to send commands and read the response of the device.
        it contains a workaroud for the 'Unknown command' problem.
        Make sure that the command implies a reply, otherwise...

        :param command: string containing the command.
        :return: the reply of the device,
        only the first line and stripped of decorations
        """
        self._reset_buffers()
        self.write((cmd + '\n').encode())
        #self._reset_buffers()
        time.sleep(t_sleep/1000)
        Buffer_length = self.in_waiting
        print(str(Buffer_length) + " Bytes Recorded")
        return self.read(Buffer_length)

    def help(self):
        """
        Prints device help to the screen
        """
        ([print(x.decode().strip()) for x in self._getresponse('help')])
