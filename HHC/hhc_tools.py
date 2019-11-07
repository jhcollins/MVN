#import background python modules#
import sys
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import os
import webbrowser
import re
from datetime import date

## Specify fonts ##
font0 = ('arial',8)
font1 = ('arial',10)
font2 = ('arial',12); font2b = ('arial',12,'bold')
font3 = ('arial',14); font3b = ('arial',14,'bold')
font4 = ('arial',16); font4b = ('arial',16,'bold')
font5 = ('arial',19); font5b = ('arial',19,'bold')

# Get today's date 
today = date.today()
# Day, month abbreviation, and year
today_ddmmyyyy = today.strftime("%d%b%Y")
today_yy_mm_dd = today.strftime("%y-%m-%d")


#-------------------------#
m=tk.Tk()                            # Create instance for master window   
m.geometry("525x650")
m.title("HHC Tools")                 # Add a title for master window
tabControl = tk.ttk.Notebook(m)      # Create Tab Control using ttk notebook

# Specify font size for tabs
s = ttk.Style()
s.configure('TNotebook.Tab', font=font2b)

######################## Home Tab ############################
hometab = ttk.Frame(tabControl)            # Create overtopping tab instance 

# Add image to GUI
imge1 = Image.open(".\\images\\MS_birdfoot.jpg")
photo1 = ImageTk.PhotoImage(imge1)
tab_home = tk.Label(hometab,image=photo1)
# tab_home.pack()
tab_home.grid()

tabControl.add(hometab, text='Home')      # Add the tab
# tabControl.pack(expand=1, fill="both")  # Pack to make visible

# Add title to top of GUI
title = tk.Label(hometab,text="HHC Tools",relief="solid",width=25,font=font5b,bg='white')
title.place(x=75,y=50)


######################### Menu Bar ###############################################

def disp_overtopping_doc():
    os.startfile(".\\documentation\\Overtopping_Equations.pdf")
def disp_fcst_web():
    webbrowser.open_new("https://www.weather.gov/lmrfc/obsfcst_mississippi")  
menubar = tk.Menu(m)

# create a pulldown menu, and add it to the menu bar
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=m.destroy ) # have menu close upon clicking
menubar.add_cascade(label="File", menu=filemenu) # File menu

# create a pulldown menu for documentation
documation_menu = tk.Menu(menubar, tearoff=0)
documation_menu.add_command(label="EurOtop Overtopping", command=disp_overtopping_doc)
documation_menu.add_command(label="MS River Forecast", command=disp_fcst_web)
menubar.add_cascade(label="Documentation", menu=documation_menu) # tab you see

# display the menu
m.config(menu=menubar)

######################## Overtopping Tool Begin ############################
sys.path.insert(1,'.\overtopping\eurotop')

import EurOtop_Overtopping as ot
overtopping = ttk.Frame(tabControl)            # Create overtopping tab instance 

# Add image to page
imge = Image.open(".\\images\\overtopping-manual-eurotop-image-01.jpg")
# imge = Image.open(".\overtopping\eurotop\overtopping-manual-eurotop-image-01.jpg")
photo = ImageTk.PhotoImage(imge)
lab = tk.Label(overtopping,image=photo)
lab.pack()

# Define type of input
ot_var_method = tk.StringVar()
ot_var_sim = tk.StringVar()
ot_var_in = tk.StringVar()
ot_var_out = tk.StringVar()
def ot_select_in():
    global ot_file_in
    ot_file_in = ot_var_in.get()
    ot_file_in = tk.filedialog.askopenfilename(initialdir = "/",
                                     title = "Select file",
                                     filetypes = (("XLS files","*.xls"),("CSV files","*.csv"),("all files","*.*")))
    return ot_file_in

    print(f"Input file is {ot_file_in}")

def ot_select_out():
    global ot_calc_method
    ot_calc_method = ot_var_method.get() # calculation method
    global ot_file_out
    if ot_calc_method == 'Mean Value':
        ot_file_out =  tk.filedialog.asksaveasfilename(initialdir = "/", 
                                                 initialfile = "100YR_Future2_Eurotop_MeanValue",
                                                 title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        print(f"Output file is {ot_file_out}")
    elif ot_calc_method == 'Design & Assessment':
        ot_file_out =  tk.filedialog.asksaveasfilename(initialdir = "/", 
                                                 initialfile = "100YR_Future2_Eurotop_DesignAssess", defaultextension = ".csv",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        print(f"Output file is {ot_file_out}")
    else:
        tk.messagebox.showinfo("Select output file",
                                    "Please select a calculation method.")
    return ot_file_out, ot_calc_method
    
def ot_select_run(): # Options for run simulations button
    ot_calc_method = ot_var_method.get() # calculation method
    global ot_numsim
    ot_numsim = ot_var_sim.get() # number of iterations
        
    try: ot_file_in
    except NameError: tk.messagebox.showinfo("Run Calculation","Please select an input file.")#ot_file_in = '' # None
    try: ot_file_out
    except NameError: tk.messagebox.showinfo("Run Calculation","Please select an output file.")#ot_file_out = '' # None
        
    if (ot_calc_method == "Mean Value" or ot_calc_method == "Design & Assessment") and (ot_file_in != "" and ot_file_in != None) and (ot_file_out != "" and ot_file_out != None):

        print(f"Method chosen: {ot_calc_method}")
        print(f"Number of iterations to perform: {ot_numsim}")
        tk.messagebox.showinfo("Overtopping Calculation Progress",
                                    "Program is running!")

        ot.OT(ot_numsim,ot_calc_method,ot_file_in,ot_file_out)
        
    elif ot_calc_method != 'Mean Value' and  ot_calc_method !='Design & Assessment':
        tk.messagebox.showinfo("Run Calculation",
                                    "Please select a calculation method.")
    return ot_numsim


# Create drop down menu for calculation method (mean value vs. design/assess)
# Label for dropdown menu
label_1 = tk.Label(overtopping,text="Calculation Method:",width=20,font=("arial",12,"bold"),bg='white')
label_1.place(x=50,y=374)

# Dropdown menu
list1 = ['Mean Value', 'Design & Assessment']
droplist = tk.OptionMenu(overtopping,ot_var_method,*list1)
ot_var_method.set("Select Method")
droplist.config(width=17,font=font2)
droplist.place(x=270,y=370)

# Enter text for number of iterations
label_2 = tk.Label(overtopping,text="Number of Iterations:",width=20,font=("arial",12,"bold"),bg='white')
label_2.place(x=50,y=410)
entry_2 = tk.Entry(overtopping,textvar=ot_var_sim,width=22,font=("arial",12))
entry_2.place(x=268, y=411)
entry_2.insert(tk.END,20000)

# Create button to choose input file
b_in = tk.Button(overtopping,
                 text="Select Input File",
                 width=19,
                 bg="#101820",
                 fg="#D3BC8D",
                 font=font2b,
                 command=ot_select_in)

b_in.place(x=50,y=500)

# Create button to choose where to save file
b_out = tk.Button(overtopping,
                  text="Select Output Name",
                  width=19,
                  bg="#101820",
                  fg="#D3BC8D",
                  font=font2b,
                  command=ot_select_out)

b_out.place(x=269,y=500)

# Create button to run simulations
b_run = tk.Button(overtopping,
                  text="Run Simulations",
                  width=15,
                  bg="#101820",
                  fg="#D3BC8D",
                  font=font3b,
                  command=ot_select_run)

b_run.place(x=175,y=550)

# Add title to top of page
title = tk.Label(overtopping,
                 text="EurOtop Overtopping (2018)",
                 relief="solid",
                 width=25,
                 font=font5b,
                 bg='white')

title.place(x=75,y=50)

tabControl.add(overtopping, text='Overtopping')      # Add the title to the tab 
tabControl.pack(expand=1, fill="both")   # Pack to make visible  



########################### Overtopping Tool end #############################################




############################ Rainfall Tool Begin ######################

sys.path.insert(2,'.\precipitation\predicted')
import rainfall_pred1 as prcp
rainfall = ttk.Frame(tabControl)            # Create rainfall tab instance 
tabControl.add(rainfall, text='Rainfall')      # Add the tab
tabControl.pack(expand=1, fill="both")  # Pack to make visible

img = Image.open(".\\images\\rainfall.png").resize((525,650))
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
                        font=font2b)

latitude_label.place(relx = 0.05, rely = 0.55)

longitude_label=tk.Label(rainfall, 
                         textvariable=longitude_label,
                         height=1,
                         font=font2b)

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
duration_menu.config(width=10, font=font2, height=1)
duration_menu.place(relx=0.7, rely =0.55)

annual_return_interval_variable = tk.StringVar(rainfall)
annual_return_interval_variable.set('Return')
annual_return_interval_menu = tk.OptionMenu(rainfall, annual_return_interval_variable, *annual_return_intervals)
annual_return_interval_menu.config(width=10, font=font2, height=1)
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
    fig.suptitle("Hyetograph")
    fig.tight_layout(pad=7)
    canvas = FigureCanvasTkAgg(fig, master=rainfall)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.05,rely=0.05,relheight=0.45, relwidth=0.90)

precip_run_button = tk.Button(rainfall, 
                    text='Get Predicted Rainfall', 
                    font=font3b,
                    bg="#101820",
                    fg="#D3BC8D",
                    width=25, 
                    command=lambda : precipitation(float(latitude.get()),
                                                   float(longitude.get()),
                                                   annual_return_interval_variable.get(),
                                                   duration_variable.get())) # adding button to rainfall tab
precip_run_button.place(relx=0.225,rely=0.85)

####################################### Rainfall Tool end ##############################################

################################# Begin MS River Forecast Tool ############################################

sys.path.insert(3,'.\\river_forecast\\MS_fcst\\')
import get_MS_forecast as ms_fcst

riverfcst = ttk.Frame(tabControl)            # Create rainfall tab instance 
tabControl.add(riverfcst, text='MS River Forecast')      # Add the tab
tabControl.pack(expand=1, fill="both")  # Pack to make visible

# # Add image to page
# ms_imge = Image.open(".\\images\\CarrolltonGauge.jpg")
# # imge = Image.open(".\overtopping\eurotop\overtopping-manual-eurotop-image-01.jpg")
# ms_photo = ImageTk.PhotoImage(ms_imge)
# ms_lab = tk.Label(riverfcst,image=ms_photo)
# ms_lab.pack()

ms_var_out5 = tk.StringVar()
ms_var_out28 = tk.StringVar()

def ms_select_out5():
    global ms_file_out5
    ms_file_out5 = ms_var_out5.get()
    try:
        os.mkdir("K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\" + today_yy_mm_dd)
        ms_file_out5 = tk.filedialog.asksaveasfilename(initialdir = "K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\"  + today_yy_mm_dd + "\\",
                                                       initialfile = "test_FORECAST_" + today_ddmmyyyy + ".csv",
                                                       title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
    except:
        ms_file_out5 = tk.filedialog.asksaveasfilename(initialdir = "K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\"  + today_yy_mm_dd + "\\",
                                                       initialfile = "test_FORECAST_" + today_ddmmyyyy + ".csv",
                                                       title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
    return ms_file_out5
    print(f"Output location is {ms_file_out5}")

def ms_select_out28():
    global ms_file_out28
    ms_file_out28 = ms_var_out28.get()
    try:
        os.mkdir("K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\" + today_yy_mm_dd)
        ms_file_out28 = tk.filedialog.asksaveasfilename(initialdir = "K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\"  + today_yy_mm_dd + "/",
                                                       initialfile =   "test_24hr change NWS_" + today_ddmmyyyy + ".csv",
                                                       title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
    except:
        ms_file_out28 = tk.filedialog.asksaveasfilename(initialdir = "K:\\H&H1\\WTR-MGT\\FORECAST\\test_toolbox\\"  + today_yy_mm_dd + "\\",
                                                       initialfile = "test_24hr change NWS_" + today_ddmmyyyy + ".csv",
                                                       title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
    return ms_file_out28
    print(f"Output location is {ms_file_out28}")
    
def ms_select_run(): # Options for run simulations button
#     ot_calc_method = ot_var_method.get() # calculation method
#     global ot_numsim
#     ot_numsim = ot_var_sim.get() # number of iterations
        
    try: ms_file_out5
    except NameError: tk.messagebox.showinfo("Run Calculation","Please select a 5-day output file.")#ot_file_in = '' # None
    try: ms_file_out28
    except NameError: tk.messagebox.showinfo("Run Calculation","Please select a 28-day output file.")#ot_file_out = '' # None
    
    ms_fcst.get_ms_fcst(ms_file_out5,ms_file_out28,today_ddmmyyyy)


# Create button to choose where to save file
ms_b_out5 = tk.Button(riverfcst,
                  text="Select 5-Day Output Name",
                  width=21,
                  bg="#101820",
                  fg="#D3BC8D",
                  font=font2b,
                  command=ms_select_out5)
ms_b_out5.place(x=40,y=500)
# Create button to choose where to save file
ms_b_out28 = tk.Button(riverfcst,
                  text="Select 28-Day Output Name",
                  width=21,
                  bg="#101820",
                  fg="#D3BC8D",
                  font=font2b,
                  command=ms_select_out28)
ms_b_out28.place(x=275,y=500)

# Create button to run simulations
ms_b_run = tk.Button(riverfcst,
                  text="Get Forecast",
                  width=15,
                  bg="#101820",
                  fg="#D3BC8D",
                  font=font3b,
                  command=ms_select_run)

ms_b_run.place(x=175,y=550)

####################### Begin ras plot tool ###########################
sys.path.insert(4,'.//ras_tools//vv_tool')
import vv_plots as vvp

vv_plot = ttk.Frame(tabControl)

tabControl.add(vv_plot, text='RAS CRMS Plot')      # Add the tab
tabControl.pack(expand=1, fill="both")  # Pack to make visible

abs_path=sys.path[0]
print(vvp.abs_path_vv_plots)

def vv_ras_file_select_in():
    global vv_ras_plan_file_in, vv_ras_hdf_file_in
    vv_ras_plan_file_in = tk.StringVar().get()
    vv_ras_plan_file_in = tk.filedialog.askopenfilename(initialdir = "/",
                                     title = "Select file",)
    vv_ras_hdf_file_in = vv_ras_plan_file_in+".hdf"

    print(f"RAS plan file is {vv_ras_plan_file_in}")
    print(f"RAS hdf file is {vv_ras_hdf_file_in}")

def vv_CRMS_select_in():
    global vv_CRMS_file_in_0, vv_CRMS_file_in_1
    vv_CRMS_file_in_0 = tk.StringVar().get()
    vv_CRMS_file_in_0 = tk.filedialog.askopenfilename(initialdir = "/",
                                     title = "Select file",filetypes = (("CSV files","*-0.csv"),("all files","*.*")))
    
    vv_CRMS_file_in_1=list(vv_CRMS_file_in_0)
    vv_CRMS_file_in_1[-5]='1'
    vv_CRMS_file_in_1=''.join(vv_CRMS_file_in_1)

    inputs_path_file=abs_path+'\\inputs_path.txt'
    vvp.path_write(inputs_path_file,vv_CRMS_file_in_1)    
    print(f"CRMS0 plan file is {vv_CRMS_file_in_0}")    
    print(f"CRMS1 plan file is {vv_CRMS_file_in_1}")

def vv_projection_select_in():
    global vv_RAS_projection_file
    vv_RAS_projection_file = tk.StringVar().get()
    vv_RAS_projection_file = tk.filedialog.askopenfilename(initialdir = "/",
                                     title = "Select file",filetypes = (("projection","*.prj"),("all files","*.*")))
    prj_path_file=abs_path+'\\prj_path.txt'
    vvp.path_write(prj_path_file,vv_RAS_projection_file)   
    print(f"RAS prj file is {vv_RAS_projection_file}")    
    
vv_ras_plan_file = tk.Button(vv_plot,
                 text="Select RAS Plan File",
                 width=19,
                 bg="#101820",
                 fg="#D3BC8D",
                 font=font2b,
                 command=vv_ras_file_select_in)

vv_CRMS_file = tk.Button(vv_plot,
                 text="Select CRMS File",
                 width=19,
                 bg="#101820",
                 fg="#D3BC8D",
                 font=font2b,
                 command=vv_CRMS_select_in)

vv_projection_file = tk.Button(vv_plot,
                 text="Select RAS Projection",
                 width=19,
                 bg="#101820",
                 fg="#D3BC8D",
                 font=font2b,
                 command=vv_projection_select_in)

def vv_make_plots():
    vvp.read_ras(vv_ras_hdf_file_in)
    vvp.crms_ras_results(vvp.vv_ras_results,vvp.vv_flow_areas_2d)
    vvp.crms_set_projection()
    vvp.crms_gather_data(vv_CRMS_file_in_0,vv_CRMS_file_in_1)
    vvp.vv_plots(vvp.crms_ras_xy,vvp.crms_ras_swl,vvp.vv_locations,vvp.CRMS_gauge_results,vv_plot_output_dir)

vv_make_plot_button = tk.Button(vv_plot,
                 text="Make Plots",
                 width=19,
                 bg='#E38C79',#"#101820",
                 fg="#000000",
                 font=font2b,
                 command=vv_make_plots)

def vv_plot_output_folder():
    global vv_plot_output_dir
    vv_plot_output_dir = tk.StringVar().get()
    vv_plot_output_dir = tk.filedialog.askdirectory(initialdir = os.getcwd(),
                                     title = "Select folder")

vv_plot_output_folder_select = tk.Button(vv_plot,
                 text="Select Output Location",
                 width=19,
                 bg="#101820",
                 fg="#D3BC8D",
                 font=("arial",12,"bold"),
                 command=vv_plot_output_folder) 

vv_canvas = tk.Canvas(vv_plot, width = 450, height = 300)      
vv_canvas.place(x=50,y=25)

def vv_plot_window():
    global img, img_count
    try:
        img_count+=1
    except:
        img_count=0
  
    img=Image.open(vv_plot_output_dir+"\\vv_"+str(img_count%6)+".png")
    img = img.resize((450, 300),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    vv_canvas.create_image(200,150,image=img) 
    
vv_plot_window_button = tk.Button(vv_plot,
                 text="Show Plots",
                 width=19,
                 bg="#7FE8BE",
                 fg="#000000",
                 font=font2b,
                 command=vv_plot_window)

vv_CRMS_file.place(x=50,y=500)
vv_projection_file.place(x=50,y=450)
vv_make_plot_button.place(x=300,y=450) 
vv_ras_plan_file.place(x=50,y=400)
vv_plot_output_folder_select.place(x=300,y=400)
vv_plot_window_button.place(x=300,y=500) 

####################### End ras plot tool ###########################


m.mainloop() # Start GUI
