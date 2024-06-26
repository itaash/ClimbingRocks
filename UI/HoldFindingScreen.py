from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot, QRect, QSize
import cv2, numpy as np, csv

from object_detection.utils import label_map_util, visualization_utils as viz_utils
from object_detection.utils import ops as utils_ops

class HoldFindingScreen(QWidget):
    holdsFoundSignal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.stackedLayout = QStackedLayout(self)
        self.stackedLayout.setStackingMode(1)
        self.stackedLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create labels for live feed and clear area image  
        self.liveFeed = QLabel(self)
        self.liveFeed.setScaledContents(True)
        self.liveFeed.setAlignment(Qt.AlignCenter)

        # Add the live feed and overlay layouts to the stacked layout
        self.stackedLayout.addWidget(self.liveFeed)

        # Set the main layout for the HoldFindingScreen
        # self.setLayout(self.stackedLayout)

        # Add the logo to the top left corner
        self.logoLabel = QLabel(self)
        self.logoLabel.setPixmap(QPixmap("UI/UIAssets/logo.png").scaledToWidth(160, Qt.SmoothTransformation))
        self.logoLabel.setStyleSheet("background-color: transparent;")
        self.logoLabel.setFixedSize(160, 160)
        self.logoLabel.move(35, 14)
        
        # clear area image
        self.clearAreaLabel = QLabel(self)
        self.clearAreaLabel.setFixedSize(parent.width()//2, parent.height()//2)
        clearAreaImage = QPixmap.scaledToWidth(QPixmap("UI/UIAssets/ClearArea.png"), parent.width()//2, Qt.SmoothTransformation)
        self.clearAreaLabel.setPixmap(clearAreaImage)
        self.clearAreaLabel.setAlignment(Qt.AlignCenter)
        self.clearAreaLabel.setStyleSheet("background-color: 'transparent';")
        # move the clear area image to the center of the screen
        self.clearAreaLabel.move((parent.width() - self.clearAreaLabel.width()) // 2,
                                ((parent.height() - self.clearAreaLabel.height()) *2)// 3)

        # Create status label
        self.statusLabel = QLabel(self)
        self.statusLabel.setFixedSize((parent.width())//4, parent.height()//5)
        # statusPixmap = QPixmap.scaledToWidth(QPixmap("UI/UIAssets/SearchingForHolds.png"), parent.width()//3, Qt.SmoothTransformation)
        # self.statusLabel.setPixmap(statusPixmap)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet(" background-color: 'transparent';")
        self.statusLabel.move(parent.width() - self.statusLabel.width() - 40, 20)

        # Set up the camera sender
        self.cameraSender = parent.cameraSender
        self.cameraSender.frameSignal.connect(self.updateLiveFeed)

        self.connectCameraSenderframeSignal()

        
        # flag to indicate if the holds have been found
        self.holdsTimerStarted = False
        self.holdsFound = False
        self.visible = False

        # set up the hold finding thread
        self.holdFindingThread = parent.holdFindingThread
        if parent.holdFindingModelLoaded:
            self.onHoldFindingModelLoaded()
        else:
            self.holdFindingThread.holdFindingModelLoaded.connect(self.onHoldFindingModelLoaded)

    def setObjectParent(self, parent):
        self.parent = parent

    @pyqtSlot()
    def updateLiveFeed(self):
        """
        Update the live feed label with the latest frame from the camera sender, or the frame with the holds detected once they have been found
        Feed is overlayed with the clear area image until the holds are found
        Feed is overlayed with the status label that updates based on the status of the hold finding model
        """
        if not self.holdsFound:
            frameData = self.cameraSender.getFrame()

            if frameData is not None:
                # Convert the frame data to a QImage
                frame = QImage(frameData, self.cameraSender.resolution[0], self.cameraSender.resolution[1], QImage.Format_BGR888)
                # Convert the QImage to a QPixmap
                pixmap = QPixmap(frame)
                # pixmap=QPixmap.scaledToWidth(pixmap, round(self.width()*0.9), Qt.SmoothTransformation)
                frameRect = QRect(0,int((pixmap.height()-self.height())//2),self.width(),self.height())
                pixmap=pixmap.copy(frameRect)

                # Display the QImage in the QLabel
                self.liveFeed.setPixmap(pixmap)

            else:
                # If the frame is empty, display a black screen
                self.liveFeed.setPixmap(QPixmap())
        else:
            self.liveFeed.setPixmap(self.framePixmapWithHolds)
            self.clearAreaLabel.hide()
            # self.holdsFoundSignal.emit

        if self.parent.holdFindingModelLoaded:
            # self.statusLabel.setFixedSize((self.parent.width()*1)//2, self.parent.height()//8)
            # self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
            #                         self.parent.height() - self.statusLabel.height() - 40)
            if not self.holdsFound:
                self.statusLabel.setPixmap(QPixmap("UI/UIAssets/FindingHolds.png").scaledToWidth(self.statusLabel.width(), Qt.SmoothTransformation))
            else:
                self.statusLabel.setPixmap(QPixmap("UI/UIAssets/HoldsFound.png").scaledToWidth(self.statusLabel.width(), Qt.SmoothTransformation))
        else:
            # self.statusLabel.setFixedSize((self.parent.width()*2)//4, self.parent.height()//8)
            # self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
            #                         self.parent.height() - self.statusLabel.height() - 40)
            self.statusLabel.setPixmap(QPixmap("UI/UIAssets/LoadingModel.png").scaledToWidth(self.statusLabel.width(), Qt.SmoothTransformation))

    @pyqtSlot(bool)
    def handleCameraConnection(self, connected):
        # Update the status label based on camera connection status
        if connected:
            pass # Do nothing
        else:
            self.statusLabel.setText("Camera Disconnected")
            self.statusLabel.setStyleSheet(
                "background-color: #e74c3c;"  # Red background
                "color: #ecf0f1;"  # Light text color
                "border-radius: 15px;"  # Rounded corners
                "padding: 5px;"  # Padding for pill shape
            )

    # function to be called when the screen is shown
    def showEvent(self, event):

        self.visible = True
        
        # Start timer to find holds if the model is loaded
        if self.parent.holdFindingModelLoaded and not self.holdsTimerStarted:
            self.findHoldsTimer = QTimer(self)
            self.findHoldsTimer.setSingleShot(True)
            self.findHoldsTimer.timeout.connect(self.findHolds)
            self.findHoldsTimer.start(4500)
            self.holdsTimerStarted = True

    @pyqtSlot()
    def onHoldFindingModelLoaded(self):
        """
        called when the model is loaded
        """
        self.parent.holdFindingModelLoaded = True
        if not self.holdsTimerStarted and self.isVisible():
            self.findHoldsTimer = QTimer(self)
            self.findHoldsTimer.setSingleShot(True)
            self.findHoldsTimer.timeout.connect(self.findHolds)
            self.findHoldsTimer.start(3000)
            self.holdsTimerStarted = True

    def connectCameraSenderframeSignal(self):
        self.cameraSender.frameSignal.connect(self.updateLiveFeed)

    def disconnectCameraSenderframeSignal(self):
        try:
            self.cameraSender.frameSignal.disconnect(self.updateLiveFeed)
        except TypeError:
            print("CameraSender frameSignal not connected")

    @pyqtSlot()
    def findHolds(self):
        # This function is called after the 3-second timer
        # Connect to the FindHolds function with the most recent frame
        frame = self.cameraSender.getFrame()
        # convert the frame to a jpg image
        # frame = cv2.imencode('.jpg', frame)[1].tobytes()
        # Call FindHolds function with the frame as an argument
        self.findHoldsFunction(frame)
        # Add any additional logic or transitions here

    def findHoldsFunction(self, frame):
        # modify minScore and numHolds to change the number of holds detected
        print("Finding Holds...")
        self.detections = self.holdFindingThread.runInference(frame)
        minScore = 0.1
        numHolds = 9
        frameWithHolds = self.holdFindingThread.getImageWithHoldsVolumes(frame, self.detections, minScore) # expects a numpy array
        
        # Convert image to QImage
        height, width, channel = frameWithHolds.shape
        bytesPerLine = 3 * width
        qImage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_BGR888)
        self.framePixmapWithHolds = QPixmap(qImage)
        
        # self.getImageWithHoldsVolumes(frame, self.detections, minScore)
        if self.detections is not None:
            self.holdsFound = True
            self.holdFindingThread.saveDetections(self.detections, frame, maxHolds=numHolds, threshold=minScore)
            QTimer.singleShot(3000, self.holdsFoundSignal.emit)
    
    def reset(self):
        self.visible = False
        self.holdsFound = False
        self.holdsTimerStarted = False
        self.clearAreaLabel.show()
        self.disconnectCameraSenderframeSignal()

        self.holdFindingThread.reset()
        # self.statusLabel.setFixedSize((self.parent.width()*2)//5, self.parent.height()//6) 
        # self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
        #                             self.parent.height() - self.statusLabel.height() - 40)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase

    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks')
    from DataCapture.CameraSender import CameraSender
    from DataCapture.CircularHoldFinder import HoldFindingThread
    from error import HoldModelError, CameraNotFoundError, FontError
    from PyQt5.QtGui import QFontDatabase, QFont



    app = QApplication(sys.argv)
    
    if (QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf") == -1):
        raise FontError("Could not load font")

    if (QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf") == -1):
        raise FontError("Could not load font")

    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("Climbing Rocks")
    window.setFixedSize(1280, 800)
    window.setFont(QFont("DM Sans"))
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.holdFindingModelLoaded = False
    window.cameraSender = CameraSender(window)
    window.cameraSender.start()

    # Create the hold finding thread
    window.holdFindingThread = HoldFindingThread(window)

    # Create the hold finding screen
    holdFindingScreen = HoldFindingScreen(window)

    window.setCentralWidget(holdFindingScreen)
    window.holdFindingThread.start()

    # Show the window and run the app
    window.show()
    sys.exit(app.exec_())
else:
    from DataCapture.CircularHoldFinder import HoldFindingThread
    from DataCapture.CameraSender import CameraSender