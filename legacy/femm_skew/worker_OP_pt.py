# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 16:30:02 2024

@author: harsh
"""

import numpy as np
import time
import Simulate as sim
import femm
import ClarkPark as cp
import pandas as pd
import os
import meshProcessing as mesh
import json

def SimulateHalfCycle_Worker(filename,worker,RMSCurrent,currentAngle,settings,taskAngles,saveMesh=0,verbose = 0):

    dAxisAngle_slidingBand = settings["dAxis_slidingBand"]
    usingSymmetry = settings["Symmetry"]
    polePairs =  settings["polePairs"]
    luaFileOrig = settings["MeshLuaScript"]
    [startAngle,endAngle,deltaAngle] = taskAngles
    totalSims = int((endAngle - startAngle)/ deltaAngle)+1

    airGapSavingOn = 0
    if airGapSavingOn:
        rootFolder = os.path.dirname(filename)# to save the AG Dict    
        directory = rootFolder +"\\Jsons\\OL\\"+str(RMSCurrent)+"_"+str(currentAngle)+"\\"
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        
    IdRMS = RMSCurrent * np.sin(np.deg2rad(currentAngle))
    IqRMS = RMSCurrent * np.cos(np.deg2rad(currentAngle))      
    
    femm.openfemm(1)
    femm.opendocument(filename)
    
    previousTime = 0
    alldcts=[]
    startTime = time.time()
    electricalAngle = startAngle
    for idx  in range(totalSims):
    
        t0 = time.time()
        if (verbose): 
            print ("----Worker {} {}/{}:RMS {} CA {} electricalAngle {} previousTime {}".format(worker,idx,totalSims,RMSCurrent,currentAngle,electricalAngle,previousTime))
        # on load
        [IaRMS,IbRMS,IcRMS],[alpha,beta] = cp.getABCfromDQ(IdRMS,IqRMS,electricalAngle)
        Ia = IaRMS * np.sqrt(2)
        Ib = IbRMS * np.sqrt(2)
        Ic = IcRMS * np.sqrt(2)
        # if (verbose):     
        #     print ("---OnLoadSim---")
        #     print ("Id,Iq = {},{}".format(IdRMS,IqRMS))
        #     print ("Ia,Ib,Ic = {},{},{}".format(Ia,Ib,Ic))
        
        usePrev = 0
        if idx != 0:
            usePrev = 1

        #keep smart mesh on when mesh processing for better graphics
        smartMesh_turnOn = 0
        if saveMesh:
            smartMesh_turnOn = 1
                        
        mechRotorAngle = cp.convertElAngleToMechAngle(electricalAngle,polePairs)  
        rotorAngle_into_FEM = dAxisAngle_slidingBand+mechRotorAngle #this is to move the rotor to the d axis and then current angle
        [wa,wb,wc],torque,blockTorque,agDict = sim.simulateFemm_wSlidingAirGap(filename,Ia,Ib,Ic,rotorAngle_into_FEM,
                                                                        smartMeshOn = smartMesh_turnOn,
                                                                        airGapB = airGapSavingOn,
                                                                        usePrevSolution = usePrev,
                                                                        slidingBand = "slidingBand")
        wa = wa*usingSymmetry
        wb = wb*usingSymmetry
        wc = wc*usingSymmetry
        blockTorque = blockTorque * usingSymmetry

        #we only want to save Onload airGapDict
        if airGapSavingOn:
            filename = directory +"\\AG_OL-" +str(electricalAngle) +".json"
            with open(filename, "w") as outfile: 
                json.dump(agDict, outfile)
                
        
        if saveMesh:
            # since we re using siding band and not rotating the rotor, the node indexes of a point in the rotor 
            #dont change,even if the rotor rotates.We also save only the loaded mesh, not the IQ=0 mesh
            l = mesh.MeshProcessing(filename, luaFileOrig, [RMSCurrent,currentAngle,electricalAngle,worker])
            l.replace("\\", "/")
            s = 'dofile("' + l + '")'
            #now run the script so that the results get created
            femm.callfemm(s)
            # Delete the LUA script
            os.remove(l)

        # if (verbose):
        #     print ("wa,wb,wc = {},{},{}".format(wa,wb,wc))
        #     print ("torque,blockTorque = {},{}".format(torque,blockTorque))
        
        #qAxis OC
        # if verbose:
        #     print ("---NoLoadQAxisSim---")
        [IaRMS_q,IbRMS_q,IcRMS_q],[alpha,beta] = cp.getABCfromDQ(0,IqRMS,electricalAngle)
        Ia_q = IaRMS_q * np.sqrt(2)
        Ib_q = IbRMS_q * np.sqrt(2)
        Ic_q = IcRMS_q * np.sqrt(2)

        usePrev = 1
        # if verbose:
        #     print ("Id,Iq = {},{}".format(0,IqRMS))
        #     print ("Ia_q,Ib_q,Ic_q = {},{},{}".format(Ia_q,Ib_q,Ic_q))
        [wa_q,wb_q,wc_q],torque_q,blockTorque_q,_ = sim.simulateFemm_wSlidingAirGap(filename,Ia_q,Ib_q,Ic_q,rotorAngle_into_FEM,usePrevSolution = usePrev,
                                                       slidingBand = "slidingBand")
        
        wa_q = wa_q*usingSymmetry
        wb_q = wb_q*usingSymmetry
        wc_q = wc_q*usingSymmetry
        blockTorque_q = blockTorque_q * usingSymmetry

        # if verbose:
        #     print ("wa,wb,wc = {},{},{}".format(wa_q,wb_q,wc_q))
        #     print ("torque,blockTorque = {},{}".format(torque_q,blockTorque_q))


        #print("{},{},{},{},{}:{}-{},{},{},{},{},{},{},{}".format(simulationNo,IRMS_amps,currentAngle,IqRMS,IdRMS,electricalAngle,Ia,Ib,Ic,wa,wb,wc,torque,blockTorque))
        #print ("{}:{},{},{}:{}sec,{}sec remaining".format(simulationNo,IRMS_amps,currentAngle,electricalAngle,deltaT,remainingTime))
        dct = {"Worker":worker,"electricalAngle":electricalAngle,"IRMS_amps":RMSCurrent,"currentAngle":currentAngle,"IqRMS":IqRMS,"IdRMS":IdRMS,
               "Ia":Ia,"Ib":Ib,"Ic":Ic,"wa":wa,"wb":wb,"wc":wc,"torque":torque,"blockTorque":blockTorque,
               "Ia_q":Ia_q,"Ib_q":Ib_q,"Ic_q":Ic_q,"wa_q":wa_q,"wb_q":wb_q,"wc_q":wc_q,"torque_q":torque_q,
               "blockTorque_q":blockTorque_q
              }
        alldcts.append(dct)
        previousTime = (time.time() - t0)
        electricalAngle += deltaAngle
        
    endTime = time.time()
    print("totalTime for worker {} = {}".format(worker,endTime-startTime))
    femm.closefemm()
    df = pd.DataFrame(alldcts)
    
    return df
