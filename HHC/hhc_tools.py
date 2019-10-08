#This is the main program file for the HHC-Tools GUI#

#import background python modules#
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

#-------------------------#
m=tk.Tk()                            # Create instance for master window     
m.title("HHC Tools")                 # Add a title for master window
tabControl = tk.ttk.Notebook(m)      # Create Tab Control using ttk notebook

#Overtopping Tool Begin#

sys.path.insert(1,'.\overtopping\eurotop')
#import overtopping as ot
overtopping = ttk.Frame(tabControl)            # Create overtopping tab instance 
tabControl.add(overtopping, text='overtopping')      # Add the title to the tab 
tabControl.pack(expand=1, fill="both")   # Pack to make visible  
button = tk.Button(overtopping, text='Stop', width=25, command=m.destroy) # adding button to overtopping tab
button.pack()

#Overtopping Tool end#

#Rainfall Tool Begin#

sys.path.insert(2,'.\precipitation\predicted')
#import rainfall_pred as pcip
rainfall = ttk.Frame(tabControl)            # Create rainfall tab instance 
tabControl.add(rainfall, text='rainfall')      # Add the tab
tabControl.pack(expand=1, fill="both")  # Pack to make visible
button2 = tk.Button(rainfall, text='Rainfall', width=25, command=m.destroy) # adding button to rainfall tab
button2.pack()

#Rainfall Tool end#

m.mainloop() # Start GUI
