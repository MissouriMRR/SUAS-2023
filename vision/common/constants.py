"""Constant variables and common type aliases for Vision"""

from typing import TypeAlias, TypedDict
from nptyping import NDArray, Shape, UInt8, Float64, IntC, Bool8

Image: TypeAlias = NDArray[Shape["*, *, 3"], UInt8]
# single channel image type
ScImage: TypeAlias = NDArray[Shape["*, *"], UInt8]
# single channel image of booleans
Mask: TypeAlias = NDArray[Shape["*, *"], Bool8]

Point: TypeAlias = NDArray[Shape["2"], Float64]
Vector: TypeAlias = NDArray[Shape["3"], Float64]

# return types for cv2.findContours() -> tuple[tuple[Contour, ...], Hierarchy]
Contour: TypeAlias = NDArray[Shape["*, 1, 2"], IntC]
Hierarchy: TypeAlias = NDArray[Shape["1, *, 4"], IntC]

# Format of Corners is: (top left, top right, bottom right, bottom left), or
#     1--2
#     |  |
#     4--3
Corners: TypeAlias = NDArray[Shape["4, 2"], Float64]


class Location(TypedDict):
    """
    A saved coordinate location - primarily used for ODLCs

    Attributes
    ----------
    latitude: float
        The latitude in degrees of the location
    longitude: float
        The longitude in degrees of the location
    """

    latitude: float
    longitude: float


# int is the number of the water bottle to drop
# Location is the coordinates of the standard object once found
ODLC_Dict: TypeAlias = dict[int, Location]


class CameraParameters(TypedDict):
    """
    The details on how and where a photo was taken

    Attributes
    ----------
    focal_length : float
        The camera's focal length in millimeters
    rotation_deg: list[float]
        The rotation of the drone/camera
    drone_coordinates: list[float]
        The coordinates of the drone in degrees of (latitude, longitude)
    altitude_f: float
        The altitude of the drone in feet
    """

    focal_length: float
    rotation_deg: list[float]
    drone_coordinates: list[float]
    altitude_f: float


# Sony RX100 VII sensor size in millimeters
SENSOR_WIDTH: float = 13.2
SENSOR_HEIGHT: float = 8.8

# The rotation offset of the camera to the drone. The offset is applied
#   in vision.vector_utils.pixel_intersect()
# In degrees of [roll, pitch, yaw]
# Set to [0.0, -90.0, 0.0] when the camera is facing directly downwards
ROTATION_OFFSET: list[float] = [0.0, -90.0, 0.0]
