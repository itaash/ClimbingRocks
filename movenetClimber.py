import cv2
import numpy as np
from tensorflow.lite.python import interpreter as interpreterWrapper
import math
import time
import argparse
import csv
import statistics

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

    # Draw lines for arms
    leftShoulder = keypoints[5]
    leftElbow = keypoints[7]
    leftWrist = keypoints[9]

    rightShoulder = keypoints[6]
    rightElbow = keypoints[8]
    rightWrist = keypoints[10]

    if all(keypoint[2] > threshold for keypoint in [leftShoulder, leftElbow, leftWrist]):
        cv2.line(frame, (int(leftShoulder[1] * frame.shape[1]), int(leftShoulder[0] * frame.shape[0])), (int(leftElbow[1] * frame.shape[1]), int(leftElbow[0] * frame.shape[0])), (0, 255, 0), 2)

    if all(keypoint[2] > threshold for keypoint in [rightShoulder, rightElbow, rightWrist]):
        cv2.line(frame, (int(rightShoulder[1] * frame.shape[1]), int(rightShoulder[0] * frame.shape[0])), (int(rightElbow[1] * frame.shape[1]), int(rightElbow[0] * frame.shape[0])), (0, 255, 0), 2)

def calculateArmAngles(keypoints, threshold=0.2):
    """
    Calculate the elbow angle of each arm. The angle is 0 when the hand is touching the shoulder from above.

    Args:
    keypoints (list): List of keypoints (e.g., [[x, y, score], ...]), typically from the MoveNet model.
    threshold (float): Minimum confidence score for a keypoint to be considered.

    Returns:
    tuple: The angle of each arm (e.g., (leftArmAngle, rightArmAngle)). If a keypoint is not visible, the angle is None.
    """
    
    leftShoulder = keypoints[keypointDict['left_shoulder']]
    leftElbow = keypoints[keypointDict['left_elbow']]
    leftWrist = keypoints[keypointDict['left_wrist']]

    rightShoulder = keypoints[keypointDict['right_shoulder']]
    rightElbow = keypoints[keypointDict['right_elbow']]
    rightWrist = keypoints[keypointDict['right_wrist']]

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

def calculateHandShoulderDistances(keypoints, threshold=0.2):
    """
    Calculate the distances between hand keypoints (wrists) and the corresponding shoulders.

    Args:
    keypoints (list): List of keypoints (e.g., [[x, y, score], ...]) from the MoveNet model.
    threshold (float): Minimum confidence score for a keypoint to be considered.

    Returns:
    tuple: The distances between left hand (wrist) and left shoulder, and between right hand (wrist) and right shoulder.
    If a keypoint is not visible, the distance is None.
    """
    leftShoulder = keypoints[keypointDict['left_shoulder']]
    leftHand = keypoints[keypointDict['left_wrist']]
    
    rightShoulder = keypoints[keypointDict['right_shoulder']]
    rightHand = keypoints[keypointDict['right_wrist']]

    # Initialize distances as None
    leftHandShoulderDistance = None
    rightHandShoulderDistance = None

    # Check visibility before calculating distances
    if all(part[2] > threshold for part in [leftShoulder, leftHand]):
        leftHandShoulderDistance = math.sqrt((leftHand[0] - leftShoulder[0]) ** 2 + (leftHand[1] - leftShoulder[1]) ** 2)
        leftHandShoulderDistance = round(leftHandShoulderDistance, 2)

    if all(part[2] > threshold for part in [rightShoulder, rightHand]):
        rightHandShoulderDistance = math.sqrt((rightHand[0] - rightShoulder[0]) ** 2 + (rightHand[1] - rightShoulder[1]) ** 2)
        rightHandShoulderDistance = round(rightHandShoulderDistance, 2)

    return leftHandShoulderDistance, rightHandShoulderDistance

def rolling_average_stddev(center_of_gravity_values, window_size=10):
    """
    Calculate the rolling average of the standard deviation for a list of center of gravity inputs.

    Args:
    center_of_gravity (list): List of center of gravity points (e.g., [(x1, y1), (x2, y2), ...]).
    window_size (int): Size of the rolling window.

    Returns:
    list: List of rolling standard deviation averages for the center of gravity points.
    """

    rolling_stddev_avg = []
    window = []
    
    for value in center_of_gravity_values:
        window.append(value)
        if len(window) > window_size:
            window.pop(0)

        if len(window) == window_size:
            x_values, y_values = zip(*window)
            x_std_dev = statistics.stdev(x_values)
            y_std_dev = statistics.stdev(y_values)
            std_dev_avg = (x_std_dev + y_std_dev) / 2
            rolling_stddev_avg.append(std_dev_avg)

    return rolling_stddev_avg 

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

    cgPoints = {"leftShoulder": keypoints[keypointDict['left_shoulder']], 
                "rightShoulder": keypoints[keypointDict['right_shoulder']], 
                "leftHip": keypoints[keypointDict['left_hip']], 
                "rightHip": keypoints[keypointDict['right_hip']]}  

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

    limbPositions = {"leftHand": keypoints[keypointDict['left_wrist']], 
                     "rightHand": keypoints[keypointDict['right_wrist']], 
                     "leftFoot": keypoints[keypointDict['left_ankle']], 
                     "rightFoot": keypoints[keypointDict['right_ankle']]}

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
    limbPosition (tuple): The position of a limb (e.g., (x, y))
    holdPosition (tuple): The position of a hold (e.g., (x, y))

    Returns:
    float: The distance between the limb and hold.
    """
    return np.linalg.norm(np.array(limbPosition) - np.array(holdPosition))


def main():

    cap = cv2.VideoCapture(args.source)

    frameCounter = 0
    frameData = []
    startTime = time.time() * 1000 # Convert to milliseconds
    timestamp = 0
    centerOfGravity_values = []  # List to accumulate center of gravity values
    rolling_stddev_values = []  # List to accumulate rolling standard deviation values


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
            centerOfGravity_values.append(centerOfGravity)
            smoothness = rolling_average_stddev(centerOfGravity,5)
            leftArmAngle, rightArmAngle = calculateArmAngles(keypoints)
            leftHandShoulderDistance, rightHandShoulderDistance = calculateHandShoulderDistances(keypoints)

            timestamp = int((time.time() * 1000) - startTime)

            frameRow = [timestamp, centerOfGravity[0], centerOfGravity[1], leftArmAngle, rightArmAngle]
            for usefulKeypoint in usefulKeypointDict.values():
                frameRow.extend([round(keypoints[usefulKeypoint][0], 4), 
                                 round(keypoints[usefulKeypoint][1], 4), 
                                 round(keypoints[usefulKeypoint][2], 4)])
            frameData.append(frameRow)

            if centerOfGravity != (None, None):
                cgX, cgY = centerOfGravity
                cgX = int(cgX * frame.shape[0])
                cgY = int(cgY * frame.shape[1])
                cv2.circle(frame, (cgY, cgX), 5, (0, 0, 255), -1)
                print(f"Center of gravity: ({cgX}, {cgY})")

            print("Arm angles:\nLeft arm angle: " + str(leftArmAngle) + "\nRight arm angle: " + str(rightArmAngle))
            print("Arm to shoulder distance: \nLeft: "+ str(leftHandShoulderDistance)+ "\nRight: "+ str(rightHandShoulderDistance) )
        try: 
            drawSkeleton(frame, keypoints)
        except: 
            pass
        cv2.imshow('MoveNet Skeleton', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if timestamp > 5000:  # 5 seconds in milliseconds
                rolling_stddev = rolling_average_stddev(centerOfGravity_values, window_size=10)
                rolling_stddev_values.extend(rolling_stddev)
                centerOfGravity_values = centerOfGravity_values[-10:]  # Keep the last 10 values
                
                for std_dev in rolling_stddev:
                        print(f"Smoothness score: {std_dev}")

                timestamp = 0
                rolling_stddev_values.clear()

    saveToCsv(args.output, frameData, csvHeader)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    main()
