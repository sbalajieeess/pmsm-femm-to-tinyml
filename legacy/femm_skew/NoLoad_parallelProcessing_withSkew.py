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

###WITH SLIDING BAND,MULTIPROCESSING AND SKEW
#First Create the File , then Process It
#FEMM file must have the correct stack length

DO_SIMS = 1
PROCESS_RESULTS = 1
SAVE_IMAGES= 1
SHOW_IMAGES = 0

fem_file = r"C:/Work/Projects/LTTS_Work/design5_152mm/oneEighth_60C_manufacturing.FEM" # stack length of the motor has to be set in the file correctly
fem_file =  r"C:/Work/FEMM_Server/CodeForDrawing/test/oneEighth_100C.FEM"
rootFolder = os.path.dirname(fem_file)
filename = os.path.basename(fem_file)
print ("rootDirectory = {}".format(rootFolder))
print ("filename = {}".format(filename))

Symmetry= 8
polePairs = 4
mechAnglePerPolePair = 360/polePairs
deltaAngle = 1
totalSimsPerSlice  = int(mechAnglePerPolePair/deltaAngle)

no_of_skew_Slices = 4
skew_Angles = [2.8125, 0.9375, -0.9375, -2.8125] #  [-2.5,0,2.5] #
cpu_count = 12 # no of slices does not have to be same as no of Workers.

total_overall_sims  = totalSimsPerSlice * no_of_skew_Slices

#create a folder to put all the results in
saveDirectory = rootFolder+"\\"+filename[:-4]+"\\SkewOutputs_{}Slices\\NoLoad\\".format(no_of_skew_Slices)
if not os.path.exists(saveDirectory):
    os.makedirs(saveDirectory)
    
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
        if currentAngle>=mechAnglePerPolePair:
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
    t0 = time.time()
    if DO_SIMS:
        num_processors = cpu_count
        p=mp.Pool(processes = num_processors)
        output = p.starmap(wNL_wS.WorkerNoLoad_withSkew,workerArguments)
        df = pd.concat(output,ignore_index=True) #star map guarantees orders are returned in the same order as u send it in
    
        csvFilename = saveDirectory+"\\" + "Symmetry_SlidingBand_withSkew.csv"
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
        
        csvFilename = saveDirectory+"\\" + "Symmetry_SlidingBand_withSkew.csv"
        df = pd.read_csv(csvFilename)
        #Now PROCESS and get the noLoad backemf and also location of the d Axis
        
        slicesDFs = []
        slice_FLs= []
        smoothedFLs = []
        slice_dFLs=[]
        for idx in range(no_of_skew_Slices):
            sliceDF = df[df['sliceNo'] == idx+1]
            sliceFL = np.array(sliceDF['wa']) #slice flux Linkage
            slice_dFL = np.ediff1d(sliceFL,to_end=sliceFL[0] - sliceFL[-1])
            slicesDFs.append(sliceDF)
            slice_FLs.append(sliceFL)
            slice_dFLs.append(slice_dFL)
            
        rotorAngles = slicesDFs[0]['rotorAngle']
        
        #1. plot slice FL's and slicedFL unscaled
        plt.figure()
        t1 = slice_FLs[0]
        t2 = slice_dFLs[0]*10
        rAngles = np.array(rotorAngles)
        plt.plot(rAngles,t1,'-x',label='slice1 FL')
        plt.plot(rAngles,t2,label='dFL_slice1*10')
        plt.legend()
        plt.title("1 : singleSlice's Phase BackEMF(unscaled) and FluxLinkage")
        plt.grid()
        
        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "1_singleSlice_FL_and_dFL.png"
            plt.savefig(imgName)
            print ("plot image of coggingTorque saved in {}".format(imgName))
            
         
        #2.Summing all the FLs and finding the dAxis rotorAngle
        totalFL_unscaled = 0
        total_FL_scaled = 0
        for LF in slice_FLs:
            totalFL_unscaled = totalFL_unscaled + LF
        total_FL_scaled = totalFL_unscaled * Symmetry
        
        maxIdx = int(np.argmax(totalFL_unscaled))
        maxAngle = rotorAngles.iloc[maxIdx]
        maxPhaseFluxValue =np.max(totalFL_unscaled)
            
        print("{} is maxAngle,{} is max phase U flux value (unscaled)".format(maxAngle,maxPhaseFluxValue))
        print ("scaled Max FL = {}".format(np.max(total_FL_scaled)))
        # 0 angle should be 90 electrical degrees away, in mechanical degrees that is x degrees away
        mech_90_electrical_degrees = mechAnglePerPolePair/4
        qAngle = maxAngle-mech_90_electrical_degrees
        print("{} should be q Axis ".format(qAngle))
        
        print('------------')
        if Symmetry:
            print("maxU phase flux Value = " + str(maxPhaseFluxValue *Symmetry))
            BackEMF_Vll_RMS = (maxPhaseFluxValue* Symmetry) * 104.72 * polePairs * np.sqrt(3)/np.sqrt(2) # 
        else:
            BackEMF_Vll_RMS = (maxPhaseFluxValue) * 104.72 * polePairs * np.sqrt(3)/np.sqrt(2) # 
        
        print("BackEMF of this motor is (Vll-rms) = " + str(BackEMF_Vll_RMS))
        phaseBackEMF_RMS = BackEMF_Vll_RMS/1.732
        print("BackEMF of this motor is (Vphase-rms) = " + str(phaseBackEMF_RMS))
        
        
        plt.figure()
        for idx in range(len(slice_FLs)):
            plt.plot(rAngles,slice_FLs[idx],'-',label='slice{}'.format(idx+1))
            
        plt.plot(rAngles,totalFL_unscaled,label='totalFL(unscaled)')
        plt.axvline(maxAngle,color='r')
        plt.title("2:Total fluxLinkage across one Pole pair (in Mech Degrees)")
        plt.legend()
        plt.grid()
        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "2_singleSlice_FL_and_dFL.png"
            plt.savefig(imgName)
            print ("plot image of coggingTorque saved in {}".format(imgName))
                             
    
        #3.Summing all the dFLs and seeing phase Back EMF
        total_dFL_unscaled = 0
        for dFL in slice_dFLs:
            total_dFL_unscaled = total_dFL_unscaled + dFL
            
        #assume we re rotating at 1000 RPM, then time for 1 rev = 
        revs_in_1_Sec = 1000/60
        elec_revs_in_1_Sec = revs_in_1_Sec * polePairs
        time_for_1_elec_rev =1.0/elec_revs_in_1_Sec
        time_for_each_step = time_for_1_elec_rev/totalSimsPerSlice
        
        phaseBackEMF = total_dFL_unscaled/time_for_each_step * Symmetry
        
        plt.figure()
        for idx in range(len(slice_FLs)):
            plt.plot(rAngles,slice_dFLs[idx],'-',label='slice_dFL{}'.format(idx+1))
             
        plt.plot(rAngles,total_dFL_unscaled,label='totaldFL(unscaled)')
        plt.title("3A:Total dFL across one Pole pair (in Mech Degrees)")
        plt.legend()
        plt.grid()
        
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "3A_dFLs_summed_unscaled.png"
            plt.savefig(imgName)
            print ("plot image of dFL unscaled saved in {}".format(imgName))  
            
        
        plt.figure()             
        plt.plot(rAngles,phaseBackEMF,label='phaseBackEMF(scaled)')
        plt.title("3B:phaseBackEMF across one Pole pair (in Mech Degrees)")
        plt.legend()
        plt.grid()
        
        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "3B_phaseBackEMF.png"
            plt.savefig(imgName)
            print ("plot image of phaseBackEMF saved in {}".format(imgName))  
        
        #now get L-L backEMF from the phase Back EMF
        simsPerEl360 = totalSimsPerSlice
        rows_per_120EdegShift = simsPerEl360/3
        int_rows_per_120EdegShift = int(rows_per_120EdegShift)
        if not(int_rows_per_120EdegShift == rows_per_120EdegShift):
            print ("Warning : shift for phase BackEMF is not an integer")
        
        phase2_backEMF = np.roll(phaseBackEMF,int_rows_per_120EdegShift)
        phase3_backEMF = np.roll(phaseBackEMF,2*int_rows_per_120EdegShift)
        phaseBackEMF_pk = np.round(np.max(phase2_backEMF),2)
        phaseBackEMF_rms = np.round(phaseBackEMF_pk/1.414,2)
        
        phase1_2LL_backEMF =  phaseBackEMF - phase2_backEMF
        phase1_2LL_backEMF_RMS =  phase1_2LL_backEMF/np.sqrt(2)
        pk_VLL_rms_fromPhaseBackEMFs = np.max(phase1_2LL_backEMF_RMS)
        
        plt.figure()             
        plt.plot(rAngles,phaseBackEMF,'--',label='phase1BackEMF')
        plt.plot(rAngles,phase2_backEMF,'--',label='phase2BackEMF')
        plt.plot(rAngles,phase3_backEMF,'--',label='phase3BackEMF')
        plt.plot(rAngles,phase1_2LL_backEMF,label='phases 1-2 LL backEMF')
        plt.plot(rAngles,phase1_2LL_backEMF_RMS,label='phases 1-2 LL back EMF RMS')
        plt.title("3C:phase and Line BackEMFs across one Pole pair (in Mech Degrees)")
        plt.legend()
        plt.grid()
        
        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "3C_phaseAndLineBackEMFs.png"
            plt.savefig(imgName)
            print ("plot image of phaseAndLineBackEMFs saved in {}".format(imgName))  
       
        
       # 3D compare the back emf we get from scaling the fluxLinkage with the one we get by subtracting the phase Back EMFS;
        LL_backEmf_fromFL_directly = total_FL_scaled * 104.72 * polePairs * np.sqrt(3)/np.sqrt(2)
        LL_backEmf_fromFL_directly_rolled = np.roll(LL_backEmf_fromFL_directly,-int(int_rows_per_120EdegShift))
        plt.figure()             
        plt.plot(rAngles,phase1_2LL_backEMF_RMS,label='LLBackEMF_fromSubtractingPhaseBackEMFs')
        plt.plot(rAngles,LL_backEmf_fromFL_directly_rolled,label='LLBackEMF_fromFL')
        plt.title("3D:Two Methods - Line-Line BackEMFs across one Pole pair (in Mech Degrees)")
        plt.legend()
        plt.grid()
        
        if SHOW_IMAGES:
            plt.show()
        if SAVE_IMAGES:
            imgName =  saveDirectory+ "3D_LL_BackEmfs_BothMethods.png"
            plt.savefig(imgName)
            print ("plot image of LL_BackEmfs_BothMethods saved in {}".format(imgName))  
        
        if SAVE_IMAGES:    
            plt.close('all')
       
        
        print ("---Comparing Back EMF LL Vrms from Different Methods---")
        print ("from  phase Linkage Scaled = {}".format(BackEMF_Vll_RMS))  
        print ("from  phase Back EMFs Subtracted = {}".format(pk_VLL_rms_fromPhaseBackEMFs))
        
        print ("---phase BackEMFs---")
        print ("phase Back EMF pk (from differentiating the measured fluxLinkage = {}".format(phaseBackEMF_pk))
        print ("phase Back EMF rms (from differentiating the measured fluxLinkage = {}".format(phaseBackEMF_rms))
        
        textFilename = saveDirectory  + "noLoadResults.txt"
        f = open(textFilename, "w")
        f.write("dAxis angle = " + str(maxAngle) + "\n")
        f.write("ran with Symmetry = " + str(Symmetry) + "\n")
        f.write("pole Pairs = " + str(polePairs) + "\n")
        f.write("maxU phase flux Value = = " + str(maxPhaseFluxValue * Symmetry) + "\n")
        f.write("Hence Back Emf Vllrms calculated from FL = = " + str(BackEMF_Vll_RMS) + "\n")
        
        f.write("Back Emf Vllrms calculated from phase Back EMFs = " + str(pk_VLL_rms_fromPhaseBackEMFs) + "\n")
        f.write ("phase Back EMF pk (from differentiating the measured fluxLinkage) = {}".format(phaseBackEMF_pk) + "\n")
        f.write ("phase Back EMF rms (from differentiating the measured fluxLinkage) = {}".format(phaseBackEMF_rms) + "\n")

        f.close()
        
        print ("Text Results saved in {}".format(textFilename))
    
        t1 = time.time()
        totalTime = t1 - t0
        print ("total Processing Time = {}".format(totalTime))
    
    

    
