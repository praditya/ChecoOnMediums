import requests as re
import numpy as np

import sys
sys.path.append('C:\\Users\\arajawa1\\Anaconda3\\envs\\pyblend\\lib\\site-packages')

import pandas as pd
#####################

# Session API
response = re.get("https://apigw.withoracle.cloud/formulaai/sessions")
sessionDf = pd.json_normalize(response.json())
trackId = input('Enter track name:- ')
#trackId = 'Melbourne' # User input for final application

# Separating out the df based on track id
selectedSessionDf = sessionDf[sessionDf['TRACKID'] == trackId]
selectedSessionDf = selectedSessionDf.reset_index(drop=True)
print(selectedSessionDf.to_string())
# Appending the data for each session id and lap

# apending directly in data frame ~ 40 seconds
# select particular session ID or select all
print("Enter the Session ID index separated by space, to be used for track generation, Enter -1 to select all")
inp = list(map(int, input().split()))

if (inp == [-1]):
    print("Selecting all session ID's for point cloud generation")
else:
    selectedSessionDf = selectedSessionDf.iloc[inp,:]
    print("Using selected session ID's for point cloud generation")

# import data from session ID
data = pd.DataFrame()
for index, row in selectedSessionDf.iterrows():
    laps = row.loc['LAPS']
    sessionId = row.loc['M_SESSIONID'] 
    # data should be upto lap number.. but we have data upto lap+1
    for i in range(laps):
        url = "https://apigw.withoracle.cloud/formulaai/trackData/" + sessionId + "/" + str(i+1)
        temp = pd.json_normalize(re.get(url).json())
        print("Session id- " + sessionId + " and Lap number- " + str(i+1)+ " data shape is- " + str(temp.shape)) 
        data = pd.concat([data,temp])
        

# fetch 3D world points
wx = data['WORLDPOSX'].tolist()
wy = data['WORLDPOSY'].tolist()
wz = data['WORLDPOSZ'].tolist()

wrx = data['WORLDRIGHTDIRX'].tolist()
wry = data['WORLDRIGHTDIRY'].tolist()
wrz = data['WORLDRIGHTDIRZ'].tolist()

wfx = data['WORLDFORWARDDIRX'].tolist()
wfy = data['WORLDFORWARDDIRY'].tolist()
wfz = data['WORLDFORWARDDIRZ'].tolist()

#l = np.size(wx)
#normalvecs = []
#for i in range(l):
#    a = np.cross([wrx[i], wry[i], wrz[i]],[wfx[i], wfy[i], wfz[i]])
#    normalvecs.append(a)
    

####################

# Generate 3d Point Cloud
import open3d as o3d
xyz = np.zeros((np.size(wx), 3))
xyz[:, 0] = np.reshape(wx, -1)
xyz[:, 1] = np.reshape(wy, -1)
xyz[:, 2] = np.reshape(wz, -1)
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(xyz)
#pcd.normals = o3d.utility.Vector3dVector(normalvecs)
o3d.io.write_point_cloud(trackId + ".ply", pcd)
print("Generated 3D Point Cloud for the Track sessions")

#####################

# Create 3D Mesh
#from PIL import Image
#dataname=trackId + ".ply"
#pcd = o3d.io.read_point_cloud(dataname)
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
distances = pcd.compute_nearest_neighbor_distance()
avg_dist = np.mean(distances)
radius = avg_dist * 4

mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd,o3d.utility.DoubleVector([radius, radius * 2]))
o3d.io.write_triangle_mesh(trackId + "_mesh.ply", mesh)
print("Generated 3D Mesh File for the Track")

#####################

import bpy
import bmesh
import math
import os
from pathlib import Path
from mathutils import Vector
import json

# clean preloaded environment
# print all objects
#C = bpy.context
#scene = C.scene
#bpy.ops.object.select_all(action='DESELECT')
#for ob in bpy.data.objects:
#    if ob.name in ['Cube','Cube.001']:
#        ob.select = True
#        scene.objects.active = ob
#bpy.ops.object.delete(use_global=False)

#for obj in bpy.data.objects:
#    print(obj.name)


# Import track mesh object
from io_mesh_ply import import_ply
#importing main mesh
trackMeshFile = trackId + "_mesh.ply"
trackMeshObj = trackId + "_mesh"
import_ply.load_ply(trackMeshFile)

mat = bpy.data.materials.new("Road")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load("//data\\road.jpg")
mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# Assign it to object
plane = bpy.data.objects[trackMeshObj]
plane.data.materials.append(mat)
# create curve object from path for curbs
bpy.ops.object.convert(target='CURVE', keep_original=True)

################################################# CURB ###############################################

def new_plane(mylocation, mysize, myname):
    bpy.ops.mesh.primitive_plane_add(
        size=mysize,
        calc_uvs=True,
        enter_editmode=False,
        align='WORLD',
        location=mylocation,
        rotation=(0, 0, 0),
        scale=(2, 1, 1))
    current_name = bpy.context.selected_objects[0].name
    plane = bpy.data.objects[current_name]
    plane.name = myname
    plane.data.name = myname + "_mesh"
    return

new_plane((0,0,0), 1, "Curb1")
# Cache the current object being worked on.
current = bpy.context.object
old_type = bpy.context.area.type
bpy.context.area.type = 'VIEW_3D'
bpy.context.view_layer.objects.active = current
current.select_set(True)
bpy.ops.object.editmode_toggle()
def view3d_find( return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None

region, rv3d, v3d, area = view3d_find(True)

override = {
    'scene'  : bpy.context.scene,
    'region' : region,
    'area'   : area,
    'space'  : v3d
}
bpy.ops.mesh.loopcut_slide(
    override,
    MESH_OT_loopcut = {
        "number_cuts"           : 1,
        "smoothness"            : 0,     
        "falloff"               : 'INVERSE_SQUARE',  # Was 'INVERSE_SQUARE' that does not exist
        "edge_index"            : 1,
        "mesh_select_mode_init" : (True, False, False),
        "object_index" : 0
    },
    TRANSFORM_OT_edge_slide = {
        "value"           : 0,
        "mirror"          : False, 
        "snap"            : False,
        "snap_target"     : 'CLOSEST',
        "snap_point"      : (0, 0, 0),
        "snap_align"      : False,
        "snap_normal"     : (0, 0, 0),
        "correct_uv"      : False,
        "release_confirm" : False,
        "use_accurate"    : False
    }
)

bpy.ops.object.editmode_toggle()
bpy.context.area.type = old_type 

me = current.data
bpy.ops.object.editmode_toggle()
# Get a BMesh representation
bm = bmesh.from_edit_mesh(me)

bm.faces.ensure_lookup_table()

for i in range(len(bm.faces)):
    
    bpy.data.materials.new("Mat_%i" % i)
    material = bpy.data.materials["Mat_%i" % i]
    material.use_nodes = True
    material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.2
    plane = bpy.data.objects['Curb1']
    plane.data.materials.append(material)
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1,1,1,1)
    if (i==1):
        material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1,0,0,1)

bm.faces[1].select=True
bpy.context.object.active_material_index = 1
bpy.ops.object.material_slot_assign()


# align curb along the track

bpy.ops.object.modifier_add(type='ARRAY')
bpy.context.object.modifiers["Array"].fit_type = 'FIT_CURVE'
trackCurve = trackMeshObj + ".001"
bpy.context.object.modifiers["Array"].curve = bpy.data.objects[trackCurve]
bpy.ops.object.modifier_add(type='CURVE')
bpy.context.object.modifiers["Curve"].object = bpy.data.objects[trackCurve]
bpy.ops.object.editmode_toggle()


    
############### GROUND PLANE ###################################

bpy.context.active_object.select_set(False)
new_plane((0,0,0), 10000, "Ground")
# Cache the current object being worked on.
current = bpy.context.object
bpy.ops.object.editmode_toggle()

bpy.ops.mesh.subdivide(number_cuts = 10000)

##bpy.context.space_data.context = 'MODIFIER'
#bpy.ops.object.modifier_add(type='SHRINKWRAP')
#bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[trackMeshObj]
#bpy.context.object.modifiers["Shrinkwrap"].offset = 100
bpy.ops.object.editmode_toggle()

#bpy.data.materials.new("Surface")
#material = bpy.data.materials["Surface"]
#material.use_nodes = True
#material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.2
#plane = bpy.data.objects['Ground']
#plane.data.materials.append(material)
#material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,1,0,1)
mat = bpy.data.materials.new("Grass")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load("//data\\grass.jpg")
mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# Assign it to object
plane = bpy.data.objects["Ground"]
plane.data.materials.append(mat)
###########################################################################################