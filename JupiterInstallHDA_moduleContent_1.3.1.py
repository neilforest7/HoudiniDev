import os
import hou
from PySide2 import QtCore, QtUiTools, QtWidgets


class InstallWindow(QtWidgets.QWidget):
    def __init__(self, node, doing):
        super(InstallWindow, self).__init__()
        self.action = doing
        self.installed_node_color = hou.Color((0.054, 0.325, 0.603))
        self.updated_node_color = hou.Color((0.152, 0.945, 0.674))

        # Get Environments
        # A:/AppBase/Houdini/localLib/otls/object_Neilforest.dev.jupiter_install.1.0.hda
        self.hda_path = node.type().definition().libraryFilePath()
        self.hda_typename = node.type().name()
        self.houdini_path = hou.getenv('HOUDINI_PATH')
        self.userpref_path = hou.getenv('HOUDINI_USER_PREF_DIR')
        self.userpackage_path = self.userpref_path + '/packages'
        if not os.path.exists(self.userpackage_path):
            os.makedirs(self.userpackage_path)
        self.hda_name = self.hda_path.split('/otls/')[-1]
        self.lib_path = self.hda_path.split('/otls/')[0]
        self.ocio_config = f'{self.lib_path}/config/ocio/renderman/aces1.2/config.ocio'
        #A:/AppBase/Houdini/localLib/config/ocio/renderman/aces1.2/config.ocio
        self.envfile_path = f'{self.userpref_path}/houdini.env'

        # Initial UI
        # A:\AppBase\Houdini\localLib\scripts\python\widgets\test_hou_ui.ui
        ui_file = f'{self.lib_path}/scripts/python/widgets/jupiter_install_main.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # UI Steps
        self.ui.btn_browsehda.clicked.connect(lambda: self.browseDirectory(node))
        self.ui.btn_browsejson.clicked.connect(lambda: self.browseJson(node))
        self.ui.btn_browselib.clicked.connect(lambda: self.browseLib(node))
        self.ui.btn_installocio.clicked.connect(lambda: injectOCIOEnv(self.envfile_path, self.ocio_config))
        self.ui.btn_uninstallocio.clicked.connect(lambda: removeOCIOEnv(self.envfile_path))
        self.ui.line_HDApath.setText(self.hda_path)
        self.ui.line_houdinipath.setText(self.houdini_path)
        self.ui.line_userprefdir.setText(self.userpref_path)
        self.ui.line_ocioconfig.setText(self.ocio_config)

        self.onHdaPathChange(node)

        if self.action == 'install':
            try:
                node.setName('Jupiter_Installed')
            except hou.OperationFailed:  # name exist
                hou.node('/obj/Jupiter_Installed').destroy()
                self.action == 'update'
            node.setColor(self.installed_node_color)

        if self.action == 'update':
            self.ui.label_title.setText('Jupiter Library Has Been Updated!')
            self.ui.label_restart.hide()
            try:
                node.setName('Jupiter_Updated')
                if "Jupiter_Installed" in hou.node('/obj/').children():
                    hou.node('/obj/Jupiter_Installed').destroy()
            except hou.OperationFailed:
                hou.node('/obj/Jupiter_Updated').destroy()
                node.setName('Jupiter_Updated')
            node.setColor(self.updated_node_color)

        # Set UI details
        shelf_file = f'{self.lib_path}/toolbar/jupiter_tools_shelf.shelf'
        hou.shelves.loadFile(shelf_file)
        hou.shelves.reloadShelfFiles()
        node.setUserData('nodeshape', 'star')
        node.setGenericFlag(hou.nodeFlag.Display, False)
        node.setGenericFlag(hou.nodeFlag.Selectable, False)

    def onHdaPathChange(self, node):
        self.hda_name = self.hda_path.split('/otls/')[-1]
        self.lib_path = self.hda_path.split('/otls/')[0]
        self.ui.line_libpath.setText(self.lib_path)
        self.ui.line_HDApath.setText(self.hda_path)
        # hou.ui.displayMessage('HDA_PATH Set to {}'.format(self.hda_path))
        if self.lib_path in self.houdini_path:
            if self.action == 'install':
                hou.ui.displayMessage(
                    'Target Library Path Already Exists in HOUDINI_PATH')
            self.action = 'update'
        else:
            self.action = 'install'
        self.setLib(node)

    def browseDirectory(self, node):
        self.hda_path = hou.ui.selectFile(
            title="Select Current HDA", file_type=hou.fileType.Otl)
        if self.hda_path:
            os.remove(self.jsonfile_path)
            self.onHdaPathChange(node)
            self.onUpdated(node)
        else:
            hou.ui.displayMessage('Please Select Valid Path')
            self.browseDirectory(node)

    def setLib(self, node):
        if os.path.exists(self.lib_path):
            self.jsonfile_path = self.userpackage_path + '/jupiter_localLib.json'
            if os.path.exists(self.jsonfile_path):
                if self.action == 'install':
                    hou.ui.displayMessage(
                        'JSON File Exists in HOUDINI_USER_PREF_DIR')
                self.action = 'update'
            else:
                self.action = 'install'
            # Get the json template from the Extra Files section
            f = node.type().definition().sections()['JSON_TEMPLATE'].contents()
            f = f.replace('@___lib_path___@', self.lib_path)
            with open(self.jsonfile_path, "w") as jsonfile:
                jsonfile.write(f)
            # Set UI and Parameters
            self.ui.line_jsonfilepath.setText(self.jsonfile_path)
            node.parm('str_currentjson').set(self.jsonfile_path)
            node.parm('str_currentlib').set(self.lib_path)

    def onUpdated(self, node):
        self.ui.label_title.setText('Jupiter Library Has Been Updated!')
        self.ui.label_restart.hide()
        node.setName('Jupiter_Updated')
        node.setColor(self.updated_node_color)

    def browseJson(self, node):
        openJson(node)

    def browseLib(self, node):
        openLib(node)


def onCreated(node):
    if "Jupiter_Installed" in hou.node('/obj/').children():
        oldernode = hou.node('/obj/Jupiter_Installed')
        oldernode.destroy()
    win = InstallWindow(node, 'install')
    win.show()


def onLoaded(node):
    # TODO: DOING NOTHING JUST UPDATE PARAMETERS
    # self.ui.label_title.setText('Jupiter Library Has Been Updated!')
    # self.ui.label_restart.hide()
    # self.ui.line_libpath.setText(self.lib_path)
    # self.ui.line_HDApath.setText(self.hda_path)
    # self.ui.line_jsonfilepath.setText(self.jsonfile_path)
    # node.parm('str_currentjson').set(self.jsonfile_path)
    # node.parm('str_currentlib').set(self.lib_path)
    win = InstallWindow(node, 'update')
    win.show()


def uninstall(node):
    noti = 'Confirm uninstall?\nHDAs in Jupiter Library will be removed from asset manager'
    result = hou.ui.displayMessage(noti, buttons=(
        'Yes, Delete', 'Cancel'), title='Jupiter Uninstall')
    if result == 0:
        node.setName('Jupiter_Uninstalled')
        node.setColor(hou.Color((0.160, 0.050, 0.309)))
        hda_path = node.type().definition().libraryFilePath()
        hda_name = hda_path.split('/otls/')[-1]
        lib_path = hda_path.split('/otls/')[0]
        hda_typename = node.type().name()
        houdini_path = hou.getenv('HOUDINI_PATH')
        userpref_path = hou.getenv('HOUDINI_USER_PREF_DIR')
        userpackage_path = userpref_path + '/packages'
        jsonfile_path = userpackage_path + '/jupiter_localLib.json'
        # Remove JSON
        if os.path.exists(jsonfile_path):
            os.remove(jsonfile_path)
        # Remove All HDA from Scanned Library
        otls_path = lib_path+'/otls'
        for files in os.listdir(otls_path):
            otl = os.path.join(otls_path, files)
            if os.path.isfile(otl) or os.path.isfile(hda):
                hou.hda.uninstallFile(
                    otl, oplibraries_file='Scanned Asset Library Directories')
        # Remove Embedded HDA
        hou.hda.uninstallFile('Embedded')
        hou.ui.displayMessage('Successfully Uninstalled')
        node.destroy()


def openJson(node):
    json_file = node.evalParm('str_currentjson')
    import os
    json_folder = os.path.split(json_file)[0]
    os.startfile(json_folder)


def openLib(node):
    lib_folder = node.evalParm('str_currentlib')
    import os
    os.startfile(lib_folder)

def injectOCIOEnv(envfile, ocio_config):
    import fileinput
    # Comment out old OCIO lines
    with fileinput.FileInput(envfile, inplace=True, backup='.bak') as f:
        for line in f:
            if 'OCIO' in line:
                if not line.startswith('#'):
                    print('# '+line, end = '')
                else:
                    print(line, end = '')
            else:
                print(line, end = '')
    # Append OCIO line to .env
    with open(envfile, "a+") as f:
        f.write("\n\nOCIO = "+f'"{ocio_config}"')
    hou.ui.displayMessage('OCIO Path Injected into Houdini.env')

def removeOCIOEnv(envfile):
    import fileinput
    # Remove OCIO line
    with fileinput.FileInput(envfile, inplace=True, backup='.bak') as f:
        for line in f:
            if not 'OCIO' in line:
                print(line, end = '')
    hou.ui.displayMessage('OCIO Path Removed from Houdini.env')