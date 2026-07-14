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
from shutil import copyfile

def SimulateSingleSlice_Worker(filename,worker,settings,simulation,saveMesh=0,verbose = 0,saveImage=0):

    dAxisAngle_slidingBand = settings["dAxis_slidingBand"]
    usingSymmetry = settings["Symmetry"]
    polePairs =  settings["polePairs"]
    luaFileOrig = settings["MeshLuaScript"]
    FEM_offsetAngle = settings["FEM_meshOffsetAngle"]
    FEA_Data = settings['FEA_plotPts']
    saveFEM_file = settings['save_OL_FEM_file'] 
    saveDirectory = settings['saveDirectory']
     
             
    RMSCurrent = simulation["RMSCurrent"]
    currentAngle = simulation["phaseAngle"]
    sliceIdx = simulation["sliceNo"]
    skewAngle = simulation["skewAngle"]
    rotorAngleElec = simulation["rotorAngleElec"]
        
    IdRMS = RMSCurrent * np.sin(np.deg2rad(currentAngle))
    IqRMS = RMSCurrent * np.cos(np.deg2rad(currentAngle))      
    
    femm.openfemm(1)
    femm.opendocument(filename)
    

    # if (verbose): 
    #     print ("----Worker {} RMS {} CA {} electricalAngle {} skewAngle {}".format(worker,RMSCurrent,currentAngle,rotorAngleElec,skewAngle))
    
    # on load
    [IaRMS,IbRMS,IcRMS],[alpha,beta] = cp.getABCfromDQ(IdRMS,IqRMS,rotorAngleElec)
    Ia = IaRMS * np.sqrt(2)
    Ib = IbRMS * np.sqrt(2)
    Ic = IcRMS * np.sqrt(2)
    if (verbose):     
        print ("---OnLoadSim---")
        print ("Id,Iq = {},{}".format(IdRMS,IqRMS))
        print ("Ia,Ib,Ic = {},{},{}".format(Ia,Ib,Ic))
        
    usePrev = 0 # have to simulate each time seperately
    #keep smart mesh on when mesh processing for better graphics. 8 sec wO smart mesh, 18 with, for 4 parallel sims
    smartMesh_turnOn = 0
    # if saveMesh:
    #     smartMesh_turnOn = 1
                        
    mechRotorAngle = cp.convertElAngleToMechAngle(rotorAngleElec,polePairs)  
    rotorAngle_into_FEM = dAxisAngle_slidingBand+mechRotorAngle+skewAngle #this is to move the rotor to the d axis and then current angle
    if FEA_Data is None:
       FEA_input = None
    else:
        FEA_input = [FEM_offsetAngle,FEA_Data,usingSymmetry]
        
    out = sim.simulateFemm_wSlidingAirGap(filename,Ia,Ib,Ic,rotorAngle_into_FEM,
                                          FEA_input, # input to do with getting pt or line data
                                          smartMeshOn = smartMesh_turnOn,
                                          usePrevSolution = usePrev,
                                          slidingBand = "slidingBand")
    
    [wa,wb,wc],torque,blockTorque,FEA_DF = out
    
    wa = wa*usingSymmetry
    wb = wb*usingSymmetry
    wc = wc*usingSymmetry
    blockTorque = blockTorque * usingSymmetry

    if saveFEM_file:
        saveName = saveDirectory  + os.path.basename(filename)[:-4]+"_"+str(RMSCurrent)+"_"+str(currentAngle)+".fem"
        saveName = saveName.replace("/","//")
        copyfile(filename,saveName)
        
    if (saveImage):
        #save Image
        femm.mo_zoomnatural()
        femm.mo_showdensityplot(1,0,1.6,0,"bmag")
        saveFilename = "{}_{}_{}_{}.bmp".format(sliceIdx,RMSCurrent,currentAngle,rotorAngleElec)
        femm.mo_savebitmap(saveDirectory + saveFilename)
        
    if saveMesh:
        # since we re using siding band and not rotating the rotor, the node indexes of a point in the rotor 
        #dont change,even if the rotor rotates.We also save only the loaded mesh, not the IQ=0 mesh
        l = mesh.prepareLuaScript(filename, luaFileOrig, [saveDirectory,sliceIdx,RMSCurrent,currentAngle,rotorAngleElec,worker])
        #l.replace("\\", "/")
        s = 'dofile("' + l + '")'
        femm.callfemm(s)#now run the script so that the results get created
        os.remove(l) # Delete the LUA script

    # if (verbose):
    #     print ("wa,wb,wc = {},{},{}".format(wa,wb,wc))
    #     print ("torque,blockTorque = {},{}".format(torque,blockTorque))
        
    #qAxis OC
    # if verbose:
    #     print ("---NoLoadQAxisSim---")
    [IaRMS_q,IbRMS_q,IcRMS_q],[alpha,beta] = cp.getABCfromDQ(0,IqRMS,rotorAngleElec)
    Ia_q = IaRMS_q * np.sqrt(2)
    Ib_q = IbRMS_q * np.sqrt(2)
    Ic_q = IcRMS_q * np.sqrt(2)
    # if verbose:
    #     print ("Id,Iq = {},{}".format(0,IqRMS))
    #     print ("Ia_q,Ib_q,Ic_q = {},{},{}".format(Ia_q,Ib_q,Ic_q))
    
    usePrev = 1
    
    FEA_input=None #dont want any FEM data for this simulation
    [wa_q,wb_q,wc_q],torque_q,blockTorque_q,_ = sim.simulateFemm_wSlidingAirGap(filename,Ia_q,Ib_q,Ic_q,rotorAngle_into_FEM,
                                                   FEA_input,
                                                   usePrevSolution = usePrev,
                                                   slidingBand = "slidingBand",
                                                   )
        
    wa_q = wa_q*usingSymmetry
    wb_q = wb_q*usingSymmetry
    wc_q = wc_q*usingSymmetry
    blockTorque_q = blockTorque_q * usingSymmetry

    # if verbose:
    #     print ("wa,wb,wc = {},{},{}".format(wa_q,wb_q,wc_q))
    #     print ("torque,blockTorque = {},{}".format(torque_q,blockTorque_q))


    dct = {"Worker":worker,"sliceNo":sliceIdx,"electricalAngle":rotorAngleElec,"IRMS_amps":RMSCurrent,"currentAngle":currentAngle,"IqRMS":IqRMS,"IdRMS":IdRMS,
           "Ia":Ia,"Ib":Ib,"Ic":Ic,"wa":wa,"wb":wb,"wc":wc,"torque":torque,"blockTorque":blockTorque,
           "Ia_q":Ia_q,"Ib_q":Ib_q,"Ic_q":Ic_q,"wa_q":wa_q,"wb_q":wb_q,"wc_q":wc_q,"torque_q":torque_q,
           "blockTorque_q":blockTorque_q
          }
    alldcts=[dct]
        
    femm.closefemm()
    df = pd.DataFrame(alldcts)
    FEA_DF['sliceNo'] = sliceIdx
    return [df,FEA_DF]
