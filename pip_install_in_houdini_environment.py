import subprocess, os



FOLDER = hou.text.expandString("$HOUDINI_TEMP_DIR")

PIP_FOLDER = os.path.join(hou.text.expandString("$HOUDINI_USER_PREF_DIR"), "scripts", "python")

PIPINSTALLFILE = os.path.join(FOLDER, "get-pip.py")



message = "Please enter the name of the python module you wish to install!"

button_index, module_name = hou.ui.readInput(message, buttons=('Install',"Cancel"), severity=hou.severityType.Message, default_choice=1, close_choice=1, help="HELP TEXT", title="Python Module Installer", initial_contents="scipy")



if button_index == 0:

    

    # Downloading pip “installer”

    p = subprocess.Popen(["curl", "-o", PIPINSTALLFILE, "https://bootstrap.pypa.io/get-pip.py"])

    p.communicate() # Note this line is only needed if the above process should block the thread



    # Installing pip to Houdini

    p = subprocess.Popen(["hython", PIPINSTALLFILE])

    p.communicate()



    #Installing / Upgrading setuptools because on py3.9 the netifaces module needs to be rebuilt

    p = subprocess.Popen(["hython", "-m", "pip", "install", "--target", PIP_FOLDER, module_name])

    p.communicate()