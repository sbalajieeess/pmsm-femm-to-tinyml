# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 06:25:28 2024

@author: Harsha
"""
import numpy as np


#in phase space
def calculateVphase(RPM,motorSpecs):
    out = {}
    pp = motorSpecs['polePairs']
    psiD = motorSpecs['average_psiD_RMS'] 
    avgLd = motorSpecs['Ld']
    avgLq = motorSpecs['Lq']
    IdRMS = motorSpecs['IdRMS']
    IqRMS = motorSpecs['IqRMS']
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

