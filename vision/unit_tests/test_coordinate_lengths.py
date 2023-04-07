"""
Testing vision.deskew.coordinate_lengths.py
"""

import unittest
import numpy as np

from vision.deskew.coordinate_lengths import latitude_length
from vision.deskew.coordinate_lengths import longitude_length


class TestLongitudeLength(unittest.TestCase):
    """
    Testing the longitude_length function from the coordinate lengths module
    """

    def test_max_val(self) -> None:
        """
        Asserts that longitude_length returns expected value and return type at maximum input
        (90 degrees)
        """
        max_latitude_deg: float = 90.0
        max_latitude_rad: float = np.deg2rad(max_latitude_deg)
        expected_longitude_length: float = (
            111412.84 * np.cos(max_latitude_rad)
            - 93.5 * np.cos(3 * max_latitude_rad)
            + 0.118 * np.cos(5 * max_latitude_rad)
        )
        resulting_longitude_length: float = longitude_length(max_latitude_deg)

        # Testing data types of parameters and return
        self.assertIsInstance(max_latitude_deg, float, "max_latitude_deg parameter is not a float")
        self.assertIsInstance(
            resulting_longitude_length, float, "return from longitude_length is not a float"
        )
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_longitude_length, resulting_longitude_length)

    def test_min_val(self) -> None:
        """
        Asserts that longitude_length returns expected value and return type at minimum input
        (-90 degrees)
        """
        min_latitude_deg: float = -90.0
        min_latitude_rad: float = np.deg2rad(min_latitude_deg)
        expected_longitude_length: float = (
            111412.84 * np.cos(min_latitude_rad)
            - 93.5 * np.cos(3 * min_latitude_rad)
            + 0.118 * np.cos(5 * min_latitude_rad)
        )
        resulting_longitude_length: float = longitude_length(min_latitude_deg)

        # Testing data types of parameters and return
        self.assertIsInstance(min_latitude_deg, float, "min_latitude_deg is not a float")
        self.assertIsInstance(
            resulting_longitude_length, float, "resulting_longitude_length is not a float"
        )
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_longitude_length, resulting_longitude_length)

    def test_at_zero(self) -> None:
        """
        Asserts that longitude_length returns expected value and return type at a basic input
        (0 degrees)
        """
        basic_latitude_deg: float = 0.0
        basic_latitude_rad: float = np.deg2rad(basic_latitude_deg)
        expected_longitude_length: float = (
            111412.84 * np.cos(basic_latitude_rad)
            - 93.5 * np.cos(3 * basic_latitude_rad)
            + 0.118 * np.cos(5 * basic_latitude_rad)
        )
        resulting_longitude_length: float = longitude_length(basic_latitude_rad)

        # Testing data types of parameters and return
        self.assertIsInstance(basic_latitude_deg, float, "basic_latitude_deg is not a float")
        self.assertIsInstance(
            resulting_longitude_length, float, "resulting_longitude_length is not a float"
        )
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_longitude_length, resulting_longitude_length)


class TestLatitudeLength(unittest.TestCase):
    """
    Testing the latitude_length function from the coordinate lengths module
    """

    def test_max_val(self) -> None:
        """
        Asserts that latitude_length returns expected value and return type at maximum input
        (90 degrees)
        """
        max_latitude_deg: float = 90.0
        max_latitude_rad: float = np.deg2rad(max_latitude_deg)
        expected_latitude_length: float = (
            111132.92
            - 559.82 * np.cos(2 * max_latitude_rad)
            + 1.175 * np.cos(4 * max_latitude_rad)
            - 0.0023 * np.cos(6 * max_latitude_rad)
        )
        resulting_latitude_length: float = latitude_length(max_latitude_deg)

        # Testing data types of parameters and return
        self.assertIsInstance(max_latitude_deg, float, "max_latitude_degis not a float")
        self.assertIsInstance(
            resulting_latitude_length, float, "resulting_latitude_length is not a float"
        )
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_latitude_length, resulting_latitude_length)

    def test_min_val(self) -> None:
        """
        Asserts that latitude_length returns expected value and return type at minimum input
        (-90 degrees)
        """
        min_latitude_deg: float = -90.0
        min_latitude_rad: float = np.deg2rad(min_latitude_deg)
        expected_latitude_length: float = (
            111132.92
            - 559.82 * np.cos(2 * min_latitude_rad)
            + 1.175 * np.cos(4 * min_latitude_rad)
            - 0.0023 * np.cos(6 * min_latitude_rad)
        )
        resulting_latitude_length: float = latitude_length(min_latitude_deg)

        # Testing data types of parameters and return
        self.assertIsInstance(min_latitude_deg, float, "min_latitude_deg is not a float")
        self.assertIsInstance(
            resulting_latitude_length, float, "resulting_latitude_length is not a float"
        )
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_latitude_length, resulting_latitude_length)

    def test_at_zero(self) -> None:
        """
        Asserts that latitude_length returns expected value and return type at a basic input
        (0 degrees)
        """
        basic_latitude_deg: float = 0.0
        basic_latitude_rad: float = np.deg2rad(basic_latitude_deg)
        expected_latitude_length: float = (
            111132.92
            - 559.82 * np.cos(2 * basic_latitude_rad)
            + 1.175 * np.cos(4 * basic_latitude_rad)
            - 0.0023 * np.cos(6 * basic_latitude_rad)
        )
        resulting_latitude_length: float = latitude_length(basic_latitude_rad)

        # Testing data types of parameters and return
        self.assertIsInstance(basic_latitude_deg, float, "min_latitude_deg is not a float")
        self.assertIsInstance(resulting_latitude_length, float, "min_latitude_deg is not a float")
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(expected_latitude_length, resulting_latitude_length)


if __name__ == "__main__":
    unittest.main()
