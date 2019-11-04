#!/usr/bin/env python
# coding: utf-8

# ## Gets River Forecast Data (5- and 28- Day)

# In[7]:


def get_ms_fcst(file_out5,file_out28,today_date):
    import requests as req
    import urllib.request as urlreq
    import time
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    import os
    from datetime import datetime
    import matplotlib.pyplot as plt
    import six
    
    # Define function for creating tables as/within images
    def render_mpl_table(data, col_width=2.0, row_height=0.625, font_size=14,
                         header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                         bbox=[0, 0, 1, 1], header_columns=0,
                         ax=None, **kwargs):
        if ax is None:
            size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
            fig, ax = plt.subplots(figsize=size)
            ax.axis('off')

        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)

        for k, cell in six.iteritems(mpl_table._cells):
            cell.set_edgecolor(edge_color)
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(color='w'),#weight='bold', color='w'), 
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
        return ax
    
    
    
    #################### NWS Observations and Forecasts for the Lower Mississippi/Ohio site ##################
    nws = req.get('https://www.weather.gov/lmrfc/obsfcst_mississippi')

    # Parse html data from website
    nws_html = BeautifulSoup(nws.text, "html.parser") # NOTE: data is pre-formatted <pre>

    ###################### Get 5-day forecast data ##########################
    dum = nws_html.findAll('a')[118]
    pred_5day = dum['href']
    html_5day = BeautifulSoup(req.get(pred_5day).text, "html.parser")
    text_5day = html_5day.find('pre').contents[0]

    # Separate the rows specified in the data by \n
    split_5day = text_5day.string.split('\n') # rows are separated by \n
    # Separate items in row (space)
    list_5day = [[]] * np.size(split_5day)
    for i in range(np.size(split_5day)):
        list_5day[i] = split_5day[i].split() # separate each entry within the row

    # Combine city names into one cell if multiple words (e.g., Baton Rouge, New Orleans)
    for i in range(np.size(list_5day)):
        try:
            list_5day[i][0]
            if list_5day[i][0] == '':
                next
            elif list_5day[i][1] == '':
                next
            elif list_5day[i][0] == 'STATION':
                next    
            elif list_5day[i][0] == 'STG':
                list_5day[i].insert(0,'')
                list_5day[i].insert(1,'')
            elif list_5day[i][1].isnumeric():
                list_5day[i][1] = list_5day[i][1]
            elif list_5day[i][1].isalpha():
                list_5day[i][0] = list_5day[i][0] + ' ' + list_5day[i][1]
                del list_5day[i][1]
        except:
            continue


    # Combine city names into one cell if more than two words (e.g., Red River Landing)
    for i in range(np.size(list_5day)):
        try:
            list_5day[i][0]
            if list_5day[i][0] == '':
                next
            elif list_5day[i][1] == '':
                next
            elif list_5day[i][0] == 'STATION':
                next
            elif list_5day[i][1] == 'TDA':
                next
            elif list_5day[i][1].isnumeric():
                list_5day[i][1] = fcst_5day[i][1]
            elif list_5day[i][1].isalpha():
                list_5day[i][0] = list_5day[i][0] + ' ' + list_5day[i][1]
                del list_5day[i][1]
        except:
            continue

    # Put list into dataframe
    fcst_5day = pd.DataFrame(list_5day)



    # Pause so website doesn't think we're a hacker (probably more relevant for loops)
    time.sleep(1)

    ##################### Get 28-day forecast data ############################
    dum = nws_html.findAll('a')[119]
    pred_28day = dum['href']
    html_28day = BeautifulSoup(req.get(pred_28day).text, "html.parser")
    text_28day = html_28day.findAll('pre')[0]
    # Separate the rows specified in the data by \n
    split_28day = text_28day.string.split('\n') # rows are separated by \n
    list_28day = [[]] * np.size(split_28day)
    for i in range(np.size(split_28day)):
        list_28day[i]=split_28day[i].split() # separate each entry within the row


    ############################# Save CSV output ########################

    #### Save 5-day forecast file ####
    import ntpath
    path_out5 = ntpath.dirname(file_out5)
    
    try: # Create year directory if not done so (really should only be an issue once per year)
        os.mkdir(ntpath.split(path_out5)[0])
    except:
        pass
    
    try:
        os.mkdir(path_out5) # create path for today (if not previously created)
        pd.DataFrame.to_csv(fcst_5day, path_out5 + "\\" +  "test_FORECAST_" + today_date + ".csv")
    except:
        pd.DataFrame.to_csv(fcst_5day, path_out5 + "\\" + "test_FORECAST_" + today_date + ".csv")

    #### Save 28-day forecast file ####

    # Put list into data frame
    fcst_28day = pd.DataFrame(list_28day)
    path_out28 = ntpath.dirname(file_out28)
    try: # Create year directory if not done so (really should only be an issue once per year)
        os.mkdir(ntpath.split(path_out28)[0])
    except:
        pass
    try:
        os.mkdir(path_out28) # create path for today (if not previously created)
        pd.DataFrame.to_csv(fcst_28day, path_out28 + "\\" + "test_24hr change NWS_" + today_date + ".csv", date_format='%mm-%dd-%YY')
    except:
        pd.DataFrame.to_csv(fcst_28day, path_out28 + "\\" + "test_24hr change NWS_" + today_date + ".csv", date_format='%mm-%dd-%YY')
        
    ############################### Plot Stages for New Orleans ##########################
    fcst28 = np.array(fcst_28day)

    k, l = np.where(fcst28=="NORL1") # used k and l as indices since i,j had been used

    dates_fcst21_NO = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]
    #### RIVER STAGE PREDICTIONS TABLE ####
    river_title = "RIVER STAGE PREDICTIONS"
    river_locs = ["DATE","CAIRO","ARK CITY","VICKS","NATCHEZ", "KNOX LDG", "RR LDG", "B.R.", "D'VILLE","RESERVE","N.O."]
    num_pred = 11
    # Get the dates
    time_pred10 = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+num_pred+1,0]]
    dates_pred10 = [datetime.strftime(x, "%m/%d") for x in time_pred10] # this is what goes in table
    # Get names of the days of the week
    get_wkday = [datetime.weekday(x) for x in time_pred10]
    daysofweek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] # set list of days of week for changing forecast to loop through
    weekday_pred = [daysofweek[get_wkday[y-1]] for y in get_wkday] # this is what goes in table

    # Pre-allocate table entries
    cairo_pred = np.zeros(num_pred)
    arkcity_pred = np.zeros(num_pred)
    vicks_pred = np.zeros(num_pred)
    natchez_pred = np.zeros(num_pred)
    knox_pred = np.zeros(num_pred)
    rr_ldg_pred = np.zeros(num_pred)
    br_pred = np.zeros(num_pred)
    dville_pred = np.zeros(num_pred)
    reserve_pred = np.zeros(num_pred)
    no_pred = np.zeros(num_pred)

    pred_data = list(zip(weekday_pred,cairo_pred,arkcity_pred,vicks_pred,natchez_pred,knox_pred,
            rr_ldg_pred,br_pred,dville_pred,reserve_pred,no_pred))
    pred_table = pd.DataFrame(pred_data, columns = river_locs, index = dates_pred10)
    


        
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(path_out5 + '\\MS Stages&amp;Hgraphs_' + today_date + '.pdf') as export_pdf:
        ############################### Plot Stages for New Orleans ##########################
        fcst28 = np.array(fcst_28day)
        k, l = np.where(fcst28=="NORL1") # used k and l as indices since i,j had been used

        dates_fcst21_NO = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]

        ######## Plot river stage forecast for 21 days
        # Set figure and subplot sizes
        plt.figure(figsize=[11,8.5])
        ax_NO1 = plt.subplot2grid((7,3),(0,0),rowspan=7)
        ax_NO2 = plt.subplot2grid((7,3),(1,1),colspan=2,rowspan=3)
        
        # MISSISSIPPI RIVER AT NEW ORLEANS 21-DAY FORECAST TABLE
        # Get the dates
        time_pred21 = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]
        dates_pred21 = [datetime.strftime(x, "%m/%d") for x in time_pred21] # this is what goes in table
        #pre-allocate stages
        stage_no = np.zeros(21)
        flow_no = np.zeros(21)

        fcst_hdr = ["Date","Stage","Flow"] # column headers
        pred_no = list(zip(dates_pred21,stage_no,flow_no))

        # Plot table
        pred_NO21 = pd.DataFrame(pred_no, columns = fcst_hdr)
        table_NO = render_mpl_table(pred_NO21,col_width=0.5,ax=ax_NO1)# Plot table as left subplot
        table_NO.axis('off')

        ## Plot time series
        fcst_28_NO = np.float64(fcst28[int(k)+1:int(k)+21+1,int(l)])
        ax_NO2
        plt.plot_date(dates_fcst21_NO,fcst_28_NO,fmt='--', color='purple',xdate=True,ydate=False)
        
        # Add condtionals for the y-limits to adjust for scaling
        if np.max(fcst_28_NO) >= 14:
            plt.ylim((10, 20))
            plt.hlines(11, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'r') # Stage 1 Flood Marker
            plt.hlines(15, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'g') # Stage 2 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1','Phase 2'],loc="lower left")
        elif np.max(fcst_28_NO) >= 10 and np.max(fcst_28_NO) < 14:
            plt.ylim((6, 16))
            plt.hlines(11, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'r') # Stage 1 Flood Marker
            plt.hlines(15, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'g') # Stage 2 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1','Phase 2'],loc="lower left")
        elif np.max(fcst_28_NO) < 10:
            plt.ylim((2, 12))
            plt.hlines(11, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'r') # Stage 1 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1'],loc="lower left")

        plt.xlim((dates_fcst21_NO[0],dates_fcst21_NO[-1]))
        plt.hlines(11, dates_fcst21_NO[0],dates_fcst21_NO[-1], colors = 'r') # Stage 1 Flood Marker
        plt.gca().set
        plt.grid(True)
        plt.xticks(dates_fcst21_NO )
        plt.xticks(dates_fcst21_NO[0:21:5],dates_fcst21_NO[0:21:5] )
        plt.title("Mississippi River at New Orleans")
        plt.xlabel("River Stage (ft)")
        

        plt.tight_layout()
        export_pdf.savefig()
        plt.close()

        del k, l
        ############################### Plot Stages for Red River Landing ##########################
        fcst28 = np.array(fcst_28day)
        k, l = np.where(fcst28=="RRLL1") # used k and l as indices since i,j had been used

        dates_fcst21_RR = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]
        
        # Set figure and subplot sizes
        plt.figure(figsize=[11,8.5])
        ax_RR1 = plt.subplot2grid((7,3),(0,0),rowspan=7)
        ax_RR2 = plt.subplot2grid((7,3),(1,1),colspan=2,rowspan=3)
        
        # MISSISSIPPI RIVER AT RED RIVER LANDING 21-DAY FORECAST TABLE
        #pre-allocate stages
        stage_rr = np.zeros(21)
        flow_rr = np.zeros(21)

        fcst_hdr = ["Date","Stage","Flow"] # column headers
        pred_rr = list(zip(dates_pred21,stage_rr,flow_rr))

        # Plot table
        pred_RR21 = pd.DataFrame(pred_rr, columns = fcst_hdr)
        table_RR = render_mpl_table(pred_RR21,col_width=0.5,ax=ax_RR1)# Plot table as left subplot
        table_RR.axis('off')

        ## Plot time series
        ######## Plot river stage forecast for 21 days
        fcst_28_RR = np.float64(fcst28[int(k)+1:int(k)+21+1,int(l)])
        ax_NO2
        plt.plot_date(dates_fcst21_RR,fcst_28_RR,fmt='--', color='purple',xdate=True,ydate=False)
        # Add condtionals for the y-limits to adjust for scaling
        if np.max(fcst_28_RR) >= 55:
            plt.ylim((45, 65))
            plt.hlines(48, dates_fcst21_RR[0],dates_fcst21_RR[-1], colors = 'r') # Stage 1 Flood Marker
            plt.hlines(56, dates_fcst21_RR[0],dates_fcst21_RR[-1], colors = 'g') # Stage 1 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1','Phase 2'],loc="lower left")
        elif np.max(fcst_28_RR) >= 45 and np.max(fcst_28_RR) < 55:
            plt.ylim((40, 60))
            plt.hlines(48, dates_fcst21_RR[0],dates_fcst21_RR[-1], colors = 'r') # Stage 1 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1'],loc="lower left")
        elif np.max(fcst_28_RR) >= 35 and np.max(fcst_28_RR) < 45:
            plt.ylim((30, 50))
            plt.hlines(48, dates_fcst21_RR[0],dates_fcst21_RR[-1], colors = 'r') # Stage 1 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1'],loc="lower left")
        elif np.max(fcst_28_RR) >= 25 and np.max(fcst_28_RR) < 35:
            plt.ylim((20, 40))
            plt.legend(['NWS Stage (ft)'],loc="lower left")
        elif np.max(fcst_28_RR) >= 15 and np.max(fcst_28_RR) < 25:
            plt.ylim((10, 30))
            plt.legend(['NWS Stage (ft)'],loc="lower left")        
        elif np.max(fcst_28_RR) < 15:
            plt.ylim((0, 20))
            plt.legend(['NWS Stage (ft)'],loc="lower left") 

        plt.xlim((dates_fcst21_RR[0],dates_fcst21_RR[-1]))
        #     plt.hlines(11, dates_fcst21_RR[0],dates_fcst21_RR[-1], colors = 'r') # Stage 1 Flood Marker
        plt.gca().set
        plt.grid(True)
        plt.xticks(dates_fcst21_RR )
        plt.xticks(dates_fcst21_RR[0:21:5],dates_fcst21_RR[0:21:5] )
        plt.title("Mississippi River at Red River Landing")
        plt.xlabel("River Stage (ft)")
        plt.tight_layout()
        export_pdf.savefig()
        plt.close()

        ############ Plot table for stage forecast at all Lower Mississippi River sites
        plt.figure(figsize=[11,8.5])
        render_mpl_table(pred_table, header_columns=0, col_width=1.5,rowLabels=pred_table.index)
        export_pdf.savefig()
        plt.close()


# In[1]:





# In[ ]:




