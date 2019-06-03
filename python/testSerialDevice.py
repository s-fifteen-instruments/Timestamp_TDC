# from qitdevices.usb_counter import *
import usbcount_class as UC
import numpy as np
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import serial
from serial import tools

print(serial.tools.list_ports.comports(include_links=False))
serial.tools.