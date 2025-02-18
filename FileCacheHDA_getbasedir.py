import os
node = kwargs['node']
# from A:/Projects/3d/Maya_projects/Tiktok_mini/03_Workflow/Shots/shot2-a-2-8/Scenefiles/fx/Effects/geo/untitled.filecache2/v1/untitled.filecache2_v1.0001.bgeo.sc
# A:/Projects/3d/Houdini_essential/vellum_meat/03_Workflow/Shots/a-rnd/Scenefiles/fx/Effects/shot_a-rnd_fx_Effects_v0001__lch_.hip
# A:/Projects/3d/Houdini_essential/vellum_meat/
# A:/Projects/3d/Houdini_essential/vellum_meat/88_Cache/Shots/a-rnd/Scenefiles/fx/Effects
# A:/Projects/3d/Houdini_essential/vellum_meat/88_Cache/Shots/a-rnd/fx/Effects
# A:/Projects/3d/Houdini_essential/vellum_meat/88_Cache/Shots/a-rnd/S
job = hou.getenv('JOB')
cachedir = hou.getenv('CacheDir')
file = hou.hipFile.path()
filename = hou.hipFile.basename()

if cachedir == None:
    sceneroot = hou.node('/obj/')
    sceneroot.createNode('jupiter_setup', run_init_scripts=True)
    job = hou.getenv('JOB')
    cachedir = hou.getenv('CacheDir')

# make the path
t = file.lstrip(job).split('/')[0]
basedir = file.lstrip(job+'/').replace(t,cachedir).rstrip(filename)

if 'Scenefiles' in file.split('/'):
    basedir = basedir.replace('/Scenefiles', '')

# remove tail
if basedir.endswith('/'): 
    basedir = basedir.rstrip('/')

# text path exists
if not os.path.exists(basedir):
    os.makedirs(basedir)
    hou.ui.displayMessage(f"{basedir}\nJust been Created")

# set 3 directory parameter
node.parm('basedir').set(basedir)

parent = kwargs['node'].parent()
nodeself = kwargs['node'].name()
node.parm('basename').set('Cache'+f'_{parent}'+f'_{nodeself}')

total = node.evalParm('sopoutput')
framestring = node.evalParm('framestr')
framestring_orig = r"`ifs (ch('timedependent'), '.' + fpadzero(4, if(ch('substeps')>1, 3, 0), ch('frame')), '')`"
total = total.replace(framestring, framestring_orig)
node.parm('file').set(total)

# to A:/Projects/3d/Maya_projects/Tiktok_mini/08_Cache/Shots/shot2-a-2-8/fx/Effects/CACHENAME/v3/CHACHENAME_V3.0001.bgeo.sc
# to A:/Projects/3d/Maya_projects/Tiktok_mini/07_Cache/Shots/shot2-a-2-8/fx/Effects/Cache_geo1filecacheprism2/v1/Cache_geo1filecacheprism2_v1.0001.bgeo.sc