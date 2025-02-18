import os
import hou
import PySide2


def onCreated(node):
    # Set default node name, action (for pop up window) color, and shape
    node_name = 'Jupiter_setup'
    action = 'Install'
    installed_node_color = hou.Color((0.054, 0.325, 0.603))
    updated_node_color = hou.Color((0.152, 0.945, 0.674))

    # Get Some Basic Infomation
    hdapath = node.type().definition().libraryFilePath()
    filepath = hou.hipFile.path()
    filename = hou.hipFile.basename()
    prev_job = hou.getenv("JOB")

    ################################## SET $JOB DIR ######################################
    try:
        p = filepath.split('/')
        workflow = list(filter(lambda a: 'Workflow' in a, p))[0]
        job = filepath.split('/'+workflow)[0]
        # get 'A:\Projects\3d\Maya_projects\Tiktok_mini' in 
        # A:\Projects\3d\Maya_projects\Tiktok_mini\03_Workflow\Shots\shot2-a-2-2\Scenefiles\fx\Effects\shot_shot2-a-2-2_fx_Effects_v0010__lch_.hip
    except Exception:
        job = hou.ui.selectFile(title="SelectJobFolder", file_type=hou.fileType.Directory).rstrip("/")

    try:
        hou.allowEnvironmentToOverwriteVariable("JOB", True)
        hou.unsetenv("JOB")
        hou.putenv("JOB", job)
        if job == hou.getenv('JOB'):
            hou.ui.displayMessage("$JOB successfully set to\n{}".format(job))
    except Exception as e:
        print (str(e))
    ################################## SET $JOB END ######################################

    update_cachedir(node)
    update_parm(node)
    
    node.setDisplayFlag(False)
    node.setGenericFlag(hou.nodeFlag.Selectable, False)
    node.setColor(installed_node_color)
    node.setUserData('nodeshape', 'star')

    try:
        node.setName(node_name)
    except Exception:
        hou.ui.displayMessage("Jupiter_setup Node exist\nOlder One was removed")
        older_node = hou.node('/obj/'+node_name)
        # older_node.setName(node_name+'_installed')
        older_node.destroy()
        node.setName(node_name)

def onLoaded(node):
    onCreated(node)

def update_parm(node, *arg):
    # Set Parameter On ParameterInterfaceEditor
    node.parm('scenefile_path').set(hou.hipFile.path())
    node.parm('job_path').set(hou.getenv('JOB'))
    node.parm('cache_path').set(hou.getenv('CacheDir'))
    node.parm('houdini_path').set(hou.getenv('HOUDINI_PATH'))
    if arg:
        hou.ui.displayMessage("Parameter Updated")


def print_env():
    # Get the message template from the Extra Files section
    message = hou.pwd().type().definition().sections()['SUCCESS_MESSAGE'].contents()
    message = message.replace('@___HOUDINI_USER_PREF_DIR___@', hou.getenv('HOUDINI_USER_PREF_DIR'))
    message = message.replace('@___HFS___@', hou.getenv('HFS'))
    message = message.replace('@___JOB___@', hou.getenv('JOB'))
    message = message.replace('@___CacheDir___@', hou.getenv('CacheDir'))
    PySide2.QtWidgets.QMessageBox.information(hou.qt.mainWindow(), 'Successful', message)

def reset_job(node):
    job = hou.ui.selectFile(title="SelectJobFolder", file_type=hou.fileType.Directory).rstrip("/")
    try:
        hou.allowEnvironmentToOverwriteVariable("JOB", True)
        hou.unsetenv("JOB")
        hou.putenv("JOB", job)
        if job == hou.getenv('JOB'):
            hou.ui.displayMessage("$JOB successfully set to\n{}".format(job))
    except Exception as e:
        print (str(e))
    update_cachedir(node)

def update_cachedir(node):
    job = hou.getenv('JOB')
    ################################## SET $CacheDir START ###############################
    try:
        d = os.listdir(job)
        cachefolder = list(filter(lambda a: 'Cache' in a, d))[0]
        cachedir = job + '/' + cachefolder
    except IndexError:
        cachedir = job + '/88_Cache'
        os.makedir(cachedir)
        
    # set houdini env
    hou.putenv("CacheDir", cachedir)
    if cachedir == hou.getenv('CacheDir'):
        hou.ui.displayMessage("$CacheDir successfully set to\n{}".format(cachedir))
    ################################## SET $CacheDir END #################################