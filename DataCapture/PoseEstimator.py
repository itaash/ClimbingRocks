import cv2, sys, os, logging, ast, csv
import numpy as np
from tensorflow.lite.python import interpreter as interpreterWrapper
from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot, QRect, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QStackedLayout
import math
import time

from UI.ClimbingScreen import ClimbingScreen

FRAME_SKIP = 4

class PoseEstimatorThread(QThread):
    modelLoaded = pyqtSignal()
    inferenceSignal = pyqtSignal(np.ndarray, tuple, tuple)
    climbInProgressSignal = pyqtSignal(bool)
    climbFinishedSignal = pyqtSignal(bool)
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
        self.holdCoordinatePath = "data/holdCoordinates.csv"
        self.interpreter = None
        self.inputDetails = None
        self.outputDetails = None
        self.keypointsData = []
        self.parent = parent
        self.climbInProgress = False # True if the climber has been in a valid position for at least 1 second
        self.climbBegun = False #True if the climber is in a valid position, but has not been in a valid position for at least 1 second
        self.climbSuccessful = False # True if both hands have been on or above the highest hold
        self.holdCoordinates = []
        self.holdCoordinatesLoaded = False

        # Instantiate CameraSender
        self.cameraSender = parent.cameraSender
        self.cameraSender.cameraConnectSignal.connect(self.oncameraConnectSignal)
        self.cameraSender.frameSignal.connect(self.onFrameSignal)
        try:
            self.parent.holdFindingScreen.holdsFoundSignal.connect(self.getHoldsCoordinates)
        except:
            pass

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
        self.keypoints = self.interpreter.get_tensor(int(self.outputDetails[0]['index']))[0][0]

        return
    
    @pyqtSlot()
    def getHoldsCoordinates(self):
        """
        gets the coordinates of the holds from the csv file
        """
        with open(self.holdCoordinatePath, 'r') as f:
            holdCoordinatesListOfStrings = f.read().splitlines()
            self.holdCoordinates = [ast.literal_eval(item) for item in holdCoordinatesListOfStrings]
            print("Hold coordinates from PoseEstimationThread: ", self.holdCoordinates)
        self.holdCoordinatesLoaded = True
        return

    def recordClimb(self, frame):
        """
        if all 4 limbs are above the lowest hold, the climber is in a valid position. Start recording the climb.
        Start 1 second timer to check if the climber is still in a valid position. If not, the climb is not in progress,
        and so it cannot be finished. If the climber is in a valid position after a second, the climb is in progress,
        and now if the climber is not in a valid position, the climb is finished. The timer is reset, and the recorded climb is discarded.

        We also check if both hands have been on or above the highest hold. If yes, the climbFinished signal is emitted, and the climb is no longer in progress.

        Args:
        frame (numpy.ndarray): The frame to run inference on.
        """
        # since hold coordinates are sorted by distance from the top of the frame, the lowest hold is the last one in the list
        lowestHoldY = self.holdCoordinates[-1][4]
        highestHoldY = self.holdCoordinates[0][4]

        # Extract the relevant keypoints for both hands and feet
        leftHand = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_wrist']][0:1] * frame.shape[0]
        rightHand = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_wrist']]
        leftFoot = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_ankle']]
        rightFoot = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_ankle']]

        # Check if all limbs are above the lowest hold
        if self.isClimberInValidPosition():            # Climber is in a valid position, start recording the climb
            if not self.climbBegun and not self.climbInProgress: # Climber was not in a valid position before, and is not in a valid position now
                # Start a timer to check if the climber is still in a valid position after 1 second
                self.climbBegun = True
                self.startTime = time.time() * 1000 # in milliseconds
                timer = QTimer()
                timer.singleShot(1000, self.validateClimb)

            # Store keypoints and timestamp
            centerOfGravity = self.calculateCenterOfGravity()
            leftArmAngle, rightArmAngle = self.calculateArmAngles()

            timestamp = int((time.time() * 1000) - self.startTime)

            frameRow = [timestamp, centerOfGravity[0], centerOfGravity[1], leftArmAngle, rightArmAngle]
            for usefulKeypoint in PoseEstimatorThread.usefulKeypointDict.values():
                frameRow.extend([round(self.keypoints[usefulKeypoint][0], 5), 
                                 round(self.keypoints[usefulKeypoint][1], 5)])
            self.keypointsData.append(frameRow)
            # Check if both hands have been on or above the highest hold
            if leftHand[0] < highestHoldY and rightHand[0] < highestHoldY:
                self.climbSuccessful = True


        elif not self.climbInProgress: # Climber was in a valid position before, but is not in a valid position now. The climb is finished - successful or not.
            self.climbInProgress = False
            self.climbInProgressSignal.emit(False)
            # save keypoints data to a csv file
            self.saveKeypointsData()
            if self.climbSuccessful:
                self.climbFinishedSignal.emit(True)
                print("Climb successful!")
            else:
                self.climbFinishedSignal.emit(False)
                print("Climb completed, but not successful.")


    def validateClimb(self):
        """
        Check if the climber is still in a valid position after 1 second.
        If yes, the climb is in progress. If not, the climb is reset.
        """
        self.climbBegun = False
        if self.isClimberInValidPosition():
            self.climbInProgress = True
            self.climbInProgressSignal.emit(True)
            print("Climb in progress!")
        else:
            self.climbInProgress = False
            self.climbInProgressSignal.emit(False)
            self.keypointsData = []
            print("Climb reset.")
        
    def isClimberInValidPosition(self):
        """
        Check if the climber is in a valid position.
        Returns:
        bool: True if the climber is in a valid position, False otherwise.
        """
        # Extract the relevant keypoints for both hands and feet
        leftHand = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_wrist']][0:2]
        rightHand = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_wrist']][0:2]
        leftFoot = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_ankle']][0:2]
        rightFoot = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_ankle']][0:2]

        # get shape of frame to convert from normalized coordinates to pixel coordinates
        frameShape = self.inputDetails[0]['shape'][1:3]
        print("frameShape: ", frameShape)

        # change from normalized coordinates to pixel coordinates

        # since hold coordinates are sorted by distance from the top of the frame, the lowest hold is the last one in the list
        lowestHoldY = self.holdCoordinates[-1][4]

        print("leftHand: ", leftHand)
        print("rightHand: ", rightHand)
        print("leftFoot: ", leftFoot)
        print("rightFoot: ", rightFoot)
        print("lowestHoldY: ", lowestHoldY)

        # Check if all limbs are above the lowest hold
        return leftHand[0] < lowestHoldY and rightHand[0] < lowestHoldY and leftFoot[0] < lowestHoldY and rightFoot[0] < lowestHoldY

    def completeClimbDueToTimeout(self):
        """
        Called when the climb has not been completed within the specified timeout.
        Completes the climb as unsuccessful.
        """
        self.climbInProgress = False
        self.climbInProgressSignal.emit(False)
        # Save keypoints data to a CSV file
        self.saveKeypointsData()
        self.climbFinishedSignal.emit(False)  # Mark the climb as unsuccessful
        print("Climb completed due to timeout, but not successful.")
    
    def saveKeypointsData(self):
        """
        Save keypoints data to a CSV file.
        """
        if self.keypointsData:
            filename = f"keypoints_data_{time.strftime('%Y%m%d%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Timestamp', 'Keypoints'])
                for timestamp, keypoints in self.keypointsData:
                    csvwriter.writerow([timestamp, keypoints])
            print(f"Keypoints data saved to {filename}")
            self.keypointsData = []
        

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
        # if hold coordinates have not been loaded, do not record the climb
        if not self.holdCoordinatesLoaded:
            return
        
        self.frameCounter += 1
        if self.frameCounter % FRAME_SKIP == 0:
            self.frameCounter = 0
            frame = self.cameraSender.getFrame()
            if (frame is not None) and self.poseEstimatorModelLoaded:
                inputFrame = self.preprocessFrame(frame)
                self.runInference(inputFrame)
                centerOfGravity = self.calculateCenterOfGravity()
                armAngles = self.calculateArmAngles()
                self.inferenceSignal.emit(self.keypoints, centerOfGravity, armAngles)
                self.recordClimb(frame)



    def calculateArmAngles(self, threshold=0.3):
        """
        Calculate the elbow angle of each arm. The angle is 0 when the hand is touching the shoulder from above.

        Args:
        # keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
        threshold (float): Minimum confidence score for a keypoint to be considered.

        Returns:
        tuple: The angle of each arm (e.g., (leftArmAngle, rightArmAngle)). If a keypoint is not visible, the angle is None.
        """
        
        leftShoulder = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_shoulder']]
        leftElbow = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_elbow']]
        leftWrist = self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_wrist']]

        rightShoulder = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_shoulder']]
        rightElbow = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_elbow']]
        rightWrist = self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_wrist']]

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


    def calculateCenterOfGravity(self, threshold=0.3):
        """
        Calculate the center of gravity of the body.

        Args:
        keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
        threshold (float): Minimum confidence score for a keypoint to be considered.

        Returns:
        tuple: The position of the center of gravity (e.g., (x, y)). If no keypoints are above the threshold, returns (None, None).
        """
        totalX, totalY, points = 0, 0, 0

        cgPoints = {"leftShoulder": self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_shoulder']], 
                    "rightShoulder": self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_shoulder']], 
                    "leftHip": self.keypoints[PoseEstimatorThread.usefulKeypointDict['left_hip']], 
                    "rightHip": self.keypoints[PoseEstimatorThread.usefulKeypointDict['right_hip']]}  

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
