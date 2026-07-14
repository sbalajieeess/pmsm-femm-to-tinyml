# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:18:04 2024

@author: harsh
"""

import os
import femm

def MeshProcessing(femmFile,luaScript,OP):
    #create the name of the result file           
    [RMSCurrent,currentAngle,electricalAngle,worker]=OP
    rootFolder = os.path.dirname(femmFile)
    eAngle = str(electricalAngle).replace(".", "-")
    filename_unique = str(RMSCurrent)+"_"+str(currentAngle)+"_"+str(eAngle)
    #for lua every call with the filename needs the filename to have double backslashes  
    result_filename = rootFolder + "\\\\" +filename_unique   
    
    luaScriptName = os.path.basename(luaScript)[:-4]+filename_unique+".lua"
    modifiedLuaScriptPath = rootFolder+"\\\\"+luaScriptName
    
    
    #modify the lua script the way u need it
    lines = []
    with open(luaScript) as f:
        lines = f.readlines()
        #mpdify the two top lines
        lines[0] = "path_txt = \"{}\"\n".format(result_filename)
        lines[1] = "idworker = {} \n".format(worker)
    
    with open(modifiedLuaScriptPath, 'w') as a_writer:
        a_writer.writelines(lines)
    
    return modifiedLuaScriptPath

