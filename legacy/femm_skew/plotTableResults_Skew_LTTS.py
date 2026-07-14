#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 13:23:25 2024

@author: harsha
"""
import os
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pprint import pprint

import scipy

PROCESS_ALL = 1
PROCESS_SPEEDTABLE = 0
PROCESS_LDTABLE = 0
PROCESS_LQTABLE = 0
PROCESS_TORQUE_TABLE = 0
PROCESS_ANALYTICAL_TORQUE_TABLE = 0
PROCESS_PERCENTAGE_OF_RELUCTANCE_TORQUE = 0
PROCESS_PSID_TABLE = 0
PROCESS_PSIQ_TABLE = 0
TORQUE_CURVE  = 0
SPEED_CONTOUR_MAP = 1
PHASE_ANGLE_MAP = 0
PROCESS_PSID_PK = 0

IS_MAP = 0
TORQUE_SPEED_CURVE = 0

LTTS_CSV = 1
SAVE_ALL = 1


#LTTS
currentCircles = [300,285,250,200,150,120]
speedEllipses =[5500,6000,7200,9000,10500,12000]
torque_hyperbolas = [50,70,100,150,180]
gridIdMax = -301
gridIqMax = 301
FW_angles = [30,60,70]

# 1K2
# currentCircles = [165,135,100,75,50]
# speedEllipses =[500,1000,2000,3000,4000,8000,12000,15000]
# torque_hyperbolas = [4,10,15,20,25,30,35]
# gridIdMax = -201
# gridIqMax = 200qq


imgWidth,imgHeight = (18,10) #in inches

fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_60C.FEM" # stack length of the motor has to be set in the file correctly
# fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_60C_manufacturing.FEM" # stack length of the motor has to be set in the file correctly
rootFolder = os.path.dirname(fem_file)
filename = os.path.basename(fem_file)
datafolder = rootFolder +"\\"+filename[:-4]+"\\SkewOutputs_4Slices\\OL\\"
saveFolder = rootFolder +"\\"+filename[:-4]+"\\SkewOutputs_4Slices\\summarisedData\\"
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)


filenameDict = {}
#dict has current and currentAngles as a dicts
if os.path.exists(datafolder):
    fpaths1 = glob(os.path.join(os.path.realpath(datafolder)+'\\results*.csv'))
    fpaths1 = sorted(fpaths1)
    print(fpaths1)
    for filepath in enumerate(fpaths1):
        filename = os.path.basename(filepath[1])
        parts1 = filename.split("_")
        Iq = parts1[1]
        Id = parts1[2]
        if Iq in filenameDict.keys():
            filenameDict[Iq][Id] = filename
        else:
            filenameDict[Iq]={}
            filenameDict[Iq][Id] = filename
print ("Looking in folder - " + str(datafolder))
print ("Filename and current Angles available along with their filenames:")
pprint (filenameDict)


def getDF_from_FileDict(folder,filenameDict,searchIq,searchId):
    df = None
    for Iq in filenameDict.keys():
        if Iq == searchIq:
            currentDict = filenameDict[Iq]        
            for Id in currentDict.keys():
                if (Id == searchId):
                    filename = currentDict[Id]
                    csvpath = folder + filename
                    df = pd.read_csv(csvpath)
    return df

#calculate psi,psiQ and ld and Lq for each excel row.

if (PROCESS_SPEEDTABLE or PROCESS_ALL):
     columnHeadings = []
     for key in filenameDict.keys():
         columnHeadings.append(int(key))
     columnHeadings = sorted(columnHeadings)
     
     rowHeadings=[]
     for key in filenameDict.keys():
         for CA in filenameDict[key].keys():
             if int(CA) not in rowHeadings:
                 rowHeadings.append(int(CA))
     rowHeadings = sorted(rowHeadings)
     
     speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for Iq in filenameDict.keys():
         currentDict = filenameDict[Iq]
         for Id in currentDict.keys():
             filename = currentDict[Id]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             topSpeed = float(df.loc["maxRPM","Values"])
             speedDF.loc[int(Id),float(Iq)] = np.around(topSpeed,0)
             
     #print(speedDF)
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
    
     data = np.abs(speedDF.values)
     
     #drawing the table
     fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))


     #colorMap customization
     cmapColorBar = plt.cm.Blues
     MODIFY_CBAR_RANGE = 1
     if MODIFY_CBAR_RANGE:
         minColorNo = 5000
         maxColorNo = 12000
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=minColorNo, vmax=maxColorNo)
     else:
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=np.nanmin(data), vmax=np.nanmax(data))


     # put the major ticks at the middle of each cell
     ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
     ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
     
     ax.set_xlabel("Iq RMS in Amps")
     ax.set_ylabel("Id RMS in Amps")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(speedDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, int(speedDF[y_][x_]),
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
     
     # want a more natural, table-like display
     #ax.invert_yaxis()
     ax.xaxis.tick_top()
     ax.xaxis.set_label_position('top') 
     
     ax.set_xticklabels(columnHeadings, minor=False)
     ax.set_yticklabels(rowHeadings, minor=False)

     """
     #stopped working- not sure why. removing it for now
     #will not show any color bar
     #customize the colorbar
     cbar = plt.colorbar(heatmap)
     if MODIFY_CBAR_RANGE:
         cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
         for label in cbarLabels:
             if label.get_text()==str(minColorNo):
                 label.set_text("<="+str(minColorNo))
             if label.get_text()==str(maxColorNo): 
                 label.set_text(">="+str(maxColorNo))
         cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
     plt.suptitle ("Max Speed Possible (RPM) vs Iq(RMS) and Id(RMS)")

     if SAVE_ALL:
         speedDF.T.to_csv(saveFolder + "speedMap.csv")
         plt.savefig(saveFolder + "speedMap.png")        

     plt.show()


     
    
# calculate psi,psiQ and ld and Lq for each excel row.
if (PROCESS_ANALYTICAL_TORQUE_TABLE or PROCESS_ALL):
     columnHeadings = []
     for key in filenameDict.keys():
         columnHeadings.append(int(key))
     columnHeadings = sorted(columnHeadings)
     
     rowHeadings=[]
     for key in filenameDict.keys():
         for CA in filenameDict[key].keys():
             if int(CA) not in rowHeadings:
                 rowHeadings.append(int(CA))
     rowHeadings = sorted(rowHeadings)
                  
     torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for Iq in filenameDict.keys():
        currentDict = filenameDict[Iq]
        for Id in currentDict.keys():
            filename = currentDict[Id]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            torque = float(df.loc["analyticalTorque_total","Values"])
            torqueDF.loc[int(Id),float(Iq)] = int(torque)
                # print(speedDF)
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
     torqueDF = torqueDF.astype('int')
     data = np.abs(torqueDF.values)
     
     #drawing the table
     cmapColorBar = plt.cm.PuRd
     fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
     heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                         vmin=np.nanmin(data), vmax=np.nanmax(data))
     # heatmap.cmap.set_under('black')
     # put the major ticks at the middle of each cell
     ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
     ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
     
     ax.set_xlabel("Iq RMS in Amps")
     ax.set_ylabel("Id RMS in Amps")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(torqueDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, torqueDF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'medium'
                           )
     
     # want a more natural, table-like display
     #ax.invert_yaxis()
     ax.xaxis.tick_top()
     ax.xaxis.set_label_position('top') 
     
     ax.set_xticklabels(columnHeadings, minor=False)
     ax.set_yticklabels(rowHeadings, minor=False)
     
     #plt.colorbar(heatmap)
     plt.suptitle ("Analytical Torque vs Iq(RMS) and Id(RMS)")

     if SAVE_ALL:
         torqueDF.T.to_csv(saveFolder + "analyticalTorque.csv")
         plt.savefig(saveFolder + "analyticalTorque.png")
         
     plt.show() 
     
# calculate psi,psiQ and ld and Lq for each excel row.
if (PROCESS_PERCENTAGE_OF_RELUCTANCE_TORQUE or PROCESS_ALL):
     columnHeadings = []
     for key in filenameDict.keys():
         columnHeadings.append(int(key))
     columnHeadings = sorted(columnHeadings)
     
     rowHeadings=[]
     for key in filenameDict.keys():
         for CA in filenameDict[key].keys():
             if int(CA) not in rowHeadings:
                 rowHeadings.append(int(CA))
     rowHeadings = sorted(rowHeadings)
     
             
     relPercentDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for Iq in filenameDict.keys():
        currentDict = filenameDict[Iq]
        for Id in currentDict.keys():
           filename = currentDict[Id]
           csvpath = datafolder + filename
           df = pd.read_csv(csvpath,index_col=0)
           magTorque = float(df.loc["magneticTorque","Values"])
           relTorque = float(df.loc["reluctanceTorque","Values"])
           relPercentDF.loc[int(Id),float(Iq)] = np.abs(np.around(relTorque*100/(magTorque+ relTorque),1))

           
     # print(speedDF)
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
    
     data = np.abs(relPercentDF.values)
     
     #drawing the table
     fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
     
     #colorMap customization
     cmapColorBar = plt.cm.BuGn
     MODIFY_CBAR_RANGE = 1
     if MODIFY_CBAR_RANGE:
         minColorNo = np.nanmin(data)
         maxColorNo = 20.0
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=minColorNo, vmax=maxColorNo)
     else:
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=np.nanmin(data), vmax=np.nanmax(data))


     # heatmap.cmap.set_under('black')
     # put the major ticks at the middle of each cell
     ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
     ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
     
     ax.set_xlabel("Iq RMS in Amps")
     ax.set_ylabel("Id RMS in Amps")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(relPercentDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, relPercentDF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'medium'
                           )
     
     # want a more natural, table-like display
     #ax.invert_yaxis()
     ax.xaxis.tick_top()
     ax.xaxis.set_label_position('top') 
     
     ax.set_xticklabels(columnHeadings, minor=False)
     ax.set_yticklabels(rowHeadings, minor=False)

     """
     #customize the colorbar
     cbar = plt.colorbar(heatmap)
     if MODIFY_CBAR_RANGE:
         cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
         for label in cbarLabels:
             # if label.get_text()==str(minColorNo):
             #     label.set_text("<="+str(minColorNo))
             if label.get_text()==str(maxColorNo): 
                 label.set_text(">="+str(maxColorNo))
         cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
     """
     
     plt.suptitle ("Reluctance Torque Percentage vs Iq(RMS) and Id(RMS)")
     if SAVE_ALL:
         relPercentDF.T.to_csv(saveFolder + "relPercent.csv")
         plt.savefig(saveFolder + "relPercent.png")
     plt.show() 
     
# calculate psi,psiQ and ld and Lq for each excel row.
if (PROCESS_TORQUE_TABLE  or PROCESS_ALL):
     print("Processing Torque Table")
     columnHeadings = []
     for key in filenameDict.keys():
         columnHeadings.append(int(key))
     columnHeadings = sorted(columnHeadings)
     
     rowHeadings=[]
     for key in filenameDict.keys():
         for CA in filenameDict[key].keys():
             if int(CA) not in rowHeadings:
                 rowHeadings.append(int(CA))
     rowHeadings = sorted(rowHeadings)
     
     
             
     torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for Iq in filenameDict.keys():
        currentDict = filenameDict[Iq]
        for Id in currentDict.keys():
           filename = currentDict[Id]
           csvpath = datafolder + filename
           df = pd.read_csv(csvpath,index_col=0)
           torque =float(df.loc["OL_torque","Values"]) 
           torqueDF.loc[int(Id),float(Iq)] = np.around(torque,2)
             
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
    
     data = np.abs(torqueDF.values)
     
     #drawing the table
     fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))

     #colorMap customization
     cmapColorBar = plt.cm.Oranges
     MODIFY_CBAR_RANGE = 1
     if MODIFY_CBAR_RANGE:
         minColorNo = 20#np.nanmin(data)
         maxColorNo = 180
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=minColorNo, vmax=maxColorNo)
     else:
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=np.nanmin(data), vmax=np.nanmax(data))

     # put the major ticks at the middle of each cell
     ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
     ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
     
     ax.set_xlabel("Iq RMS in Amps")
     ax.set_ylabel("Id RMS in Amps")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(torqueDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, np.abs(torqueDF[y_][x_]),
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'medium'
                           )
     
     # want a more natural, table-like display
     #ax.invert_yaxis()
     ax.xaxis.tick_top()
     ax.xaxis.set_label_position('top') 
     
     ax.set_xticklabels(columnHeadings, minor=False)
     ax.set_yticklabels(rowHeadings, minor=False)
     
     #customize the colorbar
     """
     cbar = plt.colorbar(heatmap)
     if MODIFY_CBAR_RANGE:
         cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
         for label in cbarLabels:
             if label.get_text()==str(minColorNo):
                 label.set_text("<="+str(minColorNo))
             if label.get_text()==str(maxColorNo): 
                 label.set_text(">="+str(maxColorNo))
         cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
     """
     
     plt.suptitle ("Torque (Nm) vs Iq(RMS) and Id(RMS)")
     if SAVE_ALL:
         torqueDF.T.to_csv(saveFolder + "feaTorque.csv")
         plt.savefig(saveFolder + "feaTorque.png")
     plt.show() 


if (PROCESS_LDTABLE or PROCESS_ALL):
     columnHeadings = []
     for key in filenameDict.keys():
         columnHeadings.append(int(key))
     columnHeadings = sorted(columnHeadings)
     
     rowHeadings=[]
     for key in filenameDict.keys():
         for CA in filenameDict[key].keys():
             if int(CA) not in rowHeadings:
                 rowHeadings.append(int(CA))
     rowHeadings = sorted(rowHeadings)
                  
     LdDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for Iq in filenameDict.keys():
        currentDict = filenameDict[Iq]
        for Id in currentDict.keys():
           filename = currentDict[Id]
           csvpath = datafolder + filename
           df = pd.read_csv(csvpath,index_col=0)
           Ld =float(df.loc["Ld","Values"]) 
           LdDF.loc[int(Id),float(Iq)] = np.around(Ld * 1E6,1)
             
     # print(speedDF)
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
    
     data = np.abs(LdDF.values)
     
     #drawing the table
     fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
     
     #colorMap customization
     cmapColorBar = plt.cm.Greens
     MODIFY_CBAR_RANGE = 1
     if MODIFY_CBAR_RANGE:
         minColorNo =  np.nanmin(data)
         maxColorNo = np.nanmax(data)
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=minColorNo, vmax=maxColorNo)
     else:
         heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                             vmin=np.nanmin(data), vmax=np.nanmax(data))

     # heatmap.cmap.set_under('black')
     # put the major ticks at the middle of each cell
     ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
     ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
     
     ax.set_xlabel("Iq RMS in Amps")
     ax.set_ylabel("Id RMS in Amps")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(LdDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, LdDF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
     
     # want a more natural, table-like display
     #ax.invert_yaxis()
     ax.xaxis.tick_top()
     ax.xaxis.set_label_position('top') 
     
     ax.set_xticklabels(columnHeadings, minor=False)
     ax.set_yticklabels(rowHeadings, minor=False)

     """"
     #customize the colorbar
     cbar = plt.colorbar(heatmap)
     if MODIFY_CBAR_RANGE:
         cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
         for label in cbarLabels:
             if label.get_text()==str(minColorNo):
                 label.set_text("<="+str(minColorNo))
             if label.get_text()==str(maxColorNo): 
                 label.set_text(">="+str(maxColorNo))
         cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
     """    
         
     plt.suptitle ("Ld(uH)vs Iq(RMS) and Id(RMS)")
     if SAVE_ALL:
         LdDF.T.to_csv(saveFolder + "Ld.csv")
         plt.savefig(saveFolder + "Ld.png")
     plt.show() 

if (PROCESS_LQTABLE or PROCESS_ALL):
    print("Processing LQ Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
    LqDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          df = pd.read_csv(csvpath,index_col=0)
          Lq = float(df.loc["Lq","Values"])
          LqDF.loc[int(Id),float(Iq)] = np.around(Lq * 1E6,1)
                         
            
    # print(torqueDF)
    
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend

    data = np.abs(LqDF.values)
    
    #drawing the table
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    
    #colorMap customization
    cmapColorBar = plt.cm.YlGn
    MODIFY_CBAR_RANGE = 1
    if MODIFY_CBAR_RANGE:
        minColorNo = np.nanmin(data)
        maxColorNo = np.nanmax(data)
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=minColorNo, vmax=maxColorNo)
    else:
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=np.nanmin(data), vmax=np.nanmax(data))

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps")
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(LqDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, LqDF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)

    """
    #customize the colorbar
    cbar = plt.colorbar(heatmap)
    if MODIFY_CBAR_RANGE:
        cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
        for label in cbarLabels:
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("Lq(uH)vs Iq(RMS) and Id(RMS)")
    if SAVE_ALL:
         LqDF.T.to_csv(saveFolder + "Lq.csv")
         plt.savefig(saveFolder + "Lq.png")
    plt.show() 
    
if (PROCESS_PSID_TABLE or PROCESS_ALL):
    print("Processing PsiD Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
            
    psiD_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          df = pd.read_csv(csvpath,index_col=0)
          psiD_RMS = float(df.loc["psiD_RMS","Values"])
          psiD_DF.loc[int(Id),float(Iq)] = np.around(psiD_RMS,3)

              
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend

    data = np.abs(psiD_DF.values)
    
    #drawing the table
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    
    #colorMap customization
    cmapColorBar = plt.cm.YlGn
    MODIFY_CBAR_RANGE = 0
    if MODIFY_CBAR_RANGE:
        minColorNo = np.nanmin(data)
        maxColorNo = np.nanmax(data)
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=minColorNo, vmax=maxColorNo)
    else:
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=np.nanmin(data), vmax=np.nanmax(data))

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps")
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(psiD_DF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, psiD_DF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)

    """
    #customize the colorbar
    cbar = plt.colorbar(heatmap)
    if MODIFY_CBAR_RANGE:
        cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
        for label in cbarLabels:
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("psiD_RMS(Wb)vs Iq(RMS) and Id(RMS)")
    if SAVE_ALL:
         psiD_DF.T.to_csv(saveFolder + "psiD_RMS.csv")
         plt.savefig(saveFolder + "psiD_RMS.png")
    plt.show() 
    

if (PROCESS_PSIQ_TABLE or PROCESS_ALL):
    print("Processing PsiQ Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
           
    psiQ_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          df = pd.read_csv(csvpath,index_col=0)
          psiQ_RMS = float(df.loc["psiQ_RMS","Values"])
          psiQ_DF.loc[int(Id),float(Iq)] = np.around(psiQ_RMS,3)

              
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend

    data = np.abs(psiQ_DF.values)
    
    #drawing the table
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    
    #colorMap customization
    cmapColorBar = plt.cm.YlGn
    MODIFY_CBAR_RANGE = 0
    if MODIFY_CBAR_RANGE:
        minColorNo = np.nanmin(data)
        maxColorNo = np.nanmax(data)
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=minColorNo, vmax=maxColorNo)
    else:
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=np.nanmin(data), vmax=np.nanmax(data))

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps") 
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(psiQ_DF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, psiQ_DF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)

    """
    #customize the colorbar
    cbar = plt.colorbar(heatmap)
    if MODIFY_CBAR_RANGE:
        cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
        for label in cbarLabels:
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("psiQ_RMS(Wb)vs Iq(RMS) and Id(RMS)")
    if SAVE_ALL:
         psiQ_DF.T.to_csv(saveFolder + "psiQ_RMS.csv")
         plt.savefig(saveFolder + "psiQ_RMS.png")
    plt.show() 

if ( PHASE_ANGLE_MAP or PROCESS_ALL):
    print("Processing phaseAngle Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
           
    phaseAngleDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          phaseAngle= np.round(np.rad2deg(np.arctan(float(Id)/float(Iq))),1)
          phaseAngleDF.loc[int(Id),float(Iq)] = phaseAngle

              
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend

    data = np.abs(phaseAngleDF.values)
    
    #drawing the table
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    
    #colorMap customization
    cmapColorBar = plt.cm.YlGn
    MODIFY_CBAR_RANGE = 0
    if MODIFY_CBAR_RANGE:
        minColorNo = np.nanmin(data)
        maxColorNo = np.nanmax(data)
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=minColorNo, vmax=maxColorNo)
    else:
        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=np.nanmin(data), vmax=np.nanmax(data))

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps") 
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(phaseAngleDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, phaseAngleDF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)

    """
    #customize the colorbar
    cbar = plt.colorbar(heatmap)
    if MODIFY_CBAR_RANGE:
        cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
        for label in cbarLabels:
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("phaseAngle (deg) vs Iq(RMS) and Id(RMS)")
    if SAVE_ALL:
         phaseAngleDF.T.to_csv(saveFolder + "phaseAngles.csv")
         plt.savefig(saveFolder + "phaseAngles.png")
    plt.show()
    
    
if ( IS_MAP or PROCESS_ALL):
    print("Processing Is Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
           
    Is_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          Id = float(Id)
          Iq = float(Iq)
          Is= np.round(np.sqrt(Id*Id + Iq*Iq),1)
          Is_DF.loc[int(Id),float(Iq)] = Is

              
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend

    data = np.abs(Is_DF.values)
    
    #drawing the table
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    
   

        
    #colorMap customization
    cmapColorBar = plt.cm.YlGn
    MODIFY_CBAR_RANGE = 0
    if MODIFY_CBAR_RANGE:
        minColorNo = np.nanmin(data)
        maxColorNo = np.nanmax(data)

        heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                            vmin=minColorNo, vmax=maxColorNo)
    else:
        heatmap = ax.pcolor(data,cmap=cmapColorBar, 
                            vmin=np.nanmin(data), vmax=np.nanmax(data))

    
    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps") 
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(Is_DF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, Is_DF[y_][x_],
                           horizontalalignment='center',
                           verticalalignment='center',
                           weight='bold',
                           size = 'small'
                           )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)

  
    """
    #customize the colorbar
    cbar = plt.colorbar(heatmap)
    if MODIFY_CBAR_RANGE:
        cbarLabels = cbar.ax.get_yaxis().get_ticklabels(minor=False,which='major')
        for label in cbarLabels:
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("Is(RMS) vs Iq(RMS) and Id(RMS)")
    if SAVE_ALL:
         Is_DF.T.to_csv(saveFolder +"Is_RMS.csv")
         plt.savefig(saveFolder + "Is_RMS.png")

    plt.show()
    

if (TORQUE_CURVE or PROCESS_ALL):
    fig = plt.figure(figsize=(imgWidth,imgHeight))
    ax = fig.gca()
    Iq_keys = filenameDict.keys()
    Iq_list = []
    for string in Iq_keys:
        Iq_list.append(int(string))
    Iq_list.sort()
    Iq_list.reverse()

    torqueCurveDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     
    for Iq in Iq_list:
        currentDict_keys = filenameDict[str(Iq)].keys()
        Id_list = []
        for string in currentDict_keys:
            Id_list.append(int(string))
        Id_list.sort()
        Id_list.reverse()
                   
        lineX = []
        lineY = []
        for Id in Id_list:
            filename = filenameDict[str(Iq)][str(Id)]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            meanTorque = float(df.loc["OL_torque","Values"])
            lineX.append(-float(Id))
            lineY.append(-meanTorque)
            
            torqueCurveDF.loc[int(Id),float(Iq)] = np.around(-meanTorque,1)
            
        plt.plot(lineX,lineY,'-x',label=str(Iq) + " ARms")

    plt.title("Current-Torque Curves")
    ax.set_xlabel("Id (RMS)")
    ax.set_ylabel("Torque in Nm")
    plt.legend()
    plt.grid()
    
    if SAVE_ALL:
         torqueCurveDF.to_csv(saveFolder + "torqueAngleCurve.csv")
         plt.savefig(saveFolder + "torqueAngleCurve.png")
         
    plt.show()
            
def getPtsSatisfyingTorqueSpeed(torqueDF,speedDF,torque,speed,dTorque=5,dSpeed=25):
    print ("looking for Pts with {}Nm and {}RPM".format(torque,speed))
    t1 = (torqueDF.abs()-torque).abs()
    s1 = (speedDF.abs()-speed).abs()
    mask1 = t1 <= dTorque
    mask2 = s1 <= dSpeed
    mask = mask1 & mask2
    
    
    out = torqueDF.copy()
    out[~mask] = 0
    pts = np.argwhere(out!=0)
    
    outData = []
    if len(pts)> 0:
        for pt in pts:
            Id = torqueDF.index[pt[0]]
            Iq = torqueDF.columns[pt[1]]
            outData.append((Iq,Id))
    """else:
        out1 = torqueDF.copy()
        out1[~mask1] = 0
        pts1 = np.argwhere(out1!=0)
        for pt in pts1:
            Id = torqueDF.index[pt[0]]
            Iq = torqueDF.columns[pt[1]]
            outData.append((Iq,Id))
        
        out2 = torqueDF.copy()
        out2[~mask2] = 0
        pts2 = np.argwhere(out2!=0)
        for pt in pts2:
            Id = torqueDF.index[pt[0]]
            Iq = torqueDF.columns[pt[1]]
            outData.append((Iq,Id))"""
        
    print("{} points Found!".format(len(outData)))
    return outData 
    
                                 
def getReorderedDict_Id(currentDict,IdMax):
    reOrderedDict= {}
    Id_order = np.arange(0,IdMax,-10)
    for Id in Id_order:
        for key in currentDict.keys():
            if float(key) == Id:
                reOrderedDict[str(Id)] = currentDict[key]
                
    # print (reOrderedDict)
    return reOrderedDict
                
def getReorderedDict_Iq(currentDict,IqMax):
    reOrderedDict= {}
    Id_order = np.arange(0,IqMax,10)
    for Id in Id_order:
        for key in currentDict.keys():
            if float(key) == Id:
                reOrderedDict[str(Id)] = currentDict[key]
                
    # print (reOrderedDict)
    return reOrderedDict      
    
if ( SPEED_CONTOUR_MAP or PROCESS_ALL):
    
    print("Processing SPEED_CONTOUR_MAP")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
     
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
 
    #get all the data u want with Id and Iq, speed     
    #the data is not regularly spaced, sO we put all the Iqs in a list, then sort
    #do the same for Id, We then have to keep the top speed data in the correct order    
    speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    Iqs = []
    Ids = []
    speeds =[]
    torques = []
    
    Iq_ordered = getReorderedDict_Iq(filenameDict,gridIqMax)
    for Iq in Iq_ordered.keys():
        currentDict = Iq_ordered[Iq]
        Id_ordered = getReorderedDict_Id(currentDict,gridIdMax)
        for Id in Id_ordered.keys():
            filename = Id_ordered[Id]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
                                
            topSpeed = np.around(float(df.loc["maxRPM","Values"]),2)
            meanTorque = float(df.loc["OL_torque","Values"])
            
            Iqs.append(Iq)
            Ids.append(Id)
            speeds.append(topSpeed)
            torques.append(meanTorque)
            speedDF.loc[int(Id),float(Iq)] = np.around(topSpeed,2)
            torqueDF.loc[int(Id),float(Iq)] = np.around(meanTorque,2)
            
    Iq_arr = np.array(Iqs).astype('float')
    Id_arr = np.array(Ids).astype('float')
    speedData = np.abs(speedDF.values)
    torqueData = np.abs(torqueDF.values)
   
    X_unique = speedDF.index.unique()
    Y_unique = speedDF.columns.unique()
    X, Y = np.meshgrid(X_unique, Y_unique)

    pkSpeedPts = getPtsSatisfyingTorqueSpeed(torqueDF,speedDF,49,10500,dTorque = 10,dSpeed = 150)
    pkPowerPts = getPtsSatisfyingTorqueSpeed(torqueDF,speedDF,180,5300,dTorque = 10,dSpeed = 100)
    ratedPts = getPtsSatisfyingTorqueSpeed(torqueDF,speedDF,70,7200,dTorque = 5,dSpeed = 100)

    speedData_flatten = speedData.flatten()
    torqueData_flatten = torqueData.T.flatten()
    def fmt(x, y):
        # get closest point with known data
        dist = np.linalg.norm(np.vstack([Id_arr - x, Iq_arr - y]), axis=0)
        idx = np.argmin(dist)
        z = speedData_flatten[idx]
        t = torqueData_flatten[idx]
        return 'Id={x:.5f}  Iq={y:.5f}  Speed={z:.5f} Torque={t:.5f}'.format(x=x, y=y, z=z,t=t)


    #plotting
    fig, ax = plt.subplots(figsize=[imgWidth,imgHeight])

    cb = ax.contour(X,Y,speedData.T,speedEllipses,colors='k',linewidths=1.0)
    cb2 = ax.contour(X,Y,torqueData.T,torque_hyperbolas,colors='green',linewidths=1.0,linestyles='--')
    
    # plt.colorbar(cb, ax=ax,label='intensity')
    plt.clabel(cb, inline=1, fontsize=10)
    plt.clabel(cb2, inline=1, fontsize=10)
    
    #contour labels
    h1,_ = cb.legend_elements()
    h2,_ = cb2.legend_elements()
    ax.legend([h1[0], h2[0]], ['Speeds(RPM)', 'Torques(Nm)'])
    
    #draw two lines at FW angles
    for angle in FW_angles:
        extreme_pt_y = np.sin(np.deg2rad(90-angle)) * np.abs(gridIdMax)
        extreme_pt_x = np.cos(np.deg2rad(90-angle)) * np.abs(gridIdMax)
        plt.plot([0,-extreme_pt_x],[0,extreme_pt_y],'--')
        plt.text(-extreme_pt_x,extreme_pt_y,str(angle)+"Deg",color='k')
    
    
    # Scatter the original data points on both subplots
    ax.set_xlabel('Id (RMS)')
    ax.set_ylabel('Iq (RMS)')
    ax.scatter(Id_arr, Iq_arr, color='black', alpha=.5, s=3)
    
    #draw current Circles
    rads = np.linspace(np.pi/2,np.pi+0.01,20)
    for R in currentCircles :
        Rx = R*np.cos(rads)
        Ry = R*np.sin(rads)  
        plt.plot(Rx,Ry,'r--')
        plt.text(0,R,str(R)+"ARMS",color='r',
                 horizontalalignment='right',
                 size='small')
        
    for pt in pkSpeedPts:
        ax.scatter(pt[1], pt[0], color='b',marker='o')
    for pt in pkPowerPts:
        ax.scatter(pt[1], pt[0], color='g',marker='o')
    for pt in ratedPts:
        ax.scatter(pt[1], pt[0], color='r',marker='o')

    ax.set_title('Torque Speed Constraint Curves')
    # ax.format_coord = fmt
    ax.set_aspect('equal')

    if SAVE_ALL:
         plt.savefig(saveFolder + "torqueSpeedConstraintCurve.png")
    
    plt.show()
    
if (PROCESS_PSID_PK or PROCESS_ALL):
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
    psiM_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for Iq in filenameDict.keys():
        currentDict = filenameDict[Iq]
        for Id in currentDict.keys():
            filename = currentDict[Id]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            psiM = float(df.loc["psiD_q_RMS","Values"])
            psiM_DF.loc[int(Id),float(Iq)] = np.around(psiM,4)

         # print(speedDF)
         
    #make a table with torques across current and current angles
    #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
   
    data = psiM_DF.values
    
    #drawing the table
    cmapColorBar = plt.cm.PuRd
    fig, ax = plt.subplots(figsize=(imgWidth,imgHeight))
    heatmap = ax.pcolor(data, cmap=cmapColorBar, 
                        vmin=np.nanmin(data), vmax=np.nanmax(data))
    # heatmap.cmap.set_under('black')
    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
    
    ax.set_xlabel("Iq RMS in Amps")
    ax.set_ylabel("Id RMS in Amps") 
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(psiM_DF[y_][x_])):
                plt.text(y + 0.5, x + 0.5, psiM_DF[y_][x_],
                          horizontalalignment='center',
                          verticalalignment='center',
                          weight='bold',
                          size = 'small'
                          )
    
    # want a more natural, table-like display
    #ax.invert_yaxis()
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 
    
    ax.set_xticklabels(columnHeadings, minor=False)
    ax.set_yticklabels(rowHeadings, minor=False)
    
    #plt.colorbar(heatmap)
    plt.suptitle ("PsiM RMS(V/s) vs Iq(RMS) and Id(RMS)")

    if SAVE_ALL:
        psiM_DF.T.to_csv(saveFolder + "psi_M.csv")
        plt.savefig(saveFolder + "psi_M.png")
        
    plt.show() 


TargetMotorPts={}
TargetMotorPts['PKTorque'] = [1100,180] #RPM,Torque
TargetMotorPts['PKPower'] = [5600,180] #RPM,Torque
TargetMotorPts['Rated Speed'] = [7200,70] #RPM,Torque
TargetMotorPts['PkSpeed'] = [10500,48] #RPM,Torque

                
#doesnt work because the RMS is not constant in the grid for Iq constant. need to
#find some way of getting the RMS constant from the grid.
if TORQUE_SPEED_CURVE:
    print("Processing TORQUE_SPEED_CURVE")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(float(key))
    columnHeadings = sorted(columnHeadings)
     
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
    fig = plt.figure(figsize=(imgWidth,imgHeight))
    
    #get all the data u want with Id and Iq, speed     
    #the data is not regularly spaced, sO we put all the Iqs in a list, then sort
    #do the same for Id, We then have to keep the top speed data in the correct order    
    speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)

    currentVal = [160]#[30,70,120,150,200,250,280,300]
    
    linestyles = ['-x','-']
    labels = ["Continuous Power and Torque","Peak Power and Torque"]
    i=0
    
    for current in filenameDict.keys():
        if int(current) in currentVal:
            speeds =[]
            torques = []
            powers = []
            currentDict = filenameDict[current]
            Id_dict = getReorderedDict_Id(currentDict,gridIdMax)
            for Id in Id_dict.keys():
                filename = currentDict[Id]
                csvpath = datafolder + filename
                df = pd.read_csv(csvpath,index_col=0)
                print(Iq,Id)
                Iq = np.around(float(current),2)
                Id = np.around(float(Id),2)
                
               
                topSpeed = np.around(float(df.loc["maxRPM","Values"]),2)
                meanTorque = np.mean(float(df.loc["OL_torque","Values"]))
                power = np.round((np.abs(meanTorque * topSpeed/60*2*np.pi)/1000),2)
                speeds.append(topSpeed)
                torques.append(meanTorque)
                powers.append(power)
                
            torque_arr = np.array(np.abs(torques))
            speed_arr = np.array(np.abs(speeds))
            power_arr = np.array(np.abs(powers))
            
            print(torque_arr)
            print(speed_arr)
            maxTorque  = np.max(torque_arr)
            maxidx = np.argmax(torque_arr)
            
            torque_arr1 = torque_arr[maxidx:]
            speed_arr1 = speed_arr[maxidx:]
            power_arr1 = power_arr[maxidx:]
            
            torques2 = list(torque_arr)
            speeds2 = list(speed_arr)
            # powers2 = list(power_arr1)
        
            speeds2.insert(0,0)
            torques2.insert(0,torques2[0])
            # powers2.insert(0,0)
            plt.plot(speeds2,torques2,linestyles[i])
            # plt.plot(speeds2,powers2,linestyles[i])
            plt.plot([],[],linestyles[i],label = labels[i])
            i=i+1
            
    # for key in TargetMotorPts.keys():
    #     speed,torque = TargetMotorPts[key]
    #     plt.plot(speed,torque,'o',label = key)
        
    plt.legend()
    plt.grid()
    ax = plt.gca()
    ax.set_xlabel("Motor RPM ")
    ax.set_ylabel("Torque in Nm / Power in KW")
    plt.title("Continuous and Peak Operation")
    
    if SAVE_ALL:
       plt.savefig(saveFolder + "TorqueSpeedCurves.png")    
       
       


if LTTS_CSV:
    print("Preparing LTTS CSV")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
    
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)

       
    allData=[]
    
    reorderedIq = getReorderedDict_Iq(filenameDict,gridIqMax)
    for Iq in reorderedIq.keys():
       currentDict = reorderedIq[Iq]
       reOrderedDict = getReorderedDict_Id(currentDict,gridIdMax)
       for Id in reOrderedDict.keys():
          filename = reOrderedDict[Id]
          csvpath = datafolder + filename

          df = pd.read_csv(csvpath,index_col=0)
          psiM_RMS = float(df.loc["psiD_q_RMS","Values"])
          psiD_RMS = float(df.loc["psiD_RMS","Values"])
          psiQ_RMS = float(df.loc["psiQ_RMS","Values"])
          psiM_Pk = psiM_RMS * np.sqrt(2)
          psiD_Pk = psiD_RMS * np.sqrt(2)
          psiQ_Pk = psiQ_RMS * np.sqrt(2)
          Lq = float(df.loc["Lq","Values"])
          Ld =float(df.loc["Ld","Values"])
          torque =float(df.loc["OL_torque","Values"]) 
          topSpeed = float(df.loc["maxRPM","Values"])
          Id_RMS = float(Id)
          Iq_RMS = float(Iq)
          Is_RMS = np.round(np.sqrt(Id_RMS*Id_RMS + Iq_RMS*Iq_RMS),1)
          
          Id_Pk = Id_RMS * np.sqrt(2)
          Iq_Pk = Iq_RMS * np.sqrt(2)
          Is_Pk = Is_RMS * np.sqrt(2)
          phaseAngle= np.round(np.rad2deg(np.arctan(float(Id_RMS)/float(Iq_RMS))),1)
          
          out = [Iq_RMS,Id_RMS,Is_RMS,Iq_Pk,Id_Pk,Is_Pk,phaseAngle,psiM_RMS,psiD_RMS,psiQ_RMS,psiM_Pk,psiD_Pk,psiQ_Pk,
                 Lq,Ld,torque,topSpeed]
          allData.append(out)

    cols = ['Iq_RMS','Id_RMS','Is_RMS','Iq_Pk','Id_Pk','Is_Pk','currentAngle','psiM_RMS','psiD_RMS','psiQ_RMS','psiM_Pk','psiD_Pk','psiQ_Pk',
           'Lq','Ld','Torque(Nm)','TopSpeed']
    df = pd.DataFrame(allData,columns= cols)
    df.to_csv(saveFolder+"LTTS.csv")
          
          
   
if SAVE_ALL:
    plt.close('all')
    
   
# WHY TO NOT DO 
DO_THIS = 0
if DO_THIS :
    print("Processing Is Table")
    columnHeadings = []
    for key in filenameDict.keys():
        columnHeadings.append(int(key))
    columnHeadings = sorted(columnHeadings)
        
    rowHeadings=[]
    for key in filenameDict.keys():
        for CA in filenameDict[key].keys():
            if int(CA) not in rowHeadings:
                rowHeadings.append(int(CA))
    rowHeadings = sorted(rowHeadings)
    
    Is_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    speed_xs = []
    torque_ys = []
    for Iq in filenameDict.keys():
       currentDict = filenameDict[Iq]
       for Id in currentDict.keys():
          filename = currentDict[Id]
          csvpath = datafolder + filename
          df = pd.read_csv(csvpath,index_col=0)
          
          Id = float(Id)
          Iq = float(Iq)
          Is= np.round(np.sqrt(Id*Id + Iq*Iq),1)
          Is_DF.loc[int(Id),float(Iq)] =  Is
          
          torque =float(df.loc["OL_torque","Values"]) 
          torqueDF.loc[int(Id),float(Iq)] = np.around(torque,2)
          
          topSpeed = float(df.loc["maxRPM","Values"])
          speedDF.loc[int(Id),float(Iq)] = np.around(topSpeed,0)
          
          torque_ys.append(np.abs(np.around(torque,2)))
          speed_xs.append(np.around(topSpeed,0))
          
    data = np.abs(Is_DF.values)
    torqueData = np.abs(torqueDF.values)
    speedData = np.abs(speedDF.values)
    
    plt.figure()
    plt.grid()
    currents = [300,250,200,150,100,50]
    maxRPM = 99000
    for current in currents:
        # to find points close to the RMS you want
        mask = abs(data - current) < 3 
        indices = (np.argwhere(mask))
        
        Ids = []
        Iqs = []
        torques = []
        speeds = []
        for index in indices[::-1]:
            c,r = index
            Id = rowHeadings[r]
            Iq = columnHeadings[c]
            Ids.append(Id)
            Iqs.append(Iq)
            
            torques.append(torqueData[index[0],index[1]])
            speeds.append(speedData[index[0],index[1]])
            
        
        torque_arr = np.array(torques)
        maxTorque  = np.max(torque_arr)
        maxidx = np.argmax(torque_arr)
        torque_arr[:maxidx] = maxTorque
        torques = list(torque_arr)
        torques.insert(0,maxTorque)
        speeds.insert(0,0)
        
        mask = np.array(speeds) <= maxRPM
        speeds2 = list(np.array(speeds)[mask])
        torques2 = list(np.array(torques)[mask])

        plt.plot(speeds2,torques2)
        
    ax = plt.gca()
    # Scatter the original data points on both subplots
    ax.set_xlabel('Id (RMS)')
    ax.set_ylabel('Iq (RMS)')
    ax.scatter(speed_xs, torque_ys, color='black', alpha=.5, s=3)

    
        
    
    
    
    
    
    
    
    
          
        