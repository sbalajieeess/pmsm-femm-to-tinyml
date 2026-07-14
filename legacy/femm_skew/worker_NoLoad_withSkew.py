import Simulate as sim
import pandas as pd
import time
import sys
import femm
import os
import json

import numpy as np
import matplotlib.pyplot as plt


def WorkerNoLoad_withSkew(filename,workerNo,noOfTasks,angles,sliceNos,skews,saveFolderIn=-1,verbose = 0):
    totalSims = noOfTasks
    
    alldcts = []
    
    usePrev = 0
    overall_start_time = time.time() 
    
    #rootFolder = os.path.dirname(filename)# to save the AG Dict   
    # directory = rootFolder +"\\Jsons\\OC\\"
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    
    femm.openfemm(1)
    femm.opendocument(filename)
    
    for idx in range(noOfTasks):
        rotorMechAngle = angles[idx] 
        sliceNo = sliceNos[idx]
        skewMechAngle = skews[idx]
        
        t0 = time.time()
        #all currents are zero
        Ia = 0
        Ib = 0
        Ic = 0
    
        if (idx != 0):
            usePrev = 1
                
            
        angle_withSkew = rotorMechAngle  + skewMechAngle
        [wa,wb,wc],torque,blockTorque,_ = sim.simulateFemm_wSlidingAirGap(filename,Ia,Ib,Ic,angle_withSkew,
                                                           None, # input to do with getting pt or line data
                                                           smartMeshOn = 0,
                                                           usePrevSolution = usePrev,
                                                           slidingBand = "slidingBand")
            
        dct = {"sliceNo":sliceNo,"skewMechAngle":skewMechAngle,"rotorAngle":rotorMechAngle,"AngleWithSkew":angle_withSkew,"wa":wa,"wb":wb,"wc":wc,"torque":torque,"blockTorque":blockTorque}
        alldcts.append(dct)
        
        t1 = time.time()
                    
        if verbose:
            print("workerNo {},sliceNo = {},skewMechAngle = {},rotorangle = {},AngleWithSkew={},simNo={}/{},runtime = {}s".format(workerNo,sliceNo,skewMechAngle,rotorMechAngle,angle_withSkew,idx+1,noOfTasks,(t1 - t0)),flush=True) 
            #print("wa = {},wb= {},wc= {}".format(wa,wb,wc))
        
    femm.closefemm()    
    overall_end_time = time.time()
    print("--- workerNo {} overall {} seconds ---".format(workerNo,(overall_end_time- overall_start_time)))
    df = pd.DataFrame(alldcts)
    return df

