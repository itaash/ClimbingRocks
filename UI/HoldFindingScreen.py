from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QColor

class HoldFindingScreen(QWidget):
    def __init__(self, cameraSender):
        super().__init__()

        self.cameraSender = cameraSender
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.findHolds)

        # Set up the layout
        layout = QVBoxLayout()

        # Large image titled "Clear Area" in the center
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setText("Clear Area")  # Placeholder text, you can replace it with an image if needed
        layout.addWidget(self.imageLabel)

        # Status label at the bottom center
        self.statusLabel = QLabel("Searching for Holds")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet(
            "background-color: #3498db;"  # Blue background
            "color: #ecf0f1;"  # Light text color
            "border-radius: 10px;"  # Rounded corners
        )
        layout.addWidget(self.statusLabel)

        # Set the main layout for the HoldFindingScreen
        self.setLayout(layout)

        # Show the screen and start the timer
        self.show()
        self.startTimer()

    def startTimer(self):
        # Start a timer for 3 seconds
        self.timer.start(3000)

    def findHolds(self):
        # Get the most recent frame from the camera
        frame = self.cameraSender.getFrame()

        # Call the FindHolds function with the frame
        self.findHoldsFunction(frame)

        # Stop the timer after it has run out
        self.timer.stop()

    def findHoldsFunction(self, frame):
        # Add your logic to process the frame and find holds
        # This function will be called once the timer runs out
        # You can update the UI or perform other actions based on the frame
        # Example: Display the processed frame or update the status label
        self.statusLabel.setText("Holds Found!")  # Placeholder text, update as needed
