# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 11:04:08 2024

@author: Harsha
"""

STATOR_SLOTS = 48
STACK_LENGTH = 120
NO_OF_SLICES = 5

SLOT_PITCH = 360/STATOR_SLOTS
SKEW_ANGLE = SLOT_PITCH

print("STATOR_SLOTS = {}".format(STATOR_SLOTS))
print("NO_OF_SLICES = {}".format(NO_OF_SLICES))
print("SLOT_PITCH = {}".format(SLOT_PITCH))
print("SKEW_ANGLE = {}".format(SKEW_ANGLE))

#find angles centred around zero.
sliceAngles = []
if (NO_OF_SLICES%2==0):
    angle_per_slice = SKEW_ANGLE/NO_OF_SLICES
    print("angle_per_slice = {}".format(angle_per_slice))
    for i in range(NO_OF_SLICES):
        sliceAngles.insert(i,0)
    innerSliceAngles = angle_per_slice/2
    sliceAngles[int(NO_OF_SLICES/2)-1] = innerSliceAngles
    sliceAngles[int(NO_OF_SLICES/2)] = -innerSliceAngles
    insertedIndices = [int(NO_OF_SLICES/2)-1,int(NO_OF_SLICES/2)]
    
    for i in range(NO_OF_SLICES):
        if i not in insertedIndices:
            if i < int(NO_OF_SLICES/2)-1:
                i_actual = int(NO_OF_SLICES/2)-1 - i
                sliceAngles[i] = innerSliceAngles + i_actual*angle_per_slice
            else :
                i_actual = i - int(NO_OF_SLICES/2)
                sliceAngles[i] = -(innerSliceAngles + i_actual*angle_per_slice)
    # print(sliceAngles)
    # outerAngle = innerSliceAngles + angle_per_slice
    # print (outerAngle,innerSliceAngles,-innerSliceAngles,-outerAngle)
else:
    angle_per_slice = round(SKEW_ANGLE/(NO_OF_SLICES),3)
    print("angle_per_slice = {}".format(angle_per_slice))
    centreAngle = 0
    halfSliceVal = int(NO_OF_SLICES/2)
    for i in range(halfSliceVal,-halfSliceVal-1,-1):
        if i != 0:
            sliceAngles.append(i * angle_per_slice)
        else:
            sliceAngles.append(0)
            
print ("SliceAngles in Mech degrees = {}".format(sliceAngles))
    # print(sliceAngles)
    # outerAngle = centreAngle + angle_per_slice
    # print (outerAngle,centreAngle,-outerAngle)