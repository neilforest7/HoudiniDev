import os
import hou
import PySide2


def onCreated(node):
    node_name = 'Jupiter_Set_Job'
    action = 'Install'
    installed_node_color = hou.Color((0.054, 0.325, 0.603))

    # Get Some Basic Infomation
    hdapath = node.type().definition().libraryFilePath()
    filepath = hou.hipFile.path()
    filename = hou.hipFile.basename()
    prev_job = hou.getenv("JOB")
    prismjob = hou.getenv("PRISMJOB")
    job = ''

    ################################## SET $JOB DIR ######################################
    try:
        if os.path.exists(prismjob):
            job = prismjob
        else:
            p = filepath.split('/')
            workflow = list(filter(lambda a: 'Workflow' in a, p))[0]
            job = filepath.split('/' + workflow)[0]
            # get 'A:\Projects\3d\Maya_projects\Tiktok_mini' in
            # A:\Projects\3d\Maya_projects\Tiktok_mini\03_Workflow\Shots\shot2-a-2-2\Scenefiles\fx\Effects\shot_shot2-a-2-2_fx_Effects_v0010__lch_.hip
    except Exception as e:
        print(str(e))
        job = ask_for_job(node)

    try:
        hou.allowEnvironmentToOverwriteVariable("JOB", True)
        hou.unsetenv("JOB")
        hou.putenv("JOB", job)
        if job == hou.getenv('JOB'):
            hou.ui.displayMessage(f"$JOB successfully set to\n{job}")
    except Exception as e:
        print(str(e))
    ################################## SET $JOB END ######################################

    update_cachedir('popmessage')
    update_parm(node)
    node.setDisplayFlag(False)
    node.setGenericFlag(hou.nodeFlag.Selectable, False)
    node.setColor(installed_node_color)
    node.setUserData('nodeshape', 'star')

    try:
        node.setName(node_name)
    except Exception as e:
        print(str(e))
        hou.ui.displayMessage("JupiterSetJob Node exist\nOlder One was removed")
        older_node = hou.node('/obj/' + node_name)
        older_node.destroy()
        node.setName(node_name)


# Set default node name, action (for pop up window) color, and shape
def onLoaded(node):
    updated_node_color = hou.Color((0.31, 0.649, 0.345))
    update_cachedir()
    update_parm(node)
    node.setDisplayFlag(False)
    node.setGenericFlag(hou.nodeFlag.Selectable, False)
    node.setColor(updated_node_color)
    node.setUserData('nodeshape', 'star')

    if node.parm('autosave_btn').eval():
        hou.setPreference('autoSave', '1')


def autoSave(node, *arg):
    if not node.parm('autosave_btn').eval():
        hou.setPreference('autoSave', '0')
    else:
        hou.setPreference('autoSave', '1')


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


def ask_for_job(node):
    job = hou.ui.selectFile(title="SelectJobFolder", file_type=hou.fileType.Directory).rstrip("/")
    job = hou.text.expandString(job)
    if os.path.exists(job):
        return job
    # use a loop to ensure the existence of job dir
    else:
        hou.ui.displayMessage("Please Select Valid $JOB Path")
        reset_job(node)


# used for reset_job button
def reset_job(node):
    job = hou.ui.selectFile(title="SelectJobFolder", file_type=hou.fileType.Directory).rstrip("/")
    job = hou.text.expandString(job)
    if os.path.exists(job):
        hou.allowEnvironmentToOverwriteVariable("JOB", True)
        hou.unsetenv("JOB")
        hou.putenv("JOB", job)
        if job == hou.getenv('JOB'):
            hou.ui.displayMessage("$JOB successfully set to\n{}".format(job))
        update_cachedir()
        update_parm(node)
    # use a loop to ensure the existence of job dir
    else:
        hou.ui.displayMessage("Please Select Valid $JOB Path")
        reset_job(node)


# update $CacheDir
def update_cachedir(*arg):
    job = hou.getenv('JOB')
    try:
        d = os.listdir(job)
        cachefolder = list(filter(lambda a: ('Cache' in a), d))[0]
        cachedir = os.path.join(job, cachefolder)
    except IndexError:
        cachedir = os.path.join(job, "88_Cache")
        os.makedirs(cachedir)
    # set houdini env
    if os.path.exists(cachedir):
        hou.putenv("CacheDir", cachedir)
    if cachedir == hou.getenv('CacheDir'):
        if arg:
            hou.ui.displayMessage(f"$CacheDir successfully set to\n{cachedir}")
