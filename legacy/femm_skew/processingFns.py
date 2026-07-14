# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 06:33:22 2024

@author: Harsha
"""

import scipy
import ClarkPark as cp
from collections import OrderedDict
import numpy as np
    
import optimization as opt

def processSingle_OP_Results(df,settings):
    results = OrderedDict()
    
    results['IdRMS'] = float(df['IdRMS'].iloc[0])
    results['IqRMS'] = float(df['IqRMS'].iloc[0])
                
    results['OL_waTotal'] = df['wa'].sum()
    results['OL_wbTotal'] = df['wb'].sum()   
    results['OL_wcTotal'] = df['wc'].sum()
    results['OL_torque']  = df['torque'].sum()
    results['OL_blockTorque']  = df['blockTorque'].sum()
    
    results['OC_waTotal'] = df['wa_q'].sum()
    results['OC_wbTotal'] = df['wb_q'].sum()   
    results['OC_wcTotal'] = df['wc_q'].sum()
    
    #onLoad
    [psiD,psiQ],_ =  cp.getDQfromABC(results['OL_waTotal'],results['OL_wbTotal'],results['OL_wcTotal'], settings['rotorAngleElec'])
    results['psiD_RMS'] = psiD/np.sqrt(2)
    results['psiQ_RMS'] = psiQ/np.sqrt(2)
    
    #Q axis OC
    [psiD_q,psiQ_q],_ =  cp.getDQfromABC(results['OC_waTotal'],results['OC_wbTotal'],results['OC_wcTotal'],settings['rotorAngleElec'])
    results['psiD_q_RMS'] = psiD_q/np.sqrt(2)
    results['psiQ_q_RMS'] = psiQ_q/np.sqrt(2)
    
    if (results['IdRMS'] != 0):
    	Ld = (results['psiD_RMS'] - results['psiD_q_RMS'])/results['IdRMS']
    else:
        Ld = 0
    results['Ld'] =Ld
    if (results['IqRMS'] != 0) :
        results['Lq'] = results['psiQ_RMS']/results['IqRMS']
    else:
        results['Lq'] = 0
          
    results['magneticTorque'] = results['psiD_q_RMS'] * results['IqRMS'] * 3 * settings['polePairs']
    results['reluctanceTorque'] = results['IdRMS'] *results['IqRMS'] *( results['Ld'] - results['Lq']) * 3 * settings['polePairs']
    results['analyticalTorque_total'] = results['magneticTorque'] + results['reluctanceTorque']
    if results['analyticalTorque_total'] != 0:
        results['reluctanceTorqueratio'] =  np.round(results['reluctanceTorque']*100/results['analyticalTorque_total'],2)
    else:
        results['reluctanceTorqueratio'] = 0
    #calculate top Speed
    results['VLLRMS'] = settings["DC_Voltage"]/np.sqrt(2)          
    results['VphaseMax'] = settings["DC_Voltage"]/np.sqrt(3)/np.sqrt(2)
    motorSpecs={}
    motorSpecs['polePairs'] = settings["polePairs"]
    motorSpecs['average_psiD_RMS'] = results['psiD_q_RMS']
    motorSpecs['Ld'] = results['Ld']
    motorSpecs['Lq'] = results['Lq']
    motorSpecs['IdRMS'] = results['IdRMS']
    motorSpecs['IqRMS'] = results['IqRMS']
    
    solved = scipy.optimize.minimize(opt.optimizeRPM,1000,(results['VphaseMax'],motorSpecs),method='Nelder-Mead')
    if (solved.success == True):
        maxRPM = solved.x[0]
        results['maxRPM'] = maxRPM
    else:
        results['maxRPM'] = 'NA'
        
    return results