from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
import sys
import time

class TheBoss(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TheBoss, self).__init__(parent)
        self.resize(300,200)
        self.VL = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.VL.addWidget(self.label)
        self.logger = Logger()
        self.logger.sec_signal.connect(self.label.setText)
        self.logger.start()

    def closeEvent(self,event):
        self.logger.terminate()

class Logger(QtCore.QThread):
    sec_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super(Logger, self).__init__(parent)
        self.current_time = 0
        self.go = True
    def run(self):
        #this is a special fxn that's called with the start() fxn
        while self.go:
            time.sleep(1)
            self.sec_signal.emit(str(self.current_time))
            self.current_time += 1

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Thread Example")
    window = TheBoss()
    window.show()
    sys.exit(app.exec_())