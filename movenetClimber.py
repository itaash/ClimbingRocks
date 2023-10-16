import cv2
import numpy as np
from tensorflow.lite.python import interpreter as interpreterWrapper
import math
import time
import argparse
import csv

# Load the MoveNet model
interpreter = interpreterWrapper.Interpreter(model_path="models/movenet_lightning_f16.tflite")
interpreter.allocate_tensors()
inputDetails = interpreter.get_input_details()
outputDetails = interpreter.get_output_details()

# Argument parsing
argParser = argparse.ArgumentParser(description="Real-time or video-based MoveNet pose analysis.")
argParser.add_argument("--input", type=str, choices=['i', 'v', 'r'], default='r',
                       help="i: image, v: video, r: real-time (default)")
argParser.add_argument("--source", type=str, default=0,
                       help="Path to video file or image (e.g., 'video.mp4' or 'image.jpg')")
argParser.add_argument("--frame_skip", type=int, default=4,
                       help="Number of frames to skip between pose analysis (default: 4)")
argParser.add_argument("--output", type=str, default="data/output.csv",
                       help="Path to the output CSV file (default: 'data/output.csv')")

args = argParser.parse_args()

csvHeader = ['Timestamp(ms)', 'Center of Gravity X', 'Center of Gravity Y', 'Left Arm Angle', 'Right Arm Angle']

keypointDict = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
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

for keypointName in usefulKeypointDict.keys():
    csvHeader.extend([f'{keypointName}_X', f'{keypointName}_Y', f'{keypointName}_Score'])

def saveToCsv(filename, data, header):
    with open(filename, mode='w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(header)
        writer.writerows(data)

def preprocessFrame(frame):
    inputFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    inputFrame = cv2.resize(inputFrame, (192, 192))
    inputFrame = np.expand_dims(inputFrame, axis=0)
    inputFrame = (inputFrame.astype(np.uint8))
    inputFrame = ((inputFrame / 255.0) * 255).astype(np.uint8)
    return inputFrame

def drawSkeleton(frame, keypoints, threshold=0.2):
    for keypoint in keypoints:
        x, y, score = keypoint[0], keypoint[1], keypoint[2]
        if score > threshold:
            cv2.circle(frame, (int(y * frame.shape[1]), int(x * frame.shape[0])), 5, (0, 255, 0), -1)

def calculateArmAngles(keypoints, threshold=0.2):
    # Extract relevant keypoints for both arms
    
    leftShoulder = keypoints[5]
    leftElbow = keypoints[7]
    leftWrist = keypoints[9]

    rightShoulder = keypoints[6]
    rightElbow = keypoints[8]
    rightWrist = keypoints[10]

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


def calculateCenterOfGravity(keypoints, threshold=0.2):
    """
    Calculate the center of gravity of the body.

    Args:
    keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
    threshold (float): Minimum confidence score for a keypoint to be considered.

    Returns:
    tuple: The position of the center of gravity (e.g., (x, y)). If no keypoints are above the threshold, returns (None, None).
    """
    totalX, totalY, points = 0, 0, 0

    cgPoints = {"leftShoulder": keypoints[5], "rightShoulder": keypoints[6], "leftHip": keypoints[11], "rightHip": keypoints[12]}  

    for keypoint in cgPoints.values():
        x, y, score = keypoint[0], keypoint[1], keypoint[2]

        if score > threshold:
            totalX += x
            totalY += y
            points += 1

    if points > 0:
        cgX = round (totalX / points, 4)
        cgY = round (totalY / points, 4)
        return (cgX, cgY)
    else:
        return (None, None)
    
def getClosestHoldFromLimb(limbPosition, holdPositions):
    """
    Find the closest hold from a given limb position.

    Args:
    limbPosition (tuple): The position of a limb (e.g., (x, y)).
    holdPositions (list): List of hold positions.

    Returns:
    tuple: The position of the closest hold (e.g., (x, y)).
    """
    minDistance = float('inf')
    closestHold = None

    for holdPosition in holdPositions:
        distance = np.linalg.norm(np.array(limbPosition) - np.array(holdPosition))
        if distance < minDistance:
            minDistance = distance
            closestHold = holdPosition

    return closestHold

def getClosestLimbFromHold(holdPosition, keypoints):
    """
    Find the closest limb from a given hold position.

    Args:
    holdPosition (tuple): The position of a hold (e.g., (x, y)).
    limbPositions (list): List of limb positions.

    Returns:
    tuple: The position of the closest limb (e.g., (x, y)).
    """

    limbPositions = {"leftHand": keypoints[9], "rightHand": keypoints[10], "leftFoot": keypoints[15], "rightFoot": keypoints[16]}

    minDistance = 9999
    closestLimb = None

    for limbPosition in limbPositions.values:
        distance = np.linalg.norm(np.array(holdPosition) - np.array(limbPosition))
        if distance < minDistance:
            minDistance = distance
            closestLimb = limbPosition

    return closestLimb

def getDistanceBetweenLimbHold(limbPosition, holdPosition):
    """
    Calculate the distance between a given limb and hold.

    Args:
    limbPosition (tuple): The position of a limb (e.g., (x, y)).
    holdPosition (tuple): The position of a hold (e.g., (x, y)).

    Returns:
    float: The distance between the limb and hold.
    """
    return np.linalg.norm(np.array(limbPosition) - np.array(holdPosition))
    

def main():

    cap = cv2.VideoCapture(args.source)

    frameCounter = 0
    frameData = []
    startTime = time.time() * 1000 # Convert to milliseconds


    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frameCounter += 1

        if frameCounter % (args.frame_skip + 1) == 0:

            frameCounter = 0

            inputFrame = preprocessFrame(frame)
            interpreter.set_tensor(int(inputDetails[0]['index']), inputFrame)
            interpreter.invoke()
            keypoints = interpreter.get_tensor(int(outputDetails[0]['index']))[0][0]
            
            centerOfGravity = calculateCenterOfGravity(keypoints)
            leftArmAngle, rightArmAngle = calculateArmAngles(keypoints)

            timestamp = int((time.time() * 1000) - startTime)

            frameRow = [timestamp, centerOfGravity[0], centerOfGravity[1], leftArmAngle, rightArmAngle]
            for usefulKeypoint in usefulKeypointDict.values():
                frameRow.extend([round(keypoints[usefulKeypoint][0], 4), 
                                 round(keypoints[usefulKeypoint][1], 4), 
                                 round(keypoints[usefulKeypoint][2], 4)])q
            frameData.append(frameRow)

            if centerOfGravity:
                cgX, cgY = centerOfGravity
                cgX = int(cgX * frame.shape[0])
                cgY = int(cgY * frame.shape[1])
                cv2.circle(frame, (cgY, cgX), 5, (0, 0, 255), -1)
                print(f"Center of gravity: ({cgX}, {cgY})")

            print("Arm angles:\nLeft arm angle: " + str(leftArmAngle) + "\nRight arm angle: " + str(rightArmAngle))

        try: 
            drawSkeleton(frame, keypoints)
        except:
            pass
        cv2.imshow('MoveNet Skeleton', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    saveToCsv(args.output, frameData, csvHeader)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    main()
