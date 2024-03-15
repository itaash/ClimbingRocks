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
        self.currentForceList = [] # List to store the force values received from the Arduino
        self.parent = parent

        self.connectToArduino("COMx", 9600)

        self.recording = False

        parent.poseEstimatorThread.climbBegunSignal.connect(self.startRecording)
        parent.poseEstimatorThread.climbFinishedSignal.connect(self.stopRecording)

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
            raise e

    @pyqtSlot(bool)
    def startRecording(self, climbStarted):
        """
        Begins receiving force data from the Arduino.
        """

        self.startTime = time.time() * 1000 # Start time in milliseconds
        if self.connected:
            if climbStarted:
                self.recording = True
                self.recordForce()
            else: # If the climb has not started, clear the force list
                self.forceList.clear()
                self.recording = False
                
    @pyqtSlot(bool)
    def stopRecording(self, climbSuccessfull):
        """
        Stops receiving force data from the Arduino. Saves the force list to a file.
        """
        self.recording = False

        if self.connected:
            # self.ser.close()
            # self.connected = False
        # Save the force list to a file with timestamps
            pass
        with open("forceData.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["Time"] + [f"Force_hold_{i}" for i in range(0, self.numHolds)])
            writer.writerows(self.forceList)    

    
    def recordForce(self):
        """
        Receives force data from the Arduino and appends it to the force list.
        """
        while self.connected and self.recording:
            try:
                force = self.ser.readline().split( )
            except Exception as e:
                print("Error receiving force: ", e)
                self.connected = False
                self.connectedToArduino.emit(self.connected)
                break

            self.currentForceList.append(force)
            if len(self.currentForceList) == self.numHolds:
                # Append the current force list to the force list with a timestamp
                self.forceList.append([time.time() * 1000 - self.startTime] + self.currentForceList)
                self.currentForceList = []