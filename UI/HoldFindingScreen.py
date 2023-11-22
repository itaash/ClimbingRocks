from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot, QRect
import cv2

class HoldFindingScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

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

        
        # clear area image
        self.clearAreaLabel = QLabel(self)
        clearAreaImage = QPixmap("UI/UIAssets/ClearArea.png")
        self.clearAreaLabel.setPixmap(clearAreaImage)
        self.clearAreaLabel.setAlignment(Qt.AlignHCenter)
        # self.clearAreaLabel.setStyleSheet("background-color: 'transparent';")
        # move the clear area image to the center of the screen
        self.clearAreaLabel.setGeometry(QRect((self.width() - self.clearAreaLabel.width()) // 2, 
                                              (self.height() - self.clearAreaLabel.height()) // 2, 
                                              self.clearAreaLabel.width(), 
                                              self.clearAreaLabel.height()))

        # Create status label
        self.statusLabel = QLabel(self)
        statusPixmap = QPixmap("UI/UIAssets/SearchingForHolds.png")
        self.statusLabel.setPixmap(statusPixmap)
        self.statusLabel.setAlignment(Qt.AlignHCenter)
        # self.statusLabel.setStyleSheet("background-color: 'transparent';")
        # move the status label to the bottom center of the screen
        self.statusLabel.setGeometry(QRect((self.width() - self.statusLabel.width()) // 2, 
                                            self.height() - self.statusLabel.height() - 40, 
                                            self.statusLabel.width(), 
                                            self.statusLabel.height()))        

        # Set up the camera sender
        self.cameraSender = parent.cameraSender
        self.cameraSender.frameSignal.connect(self.updateLiveFeed)
        self.cameraSender.cameraConnectSignal.connect(self.handleCameraConnection)

        # Set up a timer for 3 seconds to trigger FindHolds function
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.findHolds)
        self.timer.start(3000)

    @pyqtSlot()
    def updateLiveFeed(self):
        # Update the live feed label with the latest frame from the camera
        frameData = self.cameraSender.getFrame()

        if frameData is not None:
            # Convert the frame data to a QImage
            frame = QImage(frameData, self.cameraSender.resolution[0], self.cameraSender.resolution[1], QImage.Format_BGR888)
            # Convert the QImage to a QPixmap
            pixmap = QPixmap.fromImage(frame)
            # pixmap=pixmap.scaledToWidth(self.width())
            frameRect = QRect(0,int((pixmap.height()-self.height())//2),self.width(),self.height())
            # pixmap=pixmap.copy(frameRect)

            # Display the QImage in the QLabel
            self.liveFeed.setPixmap(pixmap)

        else:
            # If the frame is empty, display a black screen
            self.liveFeed.setPixmap(QPixmap())

    @pyqtSlot(bool)
    def handleCameraConnection(self, connected):
        # Update the status label based on camera connection status
        if connected:
            """
            self.statusLabel.setText("Searching for Holds")
            self.statusLabel.setStyleSheet(
                "background-color: #3498db;"  # Blue background
                "color: #ecf0f1;"  # Light text color
                "border-radius: 15px;"  # Rounded corners
                "padding: 5px;"  # Padding for pill shape
            )
            """
            pass
        else:
            self.statusLabel.setText("Camera Disconnected")
            self.statusLabel.setStyleSheet(
                "background-color: #e74c3c;"  # Red background
                "color: #ecf0f1;"  # Light text color
                "border-radius: 15px;"  # Rounded corners
                "padding: 5px;"  # Padding for pill shape
            )

    @pyqtSlot()
    def findHolds(self):
        # This function is called after the 3-second timer
        # Connect to the FindHolds function with the most recent frame
        frame = self.cameraSender.getFrame()
        # convert the frame to a jpg image
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        # Call FindHolds function with the frame as an argument
        self.findHoldsFunction(frame)
        # Add any additional logic or transitions here

    def findHoldsFunction(self, frame):
        # Placeholder for the FindHolds function
        # Implement your logic to find holds in the frame
        print("Finding Holds...")
        # Add your hold detection logic here
        # Update the status label or perform other actions based on hold detection results
        """
        self.statusLabel.setText("Holds Detected")
        self.statusLabel.setStyleSheet(
            "background-color: #2ecc71;"  # Green background
            "color: #ecf0f1;"  # Light text color
            "border-radius: 15px;"  # Rounded corners
            "padding: 5px;"  # Padding for pill shape
        )
        """

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase

    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks')   
    from DataCapture.CameraSender import CameraSender


    app = QApplication(sys.argv)

    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("Climbing Rocks")
    window.setFixedSize(1280, 800)
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.cameraSender = CameraSender(window)
    window.cameraSender.start()

    # Create the hold finding screen
    holdFindingScreen = HoldFindingScreen(window)
    window.setCentralWidget(holdFindingScreen)

    # Show the window and run the app
    window.show()
    sys.exit(app.exec_())