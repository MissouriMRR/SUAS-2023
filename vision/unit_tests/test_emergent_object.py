"""
Testing vision.pipeline.emergent_pipeline.py
"""

import unittest
import cv2
import numpy as np
import os.path

from vision.common.bounding_box import BoundingBox, ObjectType, Vertices, tlwh_to_vertices
from vision.common.constants import Image
from typing import Any, Callable, TypedDict


import vision.emergent_object.emergent_object as emg_obj


class TestCreateEmergentModel(unittest.TestCase):
    def test_load(self) -> None:
        """
        Asserts that the model file exists
        """
        
        self.assertTrue(os.path.isfile(emg_obj.EMG_MODEL_PATH), "model file is missing")
        
        model: Callable[[Image], Any] = emg_obj.create_emergent_model()
        
        self.assertIsInstance(model, Callable, "model is not a Callable")


class TestDetectEmergentObject(unittest.TestCase):
    def test_detect(self) -> None:
        """
        Tests that the output matches the expected output
        """
        
        test_img_path = "smaller.jpg"
        img = cv2.imread(test_img_path)
        
        self.assertTrue(os.path.isfile(test_img_path), "image file is missing")
        
        model: Callable[[Image], Any] = emg_obj.create_emergent_model()
        
        detected_humanoids: list[BoundingBox] = emg_obj.detect_emergent_object(img, model)
        
        self.assertEquals(len(detected_humanoids), 1, "incorrect number of detections")
        
        
        for detection in detected_humanoids:
            self.assertIsInstance(detection.obj_type)
            self.assertIsInstance(detection.vertices)
            self.assertIsInstance(detection.obj_type)
            self.assertIsInstance(detection.attributes)
        
        
        detection = detected_humanoids[0]
        
        # Test detection position compared to expected location
        self.assertGreater(detection.get_x_avg(), 338)
        self.assertLess(detection.get_x_avg(), 397)
        
        self.assertGreater(detection.get_y_avg(), 195)
        self.assertLess(detection.get_y_avg(), 241)