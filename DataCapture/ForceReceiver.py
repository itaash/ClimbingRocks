import serial, time, csv
import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class ForceReceivingThread(QThread):
    connectedToArduino = pyqtSignal(bool)

    def __init__(self, numHolds, parent=None):
        super(ForceReceivingThread, self).__init__(parent)
        self.connected = False
        self.forceList = [] # List to store all the force values received from the Arduino over time
        self.numHolds = numHolds # Number of holds on the wall, determines the number of force sensors and the size of the forceList
        self.parent = parent
        self.recording = False

        self.connectToArduino("COM3", 115200)

        self.startRecordingFlag = False # Flag to start recording force data
        self.recording = False # Flag to indicate if force data is being recorded
        self.stopRecordingFlag = False # Flag to stop recording force data

        parent.poseEstimatorThread.climbBegunSignal.connect(self.startRecording)
        parent.poseEstimatorThread.climbFinishedSignal.connect(self.stopRecording)

    def run(self):
        self.recordForce()

    def connectToArduino(self, port, baudrate):
        """
        Connects to the Arduino using the given port and baudrate.
        """
        try:
            self.ser = serial.Serial(port, baudrate)
            # time.sleep(1) # need to wait for the arduino to initialize
            self.connected = True
            self.connectedToArduino.emit(self.connected)
            print("Connected to Arduino")
        except Exception as e:
            print("Error connecting to Arduino: ", e)
            self.connected = False
            self.connectedToArduino.emit(self.connected)
            self.deleteLater()
            raise e
    

    @pyqtSlot(bool)
    def startRecording(self, climbStarted):
        """
        Changes state variables to start recording if climbStarted is true or to discard the recorded values if climbStarted is False
        """
        self.recording = climbStarted
        if not climbStarted:
            # Clear the force list if climb has not started
            self.forceList.clear()
            print("Cleared force data")
        else:
            self.startTime = time.time() * 1000
            print("Started recording force data")
                
    @pyqtSlot(bool)
    def stopRecording(self, climbSuccessfull):
        """
        Stops receiving force data from the Arduino. Saves the force list to a file.
        """
        self.recording = False

        print("Force data recording ended")

        if self.connected:
            # self.ser.close()
            # self.connected = False
            pass  # Placeholder for closing serial connection
        # Save the force list to a file with timestamps
        with open("data/forceData.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["Time"] + [f"hold{i}" for i in range(0, self.numHolds)])
            writer.writerows(self.forceList)
        self.forceList.clear()

    
    def recordForce(self):
        """
        Receives force data from the Arduino.
        Starts recording force data when the climb begins and stops when the climb ends. 
        Clears the force list if the climbBegunSignal is received with a False argument.
        When the climbFinishedSignal is received, saves the force list to a file and clears the force list.

        """
        while True:
            if self.recording and self.connected:
                # Read force data from Arduino
                forceData = self.ser.readline().decode('utf-8')
                # Split force data into individual force values for each hold
                forces = forceData.split(',')
                try:
                    forces = forces[0:len(forces)-1]
                except Exception as e:
                    pass

                if len(forces) == self.numHolds:
                    # Append force values to the force list
                    self.forceList.append([(time.time() * 1000) - self.startTime] + forces)
                    # time.sleep(0.1)
            
            time.sleep(0.1) # Sleep for 100ms if not recording or not connected to the Arduino to avoid busy waiting

        # while self.connected and self.recording:
        #     try:
        #         force = self.ser.readline().split( )
        #     except Exception as e:
        #         print("Error receiving force: ", e)
        #         self.connected = False
        #         self.connectedToArduino.emit(self.connected)
        #         break

        #     self.currentForceList.append(force)
        #     if len(self.currentForceList) == self.numHolds:
        #         # Append the current force list to the force list with a timestamp
        #         self.forceList.append([time.time() * 1000 - self.startTime] + self.currentForceList)
        #         self.currentForceList = []