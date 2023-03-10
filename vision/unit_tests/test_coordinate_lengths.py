"""
Testing vision.deskew.coordinate_lengths.py
"""

import unittest

import numpy as np

from vision.deskew.coordinate_lengths import latitude_length
from vision.deskew.coordinate_lengths import longitude_length


class TestCoordinates(unittest.TestCase):
    """
    Testing the coordinate lengths module
    """

    # Testing latitude_length

    # Tests the maximum possible latitude in degrees as an input to the latitude_length function
    def test_latitude_length_at_max_val(self) -> None:
        """
        Asserts that latitude_length returns expected value at maximum input (90 degrees)

        Returns
        -------
        None
        """
        max_input_in_degrees = 90
        max_input_in_radians: float = np.deg2rad(max_input_in_degrees)
        latitude_length_at_max_latitude: float = (
            111132.92
            - 559.82 * np.cos(2 * max_input_in_radians)
            + 1.175 * np.cos(4 * max_input_in_radians)
            - 0.0023 * np.cos(6 * max_input_in_radians)
        )
        function_return_at_max_latitude = latitude_length(max_input_in_degrees)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(latitude_length_at_max_latitude, function_return_at_max_latitude)

    # Tests the minimum possible latitude in degrees as an input to the latitude_length function
    def test_latitude_length_min_val(self) -> None:
        """
        Asserts that latitude_length returns expected value at minimum input (-90 degrees)

        Returns
        -------
        None
        """
        max_input_in_degrees = -90
        min_input_in_radians: float = np.deg2rad(max_input_in_degrees)
        latitude_length_at_min_latitude: float = (
            111132.92
            - 559.82 * np.cos(2 * min_input_in_radians)
            + 1.175 * np.cos(4 * min_input_in_radians)
            - 0.0023 * np.cos(6 * min_input_in_radians)
        )
        function_return_at_min_latitude = latitude_length(max_input_in_degrees)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(latitude_length_at_min_latitude, function_return_at_min_latitude)

    # Tests a basic input in degrees as an input to the latitude_length function
    def test_latitude_length_at_zero(self) -> None:
        """
        Asserts that latitude_length returns expected value at a basic input (0 degrees)

        Returns
        -------
        None
        """
        basic_input_in_degrees = 0
        basic_input_in_radians: float = np.deg2rad(basic_input_in_degrees)
        latitude_length_at_zero_degrees_latitude: float = (
            111132.92
            - 559.82 * np.cos(2 * basic_input_in_radians)
            + 1.175 * np.cos(4 * basic_input_in_radians)
            - 0.0023 * np.cos(6 * basic_input_in_radians)
        )
        function_return_at_zero_degrees_latitude = latitude_length(basic_input_in_radians)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(
            latitude_length_at_zero_degrees_latitude, function_return_at_zero_degrees_latitude
        )

    # Testing longitude_length

    # Tests the maximum possible latitude in degrees as an input to the latitude_length function
    def test_longitude_length_at_max_val(self) -> None:
        """
        Asserts that longitude_length returns expected value at maximum input (90 degrees)

        Returns
        -------
        None
        """
        max_input_in_degrees = 90
        max_input_in_radians: float = np.deg2rad(max_input_in_degrees)
        longitude_length_at_max_latitude: float = (
            111412.84 * np.cos(max_input_in_radians)
            - 93.5 * np.cos(3 * max_input_in_radians)
            + 0.118 * np.cos(5 * max_input_in_radians)
        )
        function_return_at_max_latitude = longitude_length(max_input_in_degrees)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(longitude_length_at_max_latitude, function_return_at_max_latitude)

    # Tests the minimum possible latitude in degrees as an input to the latitude_length function
    def test_longitude_length_min_val(self) -> None:
        """
        Asserts that longitude_length returns expected value at minimum input (-90 degrees)

        Returns
        -------
        None
        """
        max_input_in_degrees = -90
        min_input_in_radians: float = np.deg2rad(max_input_in_degrees)
        longitude_length_at_min_latitude: float = (
            111412.84 * np.cos(min_input_in_radians)
            - 93.5 * np.cos(3 * min_input_in_radians)
            + 0.118 * np.cos(5 * min_input_in_radians)
        )
        function_return_at_min_latitude = longitude_length(max_input_in_degrees)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(longitude_length_at_min_latitude, function_return_at_min_latitude)

    # Tests a basic input in degrees as an input to the latitude_length function
    def test_longitude_length_at_zero(self) -> None:
        """
        Asserts that longitude_length returns expected value at a basic input (0 degrees)

        Returns
        -------
        None
        """
        basic_input_in_degrees = 0
        basic_input_in_radians: float = np.deg2rad(basic_input_in_degrees)
        longitude_length_at_zero_degrees_latitude: float = (
            111412.84 * np.cos(basic_input_in_radians)
            - 93.5 * np.cos(3 * basic_input_in_radians)
            + 0.118 * np.cos(5 * basic_input_in_radians)
        )
        function_return_at_zero_degrees_latitude = longitude_length(basic_input_in_radians)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(
            longitude_length_at_zero_degrees_latitude, function_return_at_zero_degrees_latitude
        )


if __name__ == "__main__":
    unittest.main()  # add "verbosity=2" in the parameters to main here for more detailed output
