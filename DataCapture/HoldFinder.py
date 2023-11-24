import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import tensorflow as tf
from PIL import Image
from object_detection.utils import label_map_util, visualization_utils as viz_utils

# Define the QThread-based class
class InferenceThread(QThread):
    model_loaded = pyqtSignal()

    def __init__(self, parent=None):
        super(InferenceThread, self).__init__(parent)
        self.model_path = "models/HoldModel/saved_model"
        self.detect_fn = None
        self.load_model()

    def load_model(self):
        print('Loading model...', end='')
        self.detect_fn = tf.saved_model.load(self.model_path)
        print('Done!')
        self.model_loaded.emit()

    def run_inference(self, image_path):
        print('Running inference for {}... '.format(image_path), end='')
        image_np = self.load_image_into_numpy_array(image_path)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = self.detect_fn(input_tensor)
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
        print('Done!')
        return detections

    def load_image_into_numpy_array(self, path):
        return np.array(Image.open(path))

    def run(self):
        # This method is called when you start the thread, but we don't need it for this example
        pass


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.inference_thread = InferenceThread()

        # Connect the signals
        self.inference_thread.model_loaded.connect(self.on_model_loaded)

        # Start the thread
        self.inference_thread.start()

        # Set up the GUI
        self.image_paths = ['models/HoldModel/test/wall0.jpg', 'models/HoldModel/test/wall1.jpg', 'models/HoldModel/test/wall2.jpg',
                            'models/HoldModel/test/wall3.jpg', 'models/HoldModel/test/wall5.jpg', 'models/HoldModel/test/wall6.jpg',
                            'models/HoldModel/test/wall7.jpg']
        self.current_image_index = 0

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_label)

        self.load_next_image()

        print("HoldFinder initialized.")

    def load_next_image(self):
        if self.inference_thread.detect_fn is not None:
            if self.current_image_index < len(self.image_paths):
                image_path = self.image_paths[self.current_image_index]
                self.current_image_index += 1
                detections = self.inference_thread.run_inference(image_path)
                self.show_image(image_path, detections)
            else:
                print("All images processed.")
        else:
            print("Model not loaded yet. Please wait.")

    def show_image(self, image_path, detections):
        image_np_with_detections = cv2.imread(image_path)
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            label_map_util.create_category_index_from_labelmap(
                'models/HoldModel/hold-detection_label_map.pbtxt', use_display_name=True),
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.30,
            agnostic_mode=False)

        # Convert image to QImage
        height, width, channel = image_np_with_detections.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_np_with_detections.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap(q_image)

        # Display the image
        self.image_label.setPixmap(pixmap)

    def on_model_loaded(self):
        print("Model loaded. You can now process images.")
        # If you want to load an image automatically after the model is loaded, uncomment the line below.
        # self.load_next_image()


if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
