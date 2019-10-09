#!/usr/bin/env python
# coding: utf-8

# ## EurOtop Overtopping calculations
# Overtopping calculations as described in the EurOtop Manual on wave overtopping of sea defences and related structures (Second Edition 2018; www.overtopping-manual.com).
# 
# With this interface, you will be able to load an input Excel file, specify number of Monte Carlo simulations (default 20,000), and specify the name and location of the output figures and Excel file detailing the design heights for each structure.
# 
# EurOtop, 2018. Manual on wave overtopping of sea defences and related structures. An overtopping manual largely based on European research, but for worldwide application. Van der Meer, J.W., Allsop, N.W.H., Bruce, T., De Rouck, J., Kortenhaus, A., Pullen, T., Schüttrumpf, H., Troch, P. and Zanuttigh, B., www.overtopping-manual.com.

# In[1]:


# Import necessary packages
import numpy as np
from pandas import DataFrame#, read_csv
import matplotlib.pyplot as plt
import pandas as pd 
from scipy.stats import norm
# Import libraries
import ipywidgets as widgets
from ipywidgets.widgets import *
from IPython.display import display
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk # pip install_pillow
import warnings
import tkinter.messagebox
import time


# ## Load Excel file and set parameters
# Load file with levee or wall information (.xls or .csv).

# In[9]:


# Make GUI
root = Tk()
root.geometry("500x600")
root.title("Overtopping Calculation")



# Add image to GUI
# imge = Image.open("C:/Users/b2edhdf9/Desktop/MATLAB_to_Python/overtopping-manual-eurotop-image-01.jpg")
# photo = ImageTk.PhotoImage(imge)
# lab = Label(image=photo)
# lab.pack()

# Define type of input
var_method = StringVar()
var_sim = StringVar()
var_in = StringVar()
var_out = StringVar()
def select_in():
    global file_in
    file_in = var_in.get()
    file_in = filedialog.askopenfilename(initialdir = "/",
                                     title = "Select file",
                                     filetypes = (("XLS files","*.xls"),("CSV files","*.csv"),("all files","*.*")))
    return file_in

    #if file_in:
    #    print(f"Input file is {file_in}")
    print(f"Input file is {file_in}")
    #else:
    #    warnings.warn('Please select an input file')
def select_out():
    global calc_method
    calc_method = var_method.get() # calculation method
    global file_out
    if calc_method == 'Mean Value':
        file_out =  filedialog.asksaveasfilename(initialdir = "/", 
                                                 initialfile = "100YR_Future2_Eurotop_MeanValue",
                                                 title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        print(f"Output file is {file_out}")
    elif calc_method == 'Design & Assessment':
        file_out =  filedialog.asksaveasfilename(initialdir = "/", 
                                                 initialfile = "100YR_Future2_Eurotop_DesignAssess", defaultextension = ".csv",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        print(f"Output file is {file_out}")
    else:
        tkinter.messagebox.showinfo("Select output file",
                                    "Please select a calculation method.")
        #warnings.warn('Please select a calculation method')#file_out =  filedialog.asksaveasfilename(initialdir = "/", initialfile = "100YR_Future2_Eurotop_DesignAssess", defaultextension = ".csv",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
    return file_out, calc_method
    
def select_run(): # Options for run simulations button
    calc_method = var_method.get() # calculation method
    global numsim
    numsim = var_sim.get() # number of iterations
        
    try: file_in
    except NameError: tkinter.messagebox.showinfo("Run Calculation","Please select an input file.")#file_in = '' # None
    try: file_out
    except NameError: tkinter.messagebox.showinfo("Run Calculation","Please select an output file.")#file_out = '' # None
        
    if (calc_method == "Mean Value" or calc_method == "Design & Assessment") and (file_in != "" and file_in != None) and (file_out != "" and file_out != None):
#     if (calc_method == "Mean Value" or calc_method == "Design & Assessment") and file_in and file_out:
        print(f"Method chosen: {calc_method}")
        print(f"Number of iterations to perform: {numsim}")
        tkinter.messagebox.showinfo("Overtopping Calculation Progress",
                                    "Program is running!")
        root.destroy() # closes window

        
    elif calc_method != 'Mean Value' and  calc_method !='Design & Assessment':
        tkinter.messagebox.showinfo("Run Calculation",
                                    "Please select a calculation method.")
    return numsim


# Create drop down menu for calculation method (mean value vs. design/assess)
# Label for dropdown menu
label_1 = Label(root,text="Calculation Method:",width=20,font=("arial",12,"bold"))
label_1.place(x=50,y=374)
# Dropdown menu
list1 = ['Mean Value', 'Design & Assessment']
droplist = OptionMenu(root,var_method,*list1)
var_method.set("Select Method")
droplist.config(width=17,font=("arial",12))
droplist.place(x=270,y=370)

# Enter text for number of iterations
label_2 = Label(root,text="Number of Iterations:",width=20,font=("arial",12,"bold"))
label_2.place(x=50,y=410)
entry_2 = Entry(root,textvar=var_sim,width=22,font=("arial",12))
entry_2.place(x=268, y=411)
entry_2.insert(END,20000)

# Create button to choose input file
#b_in = Button(root,text="Input File",width=12,bg=((16,24,31)),fg=(211,188,141) )#  ,command=select_in)
b_in = Button(root,text="Select Input File",width=19,bg="#101820",fg="#D3BC8D",font=("arial",12,"bold"),command=select_in)
b_in.place(x=50,y=500)

# Create button to choose where to save file
b_out = Button(root,text="Select Output Name",width=19,bg="#101820",fg="#D3BC8D",font=("arial",12,"bold"),command=select_out)
b_out.place(x=269,y=500)


# # Add progress bar
# prog_it = Progressbar(root, orient = HORIZONTAL, length = 100, mode = 'determinate') # progress bar for iteration number 
# prog_it.pack() # iteration number progress bar


# Create button to run simulations
b_run = Button(root,text="Run Simulations",width=15,bg="#101820",fg="#D3BC8D",font=("arial",14,"bold"),command=select_run)
b_run.place(x=175,y=550)

# Add title to top of GUI
title = Label(root,text="EurOtop Overtopping (2018)",relief="solid",width=25,font=("arial",19,"bold"))
title.place(x=75,y=50)

# Inputs: method, no. of iterations, file in, file out


root.mainloop()


# In[10]:


# Add progress bar
# pbar=Tk()
# prog_it = Progressbar(pbar, orient = HORIZONTAL, length = 100, mode = 'determinate', maximum = numsim) # progress bar for iteration number 


# In[11]:


# Import overtopping function
from EurOtop_Overtopping import * 


# In[ ]:


# Calculate overtopping
OT(numsim,calc_method,file_in,file_out)


# In[ ]:




