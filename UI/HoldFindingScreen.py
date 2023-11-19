from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot, QRect

class HoldFindingScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        stackedLayout = QStackedLayout(self)
        stackedLayout.setStackingMode(1)
        stackedLayout.setContentsMargins(0, 0, 0, 0)
        stackedLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create labels for live feed and clear area image
        self.liveFeed = QLabel(self)
        self.liveFeed.setScaledContents(True)
        self.liveFeed.setAlignment(Qt.AlignCenter)

        # Add the live feed and overlay layouts to the stacked layout
        stackedLayout.addWidget(self.liveFeed)

        # Set the main layout for the HoldFindingScreen
        self.setLayout(stackedLayout)


        # clear area image
        self.clearAreaLabel = QLabel(self)
        clearAreaImage = QPixmap("UI/UIAssets/ClearArea.png")
        self.clearAreaLabel.setPixmap(clearAreaImage)
        self.clearAreaLabel.setAlignment(Qt.AlignCenter)

        # Create status label
        self.statusLabel = QLabel(self)
        statusPixmap = QPixmap("UI/UIAssets/SearchForHolds.png")
        self.statusLabel.setAlignment(Qt.AlignHCenter)
        self.statusLabel.setPixmap(statusPixmap)
        # Calculate the y-coordinate for the status label
        y_coordinate = self.height() - 100 - (self.statusLabel.height() // 2)
        # Set the geometry of the status label
        self.statusLabel.setGeometry(QRect(0, y_coordinate, 300, 100))

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
        frame = self.cameraSender.getFrame()

        if frame:
            pixmap = QPixmap()
            pixmap.loadFromData(frame)
            pixmap=pixmap.scaledToWidth(self.width())
            frameRect = QRect(0,int((pixmap.height()-self.height())//2),self.width(),self.height())
            pixmap=pixmap.copy(frameRect)
            self.liveFeed.setPixmap(pixmap)
            self.liveFeed.adjustSize()

    @pyqtSlot(bool)
    def handleCameraConnection(self, connected):
        # Update the status label based on camera connection status
        if connected:
            self.statusLabel.setText("Searching for Holds")
            self.statusLabel.setStyleSheet(
                "background-color: #3498db;"  # Blue background
                "color: #ecf0f1;"  # Light text color
                "border-radius: 15px;"  # Rounded corners
                "padding: 5px;"  # Padding for pill shape
            )
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
        # Call FindHolds function with the frame as an argument
        self.findHoldsFunction(frame)
        # Add any additional logic or transitions here

    def findHoldsFunction(self, frame):
        # Placeholder for the FindHolds function
        # Implement your logic to find holds in the frame
        print("Finding Holds...")
        # Add your hold detection logic here
        # Update the status label or perform other actions based on hold detection results
        self.statusLabel.setText("Holds Detected")
        self.statusLabel.setStyleSheet(
            "background-color: #2ecc71;"  # Green background
            "color: #ecf0f1;"  # Light text color
            "border-radius: 15px;"  # Rounded corners
            "padding: 5px;"  # Padding for pill shape
        )
