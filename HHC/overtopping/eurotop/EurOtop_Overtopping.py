#!/usr/bin/env python
# coding: utf-8

# ## EurOtop Overtopping calculations
# Overtopping calculations as described in the EurOtop Manual on wave overtopping of sea defences and related structures (Second Edition 2018; www.overtopping-manual.com).
# 
# With this interface, you will be able to load an input Excel file, specify number of Monte Carlo simulations (default 20,000), and specify the name and location of the output figures and Excel file detailing the design heights for each structure.
# 
# EurOtop, 2018. Manual on wave overtopping of sea defences and related structures. An overtopping manual largely based on European research, but for worldwide application. Van der Meer, J.W., Allsop, N.W.H., Bruce, T., De Rouck, J., Kortenhaus, A., Pullen, T., Schüttrumpf, H., Troch, P. and Zanuttigh, B., www.overtopping-manual.com.

# In[ ]:


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
import os


# ## Define Function for overtopping calculation
# Equations from EurOtop Manual indicated by variable name indicating the equation number from the 2018 edition of EurOtop
# 
# $\textbf{Positive Freeboard (Levee)}$
# 
# $\textit{Mean Value Approach}$:
# $$q = \sqrt{gH_{m0}^3}\dfrac{0.023}{\tan\alpha}\gamma_b \xi_{m-1,0}\exp\left[-\left(2.7\dfrac{R_c}{\xi_{m-1,0}H_{m0}\gamma_b\gamma_f\gamma_{\beta}\gamma_{v}}\right)^{1.3}\right]$$
# 
# with maximum
# 
# $$q = 0.09\sqrt{gH_{m0}^3}\exp\left[-\left(1.5\dfrac{R_c}{H_{m0}\gamma_f\gamma_{\beta}\gamma^{\ast}}\right)^{1.3}\right]$$
# 
# $\textit{Design & Assessment}$:
# $$q = \sqrt{gH_{m0}^3}\dfrac{0.026}{\tan\alpha}\gamma_b \xi_{m-1,0}\exp\left[-\left(2.5\dfrac{R_c}{\xi_{m-1,0}H_{m0}\gamma_b\gamma_f\gamma_{\beta}\gamma_{v}}\right)^{1.3}\right]$$
# 
# with maximum
# 
# $$q = 0.1035\sqrt{gH_{m0}^3}\exp\left[-\left(1.35\dfrac{R_c}{H_{m0}\gamma_f\gamma_{\beta}\gamma^{\ast}}\right)^{1.3}\right]$$
# 
# $\textbf{Positive Freeboard (Vertical Wall)}$
# 
# $\textit{Mean Value Approach}$:
# $$q = 0.047\sqrt{gH_{m0}^3}\exp\left[-\left(2.35\dfrac{R_c}{H_{m0}\gamma_f\gamma_{\beta}}\right)^{1.3}\right]$$
# 
# $\textbf{Postive Freeboard}$
# $\textit{Broad-crested weir}$
# $$q = 1.5\sqrt{g\left|-R_c^3\right|}$$

# In[ ]:


# Function for calculating overtopping
def SWOTp(LW,Elevation,width,slope,surgeStorm,HS,TM,Gb,Gf,GB,Gv,gacc,Ca,Cb,Cc,Cd,CWa,CWb,calc_method):
# LW = Levee or Wall. Enter 1 for levee, 0 for WALL
# Elevation = Elevation profile of structure
# width = width of each individual segment. (not total length of segment). 
# # NOTE: both Elevation and Width must be same length vectors.
# SurgeStorm = time-series of water levels
# HS = time-series of wave heights
# Tm = time-series of mean wave periods. Sure and wave must have same length
# Gb, Gf, GB, Gv = overtopping (OT) factors. 
# gacc = acceleration due to gravity use 9.81m/s2 for metric or 32.2ft/s2 for standard
# Ca,Cb,Cc,Cd = 0.023,2.7,0.09,1.5 (std = 0.003, 0.2, 0.0134, 0.15)
    
    minOT = 0.0001 # minimum overtopping (OT) rate for output (cfs/ft) or (cms/m)

    Rc = Elevation-surgeStorm # relative freeboard   
    
    if Rc >= 0 and LW == 1: # levee surge below crest
        s0 = 2*np.pi*HS/(gacc*TM**2)
        Em = slope/(s0**0.5) 
        if calc_method == 'Mean Value':#method.value == 'Mean Value':
            E510 = width * np.sqrt(gacc*(HS**3)) * (Ca/(slope**0.5)) * Gb * Em * np.exp(-1*(Cb*(Rc/(Em*HS*Gb*Gf*GB*Gv)))**1.3)
            E511 = width * np.sqrt(gacc*(HS**3)) *Cc * np.exp(-1*( Cd*(Rc/(HS*Gf*GB)))**1.3)
            Q = np.min(np.array([E510, E511]))
        elif calc_method == 'Design & Assessment': #method.value == 'Design & Assessment':
            E512 = width * np.sqrt(gacc*(HS**3)) * (0.026/slope**0.5)*Gb*Em*np.exp(-1*( 2.5*(Rc/(Em*HS*Gb*Gf*GB*Gv))**1.3))
            E513 = width * np.sqrt(gacc*(HS**3)) * 0.1035*np.exp(-1*( 1.35*(Rc/((HS*Gf*GB)))**1.3))
            Q = np.min(np.array([E512, E513]))
            
    elif Rc >= 0 and LW == 0: # wall surge below crest

        E517 = width*np.sqrt(gacc*(HS**3))*CWa*np.exp(-1*( CWb*(Rc/(HS*Gf*GB)))**1.3) # Eqn 5.17 steep slope up to vertical wall
        Q = E517
                                                             
    elif Rc < 0 and LW == 1: # Levee surge > crest
        Rcn = 0 # special condition for surge > crest
        s0 = 2*np.pi*HS/(gacc*TM**2)
        Em = slope/(s0**0.5)

        # Equation for broad-crested weir
        Cweir = np.random.uniform(1.5,3) # have the Weir coeff vary uniformly between 1.5 and 3
        weirf_eq1 = Cweir*width * (-1*Rc)**(3/2)
        
        if calc_method == 'Mean Value': #method.value == 'Mean Value':
            E510 = width *np.sqrt(gacc*(HS**3)) * (Ca/(slope**0.5))*Gb*Em*np.exp(-1*( Cb*(Rcn/(Em*HS*Gb*Gf*GB*Gv)))**1.3)
            E511 = width *np.sqrt(gacc*(HS**3)) * Cc*np.exp(-1*( Cd*(Rcn/(HS*Gf*GB)))**1.3)
            Q = np.min(np.array([E510, E511])) + weirf_eq1
        elif calc_method == 'Design & Assessment': #method.value == 'Design & Assessment':
            E512 = width *np.sqrt(gacc*(HS**3)) * (0.026/slope**0.5)*Gb*Em*np.exp(-1*( 2.5*(Rcn/(Em*HS*Gb*Gf*GB*Gv)))**1.3) 
            E513 = width *np.sqrt(gacc*(HS**3))*0.1035*np.exp(-1*( 1.35*(Rcn/(HS*Gf*GB)))**1.3)
            Q = np.min(np.array([E512, E513])) + weirf_eq1


    elif Rc < 0 and LW == 0:  # wall surge greater than wall (i.e., negative freeboard)
        Rcn = 0 # special condition for surge > crest
        E517 = (width) *np.sqrt((gacc)*((HS)**3))*CWa*np.exp(-1*( CWb*(Rcn/((HS)*Gf*GB)))**1.3)
        
        # Equation for broad-crested weir
        Cweir = np.random.uniform(1.5,3) # have the Weir coeff vary uniformly between 1.5 and 3
        weirf_eq1 = Cweir*width * (-1*Rc)**(3/2)
        Q = E517 + weirf_eq1

    if (Q/(width)) < minOT: # if average OT is less than min, then set to 0. 
        Q = 0

    return Q


# ## Loop through each structure in file

# In[ ]:


def OT(numsim,calc_method,file_in,file_out):
#   Input: numsim - number of Monte Carlo iterations to run
#          calc_method - string input for Mean Value or Design & Assessment method
#          file_in - path and filename of input Excel file
#          file_out - path and filename of output CSV
#
#   Output: CSV file with results of design height, q50, and q90
#           Figures contained in plots/ directory with CSV output file

    # Set file name specified in GUI
    XLSname = file_in # Load file with levee or wall information (.xls or .csv)
    
    # Import Hydraulic Boundary Conditions and Levee Design Info from XLS file
    if ".xls" in XLSname:
        DesI = pd.read_excel(XLSname, sheet_name = 'Sheet1', skiprows = 7 , usecols = "A:U") #import design data matrix 
    elif ".csv" in XLSname:
        DesI = pd.read_csv(XLSname, skiprows = 7)#, usecols = "A:U") #import design data matrix 
        
    # Finds path for user-specified location of CSV output     
    import ntpath
    path_out = ntpath.dirname(file_out) # path used to tell where plots/ directory will be
    
    # Set Constants/Coefficients
    g = 32.2 #acceleration of gravity (ft/s)
    N = int(numsim) #dum.value #number of monte carlo simulations
    
    # Import section names
    SecN = DesI[u'Levee Section ']
    S = np.size(DesI,0) # number of levee segments
    
    # Pre-allocate new variables before loop
    OvertoppingRate_q50 = np.zeros(S)
    OvertoppingRate_q90 = np.zeros(S)
    
    # Begin loop for finding the structure deisgn height
    for f in range(0, S):
        print('Levee Section: ' + str(SecN[f])) # prints string; command "str" converts from unicode to regular string

    #Import design info for levee and convert to metric
        DYR = DesI['Design Year'][f] # Design Year
        RTP = DesI['Return Period'][f] # Return Period

        LoFL = DesI['Levee/Floodwall'][f] # Loads logical information on levee or floodwall (levee==1; floodwall==0)
        if LoFL == 1:
            structtype = 'Levee'
            sl = DesI['Levee Slope'][f] # Tan(a) where a is levee angle = "slope" (rise/run) eg. sl = 1/4 = "one on four levee" (-)  
        else:
            structtype = 'Floodwall'
            sl = 99

        swl = DesI['SWL'][f] # still water elevation (ft)
        swlstd = DesI['SWL STD'][f] # still water standard deviation (ft)
        hs = DesI['Hs'][f]    # Hm0 = significant wave height = hs (ft)

        if hs < 1.5:
            hs = 1.5

        hsstd = hs*0.1    # standard deviation of Hs (ft)

        tm10 = DesI['Tm'][f]#(f,8); #spectral wave period (s) 
        if tm10 < 2.0:
            tm10 = 2.0

        tm10std = tm10*0.2 #standard deviation of spectral wave period (s) 


        gb = DesI.values[f,11]   # influence factor for a berm (-)
        gf = DesI.values[f,12]   # influence factor for roughness elements on slope (-)
        gB = DesI.values[f,13]   # influence factor for angled wave attack (-)
        gv = DesI.values[f,14]   # influence factor for vertical wall (-)
        berm = DesI['BermElevation'][f] # values[f,16]  # berm elevation 
        BR = 0.4 # breaker parameter over berm
        DH = (round((swl))) # set initial design height to swl + hs. Program will loop until DS is reached.
        # initialize overtopping values so that while loop will begin
        q50 = 1
        q90 = 1

        if LoFL == 1:
            q50L = 0.01 # value for levee
        else:
            q50L = 0.03 # value for wall

        while (q50 > q50L) or (q90 > 0.1): # design constraints
            DH += 0.5 # Add 0.5 ft to design height for each iteration
            print(str(DH)+' ft')

            OTR = np.zeros(N) # pre-allocate output
                   # Monte Carlo Simulation
            for i in range(N):

                m = np.random.uniform(0,1) # random number from a uniform distribution between 0 and 1
                Pswl = norm.ppf(m, loc = swl, scale = swlstd) # generate swl from normal distribution; loc = mean (mu), scale is stddev (sigma)
                n = np.random.uniform(0,1)
                Phs  = norm.ppf(n, loc = hs, scale = hsstd) # generate hs and tm10 from normal distribution
                Ptm10 = norm.ppf(n, loc = tm10, scale = tm10std) # generate hs and tm10 from normal distribution


                if Phs > np.max([(Pswl-berm)*BR, 0.25]): # depth limited waves in iteration
                    Phs =  np.max([(Pswl-berm)*BR, 0.25])

                if Phs <= 0:
                    Phs = 0.25

                if Ptm10 <= 0:
                    Ptm10 = 0.25


                p = np.random.uniform(0,1); Ca  = norm.ppf(p,loc = 0.023,scale = 0.003); 
                p = np.random.uniform(0,1); Cb  = norm.ppf(p,loc = 2.7,scale = 0.2); 
                p = np.random.uniform(0,1); Cc  = norm.ppf(p,loc = 0.09,scale = 0.0134); 
                p = np.random.uniform(0,1); Cd  = norm.ppf(p,loc = 1.5,scale = 0.15); 
                p = np.random.uniform(0,1); CWa = norm.ppf(p,loc = 0.047,scale = 0.007); 
                p = np.random.uniform(0,1); CWb = norm.ppf(p,loc = 2.35,scale = 0.23); 

                        #           if LoFL==1;#levee overtopping

                OTR[i] = SWOTp(LoFL,DH,1,sl,Pswl,Phs,Ptm10,gb,gf,gB,gv,g,Ca,Cb,Cc,Cd,CWa,CWb,calc_method)

            OTR = np.sort(OTR, axis=0) # sort results of monte carlo simulation
            OTR = np.append([OTR], [np.zeros(N)], 0)

            for j in range(N):
                OTR[1,j] = 1-((np.float32(j)+1)/(np.float32(N)+1)) #fill in probabilities

            q50 = OTR[0,int(0.5*(N))] # pull overtopping rate q50
            q90 = OTR[0,int(0.9*(N))] # pull overtopping rate q90

        print('Final Design Elevation = ' + str(DH) + ' ft')


        # plot loglog 
        plt.figure(figsize=[8,6])
        plt.subplot(2,1,1)
        plt.loglog(OTR[1,:],OTR[0,:])
        plt.loglog([0.1, 0.1],[0.0001, 0.1],'r-',linewidth=2); # draw design constraint lines
        plt.loglog([0.5, 0.5],[0.0001, q50L],'r--',linewidth=2); # draw design constraint lines
        plt.loglog([1, 0.1],[0.1, 0.1],'r-',linewidth=2); # draw design constraint lines
        plt.loglog([1, 0.5],[q50L, q50L],'r--',linewidth=2); # draw design constraint lines
        plt.loglog([0.1, 0.1],[0.1, 0.1],'ro', markersize=5, markerfacecolor=[1, 0, 0], markeredgecolor=[0, 0, 0]) # draw design constraint point
        plt.loglog([0.5, 0.5],[q50L, q50L],'ro',markersize=5, MarkerFaceColor=[1, 0, 0], MarkerEdgeColor=[0, 0, 0]) # draw design constraint point
        plt.plot(0.5,q50,'gd',MarkerFaceColor=[0, 1, 0],MarkerEdgeColor=[0, 0, 0]) #plot q50 point
        plt.plot(0.1,q90,'gd',MarkerFaceColor=[0, 1, 0],MarkerEdgeColor=[0, 0, 0]) #plot q90 point
        plt.text(0.5-0.05,q50,r'$q_{50}$ = ' + str(np.round(q50, decimals=4)) + ' cfs/ft', BackgroundColor=[1, 1, 1], fontsize=10, bbox=dict(facecolor=[1, 1, 1], edgecolor='black'))#, EdgeColor=[0, 0, 0], fontsize=8) #labels
        plt.text(0.1-0.01,q90,r'$q_{90}$ = ' + str(np.round(q90, decimals=4)) + ' cfs/ft', BackgroundColor=[1, 1, 1], fontsize=10, bbox=dict(facecolor=[1, 1, 1], edgecolor='black'))#, EdgeColor=[0, 0, 0], fontsize=8) #labels
        plt.text(0.055,0.00015,'number of simulations = ' + str(N),fontsize=10)
        plt.axis([0.01, 1.0, 0.0001, 1.0])
        plt.xlabel('Probability of Exceedance (-)',fontsize=12)
        plt.ylabel('Overtopping Rate (cfs/ft)',fontsize=12)
        plt.title(structtype+'-'+str(SecN[f])+', Return Period: '+str(RTP)+' YR'+', Project Year: '+str(DYR),fontsize=14)
        plt.xlim(1, 0.01)

        plt.grid(True, which='both', ls =':')


        plt.subplot(2,1,2) 
        Yscale = 30 # roundn((max(DesI(f,4))+10),1);# Y scale for plot
        swlp = swl # swl convert back to ft
        adj = 1 # wave period adjustment (to make plot look good)
        DHp = DH # Design height converted back to ft
        Hsp = hs # design wave converted back to ft
        off = 10 # offset to start levee
        off2 = 200  # total length of levee plot
        xaty0 = (DHp + (sl*off) )/ sl # x-intercept where levee line y = 0
        xswl = (-swlp+DHp+sl*off)/ sl # intercept of swl and levee line
        if LoFL == 1:
            plt.plot([0, off, xaty0, off2],[DHp, DHp, 0, 0], linewidth=3, Color=[0, 1, 0])
        else:
            plt.plot([0, 0, off, xaty0, off2],[0, DHp, DHp, 0, 0], linewidth=3, Color=[0.5, 0.5, 0.5]); 

        plt.plot([xswl, off2],[swlp, swlp],'b--',linewidth=0.5) # plot swl dashed
        sintime = np.arange(0, (off2-xswl), 0.1) # syntax is (a,b,delta_x)
        wave = (Hsp/2)*np.sin(sintime*(1/tm10*adj)) # compute wave with Hs amplitude (np.sin uses radian input)
        plt.plot(sintime + xswl, wave + swlp,Color=[0, 0.2, 0.9]) # plot wave line
        plt.axis([-10, 200, -1, Yscale]) # set scale
        plt.xlabel('Stationing (ft)',fontsize=12)
        plt.ylabel('Elevation \n (ft. NAVD88 2009.55)',fontsize=12)
        plt.text(-4,Yscale-.10*Yscale,'Design Elevation = ' + str(DHp) + 'ft')
        if LoFL == 1:
            plt.text(-4,Yscale - 0.60*Yscale, 'Slope = 1:' + str(1/sl),fontsize=10);
            plt.text(-4,Yscale - 0.70*Yscale, 'Berm Factor = ' + str(gb),fontsize=10);
            plt.text(-4,Yscale - 0.80*Yscale, 'Roughness Factor = ' + str(gf),fontsize=10);
            plt.text(-4,Yscale - 0.90*Yscale, 'Wave Angle Factor = ' + str(gB),fontsize=10);
        else:
        #plt.text(-4,Yscale-.60*Yscale,['Slope = floodwall']);
        #plt.text(-4,Yscale-.70*Yscale,['Berm Factor = floodwall']);
        #plt.text(-4,Yscale-.80*Yscale,['Roughness Factor = floodwall']);
        #plt.text(-4,Yscale-.80*Yscale,['Wave Angle Factor = ',str(gB)],fontsize=8);
            plt.text(-4,Yscale-0.9*Yscale,'Vertical Wall Factor = ' + str(gv), fontsize=8)

        plt.text(70, Yscale - 0.07*Yscale, 'Hydraulic design characteristics',fontsize=10, weight="bold")
        plt.text(70, Yscale - 0.37*Yscale, 'Mean period $T_m$ = ' + str(tm10) + 's; '+ '$\sigma_{T_m}$ = ' + str(np.round(tm10std,decimals=2)) + 's', fontsize=10)
        plt.text(70, Yscale - 0.17*Yscale, 'Still water level $\zeta$ = ' + str(swlp) + 'ft; ' + '$\sigma_{\zeta}$ = ' + str(swlstd) + 'ft', fontsize=10)
        plt.text(70, Yscale - 0.27*Yscale, 'Significant wave height at toe $H_s$ = ' + str(Hsp) + 'ft; ' + '$\sigma_{H_s}$ =' + str(np.round(hsstd,decimals=2)) + 'ft', fontsize=10)

        plt.grid(True)
        plt.tight_layout()
        dd = '00' + str(f)

        # Add plots to plots/ directory
        ntpath.dirname(file_out)
        try:
            plt.savefig(path_out + "/plots/" + dd[-1:] + "_" + str(SecN[f]) + "_Design.png")#,format = 'png')
        except: 
            os.mkdir(path_out + "/plots/")
            plt.savefig(path_out + "/plots/" + dd[-1:] + "_" + str(SecN[f]) + "_Design.png")#,format = 'png')
        plt.show() # must come after save or file will save as blank image
        plt.close()

        # Update table with design values
        DesI.loc[f,'Levee Elevation'] = DH
        OvertoppingRate_q50[f] = q50
        OvertoppingRate_q90[f] = q90

        del DH
    
    # Add two new columns to output
    DesI['q50 Overtopping Rate'] = OvertoppingRate_q50
    DesI['q90 Overtopping Rate'] = OvertoppingRate_q90
    
    ## Save output dataframe into CSV
    fname = file_out #root.filename #dum.value

    print("Saved!")

