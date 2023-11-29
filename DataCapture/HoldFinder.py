import cv2, time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util, visualization_utils as viz_utils

class HoldFindingThread(QThread):
    modelLoaded = pyqtSignal()

    def __init__(self, parent=None):
        super(HoldFindingThread, self).__init__(parent)
        self.modelPath = "models/HoldModel/saved_model"
        self.detectFn = None
        print("Inference thread created.")

    def loadModel(self):
        print('Loading model...', end='')
        self.detectFn = tf.saved_model.load(self.modelPath)
        print('Done!')
        self.modelLoaded.emit()

    def runInference(self, frame):
        if self.detectFn is not None:
            print('Running inference... ', end='')
            imageNp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inputTensor = tf.convert_to_tensor(imageNp)
            inputTensor = inputTensor[tf.newaxis, ...]
            detections = self.detectFn(inputTensor)
            numDetections = int(detections.pop('num_detections'))
            detections = {key: value[0, :numDetections].numpy() for key, value in detections.items()}
            detections['num_detections'] = numDetections
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            print('Done!')
            return detections
        else:
            print("Model not loaded yet. Please wait.")
            return None

    def loadImageIntoNumpyArray(self, path):
        return np.array(Image.open(path))

    def run(self):
        self.loadModel()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.holdFindingThread = HoldFindingThread()

        # Connect the signals
        self.holdFindingThread.modelLoaded.connect(self.onModelLoaded)

        # Start the thread
        self.holdFindingThread.start()

        # Set up the GUI
        self.imagePaths = ['models/HoldModel/test/wall0.jpg', 'models/HoldModel/test/wall1.jpg', 'models/HoldModel/test/wall2.jpg',
                            'models/HoldModel/test/wall3.jpg', 'models/HoldModel/test/wall5.jpg', 'models/HoldModel/test/wall6.jpg',
                            'models/HoldModel/test/wall7.jpg']
        self.currentImageIndex = 0

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.imageLabel)

        print("Main window created.")

    def loadNextImage(self):
        if self.holdFindingThread.detectFn is not None:
            if self.currentImageIndex < len(self.imagePaths):
                imagePath = self.imagePaths[self.currentImageIndex]
                self.currentImageIndex += 1
                imageNp = self.loadImageIntoNumpyArray(imagePath)
                imageNp = cv2.cvtColor(imageNp, cv2.COLOR_BGR2RGB)
                detections = self.holdFindingThread.runInference(imageNp)
                if detections is not None:
                    self.showImage(imagePath, detections)
            else:
                print("All images processed.")
                self.close()
        else:
            print("Model not loaded yet. Please wait.")

    def showImage(self, imagePath, detections):
        imageNpWithDetections = cv2.imread(imagePath)
        viz_utils.visualizeBoxesAndLabelsOnImageArray(
            imageNpWithDetections,
            detections['detectionBoxes'],
            detections['detectionClasses'],
            detections['detectionScores'],
            label_map_util.createCategoryIndexFromLabelmap(
                'models/HoldModel/hold-detection_label_map.pbtxt', useDisplayName=True),
            useNormalizedCoordinates=True,
            maxBoxesToDraw=200,
            minScoreThresh=.30,
            agnosticMode=False)

        # Convert image to QImage
        height, width, channel = imageNpWithDetections.shape
        bytesPerLine = 3 * width
        qImage = QImage(imageNpWithDetections.data, width, height, bytesPerLine, QImage.Format_BGR888)
        pixmap = QPixmap(qImage)

        # Display the image
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.resize(pixmap.width(), pixmap.height())
        self.resize(pixmap.width(), pixmap.height())   

        # show the image by displaying the window
        self.show()

        # Wait for a 4 seconds before loading the next image
        QTimer.singleShot(4000, self.loadNextImage)

    def loadImageIntoNumpyArray(self, path):
        return np.array(Image.open(path))


    @pyqtSlot()
    def onModelLoaded(self):
        print("Model loaded. You can now process images.")
        # Load an image automatically after the model is loaded
        self.loadNextImage()


if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    app.exec_()
