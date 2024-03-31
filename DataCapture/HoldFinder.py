import cv2, time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util, visualization_utils as viz_utils
import csv

class HoldFindingThread(QThread):
    holdFindingModelLoaded = pyqtSignal()

    def __init__(self, parent=None):
        super(HoldFindingThread, self).__init__(parent)
        self.modelPath = "models/HoldModel/saved_model"
        self.detectFn = None
        print("Inference thread created.")

    def loadModel(self):
        """
        Loads the model from the model path.
        """
        self.detectFn = tf.saved_model.load(self.modelPath)
        print('Hold finding model loaded')
        self.holdFindingModelLoaded.emit()

    def runInference(self, frame):
        """
        Runs inference on the given frame.
        """
        if self.detectFn is not None:
            print('Running HoldFinder... ', end='')
            imageNp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inputTensor = tf.convert_to_tensor(imageNp)
            inputTensor = inputTensor[tf.newaxis, ...]
            detections = self.detectFn(inputTensor)
            numDetections = int(detections.pop('num_detections'))
            detections = {key: value[0, :numDetections].numpy() for key, value in detections.items()}
            detections['num_detections'] = numDetections
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            print('HoldFinder done!')
            return detections
        else:
            print("Model not loaded yet. Please wait.")
            return None

    def loadImageIntoNumpyArray(self, path):
        """
        heper function to load an image into a numpy array 
        """
        return np.array(Image.open(path))

    def run(self):
        print('Loading hold finding model...', end='')

        self.loadModel()

    def reset(self):
        """
        Resets all the variables to their initial state. Keeps the model loaded to save time on the next run.
        
        """

    def getImageWithHoldsVolumes(self, frame, detections, threshold=0.3, left=0, right=1) -> np.ndarray:
        """
        Draw the detected holds and volumes on the frame

        Args:
            frame: The frame to draw the detected holds and volumes on
            detections: The output of the hold finding model
            threshold: The minimum score threshold for a hold to be drawn. Default is 0.3
            left: The left bound of the frame to draw the holds and volumes on. Default is 0
            right: The right bound of the frame to draw the holds and volumes on. Default is 1

        Returns:
            frame: The frame with the detected holds and volumes drawn on it
        """
        viz_utils.visualize_boxes_and_labels_on_image_array(
            frame,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            label_map_util.create_category_index_from_labelmap(
                'models/HoldModel/hold-detection_label_map.pbtxt', use_display_name=True),
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=threshold,
            agnostic_mode=False,
            skip_scores=False)
        
        return frame
    
    def saveDetections(self, detections, maxHolds=20, threshold=0.3):
        """
        Save the locations of the detected holds to a file

        Args:
            detections: The output of the hold finding model
            maxHolds: The maximum number of holds to save
            threshold: The minimum score threshold for a hold to be saved

        """
        if detections is not None:

            filteredDetectionswithHolds = self.filterResultsforHolds(detections, threshold)
            filteredDetectionswithHoldsInCenterHalf = self.filterResultsforCenterHalf(filteredDetectionswithHolds, leftBound=0.25, rightBound=0.75)
            sortedDetections = self.sortDetectionsbyScore(filteredDetectionswithHoldsInCenterHalf)


            # Get the coordinates of the detected holds(class 1), not volumes (class 2)
            boxes = sortedDetections['detection_boxes']
            # Get the scores of the detected holds
            scores = sortedDetections['detection_scores']
            # Get the classes of the detected holds
            classes = sortedDetections['detection_classes']

            # Create a list to store the coordinates of the detected holds
            holdCoordinates = []

            # Create a counter to keep track of the number of holds being saved
            i = 0
            # Iterate through the detected holds
            while i < min(maxHolds, len(boxes)):
                # If the score of the hold is above the threshold
                if classes[i] == 1 and scores[i] > threshold:
                    # Get the coordinates of the hold
                    ymin, xmin, ymax, xmax = boxes[i]
                    # Convert the coordinates from normalized to pixel coordinates
                    ## currently trying to use normalized coordinates for analysis, otherwise would use pixel coordinates
                    left, right, top, bottom = round(xmin, 4), round(xmax, 4), round(ymin, 4), round(ymax, 4)
                    holdCoordinates.append((left, right, top, bottom))
                    i += 1

            
            # Sort the coordinates of the detected holds by their ymax coordinate(column 3) in descending order
            # The hold coordinates are stored as a list of lists, where each sublist contains the xmin, xmax, ymin, and ymax coordinates of a hold
            holdCoordinates = sorted(holdCoordinates, key=lambda x: x[3], reverse=True)

            print(holdCoordinates) # for debugging

            # Save the coordinates of the detected holds to a file
            with open('data/holdCoordinates.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                # Iterate through the coordinates of the detected holds
                print("Saving coordinates of", len(holdCoordinates), "holds")
                header = ["holdNumber", "left", "right", "top", "bottom"]
                writer.writerow(header)
                for i, (left, right, top, bottom) in enumerate(holdCoordinates):
                    # Write the coordinates to the file
                    writer.writerow([i, left, right, top, bottom])

    def filterResultsforHolds(self, detections, threshold=0.3):
        """
        Filter the results of the hold finding model to only include holds, not volumes

        Args:
            detections: The output of the hold finding model
            threshold: The minimum confidence threshold for a detection to be included. Default is 0.3

        Returns:
            filteredResults: The filtered results of the hold finding model that only include holds, not volumes
        """
        scores = np.array(detections['detection_scores'])
        classes = np.array(detections['detection_classes'])
        mask = (scores >= threshold) & (classes == 1)

        filteredResults = {
            'detection_anchor_indices': np.array(detections['detection_anchor_indices'])[mask],
            'detection_boxes': np.array(detections['detection_boxes'])[mask],
            'detection_classes': classes[mask],
            'detection_multiclass_scores': np.array(detections['detection_multiclass_scores'])[mask],
            'detection_scores': scores[mask]
        }

        return filteredResults
        
    def filterResultsforCenterHalf(self, detections, leftBound=0.25, rightBound=0.75):
        """
        Filter the results of the hold finding model to only include holds in the center half of the frame
        
        Args:
            detections: The output of the hold finding model
            leftBound: The left bound of the center chunk of the frame to include. Default is 0.25
            rightBound: The right bound of the center half of the frame to include. Default is 0.75

        Returns:
            filteredResults: The filtered results of the hold finding model that only include holds in the center half of the frame
        """
        print(detections['detection_boxes'], detections['detection_scores'])
        mask = (np.array(detections['detection_boxes'])[:, 1] >= leftBound) & (np.array(detections['detection_boxes'])[:, 1] <= rightBound)

        filteredResults = {
            'detection_anchor_indices': np.array(detections['detection_anchor_indices'])[mask],
            'detection_boxes': np.array(detections['detection_boxes'])[mask],
            'detection_classes': np.array(detections['detection_classes'])[mask],
            'detection_multiclass_scores': np.array(detections['detection_multiclass_scores'])[mask],
            'detection_scores': np.array(detections['detection_scores'])[mask]
        }

        return filteredResults
        
    def sortDetectionsbyScore(self, detections):
        """
        Sort the results of the hold finding model by their score in descending order. The highest scoring detection will be first in the list so that the highest scoring holds are saved based on the maxHolds parameter in saveDetections.

        Args:
            detections: The output of the hold finding model

        Returns:
            sortedResults: The sorted results of the hold finding model
        """

        sortedIndices = np.argsort(detections['detection_scores'])[::-1]

        sortedResults = {
            'detection_anchor_indices': np.array(detections['detection_anchor_indices'])[sortedIndices],
            'detection_boxes': np.array(detections['detection_boxes'])[sortedIndices],
            'detection_classes': np.array(detections['detection_classes'])[sortedIndices],
            'detection_multiclass_scores': np.array(detections['detection_multiclass_scores'])[sortedIndices],
            'detection_scores': np.array(detections['detection_scores'])[sortedIndices]
        }

        return sortedResults


        


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
