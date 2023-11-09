
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread
from UI.SplashScreen import SplashScreen
from DataCapture.CameraSender import CameraSender
from error import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Climbing Rocks")
        self.setFixedSize(1280, 800)
        self.setStyleSheet("background-color: #222222;")
        
        splashScreen = SplashScreen(self)
        self.setCentralWidget(splashScreen)

        # Create camera sender thread
        try:
            self.cameraSender = CameraSender()
            self.cameraSender.frameSignal.connect(self.updateFrame)
            self.cameraSender.cameraConnectSignal.connect(self.handleCameraConnection)
            self.cameraSender.start()
            splashScreen.setProgress(50)

        except CameraNotFoundError as e:
            self.splashScreen.setError(str(e))
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
            pass

    def updateFrame(self):
        # to implement
        pass

    def handleCameraConnection(self, connected):
        # to implement
        pass
        



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    
    sys.exit(app.exec_())
