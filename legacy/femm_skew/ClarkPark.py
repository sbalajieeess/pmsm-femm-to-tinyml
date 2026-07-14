# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 16:39:17 2024

@author: harsh
"""

import numpy as np


def inv_park(i_d,i_q,rot_angle):
    #returns i alpha and i beta from d,q
    rot_angle_rad = np.deg2rad(rot_angle)
    ialpha = i_d*np.cos(rot_angle_rad) - i_q*np.sin(rot_angle_rad)
    ibeta = i_q*np.cos(rot_angle_rad) + i_d*np.sin(rot_angle_rad)
    return ialpha,ibeta

def inv_clarke(ialpha,ibeta):
    #return ia,ib,ic from ialpha,ibeta
    ia = ialpha 
    ib = (-ialpha + ((3**0.5)*ibeta))/2
    ic = (-ialpha - ((3**0.5)*ibeta))/2
    return ia,ib,ic

def clarke(wa,wb,wc):
    #returns abc to alpha beta
    walpha = wa
    wbeta = (wa/np.sqrt(3)) + ((2/np.sqrt(3))*wb)
    return walpha,wbeta

def park(walpha,wbeta,rot_angle):
    #alpha Beta to dq axis
    rot_angle = np.deg2rad(rot_angle)
    wd = walpha*np.cos(rot_angle) + wbeta*np.sin(rot_angle)
    wq = wbeta*np.cos(rot_angle) - walpha*np.sin(rot_angle)
    return wd,wq

def getABCfromDQ(D,Q,rotorAngle,verbose = 0):
    alpha,beta = inv_park(D,Q,rotorAngle)
    A,B,C = inv_clarke(alpha,beta)
    check = 1 if (np.isclose(A+B+C, 0, rtol=1e-05, atol=1e-08, equal_nan=False)) else 0
    if verbose:
        print ("---getABCfromDQ---")
        print ("D,Q =  {},{}".format(D,Q))
        print ("IAlpha,IBeta =  {},{}".format(alpha,beta))
        print ("A,B,C =  {},{},{}".format(A,B,C))
        print ("check = {}".format(check))
    if check == 1:
        return [A,B,C],[alpha,beta]
    else:
        raise exception("Error in DQcalculation!")

def getDQfromABC(A,B,C,rotorAngle,verbose = 0):
    alpha,beta = clarke(A,B,C)
    D,Q = park(alpha,beta,rotorAngle)
    check = 1 if (np.all(np.isclose(A+B+C, 0, rtol=1e-05, atol=1e-08, equal_nan=False))) else 0
    if verbose:
        print ("---getDQfromABC---")
        print ("A,B,C =  {},{},{}".format(A,B,C))
        print ("IAlpha,IBeta =  {},{}".format(alpha,beta))
        print ("D,Q =  {},{}".format(D,Q))
        print ("check = {}".format(check))
    return [D,Q],[alpha,beta]

def convertElAngleToMechAngle(elAngle,polePairs):
    mechAnglesToOneElectricalRotation = 360.0/polePairs
    elAngleToMechAngle = mechAnglesToOneElectricalRotation/360.0
    mechAngle = elAngle*elAngleToMechAngle
    return mechAngle


def convertMechAngleToElAngle(mechAngle,polePairs):
    mechAnglesToOneElectricalRotation = 360.0/polePairs
    mechAngleMod = mechAngle%mechAnglesToOneElectricalRotation
    electricalAngle = mechAngleMod*360.0/mechAnglesToOneElectricalRotation
    return electricalAngle