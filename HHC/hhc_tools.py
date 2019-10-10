​#This is the main program file for the HHC-Tools GUI#

#import background python modules#
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
#-------------------------#
m=tk.Tk()                            # Create instance for master window   
m.geometry("500x600")
m.title("HHC Tools")                 # Add a title for master window
tabControl = tk.ttk.Notebook(m)      # Create Tab Control using ttk notebook

font0 = ('system',8)
font1 = ('system',10)
font2 = ('system',12)
font3 = ('system',14)
font4 = ('system',16)

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
import rainfall_pred1 as prcp
rainfall = ttk.Frame(tabControl)            # Create rainfall tab instance 
tabControl.add(rainfall, text='rainfall')      # Add the tab
tabControl.pack(expand=1, fill="both")  # Pack to make visible

img = Image.open(".\\images\\rainfall.png").resize((500,600))
img = ImageTk.PhotoImage(img)
background = tk.Label(rainfall, image=img)
background.place(x=0,y=0,relheight=1., relwidth=1.)
background.lower()

figure_window = tk.Canvas(master=rainfall)
figure_window.place(relx=0.05,rely=0.05,relheight=0.45, relwidth=0.90)

latitude_label=tk.StringVar()
latitude_label.set("Latitude:   ")

longitude_label=tk.StringVar()
longitude_label.set("Longitude:")

latitude_label=tk.Label(rainfall, 
                        textvariable=latitude_label, 
                        height=1, 
                        font=font2)

latitude_label.place(relx = 0.05, rely = 0.55)

longitude_label=tk.Label(rainfall, 
                         textvariable=longitude_label,
                         height=1,
                         font=font2)

longitude_label.place(relx = 0.05, rely = 0.65)

latitude = tk.Entry(rainfall,textvariable=None, font=font2, width=17)
longitude = tk.Entry(rainfall,textvariable=None, font=font2, width=17)

latitude.place(relx = 0.3, rely = 0.55)
longitude.place(relx = 0.3, rely = 0.65)

latitude.lift()
longitude.lift()

durations=['5-min',
           '10-min',
           '15-min',
           '30-min',
           '60-min',
           '2-hr',
           '3-hr',
           '6-hr',
           '12-hr',
           '24-hr',
           '2-day',
           '3-day',
           '4-day',
           '7-day',
           '10-day',
           '20-day',
           '30-day',
           '45-day',
           '60-day']

annual_return_intervals=['1',
                         '2',
                         '5',
                         '10',
                         '25',
                         '50',
                         '100',
                         '200',
                         '500',
                         '1000',
                         'all']

duration_variable = tk.StringVar(rainfall)
duration_variable.set('Duration') # default value
duration_menu = tk.OptionMenu(rainfall, duration_variable, *durations)
duration_menu.config(width=10, font=font0, height=1)
duration_menu.place(relx=0.7, rely =0.55)

annual_return_interval_variable = tk.StringVar(rainfall)
annual_return_interval_variable.set('Return')
annual_return_interval_menu = tk.OptionMenu(rainfall, annual_return_interval_variable, *annual_return_intervals)
annual_return_interval_menu.config(width=10, font=font0, height=1)
annual_return_interval_menu.place(relx=0.7, rely =0.65)

def precipitation(a,b,c,d):

    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    prcp.run_precip(a,b,c,d)
    fig = matplotlib.figure.Figure(figsize=(10, 6), dpi=100)
    mins = [i * 5 for i in prcp.hrs]
    if c == 'all':
        for i in range(len(annual_return_intervals)-2):
            fig.add_subplot(111,
                            xlabel="minutes",
                            ylabel="inches").plot(mins,prcp.list_return[i])
    else:
        fig.add_subplot(111,
                        xlabel="minutes",
                        ylabel="inches").plot(mins,prcp.list_return)
        #fig.add_subplot(111).bar(prcp.hrs,prcp.list_return)
    fig.suptitle("Hyteograph")
    fig.tight_layout(pad=7)
    canvas = FigureCanvasTkAgg(fig, master=rainfall)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.05,rely=0.05,relheight=0.45, relwidth=0.90)

precip_run_button = tk.Button(rainfall, 
                    text='Get Predicted Rainfall', font=font1,
                    width=25, 
                    command=lambda : precipitation(float(latitude.get()),
                                                   float(longitude.get()),
                                                   annual_return_interval_variable.get(),
                                                   duration_variable.get())) # adding button to rainfall tab
precip_run_button.place(relx=0.275,rely=0.85)

#Rainfall Tool end#

m.mainloop() # Start GUI
