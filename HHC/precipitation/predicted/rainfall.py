
# coding: utf-8

# In[ ]:
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import urllib
import sys
import csv
#import PyQt5 as pyqt

#-----------------------------#
#import ssl
#from functools import wraps
#def sslwrap(func):
#    @wraps(func)
#    def bar(*args, **kw):
#        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
#        return func(*args, **kw)
#    return bar

#ssl.wrap_socket = sslwrap(ssl.wrap_socket)

#-----------------------------#
fm_int=[1,2,3,6,12,24,36,72,144,288,576,864,1152,2016,2880,5760,8640,12960,17280]
duration_list=[]
ARI_list=[]
data=[]
rain_int=[]
rain_dist=[]
time_series=[]

lat=float(raw_input("Latitude in decimal degrees? "))
lon=float(raw_input("Longitude in decimal degrees? "))
lat=(str("%.4f" % lat))
lon=(str("%.4f" % lon))
ari=str(raw_input("Return period years?(1,2,5,10,etc.. or all) "))
dur=str(raw_input("Storm duration?(5-min,1-hr,2-day, etc...) "))

urllib.urlretrieve('https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/fe_text_mean.csv?lat='+lat+'&lon='+lon+'&data=depth&units=english&series=pds', 'rainfall_data.csv');
#request.get('https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/fe_text_mean.csv?lat='+lat+'&lon='+lon+'&data=depth&units=english&series=pds', 'rainfall_data.csv');
with open('rainfall_data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    rawdata=[]
    for row in csv_reader:
        rawdata.append(row)

for i in range(len(rawdata)):
    if rawdata[i] == ['PRECIPITATION FREQUENCY ESTIMATES']:
        begin_data=i+1
    else:
        pass
for i in range(len(rawdata)-3):
    if i >= begin_data:
        test=[]
        for j in range(len(rawdata[i])):
            if j>0 and i==begin_data:
                ARI_list.append(str(int(rawdata[i][j])))
            elif j>0:
                test.append(rawdata[i][j])       
        if i >begin_data:
            data.append(test)
            duration_list.append(rawdata[i][0][0:-1])
duration=dict([(key,i) for (i,key) in enumerate(duration_list)])
ARI=dict([(key,i) for (i,key) in enumerate(ARI_list)])


if ari=='all':

    dur1=duration[str(dur)]+1
    time_series_all=[]
    for t in range(len(ARI)):
        rain_int=[]
        for j in range(len(duration)):
            if j==0:
                rain_int.append(float(data[j][t]))
            else:
                rain_int.append(float(data[j][t])- float(data[j-1][t]))
        rain_dist=[]
        for i in range(int(dur1)):
            if i==0:
                rain_dist.append(rain_int[0])
            else:
                a=int((fm_int[i]-fm_int[i-1]))
                for j in range(a):
                    rain_dist.append(float("%.4f" % (rain_int[i]/a)))
        time_series=[]
        for i in range(len(rain_dist)):
            if i%2 == 0:
                time_series.append(rain_dist[i])
            else:
                time_series.insert(0,rain_dist[i])
        time_series_all.append(time_series)    
        plt.plot(range(fm_int[int(dur1-1)]),time_series)

    plt.show()
    tsa=np.array(time_series_all)
    tsa=np.transpose(tsa)
    np.savetxt("rainfall_timeseries_all.csv", tsa, delimiter=",")

else:
    ari=ARI[str(ari)]

    for i in range(1):#len(ARI))
        for j in range(len(duration)):
            if j==0:
                rain_int.append(float(data[j][ari]))
            else:
                rain_int.append(float(data[j][ari])- float(data[j-1][ari]))


    dur1=duration[str(dur)]+1
    for i in range(int(dur1)):
        if i==0:
            rain_dist.append(rain_int[0])
        else:
            a=int((fm_int[i]-fm_int[i-1]))
            for j in range(a):
                rain_dist.append(float("%.4f" % (rain_int[i]/a)))

    for i in range(len(rain_dist)):
        if i%2 == 0:
            time_series.append(rain_dist[i])
        else:
            time_series.insert(0,rain_dist[i])

    ts=np.array(time_series)
    ts=np.transpose(ts)
    np.savetxt("rainfall_timeseries.csv", ts, delimiter=",")

    plt.plot(range(fm_int[int(dur1-1)]),time_series)
    plt.show()



# In[ ]:




# In[ ]:




# In[ ]:



