#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import os
import shutil

        

def xyz2csv(file_out):
    os.chdir(file_out) #change directory to where the XYZ files are stored.
    try: #have to possibly create a secondary folder because windows permissions sometimes don't let us delete folders for about 15 minutes
        try:
            shutil.rmtree(file_out+"\CSV")
            csvfolder="CSV"
            os.mkdir(file_out+'\\'+csvfolder, 0o755)
        except:
            csvfolder="CSV"
            os.mkdir(file_out+'\\'+csvfolder, 0o755)
    except:
        try:
            shutil.rmtree(file_out+"\CSV1")
        except:
            print('.')
        csvfolder="CSV1"
        os.mkdir(file_out+'\\'+csvfolder, 0o755) #create new directory to store CSVs, so original XYZs are not overwritten

    ####Copy survey files into new directory and convert to CSV format####
    for files in os.listdir("."):
        if os.path.isfile(files) == True:
            beg = files[0:-3]
            new= (beg+"csv")
            shutil.copy(files, ".//"+csvfolder+"//"+new)
    os.chdir(file_out+ "\\" + csvfolder)
    csvlocation=file_out+ "\\" + csvfolder
    return csvlocation
    
def combinecsv(csvlocation):
    ####Combine data from all CSVs into one CSV with data in correct order####
    filenumber = 1
    for files in os.listdir(csvlocation):
        rows=0
        data=None
        while data ==None:
            try:
                data = np.loadtxt(files,delimiter = ",", skiprows = rows, usecols=(0,1,2))
                break
            except:
                rows+=1
        firsty = data[0,1]
        lasty = data[len(data)-1,1]
        if filenumber == 1: #first survey file   
            if firsty > lasty: #first survey file, so no previous data to compare to. Assume downstream is south
                RASdata = data[::-1]
            else:
                RASdata=data
        else:    
            distfirsty = abs(previouslasty - firsty)
            distlasty = abs(previouslasty - lasty)
            if (distfirsty < distlasty): #firsty is closer, so data is in correct order
                RASdata = np.concatenate((RASdata,data))
            else: #lasty is closer, so need to reverse data
                RASdata = np.concatenate((RASdata,data[::-1]))
        previouslasty = data[len(data)-1,1] 
        filenumber+=1
    return RASdata

####THIS FUNCTION CREATES RIVER STATIONS BASED ON DISTANCE BETWEEN CROSS SECTIONS
def riverstations(RASdata):
    RASdata2 = []
    RS=1 #cross section numbering starts at 1
    for i in range(len(RASdata)):
        if i>0:
            x1=RASdata[i-1][0]
            x2=RASdata[i][0]
            y1=RASdata[i-1][1]
            y2=RASdata[i][1]
            distance=(((x2-x1)**2)+((y2-y1)**2))**(0.5)
            if distance>100:
                RS+=1
        currentpoint = [RS,RASdata[i][0],RASdata[i][1],RASdata[i][2]]
        RASdata2.append(currentpoint)
    return RASdata2
    #print(currentpoint)


####THIS FUNCTION FLIPS CROSS SECTIONS SO ALL START WITH THE LEFT SIDE, WHICH IS PREFERABLE IN HEC-RAS
def flipXS(RSXYZ):
    XS = RSXYZ
    numXS = (RSXYZ[0][0]) #number of cross sections
    XS2 = []
    XSflip = []
    flip = 0
    previousRS = numXS #cross sections are numbered 1 through numXS. So the first river station is same as numXS.
    previousX = XS[0][1]
    previousY = XS[0][2]
    
    for i in range(len(XS)):
        RS = XS[i][0]
        if RS != previousRS: #first line of new cross section. time to check if this cross section is facing correct way
            if flip ==1: #last cross section needs to be appended from XSflip
                for j in range(len(XSflip)):
                    XS2.append(XSflip[len(XSflip)-j-1][:])
                #XS2.append(XSflip[::-1])
            #else:
                #XS2.append()
            XSflip = [] #now empty XSflip for next time its needed
            X1 = XS[i][1] #first point in XS
            X2 = XS[i+1][1] #second point in XS
            Y1 = XS[i][2]
            Y2 = XS[i+1][2]
            try: #if X1=X2, slope is infinite and python will fail due to dviding by 0
                m = (Y2-Y1)/(X2-X1) #slope of XS
                inversem = -1/m #slope to dummy point for evaluation
            except: #cross section slope is vertical, so dummy slope is horizontal. so give 0 slope
                inversem = 0
            theta = np.arctan(inversem)
            dx = np.absolute(100*np.cos(theta))
            dy = np.absolute(100*np.sin(theta))
            if Y2>Y1:
                if X2>X1:
                    X3 = X2 - dx #dummy point for evaluation
                    Y3 = Y2 + dy
                else:
                    X3 = X2 - dx #dummy point for evaluation
                    Y3 = Y2 - dy
            else:
                if X2>X1:    
                    X3 = X2 + dx #dummy point for evaluation
                    Y3 = Y2 + dy
                else:
                    X3 = X2 + dx #dummy point for evaluation
                    Y3 = Y2 - dy
            distreal = (((X2-previousX)**2)+((Y2-previousY))**2)**0.5 #distance from real cross section to the next upstream XS
            distdummy = (((X3-previousX)**2)+((Y3-previousY))**2)**0.5 #distance from dummy XS (downstream of real) to next upstream XS
            if distdummy > distreal: #cross section is correct
                #print(RS, "is good!")
                flip = 0
            else: #cross section needs to be flipped
                #print (RS, "needs to be flipped!")
                flip= 1
            previousRS = RS #keeping current river station so don't come into this river station again
            previousX = XS[i][1] #keeping current cross section's first coordinate for comparison to next cross section
            previousY = XS[i][2]
        if flip == 1:
            XSflip.append(XS[i][:])
        else:
            XS2.append(XS[i][:])
    if flip ==1: #last cross section needs to be appended from XSflip
        for j in range(len(XSflip)):
            XS2.append(XSflip[len(XSflip)-j-1][:])
    return XS2

#adds "RS, X, Y, Z" to the first line of the CSV. This makes it easier in RAS to go through the import CSV process
def addtextline(RASdata3):
    RASdata4=[["RS","X","Y","Z"]]
    for i in range(len(RASdata3)):
        point=[RASdata3[i][0],RASdata3[i][1],RASdata3[i][2],RASdata3[i][3]]
        RASdata4.append(point)
    return RASdata4
