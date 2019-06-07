

"""
This is a script that provides a simple GUI to take snapshots of the signal events within the integration window.

Author: Lim Chin Chean 05/2019 Modded from QO Lab Script

Note: the data rate for USB read is <125 Mbps, take that into account when you are dealing with runs that has very high count rates!
     There is some room for improvement in terms of data rate as USB 2.0 protocol should be faster than 125 Mbps, work in progress.
"""

from tkinter import *
from tkinter import ttk
import csv
import usbcount_class as UC
import numpy as np

# sets the size of the font for the counters
ft_size = 42
# sets the trigger type of input signal, PLEASE CHECK THIS. 'nim' or 'ttl'
signal_type='ttl'
pattern_loop = []
timestamp_loop = []
# set path of CSV file for timestamp data. Note that the file gets overwritten when you restart the parsing.
path = 'test1.dat'

# single shot timestamp within integration time.
def change_snap_f(*args):
    loop_flag.set(True)
    print("Integration time:" + timer_00.get() + "ms")
    [timestamp,pattern] = counter.timestamp_acq_python(timer_00.get(),signal_type)
    table = zip(pattern, timestamp)
    with open(path, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerows(table)
        csvFile.close()

# Function to start the parsing and concatenating timestamp lists from looped snapshots.
def start_f(*args):
    loop_flag.set(True)
    while loop_flag.get():
        [timestamp,pattern] = (counter.timestamp_acq_python(timer_00.get(),signal_type))
        pattern_loop.extend(pattern)
        timestamp_loop.extend(timestamp)
        root.update()

# Stop querying the timestamp function, writes collected parsed timestamps into csv file.
def stop_f(*args):
    loop_flag.set(False)
    table = zip(pattern_loop, timestamp_loop)
    with open(path, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=' ')
        writer.writerows(table)
        csvFile.close()
    pattern_loop.clear()
    timestamp_loop.clear()

"""Setting up the main window"""
root = Tk()
root.title("USB counter")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

counter = UC.FPGA_counter()
counter.mode = 'timestamp'
loop_flag = BooleanVar()
loop_flag.set(False)


timer_00 = StringVar()


# buttons
ttk.Button(mainframe, text="Start", command=start_f).grid(
    column=1, row=1, sticky=W)
ttk.Button(mainframe, text="Stop", command=stop_f).grid(
    column=2, row=1, sticky=W)
ttk.Button(mainframe, text="Timestamp Snapshot", command=change_snap_f).grid(
    column=4, row=6, sticky=W)

# controls
time_entry = Spinbox(mainframe, width=7, from_=0.1, to=5,
                     increment=.1, textvariable=timer_00)
time_entry.grid(column=5, row=6, sticky=(W, E))
timer_00.set(400)
print(timer_00.get())

# title
ttk.Label(mainframe, text='Timestamp Loop + Snapshot',
          font=("Helvetica", 22)).grid(column=4, row=1, sticky=(W, E))


# labels
ttk.Label(mainframe, text='Gate Time',
          font=("Helvetica", 14)).grid(column=4, row=6, sticky=(E))


# padding the space surrounding all the widgets
for child in mainframe.winfo_children():
    child.grid_configure(padx=10, pady=10)

# finally we run it!
root.mainloop()
