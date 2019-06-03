"""
Script to help using the USBcounter as timestamp device. Modded from QO Lab Script, C package dependencies removed from this package,
due to Windows compatability issue.
"""
# Origin: QO Lab NUS, Alessandro Cere
# Current Author: Chin Chean Lim
# Modified Date: 06/03/2019

import time
import csv
from numpy import int_

import serial_device


class FPGA_counter(serial_device.SerialDevice):

    def __init__(self, device: object = None) -> object:
        if device is None:
            try:
                device = 'COM4'#'/dev/ttyS2'   # set correct serial address, note the difference in Windows and Unix environment.
                # In Windows it is usually COM(x), in MAC /dev/tty.usbmodemTDC1..., in Ubuntu /dev/serial/by-id/usb-S-Fifteen_Instruments.......
                # In Linux, the path changes quite often and it is easier to just check the path by id, note line above
                # Please update this before you do anything.
            except IndexError:
                print('No suitable device found!')
            self._device = device
            serial_device.SerialDevice.__init__(self, device)
            self.timeout = .1  # necessary for python2
        # check what mode is the device in
        self.mode
        self.int_time

        #
        # # g2 program path, not used in current package. CCLim
        #  g2path = pathlib.Path.cwd()/'g2'
        #  g2path = g2path.absolute()
        #  g2path = g2path.as_posix()
        # #print(type(g2path))
        #  self._g2_prog = g2path
        #  if not exists(self._g2_prog):
        #      print('No g2 program installed!')
        #
        # # timestamp readevents program path ,not used in current package. CCLim
        # self._prog = pathlib.Path.cwd() / 'usbcntfpga'/'apps'/'readevents4.exe'
        # self._prog = self._prog.absolute()
        # self._prog = self._prog.as_posix()
        # #print((self._prog))
        # if not exists(self._prog):
        #     print('No readevents4 program installed!')
        #
        # # default set of parameters
        # self._t_min = 700
        # self._t_max = 1700
        # self._acc_t_min = 100
        # self._acc_t_max = 600
        # self._binwidth = 16
        # self._maxbins = 500

    @property
    def mode(self):
        self._mode = int(self._getresponse('MODE?')[0].decode().strip())
        return self._mode

    @mode.setter
    def mode(self, value):
        if value.lower() == 'singles':
            self.write(b'singles\n')
            self._mode = 0
        if value.lower() == 'pairs':
            self._mode = 1
            self.write(b'pairs\n')
        if value.lower() == 'timestamp':
            self._mode = 3
            self.write(b'timestamp\n')


    @property
    def level(self):
        """ Set the kind of pulses to count"""
        return self._getresponse('LEVEL?')[0].decode().strip()

    @level.setter
    def level(self, value):
        if value.lower() == 'nim':
            self.write(b'NIM\n')
        elif value.lower() == 'ttl':
            self.write(b'TTL\n')
        else:
            print('Acceptable input is either \'TTL\' or \'NIM\'')

    @property
    def clock(self):
        """ Choice of clock"""
        return self._getresponse('REFCLK?')[0].decode().strip()

    @clock.setter
    def clock(self, value):
        self.write('REFCLK {}\n'.format(value).encode())

    """ Functions for the counter mode"""
    @property
    def int_time(self):
        self._int_time = int(self._getresponse('TIME?')[0].decode().strip())
        return self._int_time

    @int_time.setter
    def int_time(self, value):
        self.write('TIME {}\n'.format(int(value)).encode())

    @property
    def counts(self):
        """
        Return the actual number of count read from the device buffer.
        :return: a three-element array of int
        """
        if self._mode == 3:
            print('The FPGA is set to timestamp mode!')
            return -1
        self.write('counts?\n'.encode())
        t_start = time.time()
        while time.time() - t_start < self._int_time * 1.2:
            if self.in_waiting != 0:
                return int_(self.readline().split())
        print('A timeout occured!\n')
        print(self.readlines())

#     """ Functions for the timestamp mode"""
# # Calls C-Script in readevents.c, this feature is current disabled. This does not work in Windows, yet...
#      def _timestamp_acq(self, t_acq, out_file_buffer):
#          """ Write the binary output to a buffer"""
#          if self._mode != 3:
#              print('The FPGA is set into counting mode!')
#              return -1
#          proc = subprocess.Popen([self._prog, '-U', self._device, '-a1', '-X'],stdout=out_file_buffer, stderr=subprocess.PIPE)
#          time.sleep(t_acq)
#          proc.kill()
 #       return proc.communicate()[1]

# Timestamp function that is called within Python and parsed in the same environment rather than relying on existing C-script.
# Writes it to a .dat file in CSV format.

# Sends serial command, assuming TTL signal.
    def timestamp_acq_python(self,t_int,signal):
        t_sleep = int(t_int) + 10
        self.timestamp = self._getresponseTime('*RST;'+signal+';TIME'+str(t_int)+';TIMESTAMP;COUNTS?' , t_sleep )
        bytes_hex = self.timestamp[::-1].hex()
       # print(bytes_hex)
        bin_flip = (bin(int(bytes_hex, 16)))[2:]
        split_bin = [bin_flip[i:i + 32] for i in range(0, len(bin_flip), 32)]
        timestamp_int = []
        pattern = []


# Combines lists into a table for easy processing.
        for i in range(len(split_bin)):
            timestamp_int.append(int(split_bin[i][:27], 2) * 2)
            pattern.append(split_bin[i][27:])
#        self._table = zip(pattern, timestamp_int)
#        self._table.append(zip(pattern, timestamp_int))
# Writes in CSV format.
        return timestamp_int,pattern

    # def timestamp_single_acq_python(self, t_int, signal):
    #     t_sleep = int(t_int) + 10
    #     self.timestamp = self._getresponseTime('*RST;' + signal + ';TIME' + str(t_int) + ';TIMESTAMP;COUNTS?',
    #                                                t_sleep)
    #     bytes_hex = self.timestamp[::-1].hex()
    #         # print(bytes_hex)
    #     bin_flip = (bin(int(bytes_hex, 16)))[2:]
    #     split_bin = [bin_flip[i:i + 32] for i in range(0, len(bin_flip), 32)]
    #     timestamp_int = []
    #     pattern = []
    #
    #         # Combines lists into a table for easy processing.
    #     for i in range(len(split_bin)):
    #             timestamp_int.append(int(split_bin[i][:27], 2) * 2)
    #             pattern.append(split_bin[i][27:])
    #     self._table = zip(pattern, timestamp_int)
    #
    #     # Writes in CSV format.
    #     with open('test.dat', 'w') as csvFile:
    #       writer = csv.writer(csvFile, delimiter=' ')
    #       writer.writerows(self._table)
    #       csvFile.close()
    #     return self._table

    # @property
    # def maxbins(self):
    #     """ Set the number of bins for the g2"""
    #     return self._maxbins
    #
    # @maxbins.setter
    # def maxbins(self, value):
    #     self._maxbins = int(value)
    #
    # @property
    # def binwidth(self):
    #     """ set the bin size for the g2"""
    #     return self._binwidth
    #
    # @binwidth.setter
    # def binwidth(self, value):
    #     self._binwidth = int(value)
    #
    # def _g2_from_raw(self, in_file, out_file, maxbins=None, binwidth=None):
    #     if maxbins is None:
    #         maxbins = self._maxbins
    #     if binwidth is None:
    #         binwidth = self._binwidth
    #
    #     proc = subprocess.Popen([self._g2_prog, '-m', str(maxbins),
    #                              '-t', str(binwidth),
    #                              '-o', out_file],
    #                             stderr=subprocess.PIPE,
    #                             stdin=subprocess.PIPE)
    #     outs, errs = proc.communicate(in_file)
    #     return errs
    #
    # def g2_from_raw(self, in_file, out_file, maxbins=None, binwidth=None):
    #     with open(in_file, 'rb') as in_f:
    #         self._g2_from_raw(in_f.read(), out_file, maxbins, binwidth)
    #
    # @property
    # def coincidence_range(self):
    #     return [self._t_min, self._t_max]
    #
    # @coincidence_range.setter
    # def coincidence_range(self, value):
    #     if len(value) != 2:
    #         print('Range should be an array [t_min, t_max]')
    #     else:
    #         self._t_min, self._t_max = value
    #
    # @property
    # def acc_range(self):
    #     return [self._acc_t_min, self._acc_t_max]
    #
    # @acc_range.setter
    # def acc_range(self, value):
    #     if len(value) != 2:
    #         print('Range should be an array [t_min, t_max]')
    #     else:
    #         self._acc_t_min, self._acc_t_max = value
    #
    # def count_g2(self, t_acq, t_min=None, t_max=None,
    #              acc_t_min=None, acc_t_max=None):
    #     """Returns pairs and singles counts from usbcounter timestamp data.
    #
    #     Computes g2 between channels 1 and 2 of timestamp
    #     and sum the coincidences within specified window
    #
    #     :param t_acq: acquisition time in seconds
    #     :type t_acq: float
    #     :param t_min: g2 peak left boundary in nanoseconds
    #     :type t_min: int
    #     :param t_max: g2 peak right boundary in nanoseconds
    #     :type t_max: int
    #     :param acc_t_min: accidental counting left boundary in nanoseconds
    #     :type acc_t_min: int
    #     :param acc_t_max: accidental counting right boundary in nanoseconds
    #     :type acc_t_max: int
    #     :returns: Ch1 counts, Ch2 counts, Pairs, estimated accidentals,
    #               actual acq time
    #     :rtype: {int, int, int, float, float}
    #     """
    #     if t_min is None:
    #         t_min = self._t_min
    #     if t_max is None:
    #         t_max = self._t_max
    #     if acc_t_min is None:
    #         acc_t_min = self._acc_t_min
    #     if acc_t_max is None:
    #         acc_t_max = self._acc_t_max
    #
    #     # open a temporary file to store the processed g2
    #     with NamedTemporaryFile() as f_raw, NamedTemporaryFile() as f_dat:
    #         e = self._timestamp_acq(t_acq, f_raw)
    #         if e == -1:
    #             return -1
    #         if f_raw.tell() == 0:
    #             print('Acquired an empty file!')
    #             return {'channel1': 0, 'channel2': 0, 'pairs': 0,
    #                     'accidentals': 0, 'total_time': 0}, [], []
    #         f_raw.seek(0)
    #         self._g2_from_raw(f_raw.read(), f_dat.name)
    #         metadata = [line.decode() for line, _ in zip(f_dat, range(2))]
    #         dt, g2 = [col for col in genfromtxt(f_dat.name, usecols=(0, 1)).T]
    #
    #     # get the effective acquisition time from the processed g2 metadata
    #     time_total = int(metadata[1].replace(',', ' ').split()[2]) * 1e-9 / 8
    #     # get the single counts from the processed g2 metadata
    #     s1, s2 = [int(metadata[0].replace(',', ' ').split()[i])
    #               for i
    #               in (2, 4)]
    #
    #     # calculates the pairs from the processed g2
    #     pairs = sum(g2[(dt > t_min) & (dt < t_max)])
    #
    #     # estimates accidentals for the integration time-window
    #     acc = sum(g2[(dt > acc_t_min) & (dt < acc_t_max)]) * \
    #         (t_max - t_min) / (acc_t_max - acc_t_min)
    #     return {'channel1': s1, 'channel2': s2, 'pairs': pairs,
    #             'accidentals': acc, 'total_time': time_total}, dt, g2
    #
    #
