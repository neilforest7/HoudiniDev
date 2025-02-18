import hou
from PySide2 import QtCore, QtUiTools, QtWidgets

class GeoCreator(QtWidgets.QWidget):
    def __init__(self):
        super(GeoCreator,self).__init__()
        ui_file = 'C:/temp/uiGeoCreator.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        
        # Setup "Create Geometry" button
        self.ui.btn_create.clicked.connect(self.buttonClicked)
        
    def buttonClicked(self):
        customName = self.ui.lin_name.text()
        # Execute node creation 
        if checkExisting(customName) != True:
            createGeoNode(customName)
    
    def checkExisting(self, geometryName):
        # Check if "MY_GEO" exists
        if hou.node('/obj/{}'.format(geometryName)):
            # Display fail message
            hou.ui.displayMessage('{} already exists in the scene'.format(geometryName))
            return True    

    def createGeoNode(self, geometryName):
        # Get scene root node
        sceneRoot = hou.node('/obj/')
        # Create empty geometry node in scene root
        geometry = sceneRoot.createNode('geo', run_init_scripts=False)
        # Set geometry node name
        geometry.setName(geometryName)
        # Display creation message
        hou.ui.displayMessage('{} node created!'.format(geometryName))

win = GeoCreator()
win.show()