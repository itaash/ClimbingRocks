import cv2, sys, os, logging
import numpy as np
from tensorflow.lite.python import interpreter as interpreterWrapper
from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QStackedLayout
import math
import time

FRAME_SKIP = 4

class PoseEstimatorThread(QThread):
    modelLoaded = pyqtSignal()
    inferenceSignal = pyqtSignal(np.ndarray, tuple, tuple)
    climbInProgressSignal = pyqtSignal(bool)
    climbFinishedSignal = pyqtSignal()
    usefulKeypointDict = {
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
    }   

    def __init__(self, parent):
        super(PoseEstimatorThread, self).__init__(parent)
        self.modelPath = "models/movenet_lightning_f16.tflite"
        self.interpreter = None
        self.inputDetails = None
        self.outputDetails = None
        self.keypoints = None
        self.parent = parent

        # Instantiate CameraSender
        self.cameraSender = parent.cameraSender
        self.cameraSender.cameraConnectSignal.connect(self.oncameraConnectSignal)
        self.cameraSender.frameSignal.connect(self.onFrameSignal)

        self.poseEstimatorModelLoaded = False

        self.frameCounter = 0

    def run(self):
        # Load MoveNet model
        self.loadModel()

    def runInference(self, frame) -> list:
        """
        Runs inference on the given frame.

        Args:
        frame (numpy.ndarray): The frame to run inference on.

        Returns:
        list: The keypoints detected by the model.
        """
        self.interpreter.set_tensor(int(self.inputDetails[0]['index']), frame)
        self.interpreter.invoke()
        keypoints = self.interpreter.get_tensor(int(self.outputDetails[0]['index']))[0][0]

        return keypoints


    def loadModel(self):
        self.interpreter = interpreterWrapper.Interpreter(model_path=self.modelPath)
        self.interpreter.allocate_tensors()
        self.inputDetails = self.interpreter.get_input_details()
        self.outputDetails = self.interpreter.get_output_details()
        self.modelLoaded.emit()
        self.poseEstimatorModelLoaded = True

    def preprocessFrame(self, frame):
        input_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_frame = cv2.resize(input_frame, self.inputDetails[0]['shape'][1:3])
        input_frame = np.expand_dims(input_frame, axis=0)
        input_frame = input_frame.astype(np.uint8)
        return input_frame

    @pyqtSlot(bool)
    def oncameraConnectSignal(self, connected):
        if not connected:
            logging.info("Camera disconnected. Attempting to reconnect...")

    @pyqtSlot()
    def onFrameSignal(self):
        # if isinstance(self.parent.centralWidget(), ClimbingScreen):
        #     print(self.parent.centralWidget())
        #     return
        self.frameCounter += 1
        if self.frameCounter % FRAME_SKIP == 0:
            frame = self.cameraSender.getFrame()
            self.frameCounter = 0
            if (frame is not None) and self.poseEstimatorModelLoaded:
                inputFrame = self.preprocessFrame(frame)
                keypoints = self.runInference(inputFrame)
                centerOfGravity = self.calculateCenterOfGravity(keypoints)
                armAngles = self.calculateArmAngles(keypoints)
                self.inferenceSignal.emit(keypoints, centerOfGravity, armAngles)



    def calculateArmAngles(self, keypoints, threshold=0.3):
        """
        Calculate the elbow angle of each arm. The angle is 0 when the hand is touching the shoulder from above.

        Args:
        keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
        threshold (float): Minimum confidence score for a keypoint to be considered.

        Returns:
        tuple: The angle of each arm (e.g., (leftArmAngle, rightArmAngle)). If a keypoint is not visible, the angle is None.
        """
        
        leftShoulder = keypoints[PoseEstimatorThread.usefulKeypointDict['left_shoulder']]
        leftElbow = keypoints[PoseEstimatorThread.usefulKeypointDict['left_elbow']]
        leftWrist = keypoints[PoseEstimatorThread.usefulKeypointDict['left_wrist']]

        rightShoulder = keypoints[PoseEstimatorThread.usefulKeypointDict['right_shoulder']]
        rightElbow = keypoints[PoseEstimatorThread.usefulKeypointDict['right_elbow']]
        rightWrist = keypoints[PoseEstimatorThread.usefulKeypointDict['right_wrist']]

        # Calculate angles for both arms
        # leftArmAngle = math.degrees(math.atan2(leftWrist[1] - leftElbow[1], leftWrist[0] - leftElbow[0]) - math.atan2(leftShoulder[1] - leftElbow[1], leftShoulder[0] - leftElbow[0]))
        # rightArmAngle = math.degrees(math.atan2(rightWrist[1] - rightElbow[1], rightWrist[0] - rightElbow[0]) - math.atan2(rightShoulder[1] - rightElbow[1], rightShoulder[0] - rightElbow[0]))

        # Initialize angles as None
        leftArmAngle = None
        rightArmAngle = None

        # Check visibility before calculating angles
        if all(part[2] > threshold for part in [leftShoulder, leftElbow, leftWrist]):
            leftArmAngle = math.degrees(math.atan2(leftWrist[1] - leftElbow[1], leftWrist[0] - leftElbow[0]) - math.atan2(leftShoulder[1] - leftElbow[1], leftShoulder[0] - leftElbow[0]))
            leftArmAngle = abs(round(leftArmAngle, 2))
            

        if all(part[2] > threshold for part in [rightShoulder, rightElbow, rightWrist]):
            rightArmAngle = math.degrees(math.atan2(rightWrist[1] - rightElbow[1], rightWrist[0] - rightElbow[0]) - math.atan2(rightShoulder[1] - rightElbow[1], rightShoulder[0] - rightElbow[0]))
            rightArmAngle = abs(round(rightArmAngle, 2))

        return leftArmAngle, rightArmAngle


    def calculateCenterOfGravity(self, keypoints, threshold=0.3):
        """
        Calculate the center of gravity of the body.

        Args:
        keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
        threshold (float): Minimum confidence score for a keypoint to be considered.

        Returns:
        tuple: The position of the center of gravity (e.g., (x, y)). If no keypoints are above the threshold, returns (None, None).
        """
        totalX, totalY, points = 0, 0, 0

        cgPoints = {"leftShoulder": keypoints[PoseEstimatorThread.usefulKeypointDict['left_shoulder']], 
                    "rightShoulder": keypoints[PoseEstimatorThread.usefulKeypointDict['right_shoulder']], 
                    "leftHip": keypoints[PoseEstimatorThread.usefulKeypointDict['left_hip']], 
                    "rightHip": keypoints[PoseEstimatorThread.usefulKeypointDict['right_hip']]}  

        for keypoint in cgPoints.values():
            x, y, score = keypoint[0], keypoint[1], keypoint[2]

            if score > threshold:
                totalX += x
                totalY += y
                points += 1

        if points > 0:
            cgX = round (totalX / points, 5)
            cgY = round (totalY / points, 5)
            return (cgX, cgY)
        else:
            return (None, None)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Climbing Rocks")
        self.setFixedSize(1280, 800)
        self.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")


        self.cameraSender = CameraSender()
        

        self.poseEstimatorThread = PoseEstimatorThread(self)
        self.poseEstimatorThread.modelLoaded.connect(self.onModelLoaded)
        self.poseEstimatorThread.inferenceSignal.connect(self.onInferenceSignal)
    
        self.cameraSender.start()
        self.poseEstimatorThread.start()

        self.cameraSender.frameSignal.connect(self.onFrameSignal)

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

        self.poseEstimatorModelLoaded = self.poseEstimatorThread.poseEstimatorModelLoaded
        self.keypoints = None
        self.centerOfGravity = None, None
        self.armAngles = None, None  
        print("Main window created.")

    @pyqtSlot()
    def onModelLoaded(self):
        self.poseEstimatorModelLoaded = True
        logging.info("Model loaded!")

    @pyqtSlot()
    def onFrameSignal(self):
        frame = self.cameraSender.getFrame()
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
    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks')

    from CameraSender import CameraSender
    from UI.ClimbingScreen import ClimbingScreen

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
else:
    from DataCapture.CameraSender import CameraSender
    from UI.ClimbingScreen import ClimbingScreen
