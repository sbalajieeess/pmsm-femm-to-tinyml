# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 10:43:26 2024

@author: Harsha
"""

from glob import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

imgWidth,imgHeight = (18,10) #in inches

#DEMAG CURVES
def getFileDicts(folder):
    normalCurves = {}
    intrinsicCurves={}
    files = glob(folder+"*.csv")
    for file in files:
        filename = os.path.basename(file)
        splits = filename[:-4].split("_")
        if "normalCurve" in filename:
            normalCurves[splits[1]] = file
        if "intrinsicCurve" in filename:
            intrinsicCurves[splits[1]] = file
    return normalCurves,intrinsicCurves

def generateDemagGraph(folder,which='all'):       
    normalCurves,intrinsicCurves = getFileDicts(folder)
    fig = plt.figure(figsize=(imgWidth,imgHeight))  
    colors = ["r","b","g","purple","orange","cyan","pink","m"]
    colorIdx = 0
    for key in normalCurves.keys():
        if which!='all':
            if (key not in which):
                continue
            
        file = normalCurves[key]
        df = pd.read_csv(file)
        kAm = np.array(df['x'])
        T = np.array(df[' y'])
        plt.plot(kAm,T,color = colors[colorIdx])
        colorIdx = colorIdx + 1
        
    colorIdx = 0
    for key in intrinsicCurves.keys():
        if which!='all':
            if (key not in which):
                continue
        file = intrinsicCurves[key]
        df = pd.read_csv(file)
        kAm = np.array(df['x'])
        T = np.array(df[' y'])
        plt.plot(kAm,T,'--',color = colors[colorIdx])
        maxX_idx = np.argmax(kAm)
        maxX = kAm[maxX_idx]
        maxY = np.mean(T)
        plt.text(maxX,maxY,key)
        colorIdx = colorIdx + 1
    
    plt.plot([],[],"-",color='k',label="normalCurves")
    plt.plot([],[],"--",color='k',label="intrinsicCurves")
    ax = plt.gca()
    ax.set_xlabel("DemagnetizingField H - kA/m")
    ax.invert_xaxis()
    ax.set_yticks([0,0.2,0.4,0.6,0.8,1.0,1.2,1.4],labels=['0','0.2','0.4','0.6','0.8','1.0','1.2','1.4'])
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.minorticks_on()
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    ax.set_ylabel("Flux Density B - T")
    # plt.tight_layout()
    return fig

def Tesla_to_kGauss(tesla):
    return tesla*10

def kGauss_to_Tesla(kGauss):
    return kGauss/10

def kAm_to_kOe(kA_m):
    return round(kA_m * 12.566/1000,3)

def kOe_to_kAm(kOe):
    return kOe *1000/12.566


folder=r"C:/Work/FEMM_Server/materials/N42UH_demagCurves/"

# #from arnold magnetics get the temperature coefficients for B and H
# Br_T_20C = 1.31
# Hcn_kAm_20C = 995 #normal curve
# Hci_kAm_20C = 1990 #intrinsic curve
# reversibleTempCoeff_Br = -0.12  #%/degreesC
# reversibleTempCoeff_Hc = -0.51  #%/degreesC

# Temp= 180
# Br_T = Br_T_20C * (1+(Temp-20)*reversibleTempCoeff_Br/100)
# Hci_kAm = Hci_kAm_20C * (1+(Temp-20)*reversibleTempCoeff_Hc/100)

# fig = generateDemagGraph(folder,'all')
# plt.plot([0,Hci_kAm],[Br_T,0],'--')

"""  
def markPts(magnetPts,plotOn=0):
    temp = magnetPts['T']
    T_string = str(temp) + 'C'    
    print ("----------------------------")
    print ("NoLoad @ temp={}C".format(temp))
    print ("--inputs---")
    pprint(magnetPts['noLoad'])
    
    outputs= {}
    outputs['noLoad']={}
    outputs['noLoad']['kGauss'] = Tesla_to_kGauss(magnetPts['noLoad']['B_T'])
    outputs['noLoad']['kOe'] = kAm_to_kOe(magnetPts['noLoad']['Hc_kAm'])
    outputs['noLoad']['Pc'] = round(abs(outputs['noLoad']['kGauss']/outputs['noLoad']['kOe']),3)
    outputs['noLoad']['Pci'] = outputs['noLoad']['Pc']  +  1

    print ("--outputs---")
    pprint(outputs['noLoad'])
    print ("----------------------------")
    
    print ("onLoad")
    pprint( magnetPts['onLoad'])
            
    
    if plotOn:
        fig = generateDemagGraph(folder,[T_string])
        y = magnetPts['noLoad']['B_T']
        x = magnetPts['noLoad']['Hc_kAm']
        plt.plot([x],[y],'kx')
        plt.text(x,y,T_string)
        #find a line till 1.4T, for the PC
        y2 = Tesla_to_kGauss(1.4)
        x2_in_kOe = y2/outputs['noLoad']['Pc']
        x2_in_kAm = kOe_to_kAm(x2_in_kOe)
        plt.plot([0,x2_in_kAm],[0,1.4],'r','-')
        plt.text(x2_in_kAm,1.4,'{}'.format(round(outputs['noLoad']['Pc'],2)))
        #draw the PCi also
        y2 = Tesla_to_kGauss(1.4)
        x2_in_kOe = y2/ outputs['noLoad']['Pci']
        x2_in_kAm = kOe_to_kAm(x2_in_kOe)
        plt.plot([0,x2_in_kAm],[0,1.4],'b','--')
        plt.text(x2_in_kAm-10,1.42,'{}'.format(round(outputs['noLoad']['Pci'],2)))

        
        #onLoad
        for label in magnetPts['onLoad']:
            rms = magnetPts['onLoad'][label]['RMS']
            Br = magnetPts['onLoad'][label]['Br']
            Hc = magnetPts['onLoad'][label]['Hc']
            plt.plot([Hc],[Br],'x')
        
        ratedRMS = magnetPts['onLoad']['ratedTorque']['RMS']   
        I = ratedRMS*1.414
        H_ext_Amps_m = magnetPts['turns']*I/magnetPts['poles']/magnetPts['ht_m'] * magnetPts['leakagePercent']
        H_ext_kAm = H_ext_Amps_m/1000
        #draw this line till B = 1.4
        plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
        plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'1PU')

        #5 PU
        PU_3 = I * 3
        H_ext_Amps_m = magnetPts['turns']*PU_3/magnetPts['poles']/magnetPts['ht_m'] * magnetPts['leakagePercent']
        H_ext_kAm = H_ext_Amps_m/1000
        
        plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
        plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'3PU')
        
        #5 PU
        PU_5 = I * 5
        H_ext_Amps_m = magnetPts['turns']*PU_5/magnetPts['poles']/magnetPts['ht_m'] * magnetPts['leakagePercent']
        H_ext_kAm = H_ext_Amps_m/1000
        
        plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
        plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'5PU')
        
        # # 8 PU
        # PU_8 = I * 8
        # H_ext_Amps_m = magnetPts['turns']*PU_8/magnetPts['poles']/magnetPts['ht_m'] * magnetPts['leakagePercent']
        # H_ext_kAm = H_ext_Amps_m/1000
        
        # plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
        # plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'8PU')
            
        plt.title('Demag Graph at {}, 1PU = {}ARMS'.format(T_string,ratedRMS))
        plt.show()

magnetPts={}
magnetPts['turns'] = 48
magnetPts['poles'] = 8
magnetPts['ht_m'] = 0.005
magnetPts['leakagePercent'] = 0.82 # 18% lost



magnetPts['T'] = 100
magnetPts['noLoad']={}
magnetPts['noLoad']['B_T'] =1.029
magnetPts['noLoad']['Hc_kAm'] = 117.373

magnetPts['onLoad']={}
magnetPts['onLoad']['pkSpeed']={}
magnetPts['onLoad']['pkSpeed']['RMS'] = 150
magnetPts['onLoad']['pkSpeed']['Br'] = 0.906
magnetPts['onLoad']['pkSpeed']['Hc'] = 210.513
magnetPts['onLoad']['pkPower']={}
magnetPts['onLoad']['pkPower']['RMS'] = 250
magnetPts['onLoad']['pkPower']['Br'] = 0.857
magnetPts['onLoad']['pkPower']['Hc'] = 247.920
magnetPts['onLoad']['pkTorque']={}
magnetPts['onLoad']['pkTorque']['RMS'] = 245
magnetPts['onLoad']['pkTorque']['Br'] = 0.868	
magnetPts['onLoad']['pkTorque']['Hc'] = 238.766
magnetPts['onLoad']['ratedTorque']={}
magnetPts['onLoad']['ratedTorque']['RMS'] = 115
magnetPts['onLoad']['ratedTorque']['Br'] = 0.955
magnetPts['onLoad']['ratedTorque']['Hc'] = 173.122


# magnetPts['T'] = 150
# magnetPts['noLoad']={}
# magnetPts['noLoad']['B_T'] = 0.961
# magnetPts['noLoad']['Hc_kAm'] = 109.07

# magnetPts['onLoad']={}
# magnetPts['onLoad']['pkSpeed']={}
# magnetPts['onLoad']['pkSpeed']['RMS'] = 136
# magnetPts['onLoad']['pkSpeed']['Br'] = 0.854
# magnetPts['onLoad']['pkSpeed']['Hc'] = 190.081
# magnetPts['onLoad']['pkPower']={}
# magnetPts['onLoad']['pkPower']['RMS'] = 255
# magnetPts['onLoad']['pkPower']['Br'] = 0.788
# magnetPts['onLoad']['pkPower']['Hc'] = 240.158
# magnetPts['onLoad']['pkTorque']={}
# magnetPts['onLoad']['pkTorque']['RMS'] = 255
# magnetPts['onLoad']['pkTorque']['Br'] = 0.798
# magnetPts['onLoad']['pkTorque']['Hc'] = 232.517
# magnetPts['onLoad']['ratedTorque']={}
# magnetPts['onLoad']['ratedTorque']['RMS'] = 115
# magnetPts['onLoad']['ratedTorque']['Br'] = 0.895
# magnetPts['onLoad']['ratedTorque']['Hc'] = 159.514


# magnetPts['T'] = 20
# magnetPts['noLoad']={}
# magnetPts['noLoad']['B_T'] = 1.134
# magnetPts['noLoad']['Hc_kAm'] = 133.028

# magnetPts['onLoad']={}
# magnetPts['onLoad']['pkSpeed']={}
# magnetPts['onLoad']['pkSpeed']['RMS'] = 180
# magnetPts['onLoad']['pkSpeed']['Br'] = 0.984
# magnetPts['onLoad']['pkSpeed']['Hc'] = 246.510
# magnetPts['onLoad']['pkPower']={}
# magnetPts['onLoad']['pkPower']['RMS'] = 235
# magnetPts['onLoad']['pkPower']['Br'] = 0.977
# magnetPts['onLoad']['pkPower']['Hc'] = 251.943
# magnetPts['onLoad']['pkTorque']={}
# magnetPts['onLoad']['pkTorque']['RMS'] = 235
# magnetPts['onLoad']['pkTorque']['Br'] = 0.981
# magnetPts['onLoad']['pkTorque']['Hc'] = 249.233
# magnetPts['onLoad']['ratedTorque']={}
# magnetPts['onLoad']['ratedTorque']['RMS'] = 115
# magnetPts['onLoad']['ratedTorque']['Br'] = 1.051
# magnetPts['onLoad']['ratedTorque']['Hc'] = 195.590


markPts(magnetPts,plotOn=1)

DO_150 = 0
if DO_150:
    fig = generateDemagGraph(folder,['150C'])
    #pts units are in kGauss and kOe
    
    #first get the noLoad values for 150C temperature.
    #getting from motorCad for now
    #motorcad gives min/max and average values. we use the min values for B and H inside the magnet
    #note that there are three slices so we have to look at all and pick these values.
    #150C
    noLoad_B_tesla_150C = 0.8892
    noLoad_H_Amps_m_150C = -1.761*1E5
    
    # to calculate PC we convert units to kGauss and kOe
    noLoad_B_kGauss = Tesla_to_kGauss(noLoad_B_tesla_150C)
    noLoad_H_kOe = kAm_to_kOe(noLoad_H_Amps_m_150C/1000)
    PC = abs(noLoad_B_kGauss/noLoad_H_kOe)
    PCi = PC + 1
    
    print ("---noLoad Calcs 150C---")
    print ("noLoad_B_tesla = {}".format(noLoad_B_tesla_150C))
    print ("noLoad_B_kGauss = {}".format(noLoad_B_kGauss))
    print ("noLoad_H_Amps_m = {}".format(noLoad_H_Amps_m_150C))
    print ("noLoad_H_kOe = {}".format(noLoad_H_kOe))
    print ("PC = {}".format(PC))
    print ("PCi = {}".format(PCi))
    
    y = 0.8892
    x = abs(-1.761*1E5/1000)
    plt.plot([x],[y],'kx')
    plt.text(x,y,'150C')
    #find a line till 1.4T, for the PC
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PC
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'r','-')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PC,2)))
    #draw the PCi also
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PCi
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'b','--')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PCi,2)))
    
    #current at 100RMS
    N = 48
    I = 100*1.414
    poles = 8
    magnetHt_m = 0.005
    leakagePercent = 0.75
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'100RMS')
    
    #FEM 100RMS d axis , at 150C
    B_tesla = 0.8245
    H_Amps_m = -2.403*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_100')
    
    
    I = 200*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'200RMS')
    
    #FEM 200RMS d axis , at 150C
    B_tesla = 0.701
    H_Amps_m = -3.669*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_200')
    
    
    I = 300*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'300RMS')
    
    #FEM 100RMS d axis , at 150C
    B_tesla = 0.6048
    H_Amps_m = -4.741*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_300')
    
    plt.legend()
    plt.grid()
    plt.title("N42UH Demagnetization Graph @ 150C w 5mm Magnet")
    plt.show()


DO_100 = 0
if DO_100:
    label='100C'
    color = 'b'
    fig = generateDemagGraph(folder,[label])
    #pts units are in kGauss and kOe
    
    #first get the noLoad values for 150C temperature.
    #getting from motorCad for now
    #motorcad gives min/max and average values. we use the min values for B and H inside the magnet
    #note that there are three slices so we have to look at all and pick these values.
    
    noLoad_B_tesla = 0.961
    noLoad_H_Amps_m = -1.9*1E5
    
    # to calculate PC we convert units to kGauss and kOe
    noLoad_B_kGauss = Tesla_to_kGauss(noLoad_B_tesla)
    noLoad_H_kOe = kAm_to_kOe(noLoad_H_Amps_m/1000)
    PC = abs(noLoad_B_kGauss/noLoad_H_kOe)
    PCi = PC + 1
    
    print ("---noLoad Calcs {}---".format(label))
    print ("noLoad_B_tesla = {}".format(noLoad_B_tesla))
    print ("noLoad_B_kGauss = {}".format(noLoad_B_kGauss))
    print ("noLoad_H_Amps_m = {}".format(noLoad_H_Amps_m))
    print ("noLoad_H_kOe = {}".format(noLoad_H_kOe))
    print ("PC = {}".format(PC))
    print ("PCi = {}".format(PCi))
    
    y = noLoad_B_tesla
    x = abs(noLoad_H_Amps_m/1000)
    plt.plot([x],[y],'kx')
    plt.text(x,y,label)
    #find a line till 1.4T, for the PC
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PC
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'r','-')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PC,2)))
    #draw the PCi also
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PCi
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'b','--')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PCi,2)))
    
    #current at 100RMS
    N = 48
    I = 100*1.414
    poles = 8
    magnetHt_m = 0.005
    leakagePercent = 0.75
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'100RMS')
    
    #FEM 100RMS d axis , 
    B_tesla = 0.8781
    H_Amps_m = -2.642*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_100')
    
    
    I = 200*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'200RMS')
    
    #FEM 200RMS d axis , 
    B_tesla = 0.7568
    H_Amps_m = -3.887*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_200')
    
    
    I = 300*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'300RMS')
    
    # FEM 300RMS d axis 
    B_tesla = 0.6601
    H_Amps_m = -4.931*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_300')
        
    plt.legend()
    plt.grid()
    plt.title("N42UH Demagnetization Graph - {} w 5mm magnet".format(label))
    plt.show()
    
DO_150_4mm_magnets = 0
if DO_150_4mm_magnets:
    label='150C'
    color = 'b'
    fig = generateDemagGraph(folder,[label])
    #pts units are in kGauss and kOe
    
    #first get the noLoad values for 150C temperature.
    #getting from motorCad for now
    #motorcad gives min/max and average values. we use the min values for B and H inside the magnet
    #note that there are three slices so we have to look at all and pick these values.
    
    noLoad_B_tesla = 0.9419
    noLoad_H_Amps_m = -1.903*1E5
    
    # to calculate PC we convert units to kGauss and kOe
    noLoad_B_kGauss = Tesla_to_kGauss(noLoad_B_tesla)
    noLoad_H_kOe = kAm_to_kOe(noLoad_H_Amps_m/1000)
    PC = abs(noLoad_B_kGauss/noLoad_H_kOe)
    PCi = PC + 1
    
    print ("---noLoad Calcs {}---".format(label))
    print ("noLoad_B_tesla = {}".format(noLoad_B_tesla))
    print ("noLoad_B_kGauss = {}".format(noLoad_B_kGauss))
    print ("noLoad_H_Amps_m = {}".format(noLoad_H_Amps_m))
    print ("noLoad_H_kOe = {}".format(noLoad_H_kOe))
    print ("PC = {}".format(PC))
    print ("PCi = {}".format(PCi))
    
    y = noLoad_B_tesla
    x = abs(noLoad_H_Amps_m/1000)
    plt.plot([x],[y],'kx')
    plt.text(x,y,label)
    #find a line till 1.4T, for the PC
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PC
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'r','-')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PC,2)))
    #draw the PCi also
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PCi
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'b','--')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PCi,2)))
    
    #current at 100RMS
    N = 48
    I = 100*1.414
    poles = 8
    magnetHt_m = 0.005
    leakagePercent = 0.75
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'100RMS')
    
    #FEM 100RMS d axis , 
    B_tesla = 0.8626
    H_Amps_m = -2.471*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_100')
    
    
    I = 200*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'200RMS')
    
    #FEM 200RMS d axis , 
    B_tesla = 0.7433
    H_Amps_m = -3.717*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_200')
    
    
    I = 300*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'300RMS')
    
    # FEM 300RMS d axis 
    B_tesla = 0.6144
    H_Amps_m = -4.923*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_300')
        
    plt.legend()
    plt.grid()
    plt.title("N42UH Demagnetization Graph - {} 4mm magnet".format(label) )
    plt.show()
    


DO_150_3mm_magnets = 0
if DO_150_3mm_magnets:
    label='150C'
    color = 'b'
    fig = generateDemagGraph(folder,[label])
    #pts units are in kGauss and kOe
    
    #first get the noLoad values for 150C temperature.
    #getting from motorCad for now
    #motorcad gives min/max and average values. we use the min values for B and H inside the magnet
    #note that there are three slices so we have to look at all and pick these values.
    
    noLoad_B_tesla = 0.9189
    noLoad_H_Amps_m = -2.035*1E5
    
    # to calculate PC we convert units to kGauss and kOe
    noLoad_B_kGauss = Tesla_to_kGauss(noLoad_B_tesla)
    noLoad_H_kOe = kAm_to_kOe(noLoad_H_Amps_m/1000)
    PC = abs(noLoad_B_kGauss/noLoad_H_kOe)
    PCi = PC + 1
    
    print ("---noLoad Calcs {}---".format(label))
    print ("noLoad_B_tesla = {}".format(noLoad_B_tesla))
    print ("noLoad_B_kGauss = {}".format(noLoad_B_kGauss))
    print ("noLoad_H_Amps_m = {}".format(noLoad_H_Amps_m))
    print ("noLoad_H_kOe = {}".format(noLoad_H_kOe))
    print ("PC = {}".format(PC))
    print ("PCi = {}".format(PCi))
    
    y = noLoad_B_tesla
    x = abs(noLoad_H_Amps_m/1000)
    plt.plot([x],[y],'kx')
    plt.text(x,y,label)
    #find a line till 1.4T, for the PC
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PC
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'r','-')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PC,2)))
    #draw the PCi also
    y2 = Tesla_to_kGauss(1.4)
    x2_in_kOe = y2/PCi
    x2_in_kAm = kOe_to_kAm(x2_in_kOe)
    plt.plot([0,x2_in_kAm],[0,1.4],'b','--')
    plt.text(x2_in_kAm,1.4,'{}'.format(round(PCi,2)))
    
    #current at 100RMS
    N = 48
    I = 100*1.414
    poles = 8
    magnetHt_m = 0.005
    leakagePercent = 0.9
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'100RMS')
    
    #FEM 100RMS d axis , 
    B_tesla = 0.8111
    H_Amps_m = -2.832*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_100')
    
    
    I = 200*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'200RMS')
    
    #FEM 200RMS d axis , 
    B_tesla = 0.6723
    H_Amps_m = -4.165*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_200')
    
    
    I = 300*1.414
    H_ext_Amps_m = N*I/poles/magnetHt_m * leakagePercent
    H_ext_kAm = H_ext_Amps_m/1000
    #draw this line till B = 1.4
    plt.plot([H_ext_kAm,H_ext_kAm+x2_in_kAm],[0,1.4],'r',linestyle=':')
    plt.text(H_ext_kAm+x2_in_kAm+50,1.4,'300RMS')
    
    # FEM 300RMS d axis 
    B_tesla = 0.5298
    H_Amps_m = -5.416*1E5
    H_kA_m = -H_Amps_m/1000
    plt.plot(H_kA_m,B_tesla,'rx')
    plt.text(H_kA_m,B_tesla,'FEM_300')
        
    plt.legend()
    plt.grid()
    plt.title("N42UH Demagnetization Graph - {} 3mm magnet".format(label) )
    plt.show()
    
    
"""