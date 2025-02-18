import hrpyc
con, hou = hrpyc.import_remote_module()
if False:
    import hou

# for i in range(-1,2):
#     for j in range(-1,2):
#         for k in range(-1,2):
#             myPlace = hou.node('/obj')
#             mygeo = myPlace.createNode('geo', run_init_scripts=False)
#             mybox = mygeo.createNode('box')
#             mybox.parmTuple('t').set((i,j,k))
# hou.node('obj').layoutChildren()
node = hou.node('/obj/jupiter_import_speedtree1')
mesh = "Broadleaf_var1.fbx"
node.parm("sop_path").set(mesh)
