from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot, QRect, QSize
import cv2, numpy as np

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
                                (parent.height() - self.clearAreaLabel.height()) // 4)

        # Create status label
        self.statusLabel = QLabel(self)
        self.statusLabel.setFixedSize((parent.width()*2)//5, parent.height()//6)
        # statusPixmap = QPixmap.scaledToWidth(QPixmap("UI/UIAssets/SearchingForHolds.png"), parent.width()//3, Qt.SmoothTransformation)
        # self.statusLabel.setPixmap(statusPixmap)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet(" background-color: 'transparent';"
                                        "font-size: 20px;"
                                        "color: #ffffff;"
                                        "border-radius: 45px;"
                                        "border: 10px solid #222222;")
        self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
                                    self.parent.height() - self.statusLabel.height() - 40)

        # Set up the camera sender
        self.cameraSender = parent.cameraSender
        self.cameraSender.frameSignal.connect(self.updateLiveFeed)

        self.cameraSender.cameraConnectSignal.connect(self.handleCameraConnection)

        # set up the hold finding thread
        self.holdFindingThread = parent.holdFindingThread
        if parent.holdFindingModelLoaded:
            self.onHoldFindingModelLoaded()
        else:
            self.holdFindingThread.modelLoaded.connect(self.onHoldFindingModelLoaded)

        # flag to indicate if the holds have been found
        self.holdsFound = False


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
            self.statusLabel.setFixedSize((self.parent.width()*1)//2, self.parent.height()//8)
            self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
                                    self.parent.height() - self.statusLabel.height() - 40)
            if not self.holdsFound:
                self.statusLabel.setText("Searching for Holds")
                self.statusLabel.setStyleSheet(
                    "background-color: #c58af9;"  # purple background
                    "color: #ffffff;"
                    "border-radius: 35px;"
                    "border: 10px solid #962af4;"   # darker purple border
                    "font-size: 40px;"
                    "font-family: 'Bungee';"
                    "font-weight: bold;"
                )
            else:
                self.statusLabel.setText("Holds Found")
                self.statusLabel.setStyleSheet(
                    "background-color: #63D451;"  # green background
                    "color: #ffffff;"
                    "border-radius: 45px;"
                    "border: 10px solid #3FB42D;" # darker green border
                    "font-size: 40px;"
                    "font-family: 'Bungee';"
                    "font-weight: bold;"
                )
        else:
            self.statusLabel.setFixedSize((self.parent.width()*2)//4, self.parent.height()//8)
            self.statusLabel.move((self.parent.width() - self.statusLabel.width()) // 2,
                                    self.parent.height() - self.statusLabel.height() - 40)
            self.statusLabel.setText("Loading Hold-Finding Model")
            self.statusLabel.setStyleSheet(
                "background-color: #147A8F;"  # blue background
                "color: #ffffff;"
                "border-radius: 45px;"
                "border: 10px solid #3BC7E3;" # darker blue border
                "font-size: 30px;"
                "line-height: 0.5;"
                "font-family: 'Bungee';"
                "font-weight: bold;"
            )

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

    @pyqtSlot()
    def onHoldFindingModelLoaded(self):
        """
        called when the model is loaded
        """
        self.parent.holdFindingModelLoaded = True

        # Start timer to find holds
        self.findHoldsTimer = QTimer(self)
        self.findHoldsTimer.setSingleShot(True)
        self.findHoldsTimer.timeout.connect(self.findHolds)
        self.findHoldsTimer.start(3000)

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
        # Placeholder for the FindHolds function
        # Implement your logic to find holds in the frame
        print("Finding Holds...")
        self.detections = self.holdFindingThread.runInference(frame)
        self.framePixmapWithHolds = self.getImageWithHoldsVolumes(frame, self.detections)
        if self.detections is not None:
            self.holdsFound = True
            self.saveDetections(frame)
            QTimer.singleShot(3000, self.holdsFoundSignal.emit)
    
    
    def saveDetections(self, frame, maxHolds = 20, threshold = 0.3):
        """
        # Save the locations of the detected holds to a file

        # Args:
        #     frame: The frame that the holds were detected in
        #     maxHolds: The maximum number of holds to save
        #     threshold: The minimum score threshold for a hold to be saved

        """
        if self.detections is not None:
            # Drop detections of volumes (class 2)

            # investigate why this doesn't work
            filteredDetectionswithHolds = self.filterResultsforHolds(self.detections)
            filteredDetectionswithHoldsInCenterHalf = self.filterResultsforCenterHalf(filteredDetectionswithHolds)
            sortedDetections = self.sortDetectionsbyScore(filteredDetectionswithHoldsInCenterHalf)


            # Get the coordinates of the detected holds(class 1), not volumes (class 2)
            boxes = sortedDetections['detection_boxes']
            # Get the scores of the detected holds
            scores = sortedDetections['detection_scores']
            # Get the classes of the detected holds
            classes = sortedDetections['detection_classes']

            # Get the width and height of the frame
            height, width, channel = frame.shape

            # Create a list to store the coordinates of the detected holds
            holdCoordinates = []

            # Create a counter to keep track of the number of holds being saved
            i = 0
            # Iterate through the detected holds
            while i < min(maxHolds, len(boxes)):
                # If the score of the hold is above the threshold
                if classes[i] == 1:
                    if scores[i] > threshold:
                        # Get the coordinates of the hold
                        ymin, xmin, ymax, xmax = boxes[i]
                        # Convert the coordinates from normalized to pixel coordinates
                        left, right, top, bottom = xmin * width, xmax * width, ymin * height, ymax * height
                        # Add the coordinates of the hold to the list
                        holdCoordinates.append((left, right, top, bottom))
                        i += 1

            
            # Sort the coordinates of the detected holds by their y-coordinate
            holdCoordinates.sort(key=lambda x: x[2])
            
            # Save the coordinates of the detected holds to a file
            with open('data/holdCoordinates.csv', 'w') as f:
                # Iterate through the coordinates of the detected holds
                print("Savnig coordinates of ", len(holdCoordinates), " holds")
                print(holdCoordinates)
                for i, (left, right, top, bottom) in enumerate(holdCoordinates):
                    # Write the coordinates to the file
                    f.write(f'{i},{left},{right},{top},{bottom}\n')
    
    def filterResultsforHolds(self, output, confidence_threshold=0.3):
        scores = np.array(output['detection_scores'])
        classes = np.array(output['detection_classes'])
        mask = (scores >= confidence_threshold) & (classes == 1)

        filteredResults = {
            'detection_anchor_indices': np.array(output['detection_anchor_indices'])[mask],
            'detection_boxes': np.array(output['detection_boxes'])[mask],
            'detection_classes': classes[mask],
            'detection_multiclass_scores': np.array(output['detection_multiclass_scores'])[mask],
            'detection_scores': scores[mask]
        }

        return filteredResults
        
    def filterResultsforCenterHalf(self, output):
        mask = (np.array(output['detection_boxes'])[:, 0] >= 0.25) & (np.array(output['detection_boxes'])[:, 0] <= 0.75)

        filteredResults = {
            'detection_anchor_indices': np.array(output['detection_anchor_indices'])[mask],
            'detection_boxes': np.array(output['detection_boxes'])[mask],
            'detection_classes': np.array(output['detection_classes'])[mask],
            'detection_multiclass_scores': np.array(output['detection_multiclass_scores'])[mask],
            'detection_scores': np.array(output['detection_scores'])[mask]
        }

        return filteredResults
        
    def sortDetectionsbyScore(self, output):
        sortedIndices = np.argsort(output['detection_scores'])[::-1]

        sortedResults = {
            'detection_anchor_indices': np.array(output['detection_anchor_indices'])[sortedIndices],
            'detection_boxes': np.array(output['detection_boxes'])[sortedIndices],
            'detection_classes': np.array(output['detection_classes'])[sortedIndices],
            'detection_multiclass_scores': np.array(output['detection_multiclass_scores'])[sortedIndices],
            'detection_scores': np.array(output['detection_scores'])[sortedIndices]
        }

        return sortedResults

        
    def getImageWithHoldsVolumes(self, frame, detections):
        viz_utils.visualize_boxes_and_labels_on_image_array(
            frame,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            label_map_util.create_category_index_from_labelmap(
                'models/HoldModel/hold-detection_label_map.pbtxt', use_display_name=True),
            use_normalized_coordinates=True,
            max_boxes_to_draw=10,
            min_score_thresh=.30,
            agnostic_mode=False)

        # Convert image to QImage
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_BGR888)
        pixmap = QPixmap(qImage)

        return pixmap

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase

    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks')
    from DataCapture.CameraSender import CameraSender
    from DataCapture.HoldFinder import HoldFindingThread
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
    window.holdFindingThread.start()

    # Create the hold finding screen
    holdFindingScreen = HoldFindingScreen(window)
    window.setCentralWidget(holdFindingScreen)

    # Show the window and run the app
    window.show()
    sys.exit(app.exec_())
else:
    from DataCapture.HoldFinder import HoldFindingThread
    from DataCapture.CameraSender import CameraSender