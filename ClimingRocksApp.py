
import sys, os, time, cv2
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread, QRect
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap, QImage


from UI.SplashScreen import SplashScreen
from UI.LobbyScreen import LobbyScreen
from UI.HoldFindingScreen import HoldFindingScreen
from UI.ClimbingScreen import ClimbingScreen
from UI.ResultsScreen import ResultsScreen
from DataCapture.CameraSender import CameraSender
from DataCapture.HoldFinder import HoldFindingThread
from DataCapture.PoseEstimator import PoseEstimatorThread
from error import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Climbing Rocks")
        self.setFixedSize(1280, 800)
        self.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")

        self.splashScreen = SplashScreen(self)
        self.setCentralWidget(self.splashScreen)

        # flags
        self.firstFrameReceived = False
        self.cameraConnected = False
        self.holdFindingModelLoaded = False
        self.poseEstimatorModelLoaded = False
        self.climbFinished = False

        try:    

            # Load fonts
            if (QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf") == -1):
                raise FontError("Could not load font: DMSans")
            else:
                self.setFont(QFont("DM Sans"))
            if (QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf") == -1):
                raise FontError("Could not load font: Bungee")
            self.splashScreen.setProgress(10)

            # Create camera sender thread
            self.cameraSender = CameraSender(self)
            self.cameraSender.frameSignal.connect(self.updateFrame)
            self.cameraSender.cameraConnectSignal.connect(self.handleCameraConnection)
            self.splashScreen.setProgress(20)
            self.cameraSender.start()

            # Create hold finding thread
            self.holdFindingThread = HoldFindingThread(self)
            self.holdFindingThread.modelLoaded.connect(self.onHoldFindingModelLoaded)
            self.splashScreen.setProgress(30)
            self.holdFindingThread.start()



        except CameraNotFoundError as e:
            self.splashScreen.setError(str(e))
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
            pass

        except FontError as e:
            self.splashScreen.setError(str(e))
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
            pass

        except HoldModelError as e:
            self.splashScreen.setError(str(e))
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
            pass

        except Error as e:
            self.splashScreen.setError(str(e))
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
            pass

    def goToHoldFindingScreen(self):
        self.holdFindingScreen = HoldFindingScreen(self)
        self.currentClimber = self.lobbyScreen.getClimberName()
        self.lobbyScreen.setParent(None)
        self.setCentralWidget(self.holdFindingScreen)
        self.holdFindingScreen.holdsFoundSignal.connect(self.goToClimbingScreen)

    def goToClimbingScreen(self):
        self.climbingScreen = ClimbingScreen(self)
        self.holdFindingScreen.cameraSender.frameSignal.disconnect(self.holdFindingScreen.updateLiveFeed)
        self.holdFindingScreen.setParent(None)
        self.setCentralWidget(self.climbingScreen)
        self.climbingScreen.cameraSender.frameSignal.connect(self.climbingScreen.onFrameSignal)
        self.climbingScreen.poseEstimator.climbFinishedSignal.connect(self.onClimbFinished)


    @pyqtSlot()
    def onHoldFindingModelLoaded(self):
        self.holdFindingModelLoaded = True
        self.poseEstimator = PoseEstimatorThread(self)
        self.poseEstimator.modelLoaded.connect(self.onPoseEstimatorLoaded)
        self.poseEstimator.start()

    @pyqtSlot()
    def onPoseEstimatorLoaded(self):
        self.poseEstimatorModelLoaded = True


    @pyqtSlot()
    def updateFrame(self):
        pass
    
    @pyqtSlot(bool)
    def handleCameraConnection(self, connected):
        self.cameraConnected = connected
        if not self.cameraConnected:
            self.splashScreen.setError("Failed to connect to camera. Please check your camera connection and try again.")
            timer = QTimer()
            timer.singleShot(10000, sys.exit)
        else:
            if not self.firstFrameReceived:
                for i in range(self.splashScreen.getProgress(), 95):
                    self.splashScreen.setProgress(i)
                    time.sleep(0.01)
                self.firstFrameReceived = True
                self.lobbyScreen = LobbyScreen(self)
                self.splashScreen.setParent(None)
                self.setCentralWidget(self.lobbyScreen)
        pass

    @pyqtSlot(bool)
    def onClimbFinished(self, climbSuccessful):
        self.climbFinished = True
        self.resultsScreen = ResultsScreen(self, self.currentClimber, climbSuccessful)
        self.climbingScreen.setParent(None)
        self.setCentralWidget(self.resultsScreen)
        pass
        
    def onHoldsFound(self):
        self.goToClimbingScreen()
        pass



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    # app.setWindowIcon(app.style().standardIcon(getattr(QStyle, 'SP_DesktopIcon')))
    mainWindow = MainWindow()
    mainWindow.show()
    
    sys.exit(app.exec_())
