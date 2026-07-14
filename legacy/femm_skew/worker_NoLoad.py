# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 13:02:21 2024

@author: harsh
"""

import Simulate as sim
import pandas as pd
import time
import sys
import femm
import os
import json

import numpy as np

def NoLoadSlidingBand_Parallel(filename,workerNo,startAngle,endAngle,deltaAngle,saveFolderIn=-1,verbose = 0):
    totalSims = int((endAngle - startAngle)/ deltaAngle)+1
    
    alldcts = []
    angle = startAngle
    usePrev = 0
    overall_start_time = time.time()  
    rootFolder = os.path.dirname(filename)# to save the AG Dict
    
    directory = rootFolder +"\\Jsons\\OC\\"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    femm.openfemm(1)
    femm.opendocument(filename)
    
    for currentSim in range(totalSims):
        t0 = time.time()
        #all currents are zero
        Ia = 0
        Ib = 0
        Ic = 0

        if (angle != startAngle):
            usePrev = 1
        [wa,wb,wc],torque,blockTorque,agDict = sim.simulateFemm_wSlidingAirGap(filename,Ia,Ib,Ic,angle,usePrevSolution = usePrev,
                                                       airGapB = 1,
                                                       saveFolder = saveFolderIn,
                                                       saveFilename=str(angle))
        dct = {"angle":angle,"wa":wa,"wb":wb,"wc":wc,"torque":torque,"blockTorque":blockTorque}
        alldcts.append(dct)
    
        t1 = time.time()
        
        filename = directory +"\\AG_OC-" +str(angle) +".json"
        with open(filename, "w") as outfile: 
            json.dump(agDict, outfile)
        
        if verbose:
            print("workerNo {},angle = {},simNo={}/{},runtime = {}s".format(workerNo,angle,currentSim+1,totalSims,(t1 - t0)),flush=True) 
            #print("wa = {},wb= {},wc= {}".format(wa,wb,wc))
        angle += deltaAngle
        
    femm.closefemm()    
    overall_end_time = time.time()
    print("--- workerNo {} overall {} seconds ---".format(workerNo,(overall_end_time- overall_start_time)))
    df = pd.DataFrame(alldcts)
    return df

