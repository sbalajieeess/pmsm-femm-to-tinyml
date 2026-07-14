# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 19:07:57 2024

@author: harsh
"""

import os
import numpy as np
import pyvista as pv
from glob import glob

folder = "C:/Work/FEMM_Server/iitLTTS/0-7m-airGap/fromMotorMojo/meshData/150_0"

#first draw the mesh
elementsfile = "C:/Work/FEMM_Server/iitLTTS/0-7m-airGap/fromMotorMojo/meshData/150_0/150_0_0-0elements0.txt"
nodeFile = "C:/Work/FEMM_Server/iitLTTS/0-7m-airGap/fromMotorMojo/meshData/150_0/150_0_0-0nodes0.txt"

resultsFile = "C:/Work/FEMM_Server/iitLTTS/0-7m-airGap/fromMotorMojo/meshData/150_0/150_0_0-0results0.txt"

#all Results Files
allresultFiles = glob(folder+"/*results*")
resultsDict={} #unsorted
for result in allresultFiles:
    filename = os.path.basename(result)
    # print(filename)
    splits = filename.split("_")
    # print(splits)
    splits1 = splits[2].split("r")
    rotorAngle = splits1[0].replace("-",".")
    resultsDict[rotorAngle] = result
    
keysList=[]
for keys in resultsDict.keys():
    keysList.append(float(keys))
sorted_keysList = sorted(keysList)
    

# Read the nodes and elements files
results_nodes = np.loadtxt(nodeFile, delimiter=" ")
listElem0 = np.loadtxt(elementsfile, dtype="f", delimiter=" ").astype(
    np.float64
)
NbNd = len(results_nodes)
NbElem = len(listElem0)

# Node list - now node list index starts from 0 not 1
listNd = np.zeros(shape=(NbNd, 3))
listNd[:, 0] = results_nodes[:, 0]
listNd[:, 1] = results_nodes[:, 1]

# # 1 .generates point cloud 
# mesh = pv.PolyData(listNd)
# mesh.plot(point_size=10)

#2. creates different groups mesh faces
#pv.global_theme.color_cycler = 'default' # add this for random color cycling
# groups = np.unique(listElem0[:,6])
# plotter = pv.Plotter()
# for group in groups:
    
#     mask = listElem0[:,6].astype('int') == group
#     listElem_group = listElem0[mask]
#     # Element list - first three cols are node nos, and then we get cx,cy,area and group no
#     #we first create only face list, but with indexes starting from 0
#     listElem = listElem_group[:, 0:3] - 1
    
#     #for poly data, the first column must be no of nodes that create a face, and since we re using 
#     #triangles that will be a col where all rows are 3
#     faces = np.insert(listElem,0,3,axis =1)
#     faces = faces.astype('int')
    
#     #create mesh with nodes and faces
#     mesh = pv.PolyData(listNd,faces)
#     # mesh.plot(point_size=10,show_edges=True)
    
#     random_color = (np.random.random(),np.random.random(),np.random.random())
#     plotter.add_mesh(mesh,color=random_color,show_edges = True)
    
# plotter.show()


#3. show scalar labels, ie  B field - streamlines didnt work, pickingpoints didnt work
#now add data to the cells. We first add data as cell data, ie: the data is for the whole cell
# we can also add a data for every node point, but femm doesnt give us that output. we have 
# one data point per cell. When we apply smoothing we need to apply within a group.

# data is in the results file
# results_values = np.loadtxt(resultsFile, delimiter=" ")
    
# groups = np.unique(listElem0[:,6]).astype('int')
# plotter = pv.Plotter()
# mesh = None
# # groups=[5,2]
# for group in groups:
#     mask = listElem0[:,6].astype('int') == group
#     listElem_group = listElem0[mask]
    
    # listElem = listElem_group[:, 0:3] - 1
#     faces = np.insert(listElem,0,3,axis =1)
#     faces = faces.astype('int')
    
#     #create mesh with nodes and faces
#     mesh = pv.PolyData(listNd,faces)

#     #now add data to the mesh
#     Bx = results_values[:,0][mask]
#     By = results_values[:,1][mask]
#     mesh.cell_data['Bx'] =  Bx
#     mesh.cell_data['By'] =  By
#     mesh.cell_data['B'] =  np.sqrt(np.power(Bx,2) +  np.power(By,2))
    
#     #boundary of each mesh
#     edges = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False)

    
#     #here we  and make cell data point data
#     mesh = mesh.cell_data_to_point_data()
   
#     # after getting point data we add the stream ines
#     # vectors = np.empty_like(mesh.points)
#     # vectors[:,0] = mesh.point_data['Bx']
#     # vectors[:,1] =  mesh.point_data['By']
#     # mesh.point_data['vectors'] = vectors
    
#     # stream = mesh.streamlines(
#     #     'vectors')

#     plotter.add_mesh(mesh,scalars='B',clim =[0,1.8],show_edges=True)
#     plotter.add_mesh(edges, color="red", line_width=2)
    
#     # mesh.set_active_vectors("vectors")
#     # plotter.add_mesh(mesh.arrows, lighting=True)
#     # plotter.add_mesh(stream.tube(radius=0.1))
    

plotter = None
def addResultFileToPlotter(resultsFile,nodeList,elemList,group=0,withMesh=0,smoothing=0):
    results_values = np.loadtxt(resultsFile, delimiter=" ")
    if group:
        groups = np.unique(elemList[:,6]).astype('int')
        for group in groups:
            mask = elemList[:,6].astype('int') == group
            listElem_group = elemList[mask]
            
            listElem = listElem_group[:, 0:3] - 1
            faces = np.insert(listElem,0,3,axis =1)
            faces = faces.astype('int')
            
            #create mesh with nodes and faces
            mesh = pv.PolyData(nodeList,faces)

            #now add data to the mesh
            Bx = results_values[:,0][mask]
            By = results_values[:,1][mask]
            mesh.cell_data['Bx'] =  Bx
            mesh.cell_data['By'] =  By
            mesh.cell_data['B'] =  np.sqrt(np.power(Bx,2) +  np.power(By,2))
            
            #boundary of each mesh
            edges = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False)

            if smoothing:
                #here we  and make cell data point data
                mesh = mesh.cell_data_to_point_data()
           
            plotter.add_mesh(mesh,scalars='B',clim =[0,1.8],show_edges=withMesh,lighting=False)
            plotter.add_mesh(edges, color="red", line_width=2)
    else:
        listElem = elemList[:, 0:3] - 1
        faces = np.insert(listElem,0,3,axis =1)
        faces = faces.astype('int')
        
        #create mesh with nodes and faces
        mesh = pv.PolyData(nodeList,faces)

        #now add data to the mesh
        Bx = results_values[:,0]
        By = results_values[:,1]
        mesh.cell_data['Bx'] =  Bx
        mesh.cell_data['By'] =  By
        mesh.cell_data['B'] =  np.sqrt(np.power(Bx,2) +  np.power(By,2))
        
    
       
        #boundary of each mesh
        edges = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False)

        if smoothing:
            #here we  and make cell data point data
            mesh = mesh.cell_data_to_point_data()
            Bx = mesh.point_data['Bx']
            By = mesh.point_data['By']
            mesh.point_data['vectors']=np.array((Bx,By,np.zeros_like(Bx))).T
            mesh.set_active_vectors('vectors')
            
       
        plotter.add_mesh(mesh,scalars='B',clim =[0,1.8],show_edges=withMesh,lighting=False)
        plotter.add_mesh(edges, color="red", line_width=2)
        
        plotter.add_arrows(mesh.points,mesh.point_data['vectors'],color='r',mag=0.5 ) #adding arrows when rotor poition doesnt move confuses ppl
    
        
        
        
        
        
        

#plotting gifs

# gifFile = folder +"/animation.gif"

# #now first prepare the mesh 
# contour_firstTime = 1

# plotter = pv.Plotter()
# plotter.open_gif(gifFile) # u have to save a gif file when u do the 
# resultFile0= resultsDict[str(sorted_keysList[0])]

# addResultFileToPlotter(resultFile0,listNd,listElem0,group=0,withMesh=0,smoothing=0)
# plotter.show(auto_close=False)

# for key in sorted_keysList:
#     resultsFile = resultsDict[str(key)]
#     addResultFileToPlotter(resultsFile,listNd,listElem0,group=0,withMesh=0,smoothing=0)
#     # new_contours = mesh.contour()
#     # if contour_firstTime:
#     #     contours = new_contours
#     #     plotter.add_mesh(contours, color="white", line_width=1)
#     #     contour_firstTime = 0
#     # else:
#     #     contours.copy_from(new_contours)
        
#     plotter.write_frame()  # Write this frame
# # Run through each frame

# plotter.close()



# import pyvista as pv
# import numpy as np
# x, y = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
# points = np.vstack((x.ravel(), y.ravel(), np.zeros(x.size))).T
# u = x / np.sqrt(x**2 + y**2)
# v = y / np.sqrt(x**2 + y**2)
# vectors = np.vstack(
#     (u.ravel() ** 3, v.ravel() ** 3, np.zeros(u.size))
# ).T
# pdata = pv.vector_poly_data(points, vectors)
# pdata.point_data.keys()
# pdata.glyph(orient='vectors', scale='mag').plot()


    
# #now first prepare the mesh 
# contour_firstTime = 1

plotter = pv.Plotter()

resultFile0= resultsDict[str(sorted_keysList[0])]

addResultFileToPlotter(resultFile0,listNd,listElem0,group=0,withMesh=1,smoothing=1)
plotter.show()
