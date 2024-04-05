from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage
import logging
import argparse
import cv2, sys
import time
import threading

from error import CameraNotFoundError


class CameraSender(QThread):
    frameSignal = pyqtSignal()
    cameraConnectSignal = pyqtSignal(bool)

    def __init__(self , parent=None):
        super().__init__(parent=None)
        self.frame = None
        # self.publisher = client
        #try:
            #self.cap = cv2.VideoCapture(1)
        #except:
        self.cap = cv2.VideoCapture(0)
        self.resolution = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.cameraConnected = self.cap.isOpened()
        self.frame = None
        self.frameSemaphore = threading.Semaphore(1)

        if not self.cameraConnected:
            errMsg = "Failed to connect to camera"
            logging.info(errMsg)
            self.cap.release()
            self.cameraConnectSignal.emit(self.cameraConnected)
            raise CameraNotFoundError(errMsg)
        else:
            logging.info("Camera connected.")
            self.cameraConnectSignal.emit(self.cameraConnected)

    def run(self):
        time.sleep(0.3)

        if not self.cameraConnected:
            errMsg = "Failed to connect to camera"
            logging.info(errMsg)
            self.cap.release()
            self.cameraConnectSignal.emit(self.cameraConnected)
            raise CameraNotFoundError(errMsg)
        else:
            logging.info("Camera connected.")
            self.cameraConnectSignal.emit(self.cameraConnected)

        

        while True:
            ret, frame = self.cap.read()
            if not ret:
                # Camera disconnected, emit signal
                self.cameraConnected = False
                self.cameraConnectSignal.emit(self.cameraConnected)
                logging.info("Camera disconnected. Attempting to reconnect...")
                while not self.cameraConnected:
                    self.cap.release()
                    time.sleep(0.5)
                    self.cap.open(0)  # Reconnect the camera
                    self.cameraConnected = self.cap.isOpened()
                logging.info("Camera reconnected.")
                ret, frame = self.cap.read()
                self.cameraConnectSignal.emit(self.cameraConnected)

            # Convert the frame to a JPEG image
            _, buffer = cv2.imencode('.jpg', frame)

            # Store the latest frame
            self.frameSemaphore.acquire()
            # self.frame = buffer.tobytes()
            self.frame = frame
            self.frameSemaphore.release()

            # Emit the frame captured signal to notify the GUI thread
            self.frameSignal.emit()

            # Publish the frame to the MQTT topic
            # self.publisher.client.publish(MQTT_FEED, self.frame)

            time.sleep(0.033)

        self.cap.release()
        # self.publisher.disconnect()

    def getFrame(self):
        self.frameSemaphore.acquire()
        frame = self.frame
        self.frameSemaphore.release()
        return frame