import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
import pathlib
import tensorflow as tf
import cv2

import time
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
import tensorflow as tf
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

from PyQt5.QtCore import QThread
import threading

class ModelLoaderThread(QThread):
    def __init__(self):
        super().__init__()
        self.PATH_TO_SAVED_MODEL = "HoldModel/fine_tuned_model/saved_model"
        self.PATH_TO_LABELS = 'HoldModel/just_hold.v3i.tfrecord/train/hold-detection_label_map.pbtxt'
        self.category_index = None
        self.detect_fn = None

    def run(self):
        self.setup()

    def setup(self):
        self.category_index = label_map_util.create_category_index_from_labelmap(self.PATH_TO_LABELS, use_display_name=True)
        self.detect_fn = tf.saved_model.load(self.PATH_TO_SAVED_MODEL)

class InferenceThread(QThread):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.model_loader_thread = ModelLoaderThread()

        tf.get_logger().setLevel('ERROR')           # Suppress TensorFlow logging (2)

        # Enable GPU dynamic memory allocation
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

    def run(self):
        self.model_loader_thread.start()
        self.model_loader_thread.wait()
        self.run_inference(self.image)

    def run_inference(self, image):
        image_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]

        detections = self.model_loader_thread.detect_fn(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                       for key, value in detections.items()}
        detections['num_detections'] = num_detections
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        image_np_with_detections = image_np.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
              image_np_with_detections,
              detections['detection_boxes'],
              detections['detection_classes'],
              detections['detection_scores'],
              self.model_loader_thread.category_index,
              use_normalized_coordinates=True,
              max_boxes_to_draw=200,
              min_score_thresh=.30,
              agnostic_mode=False)

        cv2.imshow('object detection', cv2.resize(image_np_with_detections, (800, 600)))
        cv2.waitKey(0)
        print('Done')

    def load_image_into_numpy_array(self, path):
        return np.array(Image.open(path))
