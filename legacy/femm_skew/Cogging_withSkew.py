# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 03:30:18 2024

@author: Harsha
"""

import pandas as pd
import femm
import time
import os
from shutil import copyfile

import numpy as np
import matplotlib.pyplot as plt

import multiprocessing as mp
import worker_NoLoad_withSkew as wNL_wS
from scipy.interpolate import CubicSpline

DO_SIMS = 1
PROCESS_RESULTS = 1
SAVE_IMAGES= 0
SHOW_IMAGES = 1

#stack length of the motor has to be set in the file correctly, otherwise magnitude of torque is wrong.
fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_100C.FEM" # stack length of the motor has to be set in the file correctly
rootFolder = os.path.dirname(fem_file)
print(rootFolder)

###WITH SLIDING BAND,MULTIPROCESSING AND SKEW
Symmetry= 8
polePairs = 4
mechAnglePerPolePair = 360/polePairs

Slots = 48
CoggingFreq= np.lcm(Slots,polePairs*2)
CoggingMechAngle = 360/CoggingFreq
simulationAngleTotal = CoggingMechAngle*2
totalSimsPerSlice = 30
deltaAngle = simulationAngleTotal/totalSimsPerSlice

print ("polePairs = {}".format(polePairs))
print ("mechAnglePerPolePair = {} \n".format(mechAnglePerPolePair))
print ("Slots = {} \n".format(Slots))
print ("CoggingFreq = {} \n".format(CoggingFreq))
print ("CoggingMechAngle = {} \n".format(CoggingMechAngle))
print ("simulationAngleTotal = {} \n".format(simulationAngleTotal))
print ("deltaAngle = {} \n".format(deltaAngle))

no_of_skew_Slices = 4
skew_Angles =  [2.8125, 0.9375, -0.9375, -2.8125] #[-2.5,0,2.5]#
cpu_count = 4 # no of slices does not have to be same as no of Workers.

#create a folder to put all the results in
saveDirectory = rootFolder +"\\SkewOutputs_{}Slices\\Cogging\\".format(no_of_skew_Slices)
if not os.path.exists(saveDirectory):
    os.makedirs(saveDirectory)

imgWidth,imgHeight = (18,10) #in inches


print("poles={},slots={},lcm={},CoggingMechAngle={}".format(polePairs*2,Slots,CoggingFreq,CoggingMechAngle))
print("simulationAngleTotal={},totalSimsPerSlice={},deltaAngle={}".format(simulationAngleTotal,totalSimsPerSlice,deltaAngle))


total_overall_sims  = totalSimsPerSlice * no_of_skew_Slices

print ("total Sims needed per slices = {}".format(totalSimsPerSlice))
print ("total overall Sims = {} ".format(total_overall_sims))
print("parallel_workers = {}".format(cpu_count))

#here since we re not sending in current all we need to do is create a list of electical angle rotations per task
tasks_per_worker = []
tasks_to_split = total_overall_sims
for idx in range(cpu_count,0,-1): # get how many tasks per worker
    tasks_per_worker.append(tasks_to_split // idx + ((tasks_to_split % idx) > 0))
    tasks_to_split -= tasks_per_worker[-1]
    
print("tasks_per_worker = {}".format(tasks_per_worker))

# split the angles so that you get the correct no per task,also create seperate Fem files so that u can run in parallel
# and then zip the results into something we can send to the parallel fn


rotorMechAnglesPerSlice = np.arange(0,mechAnglePerPolePair+1,deltaAngle)
workerArguments = []

currentAngle = 0
currentSkewIdx = 0
taskNo = 0
for i in range(cpu_count):
    workerFile = fem_file[:-4] + "_" + str(i) + ".fem"
    copyfile(fem_file, workerFile)
    noOfTasks = tasks_per_worker[i]
    workerAngles = []
    workerSkews = []
    workerSliceIdxs=[]
    for t in range(noOfTasks):
        workerSliceIdxs.append(currentSkewIdx+1) # this has to be here.
        
        # print ("taskNo = {},workerNo = {},angle = {}, skew = {}, sliceNo = {} ".format(taskNo,i,currentAngle,skew_Angles[currentSkewIdx],workerSliceIdxs[t]))
        workerAngles.append(currentAngle)
        workerSkews.append(skew_Angles[currentSkewIdx])
        
        currentAngle = currentAngle + deltaAngle
        if currentAngle>=simulationAngleTotal:
            currentAngle = 0    
        taskNo += 1
        if taskNo%totalSimsPerSlice==0:
            currentSkewIdx += 1
    
    workerArguments.append([workerFile,i,noOfTasks,workerAngles,workerSliceIdxs,workerSkews])

for i in range(len(workerArguments)):
    workerNo = workerArguments[i][1]
    sims = workerArguments[i][2]
    workerAnglesMin = min(workerArguments[i][3])
    workerAnglesMax = max(workerArguments[i][3])
    workerSlices = np.unique(np.array(workerArguments[i][4]))
    workerSkews = np.unique(np.array(workerArguments[i][5]))
    print ("WorkerNo : {},noOfSims {},Angles {},skewSlices = {},skews {},".format(workerNo,sims,str(workerAnglesMin)+"/"+str(workerAnglesMax),workerSlices,workerSkews))    

#otherArguments        
verbosePrinting = 1    
saveImageLocation = -1 # -1 for no Saving, and folder location for saving

for idx in range(len(workerArguments)):
    workerArguments[idx].append(saveImageLocation)
    workerArguments[idx].append(verbosePrinting)


if __name__ ==  '__main__': 
    if DO_SIMS:
        num_processors = cpu_count
        p=mp.Pool(processes = num_processors)
        output = p.starmap(wNL_wS.WorkerNoLoad_withSkew,workerArguments)
        df = pd.concat(output,ignore_index=True) #star map guarantees orders are returned in the same order as u send it in
    
        csvFilename = saveDirectory + "Cogging_{}slices.csv".format(no_of_skew_Slices)
        df.to_csv(csvFilename)
        print ("CSV of the values saved in {}".format(csvFilename))
        
        # Remove temporary .fem and .ans files
        print ("removing temp files...")
        for w in range(cpu_count, 0, -1):
            try:
                temp_filename = workerArguments[w-1][0]
                temp_filename2 = temp_filename[:-4]+".ans"
                os.remove(temp_filename)
                os.remove(temp_filename2)
            except Exception:
                print("Could not remove one of these files: " + temp_filename + " or " + temp_filename2)
        print("done")
        
    
    if PROCESS_RESULTS:
        csvFilename = saveDirectory+"\\" + "Cogging_{}slices.csv".format(no_of_skew_Slices)
        df = pd.read_csv(csvFilename)
        
        #TODO: below code hardcoded for 4 slices. make it generic
        sliceDFs = []
        torqueArrs = []
        for idx in range(no_of_skew_Slices):
            sliceDF = df[df['sliceNo'] == idx+1]
            sliceDFs.append(sliceDF)
            torqueArrs.append(np.array(sliceDF['torque']))
            
        rotorAngles = np.array(sliceDFs[0]['rotorAngle'])
        
        #do smooth fitting
        newRotorAngles = np.arange(np.min(rotorAngles),np.max(rotorAngles),0.1)
        smoothedTorques = []
        for torqueArr in torqueArrs:
            spl = CubicSpline(rotorAngles, torqueArr)
            smoothedTorques.append(spl(newRotorAngles))
    
        finalCoggingTorque = smoothedTorques[0]
        for idx in range(len(smoothedTorques)):
            if idx == 0:
                continue
            finalCoggingTorque =  finalCoggingTorque + smoothedTorques[idx] 
    
        print ("pk Cogging Torque = {} " .format(np.max(finalCoggingTorque)))
        
        string = 'torque'
        plt.figure(figsize=(imgWidth,imgHeight))
        for idx in range(len(torqueArrs)):
            plt.plot(rotorAngles,torqueArrs[idx],'--')
            # plt.plot(newRotorAngles,smoothedTorques[idx],'-',label='slice' + str(idx+1))
        plt.plot(newRotorAngles,finalCoggingTorque,label='fullMotor')
        plt.title("Cogging Torque with {} slices ".format(no_of_skew_Slices))
        plt.legend()
        plt.grid()

        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+"\\" + "cogging_{}Slices.png".format(no_of_skew_Slices)
            plt.savefig(imgName)
            print ("plot image of coggingTorque saved in {}".format(imgName))
                        
        if SAVE_IMAGES:    
            plt.close('all')
        
        
        
        
    
    

    
    
    

    