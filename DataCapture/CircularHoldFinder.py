import cv2, time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
# import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util, visualization_utils as viz_utils

class HoldFindingThread(QThread):
    holdFindingModelLoaded = pyqtSignal()

    def __init__(self, parent=None):
        super(HoldFindingThread, self).__init__(parent)
        # self.modelPath = "models/HoldModel/saved_model"
        self.detectFn = None
        print("Inference thread created.")

    def loadModel(self):
        """
        Loads the model from the model path.
        """
        print('Circle finding model was already loaded lol - its just cv2')
        self.holdFindingModelLoaded.emit()

    def runInference(self, frame):
        """
        Runs inference on the given frame.
        
        Args:
            frame: The frame to run inference on.
        """
        # Convert image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                            param1=125, param2=19, minRadius=8, maxRadius=25)
        numDetections = circles.shape[1] if circles is not None else 0  # Number of circles detected
        print('HoldFinder done!')
        return circles
        

    def loadImageIntoNumpyArray(self, path):
        """
        heper function to load an image into a numpy array 
        """
        return np.array(Image.open(path))

    def run(self):
        print('Loading cicle finding model...', end='')

        self.loadModel()

    def reset(self):
        """
        Resets all the variables to their initial state. Keeps the model loaded to save time on the next run.
        
        """

    def getImageWithHoldsVolumes(self, frame, circles, threshold=0.3, left=0.25, right=0.75):
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")

        # Draw detected circles
        for (x, y, r) in circles:
            if x > left * frame.shape[1] and x < right * frame.shape[1]:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)

        return frame
        
        


class MainWindow(QWidget):
    """
    Skeleton Mainwindow class to test the HoldFinder.
    """
    def __init__(self):
        super(MainWindow, self).__init__()

        self.holdFindingThread = HoldFindingThread()

        # Connect the signals
        self.holdFindingThread.holdFindingModelLoaded.connect(self.onModelLoaded)

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

    def showImage(self, imagePath, detections, threshold=0.3):
        imageNpWithDetections = cv2.imread(imagePath)
        viz_utils.visualize_boxes_and_labels_on_image_array(
            imageNpWithDetections,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            label_map_util.create_categories_from_labelmap(
                'models/HoldModel/hold-detection_label_map.pbtxt', use_display_name=True),
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=threshold,
            agnostic_mode=False)

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

        # Wait for any key press to load the next image
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.loadNextImage()

    def loadImageIntoNumpyArray(self, path):
        return np.array(Image.open(path))


    @pyqtSlot()
    def onModelLoaded(self):
        print("Model loaded. You can now process images.")
        # Load an image automatically after the model is loaded
        self.loadNextImage()


if __name__ == '__main__':
    import sys
    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)\IGEN 430/ClimbingRocks')   

    from error import HoldModelError

    app = QApplication([])
    mainWindow = MainWindow()
    app.exec_()
else:
    from error import HoldModelError
