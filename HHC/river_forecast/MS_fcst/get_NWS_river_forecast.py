#!/usr/bin/env python
# coding: utf-8

# ## Gets River Forecast Data (5- and 28- Day) from NWS
# https://www.weather.gov/lmrfc/obsfcst_mississippi

# In[2]:


def get_nws_fcst(file_out5,file_out28,today_date):
    import requests as req
    import urllib.request as urlreq
    import time
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    import os
    from datetime import datetime
    import matplotlib.pyplot as plt

    
    #################### NWS Observations and Forecasts for the Lower Mississippi/Ohio site ##################
    nws = req.get('https://www.weather.gov/lmrfc/obsfcst_mississippi')

    # Parse html data from website
    nws_html = BeautifulSoup(nws.text, "html.parser") # NOTE: data is pre-formatted <pre>

    ######### find 5- and 28-day forecasts
    ind_5day=['']*len(nws_html.findAll('a'))
    ind_28day=['']*len(nws_html.findAll('a'))
    for i in range(len(nws_html.findAll('a'))):
        ind_5day[i] = 'Lower Mississippi River 5-day Forecast Summary' in str(nws_html.findAll('a')[i])
        ind_28day[i] = 'Lower Mississippi River 28-day Forecast Summary' in str(nws_html.findAll('a')[i]) 

    ###################### Get 5-day forecast data ##########################
    dum = nws_html.findAll('a')[int(np.where(np.array(ind_5day)==True)[0])]#[118]
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

    # get today's stage at Red River Landing
    array_5day = np.array(fcst_5day)
    i_rrl, j_rrl = np.where(array_5day=='RED RIVER LNDG')
    i_stg, j_stg = np.where(array_5day=='STG')

    rrl_stg_today = np.float(array_5day[i_rrl,j_stg])

    # Pause so website doesn't think we're a hacker (probably more relevant for loops)
    time.sleep(1)

    ##################### Get 28-day forecast data ############################
    dum1 = nws_html.findAll('a')[int(np.where(np.array(ind_28day)==True)[0])]#[119]
    pred_28day = dum1['href']
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
        

    ###############################  Stages for New Orleans ##########################
    fcst28 = np.array(fcst_28day)
    k, l = np.where(fcst28=="NORL1") # find NO fcst; used k and l as indices since i,j had been used

    dates_fcst21_NO = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]

    # Get the dates
    time_pred21 = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]
    dates_pred21 = [datetime.strftime(x, "%m/%d") for x in time_pred21] # this is what goes in table

    fcst_21_NO = np.float64(fcst28[int(k)+1:int(k)+21+1,int(l)])

    del k, l
    ###############################  Stages for Red River Landing ##########################
    fcst28 = np.array(fcst_28day)
    k, l = np.where(fcst28=="RRLL1") # used k and l as indices since i,j had been used

    # River stage forecast for 21 days
    dates_fcst21_RR = [datetime.strptime(x, "%m-%d-%y").date() for x in fcst28[int(k)+1:int(k)+22,0]]
    fcst_21_RR = np.float64(fcst28[int(k)+1:int(k)+21+1,int(l)])

    return time_pred21, dates_pred21, fcst_21_NO, fcst_21_RR, rrl_stg_today


# In[ ]:




