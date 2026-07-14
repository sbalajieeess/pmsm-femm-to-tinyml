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

PROCESS_SPEEDTABLE = 0
PROCESS_LDTABLE = 0
PROCESS_LQTABLE = 0
PROCESS_TORQUE_TABLE = 0
PROCESS_ANALYTICAL_TORQUE_TABLE = 0
PROCESS_PERCENTAGE_OF_RELUCTANCE_TORQUE = 0
PROCESS_PSID_TABLE = 0
PROCESS_PSIQ_TABLE = 0
TORQUE_CURVE  = 0
SPEED_CONTOUR_MAP = 0
TORQUE_SPEED_CURVE = 1
SAVE_ALL = 0

imgWidth,imgHeight = (18,10) #in inches

fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_100C.FEM" # stack length of the motor has to be set in the file correctly
filename = os.path.basename(fem_file)
rootFolder = os.path.dirname(fem_file)
datafolder = rootFolder +"\\"+filename[:-4]+"\\SkewOutputs_4Slices\\OL\\"
saveFolder = rootFolder +"\\"+filename[:-4]+"\\SkewOutputs_4Slices\\summarisedData\\"
print(datafolder)
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
        current = parts1[1]
        currentAngle = parts1[2]
        if current in filenameDict.keys():
            filenameDict[current][currentAngle] = filename
        else:
            filenameDict[current]={}
            filenameDict[current][currentAngle] = filename
print ("Looking in folder - " + str(datafolder))
print ("Filename and current Angles available along with their filenames:")
pprint (filenameDict)


def getDF_from_FileDict(folder,filenameDict,searchCurrent,searchCA):
    df = None
    for current in filenameDict.keys():
        if current == searchCurrent:
            currentDict = filenameDict[current]        
            for angle in currentDict.keys():
                if (angle == searchCA):
                    filename = currentDict[angle]
                    csvpath = folder + filename
                    df = pd.read_csv(csvpath)
    return df

#calculate psi,psiQ and ld and Lq for each excel row.
if PROCESS_SPEEDTABLE:
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
     
     speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for current in filenameDict.keys():
         currentDict = filenameDict[current]
         for CA in currentDict.keys():
             filename = currentDict[CA]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             topSpeed = float(df.loc["maxRPM","Values"])
             speedDF.loc[int(CA),float(current)] = np.around(topSpeed,0)
     
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
     
     ax.set_xlabel("Current RMS in Amps")
     ax.set_ylabel("CurrentAngles in Deg")
     
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
         
     plt.suptitle ("Max Speed Possible (RPM) vs Current and Current Angle")

     if SAVE_ALL:
         speedDF.T.to_csv(saveFolder + "speedMap.csv")
         plt.savefig(saveFolder + "speedMap.png")        

     plt.show()


     
    
# calculate psi,psiQ and ld and Lq for each excel row.
if PROCESS_ANALYTICAL_TORQUE_TABLE:
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
     
     torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for current in filenameDict.keys():
         currentDict = filenameDict[current]
         for CA in currentDict.keys():
             filename = currentDict[CA]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             torque = float(df.loc["analyticalTorque_total","Values"])
             torqueDF.loc[int(CA),float(current)] = np.around(torque,1)
             
     # print(speedDF)
     
     #make a table with torques across current and current angles
     #from https://stackoverflow.com/questions/35905393/python-leave-numpy-nan-values-from-matplotlib-heatmap-and-its-legend
    
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
     
     ax.set_xlabel("Current RMS in Amps")
     ax.set_ylabel("CurrentAngles in Deg")
     
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
     plt.suptitle ("Analytical Torque vs Current and Current Angle")

     if SAVE_ALL:
         torqueDF.T.to_csv(saveFolder + "analyticalTorque.csv")
         plt.savefig(saveFolder + "analyticalTorque.png")
         
     plt.show() 
     
# calculate psi,psiQ and ld and Lq for each excel row.
if PROCESS_PERCENTAGE_OF_RELUCTANCE_TORQUE:
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
     
     relPercentDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for current in filenameDict.keys():
         currentDict = filenameDict[current]
         for CA in currentDict.keys():
             filename = currentDict[CA]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             magTorque = float(df.loc["magneticTorque","Values"])
             relTorque = float(df.loc["reluctanceTorque","Values"])
             relPercentDF.loc[int(CA),float(current)] = np.abs(np.around(relTorque*100/(magTorque+ relTorque),1))
             
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
     
     ax.set_xlabel("Current RMS in Amps")
     ax.set_ylabel("CurrentAngles in Deg")
     
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
     
     plt.suptitle ("Reluctance Torque Percentage vs Current and Current Angle")
     if SAVE_ALL:
         relPercentDF.T.to_csv(saveFolder + "relPercent.csv")
         plt.savefig(saveFolder + "relPercent.png")
     plt.show() 
     
# calculate psi,psiQ and ld and Lq for each excel row.
if PROCESS_TORQUE_TABLE:
     print("Processing Torque Table")
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
     
     torqueDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for current in filenameDict.keys():
         currentDict = filenameDict[current]
         for CA in currentDict.keys():
             filename = currentDict[CA]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             torque =float(df.loc["OL_torque","Values"]) 
             torqueDF.loc[int(CA),float(current)] = np.around(torque,2)
             
     
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
     
     ax.set_xlabel("Current RMS in Amps")
     ax.set_ylabel("CurrentAngles in Deg")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(torqueDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, int(np.abs(torqueDF[y_][x_])),
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
     
     plt.suptitle ("Torque (Nm) vs Current and Current Angle")
     if SAVE_ALL:
         torqueDF.T.to_csv(saveFolder + "feaTorque.csv")
         plt.savefig(saveFolder + "feaTorque.png")
     plt.show() 


if PROCESS_LDTABLE:
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
     
     LdDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     for current in filenameDict.keys():
         currentDict = filenameDict[current]
         for CA in currentDict.keys():
             filename = currentDict[CA]
             csvpath = datafolder + filename
             df = pd.read_csv(csvpath,index_col=0)
             Ld =float(df.loc["Ld","Values"]) 
             LdDF.loc[int(CA),float(current)] = np.around(Ld * 1E6,1)
             
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
     
     ax.set_xlabel("Current RMS in Amps")
     ax.set_ylabel("CurrentAngles in Deg")
     
     for x in range(data.shape[0]):
         for y in range(data.shape[1]):
             y_ = columnHeadings[y]
             x_ = rowHeadings[x]
             if not(pd.isna(LdDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, LdDF[y_][x_],
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
         
     plt.suptitle ("Ld(uH)vs Current and Current Angle")
     if SAVE_ALL:
         LdDF.T.to_csv(saveFolder + "Ld.csv")
         plt.savefig(saveFolder + "Ld.png")
     plt.show() 

if PROCESS_LQTABLE:
    print("Processing LQ Table")
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
    
    LqDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for current in filenameDict.keys():
        currentDict = filenameDict[current]
        for CA in currentDict.keys():
            filename = currentDict[CA]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            if CA == '-90':
                Lq = np.inf
            else:
                Lq = float(df.loc["Lq","Values"])
            LqDF.loc[int(CA),float(current)] = np.around(Lq * 1E6,1)

                
            
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
    
    ax.set_xlabel("Current RMS in Amps")
    ax.set_ylabel("CurrentAngles in Deg")
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(LqDF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, LqDF[y_][x_],
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
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("Lq(uH)vs Current and Current Angle")
    if SAVE_ALL:
         LqDF.T.to_csv(saveFolder + "Lq.csv")
         plt.savefig(saveFolder + "Lq.png")
    plt.show() 
    
if PROCESS_PSID_TABLE:
    print("Processing PsiD Table")
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
    
    psiD_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for current in filenameDict.keys():
        currentDict = filenameDict[current]
        for CA in currentDict.keys():
            filename = currentDict[CA]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            psiD_RMS = float(df.loc["psiD_RMS","Values"])
            psiD_DF.loc[int(CA),float(current)] = np.around(psiD_RMS,3)

              
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
    
    ax.set_xlabel("Current RMS in Amps")
    ax.set_ylabel("CurrentAngles in Deg")
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(psiD_DF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, psiD_DF[y_][x_],
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
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("psiD_RMS(Wb)vs Current and Current Angle")
    if SAVE_ALL:
         psiD_DF.T.to_csv(saveFolder + "psiD_RMS.csv")
         plt.savefig(saveFolder + "psiD_RMS.png")
    plt.show() 
    

if PROCESS_PSIQ_TABLE:
    print("Processing PsiQ Table")
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
    
    psiQ_DF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    for current in filenameDict.keys():
        currentDict = filenameDict[current]
        for CA in currentDict.keys():
            filename = currentDict[CA]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            psiQ_RMS = float(df.loc["psiQ_RMS","Values"])
            psiQ_DF.loc[int(CA),float(current)] = np.around(psiQ_RMS,3)

              
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
    
    ax.set_xlabel("Current RMS in Amps")
    ax.set_ylabel("CurrentAngles in Deg")
    
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            y_ = columnHeadings[y]
            x_ = rowHeadings[x]
            if not(pd.isna(psiQ_DF[y_][x_])):
                 plt.text(y + 0.5, x + 0.5, psiQ_DF[y_][x_],
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
            if label.get_text()==str(minColorNo):
                label.set_text("<="+str(minColorNo))
            if label.get_text()==str(maxColorNo): 
                label.set_text(">="+str(maxColorNo))
        cbar.ax.get_yaxis().set_ticklabels(cbarLabels,minor=False)
    """
         
    plt.suptitle ("psiQ_RMS(Wb)vs Current and Current Angle")
    if SAVE_ALL:
         psiQ_DF.T.to_csv(saveFolder + "psiQ_RMS.csv")
         plt.savefig(saveFolder + "psiQ_RMS.png")
    plt.show() 


if TORQUE_CURVE:
    fig = plt.figure(figsize=(imgWidth,imgHeight))
    ax = fig.gca()
    currentList_keys = filenameDict.keys()
    I_list = []
    for string in currentList_keys:
        I_list.append(int(string))
    I_list.sort()
    I_list.reverse()

    torqueCurveDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
     
    for current in I_list:
        currentDict_keys = filenameDict[str(current)].keys()
        CA_list = []
        for string in currentDict_keys:
            CA_list.append(int(string))
        CA_list.sort()
        CA_list.reverse()
                   
        lineX = []
        lineY = []
        for CA in CA_list:
            filename = filenameDict[str(current)][str(CA)]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            meanTorque = float(df.loc["OL_torque","Values"])
            lineX.append(-float(CA))
            lineY.append(-meanTorque)
            
            torqueCurveDF.loc[int(CA),float(current)] = np.around(-meanTorque,1)
            
        plt.plot(lineX,lineY,'-x',label=str(current) + " ARms")

    plt.title("Current-Torque Curves")
    ax.set_xlabel("Current Angle in Deg")
    ax.set_ylabel("Torque in Nm")
    plt.legend()
    plt.grid()
    
    if SAVE_ALL:
         torqueCurveDF.to_csv(saveFolder + "torqueAngleCurve.csv")
         plt.savefig(saveFolder + "torqueAngleCurve.png")
         
    plt.show()
            
if SPEED_CONTOUR_MAP:
    print("Processing SPEED_CONTOUR_MAP")
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
    
    #get all the data u want with Id and Iq, speed     
    #the data is not regularly spaced, sO we put all the Iqs in a list, then sort
    #do the same for Id, We then have to keep the top speed data in the correct order    
    speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
    Iqs = []
    Ids = []
    speeds =[]
    torques = []
    for current in filenameDict.keys():
        currentDict = filenameDict[current]
        for CA in currentDict.keys():
            filename = currentDict[CA]
            csvpath = datafolder + filename
            df = pd.read_csv(csvpath,index_col=0)
            
            Iq = np.around(np.cos(np.deg2rad(float(CA))) * float(current),2)
            Id = np.around(np.sin(np.deg2rad(float(CA))) * float(current),2)
            
            topSpeed = np.around(float(df.loc["maxRPM","Values"]),2)
            meanTorque = float(df.loc["OL_torque","Values"])
            
            Iqs.append(Iq)
            Ids.append(Id)
            speeds.append(topSpeed)
            torques.append(meanTorque)
            # speedDF.loc[int(CA),float(current)] = np.around(topSpeed,0)
    Iq_arr = np.array(Iqs)
    Id_arr = np.array(Ids)
    speed_arr = np.array(speeds)
    torque_arr = np.array(torques)
    
    n = len(Iqs) * 5
    minIq = np.min(Iq_arr)
    minId = np.min(Id_arr)
    maxIq = np.max(Iq_arr)
    maxId = np.min(Id_arr)
    
    #define a regular grid
    epsilon = 1. + 1e-9  # Add a little to include the endpoint in np.arange
    Id_uniform = np.arange(minId,maxId*epsilon, n)
    Iq_uniform = np.arange(minIq,maxIq*epsilon, n)
    X, Y = np.meshgrid(Id_uniform, Iq_uniform)
    
    # # Create a 2D interpolator to calculate the intensity at any position
    # pts  = np.vstack((Id_arr,Iq_arr)).T
    # z_interpolator = scipy.interpolate.CloughTocher2DInterpolator(pts,speed_arr)
    # Z = z_interpolator(np.dstack((X, Y)))
    # print(Z)

    Id_arr_flatten = Id_arr.flatten()
    Iq_arr_flatten = Iq_arr.flatten()
    speed_flatten = speed_arr.flatten()
    torque_flatten = torque_arr.flatten()
    
    def fmt(x, y):
        # get closest point with known data
        dist = np.linalg.norm(np.vstack([Id_arr_flatten - x, Iq_arr_flatten - y]), axis=0)
        idx = np.argmin(dist)
        z = speed_flatten[idx]
        t = torque_flatten[idx]
        return 'Id={x:.5f}  Iq={y:.5f}  Speed={z:.5f} Torque={t:.5f}'.format(x=x, y=y, z=z,t=t)


    #plotting
    fig, ax = plt.subplots(figsize=[imgWidth,imgHeight])
    
    # Subplot 1: Scatter plot with tricontourf, which takes randomly positioned points
    cb = ax.tricontour(Id_arr, Iq_arr, speed_arr,[6000,7500,9000,10000,12000,15000],colors='k',linewidths=1.0)
    cb2 = ax.tricontour(Id_arr, Iq_arr, abs(torque_arr),10,colors='green',linewidths=1.0,linestyles='--')
    
    # plt.colorbar(cb, ax=ax,label='intensity')
    plt.clabel(cb, inline=1, fontsize=10)
    plt.clabel(cb2, inline=1, fontsize=10)
    
    #contour labels
    h1,_ = cb.legend_elements()
    h2,_ = cb2.legend_elements()
    ax.legend([h1[0], h2[0]], ['Speeds(RPM)', 'Torques(Nm)'])

    # Scatter the original data points on both subplots
    ax.set_xlabel('Id (RMS)')
    ax.set_ylabel('Iq (RMS)')
    ax.scatter(Id_arr, Iq_arr, color='black', alpha=.5, s=3)
        
    # ax.scatter(-150, 26, color='r',marker='x')

    ax.set_title('Torque Speed Constraint Curves')
    ax.format_coord = fmt
    ax.set_aspect('equal')

    if SAVE_ALL:
         plt.savefig(saveFolder + "torqueSpeedConstraintCurve.png")
    
    plt.show()

TargetMotorPts={}
TargetMotorPts['PKTorque'] = [1100,180] #RPM,Torque
TargetMotorPts['PKPower'] = [5600,180] #RPM,Torque
TargetMotorPts['Rated Speed'] = [7200,70] #RPM,Torque
TargetMotorPts['PkSpeed'] = [10500,48] #RPM,Torque

                
def getReorderedDict_CA(currentDict):
    reOrderedDict= {}
    CA_order = np.arange(0,-90,-5)
    for CA in CA_order:
        for key in currentDict.keys():
            if float(key) == CA:
                reOrderedDict[str(CA)] = currentDict[key]
                
    # print (reOrderedDict)
    return reOrderedDict    

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

    currentVal = [125,250]#[30,70,120,150,200,250,280,300]
    
    linestyles = ['-x','-']
    labels = ["Continuous Power and Torque","Peak Power and Torque"]
    i=0
    
    for current in filenameDict.keys():
        if int(current) in currentVal:
            speeds =[]
            torques = []
            powers = []
            currentDict = filenameDict[current]
            reorderedCA_dict = getReorderedDict_CA(currentDict)
            for CA in reorderedCA_dict.keys():
                filename = currentDict[CA]
                csvpath = datafolder + filename
                df = pd.read_csv(csvpath,index_col=0)
                
                Iq = np.around(np.cos(np.deg2rad(float(CA))) * float(current),2)
                Id = np.around(np.sin(np.deg2rad(float(CA))) * float(current),2)
                
               
                topSpeed = np.around(float(df.loc["maxRPM","Values"]),2)
                meanTorque = np.mean(float(df.loc["OL_torque","Values"]))
                power = np.round((np.abs(meanTorque * topSpeed/60*2*np.pi)/1000),2)
                speeds.append(topSpeed)
                torques.append(meanTorque)
                powers.append(power)
                
            torque_arr = np.array(np.abs(torques))
            speed_arr = np.array(np.abs(speeds))
            power_arr = np.array(np.abs(powers))
            maxTorque  = np.max(torque_arr)
            maxidx = np.argmax(torque_arr)
            
            torque_arr1 = torque_arr[maxidx:]
            speed_arr1 = speed_arr[maxidx:]
            power_arr1 = power_arr[maxidx:]
            
            torques2 = list(torque_arr1)
            speeds2 = list(speed_arr1)
            powers2 = list(power_arr1)
        
            speeds2.insert(0,0)
            torques2.insert(0,torques2[0])
            powers2.insert(0,0)
            plt.plot(speeds2,torques2,linestyles[i],label= "Torque " + str(current)+"RMS")
            plt.plot(speeds2,powers2,linestyles[i],label= "Power " + str(current)+"RMS")
            # plt.plot([],[],linestyles[i],label = labels[i])
            i=i+1
            
    for key in TargetMotorPts.keys():
        speed,torque = TargetMotorPts[key]
        plt.plot(speed,torque,'o',label = key)
        
    plt.legend()
    plt.grid()
    ax = plt.gca()
    ax.set_xlabel("Motor RPM ")
    ax.set_ylabel("Torque in Nm / Power in KW")
    plt.title("Continuous and Peak Operation")
    
    if SAVE_ALL:
       plt.savefig(saveFolder + "TorqueSpeedCurves.png")    
       
        
    # imgPath = "C:/Work/Projects/LTTS_Work/design2/Continuous And Peak Operations/effMap20C_forBG.png"
    # fig, ax = plt.subplots()
    # img = plt.imread(imgPath)
    # ax.imshow(img) 
    
    

# if TORQUE_SPEED_CURVE:
    
    
#     print("Processing TORQUE_SPEED_CURVE")
#     columnHeadings = []
#     for key in filenameDict.keys():
#         columnHeadings.append(float(key))
#     columnHeadings = sorted(columnHeadings)
     
#     rowHeadings=[]
#     for key in filenameDict.keys():
#         for CA in filenameDict[key].keys():
#             if int(CA) not in rowHeadings:
#                 rowHeadings.append(int(CA))
#     rowHeadings = sorted(rowHeadings)
    
#     #get all the data u want with Id and Iq, speed     
#     #the data is not regularly spaced, sO we put all the Iqs in a list, then sort
#     #do the same for Id, We then have to keep the top speed data in the correct order    
#     speedDF = pd.DataFrame(np.nan,columns = columnHeadings,index = rowHeadings)
#     Iqs = []
#     Ids = []
#     speeds =[]
#     torques = []
#     for current in filenameDict.keys():
#         currentDict = filenameDict[current]
#         for CA in currentDict.keys():
#             filename = currentDict[CA]
#             csvpath = datafolder + filename
#             df = pd.read_csv(csvpath,index_col=0)
            
#             Iq = np.around(np.cos(np.deg2rad(float(CA))) * float(current),2)
#             Id = np.around(np.sin(np.deg2rad(float(CA))) * float(current),2)
            
#             topSpeed = np.around(float(df.loc["maxRPM","Values"]),2)
#             meanTorque = np.mean(float(df.loc["OL_torque","Values"]))
            
#             Iqs.append(Iq)
#             Ids.append(Id)
#             speeds.append(topSpeed)
#             torques.append(meanTorque)
#             # speedDF.loc[int(CA),float(current)] = np.around(topSpeed,0)
#     Iq_arr = np.array(Iqs)
#     Id_arr = np.array(Ids)
#     speed_arr = np.array(speeds)
#     torque_arr = np.array(torques)
    
#     df = pd.DataFrame(list(zip(speed_arr,np.abs(torque_arr))),columns=["Speed","Torque"])
#     df1 = df.sort_values('Speed')
    
#     df1.plot.scatter('Speed', 'Torque', color='k')
#     print(df1.groupby('Speed'))
    
#     # df1.groupby('Speed').max().plot(ax=plt.gca(), color='red')

    
   
if SAVE_ALL:
    plt.close('all')