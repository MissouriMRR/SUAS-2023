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
    def test_range(self) -> None:
        """
        Assert that the longitude_length function returns a value within a distance in meters 
        of the longitude length of the competition's coordinates
        """

        ERROR_DISTANCE: float = 1.0
        competition_longitude_length: float = 87454.68442825315 # longitude length at the competition
        competition_latitude = 38.31559695573465 # latitude of the competition
       
        actual_longitude_length: float = longitude_length(competition_latitude)

        self.assertTrue((competition_longitude_length - ERROR_DISTANCE) <= actual_longitude_length)
        self.assertTrue(actual_longitude_length <= (competition_longitude_length + ERROR_DISTANCE))



class TestLatitudeLength(unittest.TestCase):
    """
    Testing the latitude_length function from the coordinate lengths module
    """

    def test_range(self) -> None:
        """
        Assert that the latitude_length function returns a value within a distance in meters 
        of the latitude length of the competition's coordinates
        """
        ERROR_DISTANCE: float = 1.0
        competition_latitude_length: float = 111002.43151385868 # latitude length at the competition
        competition_latitude = 38.31559695573465 # latitude of the competition
       
        actual_latitude_length: float = latitude_length(competition_latitude)

        self.assertTrue((competition_latitude_length - ERROR_DISTANCE) <= actual_latitude_length)
        self.assertTrue(actual_latitude_length <= (competition_latitude_length + ERROR_DISTANCE))
        


if __name__ == "__main__":
    unittest.main()
