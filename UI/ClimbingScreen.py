from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QStackedLayout, QLabel, QWidget
from PyQt5.QtGui import QImage, QPixmap

import logging
import numpy as np, cv2


class ClimbingScreen(QWidget):
    def __init__(self, parent=None):
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

        # Set the stacked layout as the main layout
        self.setLayout(self.stackedLayout)

        # Add the logo to the top left corner
        self.logoLabel = QLabel(self)
        self.logoLabel.setPixmap(QPixmap("UI/UIAssets/logo.png").scaledToWidth(180, Qt.SmoothTransformation))
        self.logoLabel.setStyleSheet("background-color: transparent;")
        self.logoLabel.setFixedSize(180, 180)
        self.logoLabel.move(20, 20)

        # Connect signals
        self.cameraSender = parent.cameraSender
        self.cameraSender.frameSignal.connect(self.onFrameSignal)

        self.poseEstimator = parent.poseEstimator
        if parent.poseEstimatorModelLoaded:
            self.poseEstimatorModelLoaded = True
        else:
            self.poseEstimatorModelLoaded = False
            self.poseEstimator.modelLoaded.connect(self.onPoseEstimatorModelLoaded)
        self.poseEstimator.inferenceSignal.connect(self.onInferenceSignal)

        self.keypoints = None
        self.centerOfGravity = (None, None)
        self.armAngles = (None, None)


    
    @pyqtSlot()
    def onPoseEstimatorModelLoaded(self):
        self.parent.poseEstimatorModelLoaded = True
        self.poseEstimatorModelLoaded = True
        logging.info("Model loaded from Climbing Screen")

    @pyqtSlot()
    def onFrameSignal(self):
        frame = self.cameraSender.getFrame()
        if frame is None:
            return
        if self.poseEstimatorModelLoaded:
            frame = self.drawSkeleton(frame, self.keypoints, self.centerOfGravity)
        # Convert image to QImage and display it in the QLabel
        frame = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        # Convert the QImage to a QPixmap
        pixmap = QPixmap(frame)
        # pixmap=QPixmap.scaledToWidth(pixmap, round(self.width()*0.9), Qt.SmoothTransformation)
        frameRect = QRect(0,int((pixmap.height()-self.height())//2),self.width(),self.height())
        pixmap=pixmap.copy(frameRect)

        # Display the QImage in the QLabel
        self.liveFeed.setPixmap(pixmap)
        pass

    @pyqtSlot(np.ndarray, tuple, tuple)
    def onInferenceSignal(self, keypoints, centerOfGravity, armAngles):
        print("Inference signal received in ClimbingScreen")
        self.keypoints = keypoints
        self.centerOfGravity = centerOfGravity
        self.armAngles = armAngles        
        pass


    def drawSkeleton(self, frame, keypoints, centerOfGravity, threshold=0.3) -> np.ndarray:
        """
        Draw the detected skeleton on a given frame.

        Args:
        frame (numpy.ndarray): The frame to draw the skeleton on.
        keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
        centerOfGravity (tuple): The position of the center of gravity (e.g., (x, y)).
        threshold (float): Minimum confidence score for a keypoint to be considered. Defaults to 0.3.

        Returns:
        numpy.ndarray: The frame with the skeleton drawn on it.
        """
        if keypoints is None:
            return frame
        for keypoint in keypoints:
            x, y, score = keypoint[0], keypoint[1], keypoint[2]
            if score > threshold:
                cv2.circle(frame, (int(y * frame.shape[1]), int(x * frame.shape[0])), 5, (0, 255, 0), -1)

        # Draw center of gravity
        if centerOfGravity != (None, None):
            cgX, cgY = centerOfGravity
            cgX = int(cgX * frame.shape[0])
            cgY = int(cgY * frame.shape[1])
            cv2.circle(frame, (cgY, cgX), 5, (0, 0, 255), -1)

        # Draw lines for arms
        leftShoulder = keypoints[5]
        leftElbow = keypoints[7]
        leftWrist = keypoints[9]

        rightShoulder = keypoints[6]
        rightElbow = keypoints[8]
        rightWrist = keypoints[10]

        if all(keypoint[2] > threshold for keypoint in [leftShoulder, leftElbow]):
            cv2.line(frame, (int(leftShoulder[1] * frame.shape[1]), int(leftShoulder[0] * frame.shape[0])), (int(leftElbow[1] * frame.shape[1]), int(leftElbow[0] * frame.shape[0])), (0, 255, 0), 2)
        if all(keypoint[2] > threshold for keypoint in [leftElbow, leftWrist]):       
            cv2.line(frame, (int(leftElbow[1] * frame.shape[1]), int(leftElbow[0] * frame.shape[0])), (int(leftWrist[1] * frame.shape[1]), int(leftWrist[0] * frame.shape[0])), (0, 255, 0), 2)

        if all(keypoint[2] > threshold for keypoint in [rightShoulder, rightElbow]):
            cv2.line(frame, (int(rightShoulder[1] * frame.shape[1]), int(rightShoulder[0] * frame.shape[0])), (int(rightElbow[1] * frame.shape[1]), int(rightElbow[0] * frame.shape[0])), (0, 255, 0), 2)
        if all(keypoint[2] > threshold for keypoint in [rightElbow, rightWrist]):       
            cv2.line(frame, (int(rightElbow[1] * frame.shape[1]), int(rightElbow[0] * frame.shape[0])), (int(rightWrist[1] * frame.shape[1]), int(rightWrist[0] * frame.shape[0])), (0, 255, 0), 2)
        
        return frame

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase, QFont

    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks')
    from DataCapture.CameraSender import CameraSender
    from DataCapture.PoseEstimator import PoseEstimatorThread
    from error import CameraNotFoundError, FontError


    app = QApplication(sys.argv)
    
    if (QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf") == -1):
        raise FontError("Could not load font")

    if (QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf") == -1):
        raise FontError("Could not load font")

    window = QMainWindow()
    window.setWindowTitle("Climbing Rocks")
    window.setFixedSize(1280, 800)
    window.setFont(QFont("DM Sans"))
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.cameraSender = CameraSender(window)
    window.cameraSender.start()

    window.poseEstimatorModelLoaded = False
    window.poseEstimator = PoseEstimatorThread(window)
    window.poseEstimator.modelLoaded.connect(onPoseEstimatorModelLoaded)

    @pyqtSlot()
    def onPoseEstimatorModelLoaded():
        window.poseEstimatorModelLoaded = True
        print("Model loaded from Main Window")

    window.poseEstimator.start()

    window.climbingScreen = ClimbingScreen(window)
    window.setCentralWidget(window.climbingScreen)

    window.show()
    sys.exit(app.exec())
else:
    from DataCapture.CameraSender import CameraSender
    from DataCapture.PoseEstimator import PoseEstimatorThread


