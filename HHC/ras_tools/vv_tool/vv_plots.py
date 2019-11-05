import h5py as h5
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

abs_path=sys.path[0]

def path_write(path,string):
    with open(path, 'w') as the_file:
        the_file.write(string)
        the_file.close()

def crms_set_projection():
    global vv_locations
    print("converting CRMS coordinate to RAS projection")
    os.system('cmd /k "C:\Python27\ArcGIS10.2\python.exe projection.py"')
    vv_locations=np.loadtxt(abs_path+"//test_1.txt",delimiter=',',dtype='str')
    print("done!")
    
def read_ras(hdf):
    global vv_flow_areas_2d, vv_ras_results
    vv_ras_results=h5.File(hdf,'r')
    vv_flow_areas_2d=[]
    for i in range(len(vv_ras_results['/Geometry/2D Flow Areas'].values())):
        if str(list(vv_ras_results['/Geometry/2D Flow Areas'].values())[i]).split()[1] == 'group':
            vv_flow_areas_2d.append(str(list(vv_ras_results['/Geometry/2D Flow Areas'].values())[i])[37:-15])
    return vv_flow_areas_2d
        
def crms_ras_results(results,flow_areas_2d):
    global crms_ras_xy,crms_ras_swl,crms_ras_dep
    xy=np.array([])
    swl=np.array([])
    dep=np.array([])
    for i in range(len(flow_areas_2d)):
        try:
            swl_=results['/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/'+flow_areas_2d[i]+'/Water Surface']
            xy_=results['/Geometry/2D Flow Areas/'+flow_areas_2d[i]+'/Cells Center Coordinate']
            dep_=results['/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/'+flow_areas_2d[i]+'/Depth']
        
            xy=np.concatenate([xy,xy_]) if xy.size else xy_
            swl=np.concatenate([swl,swl_],axis=1) if swl.size else swl_
            dep=np.concatenate([dep,dep_],axis=1) if dep.size else dep_
        except:
            pass
    crms_ras_xy=xy
    crms_ras_swl=swl
    crms_ras_dep=dep

def crms_gather_data(CRMS_data,CRMS_info):
    CRMS_data_in=np.loadtxt(CRMS_data,delimiter=',',dtype='str')
    CRMS_info_in=np.loadtxt(CRMS_info,delimiter=',',dtype='str')
    global CRMS_gauge_results
    CRMS_gauge_results=[]
    for i in range(len(CRMS_info_in)-1):
        CRMS_data_temp=[]
        for j in range(len(CRMS_data_in)):
            if CRMS_data_in[j][0]==CRMS_info_in[i+1][0]:
                str2float=CRMS_data_in[j][3].replace('"', '')
                #CRMS_data_temp.append([CRMS_data_in[j][1],float(str2float)])
                CRMS_data_temp.append(float(str2float))
            else:
                pass
        CRMS_gauge_results.append(CRMS_data_temp)    
    
def vv_plots(crms_ras_xy,crms_ras_swl,locations,CRMS,output_dir):
    global vv_locations_indices
    vv_locations_indices=[]
    for i in range(len(locations[:,0])-1):
        vv_locations_indices.append(griddata((crms_ras_xy[:,0],
                                               crms_ras_xy[:,1]),
                                              np.array(list(range(len(crms_ras_xy)))),
                                              (locations[i+1,0],locations[i+1,1]),
                                              method='nearest'))
        plt.figure()
        plt.ylim(0.0, 5.0) 
        plt.plot(crms_ras_swl[:,vv_locations_indices[i]])
        plt.plot(np.array(CRMS_gauge_results)[i,:])
        plt.savefig(output_dir+'\\vv_'+str(i)+'.png')
        plt.show()
