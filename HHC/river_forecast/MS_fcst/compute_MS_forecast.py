#!/usr/bin/env python
# coding: utf-8

# ## Gets River Forecast Data (5- and 28- Day)

# In[3]:


def compute_USACE_MS_forecast(fcst_rrl_adjusted,time_pred21,dates_pred21,nws_21_NO,nws_21_RR,file_out5,file_out28,today_date,fcst_num):
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
    
    import ntpath
    path_out5 = ntpath.dirname(file_out5)
    
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
                cell.set_text_props(weight='bold', color='w'), 
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
        return ax

    
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(path_out5 + '\\MS Stages&amp;Hgraphs_' + today_date + '.pdf') as export_pdf:
        ############################### Plot Stages for New Orleans ##########################
        # Set figure and subplot sizes
        plt.figure(figsize=[11,8.5])
        ax_NO1 = plt.subplot2grid((7,3),(0,0),rowspan=7)
        ax_NO2 = plt.subplot2grid((7,3),(1,1),colspan=2,rowspan=3)
        
        # MISSISSIPPI RIVER AT NEW ORLEANS 21-DAY FORECAST TABLE
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
        ax_NO2
        plt.plot_date(dates_pred21,nws_21_NO,fmt='--', color='purple',xdate=True,ydate=False)
        
        # Add condtionals for the y-limits to adjust for scaling
        if np.max(nws_21_NO) >= 14:
            plt.ylim((10, 20))
            plt.hlines(11, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
            plt.hlines(15, dates_pred21[0],dates_pred21[-1], colors = 'g') # Stage 2 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1 (11 ft)','Phase 2 (15 ft)'],loc="lower left")
        elif np.max(nws_21_NO) >= 10 and np.max(nws_21_NO) < 14:
            plt.ylim((6, 16))
            plt.hlines(11, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
            plt.hlines(15, dates_pred21[0],dates_pred21[-1], colors = 'g') # Stage 2 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1 (11 ft)','Phase 2 (15 ft)'],loc="lower left")
        elif np.max(nws_21_NO) < 10:
            plt.ylim((2, 12))
            plt.hlines(11, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
            plt.legend(['NWS Stage (ft)','Phase 1 (11 ft)'],loc="lower left")

        plt.xlim((dates_pred21[0],dates_pred21[-1]))
        plt.hlines(11, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
        plt.gca().set
        plt.grid(True)
        plt.xticks(dates_pred21 )
        plt.xticks(dates_pred21[0:21:5],dates_pred21[0:21:5] )
        plt.title("Mississippi River at New Orleans")
        plt.xlabel("River Stage (ft)")
        

        plt.tight_layout()
        export_pdf.savefig()
        plt.close()

        ############################### Plot Stages for Red River Landing ##########################
        # Set figure and subplot sizes
        plt.figure(figsize=[11,8.5])
        ax_RR1 = plt.subplot2grid((7,3),(0,0),rowspan=7)
        ax_RR2 = plt.subplot2grid((7,3),(1,1),colspan=2,rowspan=3)
        
        # MISSISSIPPI RIVER AT RED RIVER LANDING 21-DAY FORECAST TABLE
        #pre-allocate stages
        stage_rr = list(fcst_rrl_adjusted) #np.zeros(21)
        flow_rr = np.zeros(21)

        fcst_hdr = ["Date","Stage","Flow"] # column headers
        pred_rr = list(zip(dates_pred21,stage_rr,flow_rr))

        # Plot table
        pred_RR21 = pd.DataFrame(pred_rr, columns = fcst_hdr)
        table_RR = render_mpl_table(pred_RR21,col_width=0.5,ax=ax_RR1)# Plot table as left subplot
        table_RR.axis('off')

        ## Plot time series
        ######## Plot river stage forecast for 21 days
        ax_NO2
        plt.plot_date(dates_pred21,fcst_rrl_adjusted,fmt='-o',xdate=True,ydate=False)
        plt.plot_date(dates_pred21,nws_21_RR,fmt='--', color='purple',xdate=True,ydate=False)
        
        # Add condtionals for the y-limits to adjust for scaling
        # round to 0 or 5
        def myround(x, base=5):
            return base * round(x/base)
        ## way to automatically find ylimits
        find_ylim = myround(np.max([nws_21_RR,fcst_rrl_adjusted]))
        plt.ylim((find_ylim-15,find_ylim+5))
        plt.hlines(48, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
        plt.hlines(56, dates_pred21[0],dates_pred21[-1], colors = 'g') # Stage 1 Flood Marker
        plt.legend(['USACE Stage (ft)','NWS Stage (ft)','Phase 1 (48 ft)','Phase 2 (56 ft)'],loc="lower left")        
#         if np.max(nws_21_RR) >= 55:
#             plt.ylim((45, 65))
#             plt.hlines(48, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
#             plt.hlines(56, dates_pred21[0],dates_pred21[-1], colors = 'g') # Stage 1 Flood Marker
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)','Phase 1','Phase 2'],loc="lower left")
#         elif np.max(nws_21_RR) >= 45 and np.max(nws_21_RR) < 55:
#             plt.ylim((40, 60))
#             plt.hlines(48, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)','Phase 1'],loc="lower left")
#         elif np.max(nws_21_RR) >= 35 and np.max(nws_21_RR) < 45:
#             plt.ylim((30, 50))
#             plt.hlines(48, dates_pred21[0],dates_pred21[-1], colors = 'r') # Stage 1 Flood Marker
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)','Phase 1'],loc="lower left")
#         elif np.max(nws_21_RR) >= 25 and np.max(nws_21_RR) < 35:
#             plt.ylim((20, 40))
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)'],loc="lower left")
#         elif np.max(nws_21_RR) >= 15 and np.max(nws_21_RR) < 25:
#             plt.ylim((10, 30))
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)'],loc="lower left")        
#         elif np.max(nws_21_RR) < 15:
#             plt.ylim((0, 20))
#             plt.legend(['USACE Stage (ft)','NWS Stage (ft)'],loc="lower left") 

        plt.xlim((dates_pred21[0],dates_pred21[-1]))
        plt.gca().set
        plt.grid(True)
        plt.xticks(dates_pred21 )
        plt.xticks(dates_pred21[0:21:5],dates_pred21[0:21:5] )
        plt.title("Mississippi River at Red River Landing")
        plt.xlabel("River Stage (ft)")
        plt.tight_layout()
        export_pdf.savefig()
        plt.close()

        ############ Plot table for stage forecast at all Lower Mississippi River sites
        # RIVER STAGE PREDICTIONS TABLE
        river_title = "RIVER STAGE PREDICTIONS"
        river_locs = ["DATE","CAIRO","ARK CITY","VICKS","NATCHEZ", "KNOX LDG", "RR LDG", "B.R.", "D'VILLE","RESERVE","N.O."]
        num_pred = 11
        # Get the dates
        time_pred10 = time_pred21[0:10]
        dates_pred10 = dates_pred21[0:10]
        # Get names of the days of the week
        get_wkday = [datetime.weekday(x) for x in time_pred10]
        daysofweek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] # set list of days of week for changing forecast to loop through
        weekday_pred = [daysofweek[get_wkday[y-1]] for y in get_wkday] # this is what goes in table

        cairo_pred = ['']*num_pred#np.zeros(num_pred)
        arkcity_pred = ['']*num_pred#np.zeros(num_pred)
        vicks_pred = ['']*num_pred#np.zeros(num_pred)
        natchez_pred = ['']*num_pred#np.zeros(num_pred)
        knox_pred = ['']*num_pred#np.zeros(num_pred)
        rr_ldg_pred = fcst_rrl_adjusted[0:num_pred]#np.zeros(num_pred)
        br_pred = ['']*num_pred#np.zeros(num_pred)
        dville_pred = ['']*num_pred#np.zeros(num_pred)
        reserve_pred = ['']*num_pred#np.zeros(num_pred)
        no_pred = ['']*num_pred#np.zeros(num_pred)

        pred_data = list(zip(weekday_pred,cairo_pred,arkcity_pred,vicks_pred,natchez_pred,knox_pred,
                rr_ldg_pred,br_pred,dville_pred,reserve_pred,no_pred))
        
        # Merge into table
        pred_table = pd.DataFrame(pred_data, columns = river_locs, index = dates_pred10)

        plt.figure(figsize=[11,8.5])
        render_mpl_table(pred_table, header_columns=0, col_width=1.5,rowLabels=pred_table.index)
        export_pdf.savefig()
        plt.close()


# In[2]:





# In[ ]:




