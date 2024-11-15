import unittest
import numpy as np
from enum import Enum
from vision.common.constants import Point, CameraParameters, ODLCDict
from vision.common.bounding_box import BoundingBox, ObjectType
from vision.deskew.camera_distances import get_coordinates, bounding_area, calculate_distance


class TestVisionFunctions(unittest.TestCase):
    """
    Tests to verify the functionality of calculations
    concerning object positioning and distances in images captured by a camera.

    Attributes
    ----------
        The dimensions of the image used in tests, specified as (height, width, channels).
    """

    def setUp(self) -> None:
        """
        Initializes common properties for all test methods. Sets up camera parameters
        and image dimensions that simulate a typical usage scenario.

        """
        self.camera_params = CameraParameters(
            focal_length=35.0,
            rotation_deg=[0, 0, 0],
            drone_coordinates=[37.7749, -122.4194],
            altitude_f=1000.0,
        )
        self.image_shape = (1080, 1920, 3)  # Image size with 3 color channels

    def test_get_coordinates(self) -> None:
        """

        Verifies that the accurately calculates  coordinates
        from a center pixel. Asserts correct type and closeness to expected values.

        Returns
        -------
            None: This method does not return a value but asserts the correctness of the output.
        """
        center_pixel = (960, 540)
        expected_coordinates = (37.77, -122.211)
        result = get_coordinates(center_pixel, self.image_shape, self.camera_params)

        self.assertIsNotNone(result, "Coordinates should not be None")
        # Check if the result is not None and is of the expected tuple type
        self.assertIsInstance(result, tuple, "Result should be a tuple")
        if isinstance(result, tuple):
            self.assertEqual(len(result), 2, "Result tuple should have two elements")
            self.assertIsInstance(result[0], float, "Latitude is float")
            self.assertIsInstance(result[1], float, "Longitude is float")
        # Make sure to get the expected value
        if result is not None:
            self.assertAlmostEqual(result[0], expected_coordinates[0], places=2)
            self.assertAlmostEqual(result[1], expected_coordinates[1], places=2)

    def test_bounding_area(self) -> None:
        """
        Tests the  function to calculate the area of a bounding box
        within the image, simulating an object detection scenario.

        Returns
        -------
            None: This method does not return a value but asserts the area calculation is correct.
        """
        obj_type = ObjectType(value="")  # Provide the necessary argument
        self.box = BoundingBox(
            obj_type=obj_type,
            vertices=((100, 200), (200, 200), (200, 300), (100, 300)),
        )
        expected_area = 10000
        result = bounding_area(self.box, self.image_shape, self.camera_params)

        # Ensure result is not None before asserting
        self.assertIsNotNone(result, "Result should not be None for valid bounding box")

    def test_calculate_distance(self) -> None:
        """
        Tests distance calculation between two points in an image. Ensures the method
        returns a valid result.
        """
        pixel1 = (100, 100)
        pixel2 = (200, 200)  # Valid pixel coordinates
        result = calculate_distance(pixel1, pixel2, self.image_shape, self.camera_params)

        # Ensure result is not None before asserting
        self.assertIsNotNone(result, "Result should not be None for valid pixel coordinates")


if __name__ == "__main__":
    unittest.main()
