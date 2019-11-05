print("Importing arcpy...")
import arcpy
import os
import sys
arcpy.env.overwriteOutput = True
print("Done!")

#wrkdir=os.getcwd()
abs_path=sys.path[0]

def get_prj():
    prj_ = open(abs_path+'\\prj_path.txt',"r+")
    prj_path=prj_.readline()
    prj_.close()
    return prj_path

def get_inputs():
    inputs_ = open(abs_path+'\\inputs_path.txt',"r+")
    inputs_path=inputs_.readline()
    inputs_.close()
    return inputs_path

try:
    prjpath=get_prj()
except:
    print("prj not set, need to write out prj_path.txt")
    
try:
    inputs=get_inputs()
except:
    print("input path not set, need to write out inputs_path.txt")
          
temp=inputs+"\\..\\projection_temp.shp" #arc needs a temporary shape file
          
def CRMS_projection(file1,out,prj):
	arcpy.ConvertCoordinateNotation_management(file1,
                                                   temp,
                                                   "Longitude",
                                                   "Latitude",
                                                   "",
                                                   "",
                                                   "Station_ID",
                                                   prj,
                                                   "")
	arcpy.AddXY_management(temp)
	arcpy.ExportXYv_stats(temp,
                              ["POINT_X","POINT_Y"],
                              "COMMA",
                              out,
                              "ADD_FIELD_NAMES")

output=inputs+"\\..\\test_1.txt"
#output=prjpath+"\\..\\test_1.txt"
print(output)
print(inputs)
CRMS_projection(inputs,output,prjpath)
