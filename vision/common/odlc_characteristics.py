"""
Contains common objects/classes for use in the classification of the standard ODLC objects.
"""

from enum import Enum


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
