import os
import hou
node = kwargs['node']

if hou.getenv('CacheDir') == None or hou.getenv("PRISM_STEP") == None:
    sceneroot = hou.node('/obj/')
    sceneroot.createNode('jupiter_set_job', run_init_scripts=True)

job = hou.getenv('JOB')
cachedir = hou.getenv('CacheDir')
prismstep = hou.getenv("PRISM_STEP")
prismcat = hou.getenv("PRISM_CATEGORY")
prismseq = hou.getenv("PRISM_SEQUENCE")
prismshot = hou.getenv("PRISM_SHOT")

# make the path
try:
    basedir = cachedir +'/Shots/'+ prismseq +'-'+ prismshot +'/'+ prismstep +'/'+ prismcat
    # test path exists
    if not os.path.exists(basedir):
        os.makedirs(basedir)
        hou.ui.displayMessage(f"{basedir}\nJust been Created")
    # set 3 directory parameter
    node.parm('basedir').set(basedir)
except TypeError:
    hou.ui.displayMessage(f"Please Put This File in Prism Workflow")
    basedir = cachedir + '/Shots'
    node.parm('basedir').set(r'$CacheDir/Shots')

parent = kwargs['node'].parent()
nodeself = kwargs['node'].name()
node.parm('basename').set('Cache'+f'_{parent}'+f'_{nodeself}')