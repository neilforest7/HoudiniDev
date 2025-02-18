import os
import hou

from hutil.Qt import QtCore, QtWidgets, QtUiTools
from commonQt.appQss import qss
path = os.path.dirname(__file__)
print(path)


class AttribManager(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        print("Hey I am in a class!!!")

        # load UI file
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load("D:/centralizeTools/houdini/scripts/python/houQt/untitled.ui")

        # Layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.setStyleSheet(qss)


def show():
    dialog = AttribManager()
    dialog.setParent(hou.qt.floatingPanelWindow(None), QtCore.Qt.Window)
    dialog.show()


if __name__ == "hou.session":
    show()