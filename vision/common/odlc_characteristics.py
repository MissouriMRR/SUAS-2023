"""
Contains common objects/classes for use in the classification of the standard ODLC objects.
"""

from enum import Enum

import numpy as np

from nptyping import NDArray, Shape, UInt8


class ODLCShapes(str, Enum):
    """
    An enumeration of all valid shapes for standard ODLC objects.
    """

    CIRCLE = "Circle"
    SEMICIRCLE = "Semicircle"
    QUARTER_CIRCLE = "Quarter circle"
    TRIANGLE = "Triangle"
    SQUARE = "Square"
    RECTANGLE = "Rectangle"
    TRAPEZOID = "Trapezoid"
    PENTAGON = "Pentagon"
    HEXAGON = "Hexagon"
    HEPTAGON = "Heptagon"
    OCTAGON = "Octagon"
    STAR = "Star"
    CROSS = "Cross"


class ODLCColors(str, Enum):
    """
    An enumeration of all valid colors for standard ODLC objects.
    """

    WHITE = "White"
    BLACK = "Black"
    GRAY = "Gray"
    RED = "Red"
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"
    PURPLE = "Purple"
    BROWN = "Brown"
    ORANGE = "Orange"


# Ranges of the colors in HSV color space
COLOR_RANGES: dict[ODLCColors, NDArray[Shape["*, 2, 3"], UInt8]] = {
    ODLCColors.WHITE: np.array([[[180, 18, 255], [0, 0, 231]]]),
    ODLCColors.BLACK: np.array([[[180, 255, 30], [0, 0, 0]]]),
    ODLCColors.GRAY: np.array([[[180, 18, 230], [0, 0, 40]]]),
    ODLCColors.RED: np.array(
        [[[180, 255, 255], [159, 50, 70]], [[9, 255, 255], [0, 50, 70]]]
    ),  # red wraps around and needs 2 ranges
    ODLCColors.BLUE: np.array([[[128, 255, 255], [90, 50, 70]]]),
    ODLCColors.GREEN: np.array([[[89, 255, 255], [36, 50, 70]]]),
    ODLCColors.YELLOW: np.array([[[35, 255, 255], [25, 50, 70]]]),
    ODLCColors.PURPLE: np.array([[[158, 255, 255], [129, 50, 70]]]),
    ODLCColors.BROWN: np.array([[[20, 255, 180], [10, 100, 120]]]),
    ODLCColors.ORANGE: np.array([[[24, 255, 255], [10, 50, 70]]]),
}
