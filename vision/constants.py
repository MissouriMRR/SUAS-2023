"""Constant variables and common type aliases for Vision"""

from typing import TypeAlias
from nptyping import NDArray, Shape, UInt8, Float64

Image: TypeAlias = NDArray[Shape["1080, 1920, 3"], UInt8]
Point: TypeAlias = NDArray[Shape["2"], Float64]
Vector: TypeAlias = NDArray[Shape["3"], Float64]

# Format of Corners is: (top left, top right, bottom right, bottom left), or
#     1--2
#     |  |
#     4--3
Corners: TypeAlias = NDArray[Shape["4, 2"], Float64]

# Sony RX100 VII sensor size
SENSOR_WIDTH: float = 13.2
SENSOR_HEIGHT: float = 8.8

# The rotation offset of the camera to the drone. The offset is applied in vision.vector_utils.pixel_intersect()
# In degrees of [roll, pitch, yaw]
# Set to [0.0, -90.0, 0.0] when the camera is facing directly downwards
ROTATION_OFFSET: Vector = [0.0, -90.0, 0.0]
