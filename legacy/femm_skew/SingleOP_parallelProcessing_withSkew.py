import pandas as pd
import femm
import time
import os,sys
from shutil import copyfile
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
from scipy.interpolate import CubicSpline
from collections import OrderedDict
import traceback

import ClarkPark as cp
import worker_SingleSlice_SinglePt as wSS_SP
import processingFns as process


###WITH SLIDING BAND,MULTIPROCESSING AND SKEW, JUST ONE SINGLE ROTOR POSITION, OC and OL
#First Create the File , then Process It
#FEMM file must have the correct stack length

DO_SIMS = 1
PROCESS_FL_TORQUE_RESULTS = 1
PROCESS_FEA_RESULTS = 0
SAVE_FEM_FILE_WITH_LOAD_CURRENTS = 0

fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_100C.FEM" # stack length of the motor has to be set in the file correctly

fem_file = r"C:/Work/FEMM_Server/CodeForDrawing/codeV_IPM/OLfemmFiles/rotor_0_100_-30.fem"
rootFolder = os.path.dirname(fem_file)
filename = os.path.basename(fem_file)
print ("rootDirectory = {}".format(rootFolder))
print ("filename = {}".format(filename))

settings=OrderedDict()
settings['filename'] = filename
settings["dAxis_slidingBand"] = 4
settings["DC_Voltage"] = 400
settings["RMSCurrent"] = 100
settings["phaseAdvanceAngle"] = -30 #angle must be -ve
settings["Symmetry"] = 8
settings["polePairs"] = 4
settings['noOfSlices'] = 4
settings['skew_AnglesMech'] = [2.8125, 0.9375, -0.9375, -2.8125]
settings['rotorAngleElec'] = 0
settings["MeshLuaScript"] = "C:/Work/FEMM_Server/multiprocessingCode/get_mesh_data_FEMM.lua"

#needs to be modified for every FEM file
B_linePlots = {}
B_linePlots['radius_statorYoke'] = 128
B_linePlots['radius_statorTeeth'] = 100
B_linePlots['radius_statorTeethPole'] = 80.6
magnetPts= [(36.81,55.23),(55.23,36.81)]
FEA_data= [B_linePlots,magnetPts] #make FEA data None if you dont want this

settings["FEM_meshOffsetAngle"] = 22.5
settings['FEA_plotPts']= FEA_data 

print ("---SimulationSettings---")
pprint(settings)
print ("---------")
    
cpu_count = 4 # no of slices does not have to be same as no of Workers.

#create a folder to put all the results in
saveDirectory = rootFolder +"\\SkewOutputs_{}Slices\\OL\\SingleOP\\{}A_{}CA_{}RA\\".format(settings['noOfSlices'],
                                                                                         settings["RMSCurrent"],
                                                                                         settings["phaseAdvanceAngle"],
                                                                                         settings["rotorAngleElec"])
if not os.path.exists(saveDirectory):
    os.makedirs(saveDirectory)
    
print ("total overall Sims (each sim has OC and OL) = {} ".format(settings['noOfSlices']))
print("parallel_workers = {}".format(cpu_count))

settings['save_OL_FEM_file'] = SAVE_FEM_FILE_WITH_LOAD_CURRENTS
settings['saveDirectory'] = saveDirectory
    
#----------------------------------------------------

#here since we re not sending in current all we need to do is create a list of electical angle rotations per task
tasks_per_worker = []
tasks_to_split = settings['noOfSlices']
for idx in range(cpu_count,0,-1): # get how many tasks per worker
    tasks_per_worker.append(tasks_to_split // idx + ((tasks_to_split % idx) > 0))
    tasks_to_split -= tasks_per_worker[-1]
    
print("tasks_per_worker = {}".format(tasks_per_worker))

workerArguments = []
verbosePrinting = 1
saveMesh = 1 # not working, something wrong with the lua script.
saveBMP_image= 0 # wont work unless you make femm.openFemm(0).Better to not use, slows things down a lot
for i in range(cpu_count):   
    workerFile = fem_file[:-4] + "_" + str(i) + ".fem"
    copyfile(fem_file, workerFile)
    print(workerFile)
    sliceSettings= {}
    sliceSettings["RMSCurrent"] = settings["RMSCurrent"]
    sliceSettings["phaseAngle"] = settings["phaseAdvanceAngle"]
    sliceSettings["rotorAngleElec"]  = settings['rotorAngleElec']
    sliceSettings["sliceNo"] = i
    sliceSettings["skewAngle"] = settings['skew_AnglesMech'][i]
    
    workerArguments.append([workerFile,i,settings,sliceSettings,saveMesh,verbosePrinting,saveBMP_image])
    print ("---worker {}---".format(i))
    pprint(sliceSettings)

if __name__ ==  '__main__': 
    try:
        if DO_SIMS:
            print ("Simulating...")
            
            startTime = time.time()
            num_processors = cpu_count
            p=mp.Pool(processes = num_processors)
            output = p.starmap(wSS_SP.SimulateSingleSlice_Worker,workerArguments)
            endTime = time.time()
            print("totalTime = {}".format(endTime-startTime))
            
            dfs = []
            agDFs = []
            for i in range(len(output)):
                dfs.append(output[i][0])
                agDFs.append(output[i][1])
                
            out_df1 = pd.concat(dfs,ignore_index=True) #star map guarantees orders are returned in the same order as u send it in
            out_df2 = pd.concat(agDFs) #star map guarantees orders are returned in the same order as u send it in
        
            csvFilename1 = saveDirectory+"\\" + "FL_and_Torque_{}_{}_{}skew.csv".format(
                                            settings["RMSCurrent"],
                                            settings["phaseAdvanceAngle"],
                                            settings['noOfSlices'])
            out_df1.to_csv(csvFilename1)
            print ("CSV of the values saved in {}".format(csvFilename1))
            
            csvFilename2 = saveDirectory+"\\" + "agReadings_{}_{}_{}skew.csv".format(
                                            settings["RMSCurrent"],
                                            settings["phaseAdvanceAngle"],
                                            settings['noOfSlices'])
            out_df2.to_csv(csvFilename2)
            print ("CSV of the values saved in {}".format(csvFilename1))        
            
                
            # # Remove temporary .fem and .ans files
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
            
                
            
        if PROCESS_FL_TORQUE_RESULTS:
            #calculates flux Linkage, torque, Ld, Lq, magnetic torque, relucatnace torque, analytical torque,
            #top speed possible for given DC voltage
            
            print ("--- Processing Results---")
            # just calculate the basics for now.
            csvFilename = saveDirectory+"\\" + "FL_and_Torque_{}_{}_{}skew.csv".format(
                                            settings["RMSCurrent"],
                                            settings["phaseAdvanceAngle"],
                                            settings['noOfSlices'])
            try:
                df = pd.read_csv(csvFilename)
            except:
                print ("CSV not found! Simulate first!")
                sys.exit()
            
            results = process.processSingle_OP_Results(df,settings)
            pprint(results)
            
            settingsdf = pd.DataFrame([settings], columns=settings.keys()).T
            resultsdf = pd.DataFrame([results], columns=results.keys()).T
            out_df = pd.concat([settingsdf,resultsdf]) 
            
            csvFilename = saveDirectory+"\\" + "results_{}_{}_{}skew.csv".format(
                                            settings["RMSCurrent"],
                                            settings["phaseAdvanceAngle"],
                                            settings['noOfSlices'])
            out_df.to_csv(csvFilename)
            print ("CSV of the results saved in {}".format(csvFilename))
        
        if PROCESS_FEA_RESULTS:
            print ("--- Processing FEA Results---")
            # just calculate the basics for now.
            csvFilename = saveDirectory+"\\" + "agReadings_{}_{}_{}skew.csv".format(
                                            settings["RMSCurrent"],
                                            settings["phaseAdvanceAngle"],
                                            settings['noOfSlices'])
            try:
                df = pd.read_csv(csvFilename)
            except:
                print ("CSV not found! Simulate first!")
                sys.exit()
            
            #plot the 4 slices of airGap taking care to offset them correctly.
            # slice0 = df[df['sliceNo'] == 0]
            # slice1 = df[df['sliceNo'] == 1]
            # slice2 = df[df['sliceNo'] == 2]
            # slice3 = df[df['sliceNo'] == 3]
            # plt.plot(slice0['angles'],slice0['airGap_B'],'--')
            # plt.plot(slice1['angles'],slice1['airGap_B'],'--')
            # plt.plot(slice1['angles'],slice2['airGap_B'],'--')
            # plt.plot(slice1['angles'],slice3['airGap_B'],'--')
            # all1 = (np.array(slice0['airGap_B'])+np.array(slice1['airGap_B']) + 
            #     np.array(slice2['airGap_B'])+np.array(slice3['airGap_B']))/4
            # plt.plot(slice0['angles'],all1,'k',label="final")
            # plt.legend()
            # plt.grid()
            
            # plt.figure()
            # plt.plot(slice0['angles'],slice0['radius_statorYoke_B'],'--')
            
            #choose some RPM and get the phasor value
            #also get the steel loss  - need maxB values from simulation for teeth and
            # stator yoke, for which we need to define the points where that contour is drawn            
            # MTPA angle
            # Losses
  
                    
    except: 
        print ("Error!")
        print(traceback.format_exc())
    
        


    


    
