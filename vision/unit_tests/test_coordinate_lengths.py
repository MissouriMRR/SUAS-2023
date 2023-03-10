"""
Testing vision.deskew.coordinate_lengths.py
"""

import unittest

import numpy as np

from vision.deskew.coordinate_lengths import latitude_length
from vision.deskew.coordinate_lengths import longitude_length



class TestCoordinates(unittest.TestCase):
    #Testing latitude_length


    #Tests the maximum possible latitude in degrees as an input to the latitude_length function
    def test_latitude_length_at_max_val(self):
        MAX_INPUT_IN_DEGREES = 90 
        MAX_INPUT_IN_RADIANS: float = np.deg2rad(MAX_INPUT_IN_DEGREES)
        LATITUDE_LENGTH_AT_MAX_LATITUDE: float = ( 
            111132.92 
            - 559.82 * np.cos(2 * MAX_INPUT_IN_RADIANS) 
            + 1.175 * np.cos(4 * MAX_INPUT_IN_RADIANS) 
            - 0.0023 * np.cos(6 * MAX_INPUT_IN_RADIANS) 
        )
        FUNCTION_RETURN_AT_MAX_LATITUDE = latitude_length(MAX_INPUT_IN_DEGREES)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LATITUDE_LENGTH_AT_MAX_LATITUDE, FUNCTION_RETURN_AT_MAX_LATITUDE)
    
    #Tests the minimum possible latitude in degrees as an input to the latitude_length function
    def test_latitude_length_min_val(self):
        MIN_INPUT_IN_DEGREES = -90
        MIN_INPUT_IN_RADIANS: float = np.deg2rad(MIN_INPUT_IN_DEGREES)
        LATITUDE_LENGTH_AT_MIN_LATITUDE: float = (
            111132.92 
            - 559.82 * np.cos(2 * MIN_INPUT_IN_RADIANS)
            + 1.175 * np.cos(4 * MIN_INPUT_IN_RADIANS)
            - 0.0023 * np.cos(6 * MIN_INPUT_IN_RADIANS) 
        )
        FUNCTION_RETURN_AT_MIN_LATITUDE = latitude_length(MIN_INPUT_IN_DEGREES)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LATITUDE_LENGTH_AT_MIN_LATITUDE, FUNCTION_RETURN_AT_MIN_LATITUDE)

    #Tests a basic input in degrees as an input to the latitude_length function
    def test_latitude_length_at_zero(self):
        BASIC_INPUT_IN_DEGREES = 0
        BASIC_INPUT_IN_RADIANS: float = np.deg2rad(BASIC_INPUT_IN_DEGREES)
        LATITUDE_LENGTH_AT_ZERO_DEGREES_LATITUDE: float = (
            111132.92 
            - 559.82 * np.cos(2 * BASIC_INPUT_IN_RADIANS) 
            + 1.175 * np.cos(4 * BASIC_INPUT_IN_RADIANS)
            - 0.0023 * np.cos(6 * BASIC_INPUT_IN_RADIANS) 
        )
        FUNCTION_RETURN_AT_ZERO_DEGREES_LATITUDE = latitude_length(BASIC_INPUT_IN_RADIANS)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LATITUDE_LENGTH_AT_ZERO_DEGREES_LATITUDE, FUNCTION_RETURN_AT_ZERO_DEGREES_LATITUDE)

    #Testing longitude_length


    #Tests the maximum possible latitude in degrees as an input to the latitude_length function
    def test_longitude_length_at_max_val(self):
        MAX_INPUT_IN_DEGREES = 90 
        MAX_INPUT_IN_RADIANS: float = np.deg2rad(MAX_INPUT_IN_DEGREES)
        LONGITUDE_LENGTH_AT_MAX_LATITUDE: float = ( 
            111412.84 * np.cos(MAX_INPUT_IN_RADIANS)
            - 93.5 * np.cos(3 * MAX_INPUT_IN_RADIANS)
            + 0.118 * np.cos(5 * MAX_INPUT_IN_RADIANS)
        )
        FUNCTION_RETURN_AT_MAX_LATITUDE = longitude_length(MAX_INPUT_IN_DEGREES)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LONGITUDE_LENGTH_AT_MAX_LATITUDE, FUNCTION_RETURN_AT_MAX_LATITUDE)
    
    #Tests the minimum possible latitude in degrees as an input to the latitude_length function
    def test_longitude_length_min_val(self):
        MIN_INPUT_IN_DEGREES = -90
        MIN_INPUT_IN_RADIANS: float = np.deg2rad(MIN_INPUT_IN_DEGREES)
        LONGITUDE_LENGTH_AT_MIN_LATITUDE: float = (
            111412.84 * np.cos(MIN_INPUT_IN_RADIANS)
            - 93.5 * np.cos(3 * MIN_INPUT_IN_RADIANS)
            + 0.118 * np.cos(5 * MIN_INPUT_IN_RADIANS)
        )
        FUNCTION_RETURN_AT_MIN_LATITUDE = longitude_length(MIN_INPUT_IN_DEGREES)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LONGITUDE_LENGTH_AT_MIN_LATITUDE, FUNCTION_RETURN_AT_MIN_LATITUDE)

    #Tests a basic input in degrees as an input to the latitude_length function
    def test_longitude_length_at_zero(self):
        BASIC_INPUT_IN_DEGREES = 0
        BASIC_INPUT_IN_RADIANS: float = np.deg2rad(BASIC_INPUT_IN_DEGREES)
        LONGITUDE_LENGTH_AT_ZERO_DEGREES_LATITUDE: float = (
            111412.84 * np.cos(BASIC_INPUT_IN_RADIANS)
            - 93.5 * np.cos(3 * BASIC_INPUT_IN_RADIANS)
            + 0.118 * np.cos(5 * BASIC_INPUT_IN_RADIANS)
        )
        FUNCTION_RETURN_AT_ZERO_DEGREES_LATITUDE = longitude_length(BASIC_INPUT_IN_RADIANS)
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(LONGITUDE_LENGTH_AT_ZERO_DEGREES_LATITUDE, FUNCTION_RETURN_AT_ZERO_DEGREES_LATITUDE)


if __name__ == '__main__':
    unittest.main() #add "verbosity=2" in the parameters to main here for more detailed output