import os
import hou
from PySide2 import QtCore, QtUiTools, QtWidgets


class GeoCreator(QtWidgets.QWidget):
    def __init__(self, node, doing):
        super(GeoCreator,self).__init__()
        ui_file = 'A:/AppBase/Houdini/localLib/scripts/python/widgets/test_hou_ui.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

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

        # UI Steps
        self.ui.btn_browsehda.clicked.connect(lambda: self.browseDirectory(node))
        self.ui.line_HDApath.setText(self.hda_path)
        self.ui.line_houdinipath.setText(self.houdini_path)
        self.ui.line_userprefdir.setText(self.userpref_path)

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

        node.setUserData('nodeshape', 'star')
        node.setDisplayFlag(False)
        node.setGenericFlag(hou.nodeFlag.Selectable, False)

    def onHdaPathChange(self, node):
        self.hda_name = self.hda_path.split('/otls/')[-1]
        self.lib_path = self.hda_path.split('/otls/')[0]
        self.ui.line_libpath.setText(self.lib_path)
        self.ui.line_HDApath.setText(self.hda_path)
        # hou.ui.displayMessage('HDA_PATH Set to {}'.format(self.hda_path))
        if self.lib_path in self.houdini_path:
            if self.action == 'install':
                hou.ui.displayMessage('Target Library Path Already Exists in HOUDINI_PATH')
            self.action = 'update'
        else:
            self.action = 'install'
        self.setLib(node)

    def browseDirectory(self, node):
        self.hda_path = hou.ui.selectFile(title="Select Current HDA", file_type=hou.fileType.Otl)
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
                    hou.ui.displayMessage('JSON File Exists in HOUDINI_USER_PREF_DIR')
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


def onCreated(node):
    if "Jupiter_Installed" in hou.node('/obj/').children():
        oldernode = hou.node('/obj/Jupiter_Installed')
        oldernode.destroy()
    win = GeoCreator(node, 'install')
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
    win = GeoCreator(node, 'update')
    win = show()

def uninstall(node):

    pass