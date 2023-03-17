"""Functions for calculating locations and distances of objects in an image"""

import numpy as np

from vision.common.constants import Point, CameraParameters
from vision.common.bounding_box import BoundingBox

from vision.deskew import coordinate_lengths
from vision.deskew import vector_utils


def get_coordinates(
    pixel: tuple[int, int],
    image_shape: tuple[int, int, int] | tuple[int, int],
    camera_parameters: CameraParameters,
) -> tuple[float, float] | None:
    """
    Calculates the coordinates of the given pixel.
    Returns None if there is no valid intersect.

    Parameters
    ----------
    pixel: tuple[int, int]
        The coordinates of the pixel in [X, Y] form
    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    camera_parameters: CameraParameters
        The details on how and where the photo was taken
        focal_length : float
            The camera's focal length in millimeters
        rotation_deg: list[float]
            The rotation of the drone in degrees. The constant ROTATION_OFFSET of the
            camera, stored in constants.py, will be applied first
        drone_coordinates: list[float]
            The coordinates of the drone in degrees of (latitude, longitude)
        altitude_f: float
            The altitude of the drone in feet

    Returns
    -------
    pixel_coordinates : tuple[float, float] | None
        The (latitude, longitude) coordinates of the pixel in degrees.
        Equal to None if there is no valid intersect.
    """

    # Calculate the latitude and longitude lengths (in meters)
    latitude_length: float = coordinate_lengths.latitude_length(
        camera_parameters["drone_coordinates"][0]
    )
    longitude_length: float = coordinate_lengths.longitude_length(
        camera_parameters["drone_coordinates"][0]
    )

    # Convert feet to meters
    altitude_m: float = camera_parameters["altitude_f"] * 0.3048

    # Find the pixel's intersect with the ground to get the location relative to the drone
    intersect: Point | None = vector_utils.pixel_intersect(
        pixel,
        image_shape,
        camera_parameters["focal_length"],
        camera_parameters["rotation_deg"],
        altitude_m,
    )

    if intersect is None:
        return None

    # Invert the X axis so that the longitude is correct
    intersect[1] *= -1

    # Convert the location to latitude and longitude and add it to the drone's coordinates
    pixel_lat: float = camera_parameters["drone_coordinates"][0] + intersect[0] / latitude_length
    pixel_lon: float = camera_parameters["drone_coordinates"][1] + intersect[1] / longitude_length

    return pixel_lat, pixel_lon


def bounding_area(
    box: BoundingBox,
    image_shape: tuple[int, int, int] | tuple[int, int],
    camera_parameters: CameraParameters,
) -> float | None:
    """
    Calculates the area in feet of the bounding box on the ground

    Parameters
    ----------
    box: BoundingBox
        The bounding box of the object
    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    camera_parameters: CameraParameters
        The details on how and where the photo was taken
        focal_length : float
            The camera's focal length in millimeters
        rotation_deg: list[float]
            The rotation of the drone in degrees. The constant ROTATION_OFFSET of the
            camera, stored in constants.py, will be applied first
        drone_coordinates: list[float]
            The coordinates of the drone. Not used in this function.
        altitude_f: float
            The altitude of the drone in feet

    Returns
    -------
    area : float | None
        The area of the bounding box in feet.
        Returns None if one or both of the points did not have an intersection
    """

    # Calculate the distance from the top left vertex to the top right vertex
    width_length: float | None = calculate_distance(
        box.vertices[0], box.vertices[1], image_shape, camera_parameters
    )

    # Calculate the distance from the top left vertex to the bottom left vertex
    height_length: float | None = calculate_distance(
        box.vertices[0], box.vertices[3], image_shape, camera_parameters
    )

    if height_length is None or width_length is None:
        return None

    return width_length * height_length


def calculate_distance(
    pixel1: tuple[int, int],
    pixel2: tuple[int, int],
    image_shape: tuple[int, int, int] | tuple[int, int],
    camera_parameters: CameraParameters,
) -> float | None:
    """
    Calculates the physical distance between two points on the ground represented by pixel
    locations. Units of `distance` will be in feet

    Parameters
    ----------
    pixel1, pixel2: tuple[int, int]
        The two input pixel locations in [X,Y] form. The distance between them will be calculated

    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    camera_parameters: CameraParameters
        The details on how and where the photo was taken
        focal_length : float
            The camera's focal length in millimeters
        rotation_deg: list[float]
            The rotation of the drone in degrees. The constant ROTATION_OFFSET of the
            camera, stored in constants.py, will be applied first
        drone_coordinates: list[float]
            The coordinates of the drone. Not used in this function.
        altitude_f: float
            The altitude of the drone in feet

    Returns
    -------
    distance : float | None
        The distance between the two pixels. Units are the same units as `altitude`
        Returns None if one or both of the points did not have an intersection
    """

    intersect1: Point | None = vector_utils.pixel_intersect(
        pixel1,
        image_shape,
        camera_parameters["focal_length"],
        camera_parameters["rotation_deg"],
        camera_parameters["altitude_f"],
    )

    intersect2: Point | None = vector_utils.pixel_intersect(
        pixel2,
        image_shape,
        camera_parameters["focal_length"],
        camera_parameters["rotation_deg"],
        camera_parameters["altitude_f"],
    )

    # Checks if the intersects were valid
    if intersect1 is None or intersect2 is None:
        return None

    # Calculate the distance between the two intersects
    distance: float = float(np.linalg.norm(intersect1 - intersect2))

    return distance
