import femm
import numpy as np
import pandas as pd

def simulateFemm_wSlidingAirGap(tempFile,IaPk,IbPk,IcPk,rotorAngle,FEA_input,slidingBand="slidingBand",usePrevSolution=0,smartMeshOn=0):
    
    
    femm.mi_setcurrent("U",IaPk)
    femm.mi_setcurrent("V",IbPk)
    femm.mi_setcurrent("W",IcPk)

    #now only move the sliding gap.
    #10 is inner boundary property

     #we reverse the angle of the angle used so that a positive angle gives us back emf in U,V,W order. from left to right.
    rotorAngle = -rotorAngle
    femm.mi_modifyboundprop(slidingBand,10,rotorAngle)
    
    if (usePrevSolution):
        sol = tempFile[:-4]+".ans"
        sol1 = (repr(sol).replace("x0",""))
        femm.mi_setprevious(sol1[1:-1])

    femm.mi_smartmesh(smartMeshOn) 
    femm.mi_createmesh()
    
    flag=2
    femm.mi_analyze(flag)
    
     #load solution
    femm.mi_loadsolution()
    
    wa = femm.mo_getcircuitproperties("U")[2] #get the flux values in each circuit
    wb = femm.mo_getcircuitproperties("V")[2]
    wc = femm.mo_getcircuitproperties("W")[2]

    #femm.mo_groupselectblock(5) # 5 is rotor
    #femm.mo_groupselectblock(4) # 4 is magnets #FOR OLD FEMM FILES COMMENT THIS, use only 5
    #blocktorque = femm.mo_blockintegral(22)
    #femm.mo_clearblock()
    blocktorque = 0

    torque2 = femm.mo_gapintegral("slidingBand",0)
    
    if FEA_input is not None:
        [FEM_offsetAngle,FEA_Data,symmetry] = FEA_input
        maxAngle = 360.0/symmetry
        angles = list(np.arange(FEM_offsetAngle,FEM_offsetAngle+maxAngle,0.5))
        angles_df = list(np.array(angles) - FEM_offsetAngle)
        df = pd.DataFrame(angles_df,columns=["angles"])
        
        B_data =  []
        Br_data=[]
        Bt_data = []
        Fr_data = []
        Ft_data = []
        mu_0 = 4 * np.pi * 1e-7
        for angle in angles:
            Br,Bt = femm.mo_getgapb("slidingBand",90-angle) # plot is clockwise in mesh, like how it is when u do it manually in femm.
            Fr = -Br * Br / (2 * mu_0) # maxwell stress force
            Ft = -Br * Bt / mu_0
            B = np.sqrt(Br*Br + Bt*Bt)
            B_data.append(B)
            Br_data.append(Br)
            Bt_data.append(Bt)
            Fr_data.append(Fr)
            Ft_data.append(Ft)
        df['airGap_B'] = B_data
        df['airGap_Br'] = Br_data
        df['airGap_Bt'] = Bt_data
        df['airGap_Fr'] = Fr_data
        df['airGap_Ft'] = Ft_data
              
        if FEA_Data is not None:
            B_linePts,magnetPts = FEA_Data
            for key in B_linePts.keys():
                radius  = B_linePts[key]
                B_data=[]
                Bx_data = []
                By_data = []
                for angle in angles:
                    pt = (radius * np.cos(np.deg2rad(90-angle)),radius * np.sin(np.deg2rad(90-angle)))
                    out = femm.mo_getpointvalues(pt[0],pt[1])
                    _,Bx,By,_,_,_,_,_,_,_,_,_,_,_ = out
                    B = np.sqrt(Bx*Bx + By*By)
                    B_data.append(B)
                    Bx_data.append(Bx)
                    By_data.append(By)
                df["{}_B".format(key)]=B_data
                df["{}_Bx".format(key)]=Bx_data
                df["{}_By".format(key)]=By_data
                
            idx =1
            for magnetCentre in magnetPts:
                out = femm.mo_getpointvalues(magnetCentre[0],magnetCentre[1])
                _,Bx,By,_,_,Hx,Hy,_,_,_,_,_,_,_ = out
                B = np.sqrt(Bx*Bx + By*By)
                H = np.sqrt(Hx*Hx + Hy*Hy)
                
                df["magnet{}_B".format(idx)] = ''
                df.loc[0,"magnet{}_B".format(idx)]= B
                df["magnet{}_H".format(idx)] = ''
                df.loc[0,"magnet{}_H".format(idx)] = H
                idx = idx + 1
    else:
        df = pd.DataFrame() # empty dataframe
        
    return [wa,wb,wc],torque2,blocktorque,df
