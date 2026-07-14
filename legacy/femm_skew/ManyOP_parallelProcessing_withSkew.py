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
from glob import glob
import traceback
import ast


import ClarkPark as cp
import worker_SingleSlice_SinglePt as wSS_SP
import processingFns as process

###WITH SLIDING BAND,MULTIPROCESSING AND SKEW, JUST MANY current and phase Angles, BUT ONLY ONE ROTOR ANGLE(0)
#First Create the File , then Process It
#FEMM file must have the correct stack length

DO_SIMS = 1
PROCESS_RESULTS = 1
PROCESS_ALL_FILES_IN_FOLDER = 1 # if zero will do the same Current and current Angles that are there in the DOSIMS input
SAVE_FEM_FILE_WITH_LOAD_CURRENTS = 1

fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_100C.FEM" # stack length of the motor has to be set in the file correctly
fem_file = r"C:/Work/FEMM_Server/CodeForDrawing/test/oneEighth_100C.FEM"
FEA_pts_file = None #r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_FEA_pts.csv"
def main():
    if __name__ ==  '__main__': 
        #SETUP FOR MULTI POINT PROCESSING
        rootFolder = os.path.dirname(fem_file)
        filename = os.path.basename(fem_file)
        print ("rootDirectory = {}".format(rootFolder))
        print ("filename = {}".format(filename))
        
        
        settings=OrderedDict()
        settings['filename'] = filename
        settings["dAxis_slidingBand"] = 4
        settings["DC_Voltage"] = 400
        settings["RMSCurrent"] = 100
        settings["phaseAdvanceAngle"] = 30
        settings["Symmetry"] = 8
        settings["polePairs"] = 4
        settings['noOfSlices'] = 4
        settings['skew_AnglesMech'] = [2.8125, 0.9375, -0.9375, -2.8125]
        settings['rotorAngleElec'] = 0
        settings['resistance_mO'] = 3.5
        settings["MeshLuaScript"] = "C:/Work/FEMM_Server/multiprocessingCode/get_mesh_data_FEMM.lua"
        print ("---SimulationSettings---")
        
        #needs to be modified for every FEM file
        if FEA_pts_file is not None:
            try:
                feaPts_df = pd.read_csv(FEA_pts_file,index_col=0)
                B_linePlots = {}
                B_linePlots['radius_statorYoke'] = float(feaPts_df.loc["radius_statorYoke","Values"])
                B_linePlots['radius_statorTeeth'] = float(feaPts_df.loc["radius_statorTeeth","Values"])
                B_linePlots['radius_statorTeethPole'] = float(feaPts_df.loc["radius_statorTeethPole","Values"])
                magnetPt1_string = feaPts_df.loc["magnetPts1","Values"]
                magnetPt2_string = feaPts_df.loc["magnetPts2","Values"]
                magnetPts= [ast.literal_eval(magnetPt1_string),ast.literal_eval(magnetPt2_string)]
                FEA_data= [B_linePlots,magnetPts] #make FEA data None if you dont want this
                FEM_meshOffsetAngle = float(feaPts_df.loc["FEM_meshOffsetAngle","Values"])
                settings["FEM_meshOffsetAngle"] = FEM_meshOffsetAngle
                settings['FEA_plotPts']= FEA_data 
            except:
                print ("Error In FEA pts File!")
                print(traceback.format_exc())
                sys.exit()
        else:
            settings["FEM_meshOffsetAngle"] = None
            settings['FEA_plotPts']= None 
                
        pprint(settings)
        print ("---------")
            
        cpu_count = 4 # no of slices does not have to be same as no of Workers.
        
        #create a folder to put all the results in
        saveDirectory = rootFolder+"\\"+filename[:-4]+"\\SkewOutputs_{}Slices\\OL\\".format(settings['noOfSlices'])
        if not os.path.exists(saveDirectory):
            os.makedirs(saveDirectory)
        
        settings['save_OL_FEM_file'] = SAVE_FEM_FILE_WITH_LOAD_CURRENTS
        settings['saveDirectory'] = saveDirectory
        
        print("parallel_workers = {}".format(cpu_count))
        
        tasks_per_worker = []
        tasks_to_split = settings['noOfSlices']
        for idx in range(cpu_count,0,-1): # get how many tasks per worker
            tasks_per_worker.append(tasks_to_split // idx + ((tasks_to_split % idx) > 0))
            tasks_to_split -= tasks_per_worker[-1]
            
        print("tasks_per_worker = {}".format(tasks_per_worker))
        
        currentList = [100]#np.arange(220,301,10)
        currentAngleList = [-30]
        total_overall_sims = len(currentList) * len(currentAngleList)
        print ("no Of currents = {} , no of CAs per current = {}".format(len(currentList),len(currentAngleList)))
        print ("total overall Sims (each sim has OC and OL) = {} ".format(total_overall_sims))
        
        # ACTUAL SIMULATION
        try:
            if DO_SIMS:
                print ("Simulating...")
                overAllTime = 0
                num_processors = cpu_count
                simulationNo = 1
                for current in currentList:
                    for CA in currentAngleList:
                        print ("---{}/{} CURRENT ={}, CA = {}, overAllTime={}".format(simulationNo,total_overall_sims,current,CA,overAllTime))
                        
                        settings["RMSCurrent"] = current
                        settings["phaseAdvanceAngle"] = CA
                        
                        workerArguments = []
                        
                        verbosePrinting = 1
                        saveBMP_image = 0
                        saveMesh = 0 # doesnt Work
                        for i in range(cpu_count):   
                            workerFile = fem_file[:-4] + "_" + str(i) + ".fem"
                            copyfile(fem_file, workerFile)
                            sliceSettings= {}
                            sliceSettings["RMSCurrent"] = settings["RMSCurrent"]
                            sliceSettings["phaseAngle"] = settings["phaseAdvanceAngle"]
                            sliceSettings["rotorAngleElec"]  = settings['rotorAngleElec']
                            sliceSettings["sliceNo"] = i
                            sliceSettings["skewAngle"] = settings['skew_AnglesMech'][i]
                            workerArguments.append([workerFile,i,settings,sliceSettings,saveMesh,verbosePrinting,saveBMP_image])
            
                            # print ("---worker {}---".format(i))
                            # pprint(sliceSettings)                    
                        
                        startTime = time.time()
                        p=mp.Pool(processes = num_processors)
                        output = p.starmap(wSS_SP.SimulateSingleSlice_Worker,workerArguments)
                        endTime = time.time()
                        print("simulationTime = {}".format(endTime-startTime))
                        overAllTime += (endTime-startTime)
                        
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
                        
                        simulationNo = simulationNo+1
                        
                        
            if PROCESS_RESULTS:
                print ("--- Processing Results---")
                
                if PROCESS_ALL_FILES_IN_FOLDER:
                    files = glob(saveDirectory+"*FL_and_Torque*.csv")
                    currentList = []
                    currentAngleList = []
                    for idx in range(len(files)):
                        filepath = files[idx]
                        filename = os.path.basename(filepath)
                        sections = filename[len("FL_and_Torque_"):].split("_")
                        current = int(sections[0])
                        currentAngle = int(sections[1])
                        currentList.append(current)
                        currentAngleList.append(currentAngle)

                    currentList = np.sort(np.unique(np.array(currentList)))
                    currentAngleList = np.sort(np.unique(np.array(currentAngleList)))[::-1]
                    total_overall_sims = len(currentList) * len(currentAngleList)
                    print ("found the following currents and current Angles simulation files in the folder :")
                    print(currentList)
                    print(currentAngleList)
                    print ("----")
                
                missed_operatingPts = []
                simulationNo = 0
                for current in currentList:
                    for CA in currentAngleList:
                        print ("---{}/{}".format(simulationNo,total_overall_sims))
                                                                                      
                        settings["RMSCurrent"] = current
                        settings["phaseAdvanceAngle"] = CA
                        

                        # just calculate the basics for now.
                        csvFilename = saveDirectory+"\\" + "FL_and_Torque_{}_{}_{}skew.csv".format(
                                                        settings["RMSCurrent"],
                                                        settings["phaseAdvanceAngle"],
                                                        settings['noOfSlices'])
                        
                        try:
                            df = pd.read_csv(csvFilename)
                        except:
                            print ("CSV not found!!")
                            missed_operatingPts.append((current,CA))
                            continue
                    
                            
                        results = process.processSingle_OP_Results(df,settings)
                        # pprint(results)
                        
                        settingsdf = pd.DataFrame([settings], columns=settings.keys()).T
                        resultsdf = pd.DataFrame([results], columns=results.keys()).T
                        out_df = pd.concat([settingsdf,resultsdf]) 
                        
                        csvFilename = saveDirectory+"\\" + "results_{}_{}_{}skew.csv".format(
                                                        settings["RMSCurrent"],
                                                        settings["phaseAdvanceAngle"],
                                                        settings['noOfSlices'])
                        
                        
                        out_df.rename(columns={out_df.columns[0]: "Values"}, inplace=True)
                        out_df.to_csv(csvFilename)
                        print ("CSV of the results saved in {}".format(csvFilename))
                        simulationNo = simulationNo + 1     
                        
          
                
        
        except: 
            print ("Error!")
            print(traceback.format_exc())
        
   
        
main()


    


    
