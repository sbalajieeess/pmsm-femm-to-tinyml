# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 23:05:34 2024

@author: harsh
"""
import pandas as pd
import matplotlib.pyplot as plt
import ClarkPark as cp
import numpy as np
import os

from glob import glob
from tqdm import tqdm
import scipy

rawFolder = r"C:/Work/FEMM_Server/iitLTTS/48-8V_ipm/raw_data//"
saveFolder= r"C:/Work/FEMM_Server/iitLTTS/48-8V_ipm/processedData//"

VDC = 400
polePairs = 4

    
#in phase space
def calculateVphase(RPM,motorSpecs):
    out = {}
    pp = motorSpecs['polePairs']
    psiD = motorSpecs['average_psiD_RMS'] 
    avgLd = motorSpecs['Ld']
    avgLq = motorSpecs['Lq']
    out['we'] = RPM/9.55 * pp
    out['backEMF'] = psiD * out['we']
    out['Xd'] = out['we']*avgLd
    out['Xq'] = out['we']*avgLq
    XdId = out['Xd'] * IdRMS
    XqIq = out['Xq'] * IqRMS
    out['Vd'] = -XqIq
    out['Vq'] = out['backEMF'] + XdId
    out['VphRMS'] = np.sqrt(out['Vd']**2 + out['Vq']**2)
    return out

def optimizeRPM(RPM,targetVph,motorSpecs):
    out = calculateVphase(RPM,motorSpecs)
    return abs(targetVph - out['VphRMS'])
    

files = glob(rawFolder+"*.csv")
# print (files)

for idx in  tqdm(range(len(files))):
    file = files[idx]
    df = pd.read_csv(file,index_col=0)
    
    #onLoad
    [psiD,psiQ],_ =  cp.getDQfromABC(df['wa'],df['wb'],df['wc'],df['electricalAngle'])
    df['psiD_RMS'] = psiD/np.sqrt(2)
    df['psiQ_RMS'] = psiQ/np.sqrt(2)
    
    #Q axis OC
    [psiD_q,psiQ_q],_ =  cp.getDQfromABC(df['wa_q'],df['wb_q'],df['wc_q'],df['electricalAngle'])
    df['psiD_q_RMS'] = psiD_q/np.sqrt(2)
    df['psiQ_q_RMS'] = psiQ_q/np.sqrt(2)
    
    #individual eAngle for each rotor Position
    if (df['IdRMS'].iloc[0] != 0):
    	df['Ld_eAngle'] = (df['psiD_RMS'] - df['psiD_q_RMS'])/df['IdRMS']
    else:
    	df['Ld_eAngle'] = 0
    df['Lq_eAngle'] = (df['psiQ_RMS']/df['IqRMS'])
          
    df['magneticTorque_eAngle'] = (df['psiD_q_RMS'] * df['IqRMS'])* 3 * polePairs
    df['reluctance_Torque_eAngle'] = (df['IdRMS']*df['IqRMS'])*(df['Ld_eAngle'] - df['Lq_eAngle']) * 3 * polePairs
    df['analyticalTorque_total_eAngle'] = df['magneticTorque_eAngle'] + df['reluctance_Torque_eAngle']
    df['reluctanceTorque%'] =  np.round(df['reluctance_Torque_eAngle']*100/df['analyticalTorque_total_eAngle'],2)
    
    
    df['average_psiD_RMS'] = np.nan
    df['averageLd'] = np.nan
    df['averageLq'] = np.nan
    df['average_magTorque'] = np.nan
    df['average_relTorque'] = np.nan
    df['average_total'] = np.nan
    df['average_psiD_RMS'] = np.nan
    
    df.loc[0,'average_psiD_RMS'] = df['psiD_q_RMS'].mean()
    df.loc[0,'averageLd'] = df["Ld_eAngle"].mean()
    df.loc[0,'averageLq'] = df["Lq_eAngle"].mean()
    df.loc[0,'average_magTorque'] = (df['average_psiD_RMS'].iloc[0] * df['IqRMS'].iloc[0])* 3 * polePairs
    df.loc[0,'average_relTorque'] = (df['IdRMS'].iloc[0]*df['IqRMS'].iloc[0])*(df['averageLd'].iloc[0] -  df['averageLq'].iloc[0]) * 3 * polePairs
    df.loc[0,'average_total'] = df['average_magTorque'].iloc[0] + df['average_relTorque'].iloc[0]
    
    #calculate top Speed
    df['VDC'] = np.nan
    df['VphaseMax'] = np.nan
    df['maxRPM'] = np.nan
    df['backEMF'] = np.nan
    df['Xd'] = np.nan
    df['Xq'] = np.nan
    df['Vd'] = np.nan
    df['Vq'] = np.nan
    df['VphRMS'] = np.nan
    
    VphaseMax = VDC/np.sqrt(3)/np.sqrt(2)

    IdRMS =  df['IdRMS'].iloc[0]
    IqRMS = df['IqRMS'].iloc[0]
    

    motorSpecs={}
    motorSpecs['polePairs'] = polePairs
    motorSpecs['average_psiD_RMS'] = df['average_psiD_RMS'].iloc[0]
    motorSpecs['Ld'] = df['averageLd'].iloc[0]
    motorSpecs['Lq'] = df['averageLq'].iloc[0]
    
    solved = scipy.optimize.minimize(optimizeRPM,1000,(VphaseMax,motorSpecs),method='Nelder-Mead')
    if (solved.success == True):
        maxRPM = solved.x[0]
        out = calculateVphase(maxRPM,motorSpecs)
        df.loc[0,'VDC'] = VDC
        df.loc[0,'VphaseMax'] = VphaseMax
        df.loc[0,'maxRPM'] = maxRPM
        df.loc[0,'backEMF'] = out['backEMF']
        df.loc[0,'Xd'] = out['Xd']
        df.loc[0,'Xq'] = out['Xq']
        df.loc[0,'Vd'] = out['Vd']
        df.loc[0,'Vq'] = out['Vq']
        df.loc[0,'VphRMS'] =  out['VphRMS']
    else:
        print ("NotSolved for RPM = filename : {} ",file)
    
    saveFilename = saveFolder+os.path.basename(file)+'_processed.csv' 
    df.to_csv(saveFilename)

# print("results written to",saveFilename)


