"""Functions that use vectors to calculate camera intersections with the ground"""

import numpy as np
from scipy.spatial.transform import Rotation
from nptyping import Float64

from vision.common.constants import Point, Vector, SENSOR_WIDTH, SENSOR_HEIGHT, ROTATION_OFFSET


# Vector pointing toward the +X axis, represents the camera's forward direction when the rotation
#   on all axes is 0
IHAT: Vector = np.array([1, 0, 0], dtype=np.float64)


def pixel_intersect(
    pixel: tuple[int, int],
    image_shape: tuple[int, int, int] | tuple[int, int],
    focal_length: float,
    rotation_deg: list[float],
    height: float,
) -> Point | None:
    """
    Finds the intersection [X,Y] of a given pixel with the ground relative to the camera.
    A camera with no rotation points in the +X direction and is centered at [0, 0, height].

    Parameters
    ----------
    pixel : tuple[int, int]
        The coordinates of the pixel in [Y, X] form
    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by image.shape when image is a numpy image array)
    focal_length : float
        The camera's focal length
    rotation_deg : list[float]
        The [roll, pitch, yaw] rotation in degrees
    height : float
        The height that the image was taken at. The units of the output will be the units of the
        input.

    Returns
    -------
    intersect : Point | None
        The coordinates [X,Y] where the pixel's vector intersects with the ground.
        Returns None if there is no intersect.
    """

    # Create the normalized vector representing the direction of the given pixel
    vector: Vector = pixel_vector(pixel, image_shape, focal_length)

    rotation_rad = np.deg2rad(rotation_deg).tolist()

    vector = euler_rotate(vector, rotation_rad)

    # Apply the constant rotation offset
    vector = euler_rotate(vector, ROTATION_OFFSET)

    intersect: Point | None = plane_collision(vector, height)

    return intersect


def plane_collision(ray_direction: Vector, height: float) -> Point | None:
    """
    Returns the point where a ray intersects the XY plane
    Returns None if there is no intersect.

    Parameters
    ----------
    ray_direction : Vector
        XYZ coordinates that represent the direction a ray faces from (0, 0, 0)
    height : float
        The Z coordinate for the starting height of the ray; can be any units

    Returns
    -------
    intersect : Point | None
        The ray's intersection with the plane in [X,Y] format
        Returns None if there is no intersect.

    """
    # Find the "time" at which the line intersects the plane
    # Line is defined as ray_direction * time + origin.
    # Origin is the point at X, Y, Z = (0, 0, height)

    intersect: Point | None = None

    time: Float64 = -height / ray_direction[2]

    # Checks if the ray intersects with the plane
    if np.isinf(time) or np.isnan(time) or time < 0:
        return intersect

    intersect = ray_direction[:2] * time

    return intersect


def pixel_vector(
    pixel: tuple[int, int], image_shape: tuple[int, int, int] | tuple[int, int], focal_length: float
) -> Vector:
    """
    Generates a vector representing the given pixel.
    Pixels are in row-major form [Y, X] to match numpy indexing.

    Parameters
    ----------
    pixel : tuple[int, int]
        The coordinates of the pixel in [Y, X] form
    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by image.shape when image is a numpy image array)
    focal_length : float
        The camera's focal length - used to generate the camera's fields of view

    Returns
    -------
    pixel_vector : Vector
        The vector that represents the direction of the given pixel
    """

    # Find the FOVs using the focal length
    fov_h: float
    fov_v: float
    fov_h, fov_v = focal_length_to_fovs(focal_length)

    return camera_vector(
        pixel_angle(fov_h, pixel[1] / image_shape[1]),
        pixel_angle(fov_v, pixel[0] / image_shape[0]),
    )


def pixel_angle(fov: float, ratio: float) -> float:
    """
    Calculates a pixel's angle from the center of the camera on a single axis. Analogous to the
    pixel's "fov"

    Only one component of the pixel is used here, call this function for each X and Y

    Parameters
    ----------
    fov : float
        The field of view of the camera in radians olong a given axis
    ratio : float
        The pixel's position as a ratio of the coordinate to the length of the image
        Example: For an image that is 1080 pixels wide, a pixel at position 270 would have a
        ratio of 0.25

    Returns
    -------
    angle : float
        The pixel's angle from the center of the camera along a single axis
    """
    return np.arctan(np.tan(fov / 2) * (1 - 2 * ratio))


def focal_length_to_fovs(focal_length: float) -> tuple[float, float]:
    """
    Converts a given focal length to the horizontal and vertical fields of view in radians

    Uses SENSOR_WIDTH and SENSOR_HEIGHT

    Parameters
    ----------
    focal_length: float
        The focal length of the camera in millimeters

    Returns
    -------
    fields_of_view : tuple[float, float]
        The fields of view in radians
        Format is [horizontal, vertical]
    """
    return get_fov(focal_length, SENSOR_WIDTH), get_fov(focal_length, SENSOR_HEIGHT)


def get_fov(focal_length: float, sensor_size: float) -> float:
    """
    Converts a given focal length and sensor length to the corresponding field of view in radians

    Parameters
    ----------
    focal_length : float
        The focal length of the camera in millimeters
    sensor_size:
        The sensor size along one axis in millimeters

    Returns
    -------
    fov : float
        The field of view in radians
    """

    return 2 * np.arctan(sensor_size / (2 * focal_length))


def camera_vector(h_angle: float, v_angle: float) -> Vector:
    """
    Generates a vector with an angle h_angle with the horizontal and an angle v_angle with the
    vertical.

    Using camera fovs will generate a vector that represents the corner of the camera's view.

    Parameters
    ----------
    h_angle : float
        The angle in radians to rotate horizontally
    v_angle : float
        The angle in radians to rotate vertically

    Returns
    -------
    camera_vector : Vector
        The vector which represents a given location in an image
    """

    # Calculate the vertical rotation needed for the final vector to have the desired direction
    edge: float = edge_angle(v_angle, h_angle)

    return euler_rotate(IHAT, [0, edge, -h_angle])


def edge_angle(v_angle: float, h_angle: float) -> float:
    """
    Finds the angle such that rotating by edge_angle on the Y axis then rotating by h_angle on
    the Z axis gives a vector an angle v_angle with the Y axis

    Can be derived using a square pyramid of height 1

    Parameters
    ----------
    v_angle : float
        The vertical angle
    h_angle : float
        The horizontal angle

    Returns
    -------
    edge_angle : float
        The angle to rotate vertically
    """

    return np.arctan(np.tan(v_angle) * np.cos(h_angle))


def euler_rotate(vector: Vector, rotation_rad: list[float]) -> Vector:
    """
    Rotates a vector based on a given roll, pitch, and yaw.

    Follows the MAVSDK.EulerAngle convention - positive roll is banking to the right, positive
    pitch is pitching nose up, positive yaw is clock-wise seen from above.

    Parameters
    ----------
    vector: Vector
        A vector represented by an XYZ coordinate that will be rotated
    rotation_deg: list[float]
        The [roll, pitch, yaw] rotation in radians

    Returns
    -------
    rotated_vector : Vector
        The vector which has been rotated
    """

    # Reverse the Y and Z rotation to match MAVSDK convention
    rotation_rad[1] *= -1
    rotation_rad[2] *= -1

    result: Vector = Rotation.from_euler("xyz", rotation_rad).apply(np.array(vector))

    return result
